#!/usr/bin/env bash
# Run this game backend locally (FastAPI/uvicorn).
#   ./start.sh            -> HTTP server on 0.0.0.0:50055
#   PORT=50060 ./start.sh -> HTTP server on 0.0.0.0:50060
# Needs a Redis instance (defaults to redis://localhost:6379/0) and, to appear
# in the web, WEB_REGISTRY_URL + GAME_PUBLIC_URL pointing at the right places.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "No .venv found. Create it with:" >&2
    echo "  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
    exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export WEB_REGISTRY_URL="${WEB_REGISTRY_URL:-http://localhost:8000}"
export GAME_PUBLIC_URL="${GAME_PUBLIC_URL:-http://localhost:${PORT:-50055}}"

exec python run.py
