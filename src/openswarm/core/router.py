"""
Open Swarm Intelligent Router
Local-first routing with automatic fallback and rate limit awareness
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import litellm
import yaml
from pydantic import BaseModel, Field

litellm.drop_params = True


class ModelProfile(BaseModel):
    name: str
    provider: str
    max_tokens: int
    purpose: str
    is_local: bool
    rate_limit_cooldown: int = 0
    fallback_to: str | None = None
    free_tier: bool = False
    last_429: datetime | None = None


class TaskAssessment(BaseModel):
    complexity: str
    domain: str
    requires_parallel: bool


class RouterConfig(BaseModel):
    strategy: str = "hybrid"
    default_local: bool = True
    enable_rate_limit_awareness: bool = True
    max_retries: int = 3
    fallback_on_429: bool = True
    purpose_mapping: dict[str, str] = Field(default_factory=dict)


class SwarmRouter:
    def __init__(self, config_path: str = "config/models.yaml"):
        self.config_path = Path(config_path)
        self.models: list[ModelProfile] = []
        self.config: RouterConfig | None = None
        self._load_config()

    def _load_config(self):
        """Load router configuration from YAML"""
        with open(self.config_path) as f:
            data = yaml.safe_load(f)

        self.models = [ModelProfile(**model_data) for model_data in data.get("models", [])]

        router_data = data.get("router", {})
        self.config = RouterConfig(**router_data)

    async def assess_task(self, task_description: str) -> TaskAssessment:
        """
        Use a tiny local model to classify the task.
        In production, this would use semantic classification.
        """
        # Simplified assessment - in production use actual LLM classification
        task_lower = task_description.lower()

        # Heuristic classification
        if any(
            word in task_lower for word in ["explore", "find", "search", "list", "grep", "read"]
        ):
            domain = "exploration"
            complexity = "low"
        elif any(
            word in task_lower for word in ["refactor", "rewrite", "implement", "code", "function"]
        ):
            domain = "coding"
            complexity = "medium"
        elif any(word in task_lower for word in ["architecture", "design", "plan", "strategy"]):
            domain = "architecture"
            complexity = "high"
        elif any(word in task_lower for word in ["test", "verify", "validate", "critique"]):
            domain = "testing"
            complexity = "medium"
        else:
            domain = "coding"
            complexity = "medium"

        # Check if parallel execution is beneficial
        requires_parallel = any(
            word in task_lower for word in ["multiple", "parallel", "simultaneous", "several"]
        )

        return TaskAssessment(
            complexity=complexity, domain=domain, requires_parallel=requires_parallel
        )

    def _get_target_purpose(self, assessment: TaskAssessment) -> str:
        """Map task assessment to model purpose"""
        if assessment.domain == "exploration":
            return "fast"
        elif assessment.domain == "testing":
            return "critique"
        elif assessment.complexity == "low":
            return "fast"
        elif assessment.complexity == "high":
            return "reasoning"
        else:
            return "coding"

    def _filter_available_models(self, purpose: str) -> list[ModelProfile]:
        """Filter models by purpose and rate limit status"""
        candidates = [m for m in self.models if m.purpose == purpose]

        # Filter out rate-limited models
        if self.config and self.config.enable_rate_limit_awareness:
            now = datetime.now()
            candidates = [
                m
                for m in candidates
                if m.last_429 is None or now - m.last_429 > timedelta(seconds=m.rate_limit_cooldown)
            ]

        # Prioritize local models
        if self.config and self.config.default_local:
            candidates.sort(key=lambda m: m.is_local, reverse=True)

        return candidates

    async def route_task(self, task_description: str) -> str:
        """
        Select the best model based on assessment and availability.
        Returns model name.
        """
        assessment = await self.assess_task(task_description)
        target_purpose = self._get_target_purpose(assessment)

        candidates = self._filter_available_models(target_purpose)

        if not candidates:
            # Fallback to any model with the purpose
            print(f"[Router] No available models for purpose {target_purpose}, trying fallbacks")
            candidates = [m for m in self.models if m.purpose == target_purpose]

        if not candidates:
            raise ValueError(f"No models available for purpose {target_purpose}")

        best_model = candidates[0]

        print(
            f"[Router] Task assessed as {assessment.complexity}/{assessment.domain}. "
            f"Routing to: {best_model.name} (local={best_model.is_local})"
        )

        return best_model.name

    async def route_with_fallback(self, task_description: str) -> str:
        """Route with automatic fallback on failure"""
        max_retries = self.config.max_retries if self.config else 3

        for attempt in range(max_retries):
            try:
                model_name = await self.route_task(task_description)
                # In production, would test model availability here
                return model_name
            except Exception as e:
                print(f"[Router] Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    # Mark model as rate limited and retry
                    continue
                raise

        raise RuntimeError(f"Failed to route task after {max_retries} attempts")

    def mark_429(self, model_name: str):
        """Mark a model as rate limited"""
        for model in self.models:
            if model.name == model_name:
                model.last_429 = datetime.now()
                print(f"[Router] Marked {model_name} as rate limited")
                break

    def get_model_stats(self) -> dict[str, Any]:
        """Get statistics about available models"""
        stats = {
            "total": len(self.models),
            "local": sum(1 for m in self.models if m.is_local),
            "cloud_free": sum(1 for m in self.models if not m.is_local and m.free_tier),
            "by_purpose": {},
        }

        for model in self.models:
            purpose = model.purpose
            if purpose not in stats["by_purpose"]:
                stats["by_purpose"][purpose] = 0
            stats["by_purpose"][purpose] += 1

        return stats


# Singleton router instance
_router_instance: SwarmRouter | None = None


def get_router() -> SwarmRouter:
    """Get or create router singleton"""
    global _router_instance
    if _router_instance is None:
        _router_instance = SwarmRouter()
    return _router_instance


async def route_task(task_description: str) -> str:
    """Convenience function for routing tasks"""
    router = get_router()
    return await router.route_with_fallback(task_description)
