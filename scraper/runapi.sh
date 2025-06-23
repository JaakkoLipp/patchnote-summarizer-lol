#!/bin/bash

# League of Legends Patch Notes API dev runner
# Check if not already in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  source .venv/bin/activate
fi
# Function to handle keyboard interrupt
cleanup() {
  echo -e "\nKeyboard interrupt detected. Cleaning up..."
  deactivate  # Deactivate the virtual environment
  exit 0
}

# Trap Ctrl+C (SIGINT) and call the cleanup function
trap cleanup SIGINT

# Run the original command
fastapi dev main.py

# Deactivate virtual environment if the command exits normally
deactivate
