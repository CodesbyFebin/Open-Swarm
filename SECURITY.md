# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report vulnerabilities by emailing: security@openswarm.dev

Or use GitHub's private vulnerability reporting feature.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- Initial response within 48 hours
- Regular updates on investigation
- Public disclosure after fix is released

## Security Best Practices

When using Open Swarm:
- Run in isolated environment with Docker
- Review playbooks before execution
- Use human approval gates for destructive operations
- Keep models updated
- Never expose API without authentication in production

## Safe Defaults

Open Swarm is designed with safety in mind:
- Docker sandboxing by default
- Read-only mounts for scout/critic agents
- Human approval gates for destructive operations
- Comprehensive audit logging
