# Version History

## 1.1 | 2026-05-22 17:48 UTC | Agent/Profile Alignment and Groq Auth Stabilization

- Fixed Groq authentication consistency across profiles and validated `default`, `alfred`, and `palazzopinto` with successful API checks.
- Updated Hermes runtime configuration to use environment-based Groq credentials to avoid stale hardcoded keys and immediate fallback.
- Renamed the workspace agent folder from `_vm_agents/hermes` to `_vm_agents/alfred`.
- Set `alfred` as the sticky default Hermes profile and updated local profile path references to the renamed agent directory.
