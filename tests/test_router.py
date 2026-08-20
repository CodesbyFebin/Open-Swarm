"""
Tests for Open Swarm router
"""

import sys
from pathlib import Path

# Add src to path for tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openswarm.core.router import SwarmRouter


def test_router_load():
    router = SwarmRouter("config/models.yaml")
    assert len(router.models) > 0
    assert router.config is not None


def test_model_filtering():
    router = SwarmRouter("config/models.yaml")
    fast_models = router._filter_available_models("fast")
    assert len(fast_models) > 0
    # Should prioritize local
    assert fast_models[0].is_local


def test_task_assessment():
    import asyncio

    router = SwarmRouter("config/models.yaml")

    async def run_test():
        assessment = await router.assess_task("Explore codebase for bugs")
        assert assessment.domain == "exploration"
        assert assessment.complexity == "low"

    asyncio.run(run_test())


if __name__ == "__main__":
    test_router_load()
    test_model_filtering()
    test_task_assessment()
    print("All tests passed!")
