#!/bin/bash
# Start Home Assistant - HomeWimpy
BASE="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH=""
exec "$BASE/venv/bin/hass" -c "$BASE/config" "$@"
