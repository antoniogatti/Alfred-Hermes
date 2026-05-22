# HomeWimpy - Home Assistant Instance

Home Assistant Core 2024.3.3 for the "HomeWimpy" smart home.

## Paths

- Install:  _vm_tools/HomeWimpy/
- Venv:     _vm_tools/HomeWimpy/venv/
- Config:   _vm_tools/HomeWimpy/config/
- Logs:     _vm_tools/HomeWimpy/home-assistant.log

## Start / Stop

Start (background):
  ./start.sh &

Or directly:
  ./venv/bin/hass -c ./config

Stop:
  pkill -f "HomeWimpy/venv/bin/hass"

## Access

URL:  http://localhost:8123
      http://<VM-IP>:8123   (if port 8123 open on NSG/firewall)

First time: create an admin account via the onboarding wizard.

## Notes

- Python 3.11 venv (3.12 recommended for future upgrades)
- josepy pinned to 1.14.0 to avoid acme/nabucasa compatibility issue
- mobile_app integration disabled (cloud dependency conflict)
- Configuration: config/configuration.yaml
  - Name: HomeWimpy
  - Timezone: Europe/Rome
  - Location: Brindisi area (update lat/lon in configuration.yaml)
  - Language: Italian
