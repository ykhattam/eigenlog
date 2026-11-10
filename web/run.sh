#!/usr/bin/env bash
# Start eigenlog web UI (localhost only).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.."

if [ ! -d .venv ]; then
  echo "Creating venv…"
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

echo "-> Eigenlog web at http://127.0.0.1:5000 (loopback only)"
echo "-> Make sure llama-server is running on http://127.0.0.1:8080"
python web/app.py
