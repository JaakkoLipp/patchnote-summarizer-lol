#!/bin/bash

# League of Legends Patch Notes API dev runner
# Check if not already in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  source .venv/bin/activate
fi
fastapi dev main.py
