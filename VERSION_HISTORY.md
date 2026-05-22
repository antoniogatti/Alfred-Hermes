# Version History

## 1.4 | 2026-05-22 22:55 UTC | HomeWimpy Config Ready for Versioning

- Added the first HomeWimpy Home Assistant config files to the repository (`configuration.yaml`, automations, scenes, scripts, blueprints, and start wrapper).
- Expanded `.gitignore` to exclude Home Assistant runtime state inside `config/.storage/`, logs, `.HA_VERSION`, and database files.
- Kept the installation assets trackable while leaving generated state out of git.

## 1.3 | 2026-05-22 22:40 UTC | HomeWimpy Home Assistant Installed

- Installed the HomeWimpy Home Assistant instance under `_vm_tools/HomeWimpy/` and documented the local start/stop workflow.
- Added `.gitignore` rules for HomeWimpy runtime artifacts so the venv, logs, database, storage, and cache files stay out of git.
- Kept the HomeWimpy configuration directory visible for intentional versioning of the actual Home Assistant setup.

## 1.2 | 2026-05-22 22:10 UTC | Profile Scope Split and Skill Reassignment

- Moved the highlighted Palazzo Pinto operational scope out of Alfred and into the Palazzopinto profile guardrails.
- Reassigned local skills so `alloggiati-web-polizia`, `azure-cost-monitoring`, `hermes-gateway-telegram-setup`, and `palazzopinto-bnb-operations` belong to Palazzopinto, while Alfred keeps the weather-oriented skill set.
- Installed `browse-sh/windy.com/geo-weather-fetch-w3o49h` on Alfred for wind and forecast lookups.
- Added a persistent operational rule to restart active Hermes gateways after profile changes.

## 1.1 | 2026-05-22 17:48 UTC | Agent/Profile Alignment and Groq Auth Stabilization

- Fixed Groq authentication consistency across profiles and validated `default`, `alfred`, and `palazzopinto` with successful API checks.
- Updated Hermes runtime configuration to use environment-based Groq credentials to avoid stale hardcoded keys and immediate fallback.
- Renamed the workspace agent folder from `_vm_agents/hermes` to `_vm_agents/alfred`.
- Set `alfred` as the sticky default Hermes profile and updated local profile path references to the renamed agent directory.
