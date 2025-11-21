#!/bin/bash

# Test runner script for spendee-python-client

echo "Running Spendee Python Client tests..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create one with EMAIL and PASSWORD variables."
    exit 1
fi

# Activate the python virtual environment
source .venv/bin/activate

# Run pytest with appropriate options
python -m pytest tests/ -v --tb=short

echo "Tests completed."
