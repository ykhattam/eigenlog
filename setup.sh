#!/usr/bin/env bash
set -e
echo "Setting up Eigenlog virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Setup complete! Run 'source .venv/bin/activate' and then 'python interactive_mind.py'."
