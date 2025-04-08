#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run the application
echo "Starting Abico Avatar Generator..."
python app.py

# Deactivate virtual environment when done
deactivate 