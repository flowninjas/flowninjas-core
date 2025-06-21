#!/bin/bash

# Start script for FlowNinjas Core API
set -e

echo "Starting FlowNinjas Core API..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

# Install development dependencies if in development mode
if [ "${ENVIRONMENT:-development}" = "development" ]; then
    echo "Installing development dependencies..."
    uv pip install -e ".[dev]"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env file with your configuration"
fi

# Create generated_workflows directory
mkdir -p generated_workflows

# Start the application
echo "Starting the API server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
