#!/bin/bash

set -e  # Exit on error

echo "=== RAG Classification Service Local Setup ==="
echo

# Verify Python version
echo "Checking Python version..."
python --version | grep -q "Python 3" || {
    echo "ERROR: Python 3.9+ is required"
    exit 1
}

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv || {
    echo "ERROR: Failed to create virtual environment"
    exit 1
}
source venv/bin/activate

# Install dependencies
echo "Installing dependencies from requirements-local.txt..."
uv pip install --upgrade pip || {
    echo "ERROR: Failed to upgrade pip"
    exit 1
}

uv pip install -r requirements.txt || {
    echo "ERROR: Failed to install dependencies"
    echo "Please ensure you have all build dependencies installed"
    exit 1
}

# Verify key dependencies
echo "Verifying key dependencies..."
python -c "import httpx, uvicorn" || {
    echo "ERROR: Critical dependencies not installed"
    exit 1
}

# Copy .env.local to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.local .env
    echo "Created .env file from template. Please edit with your configuration."
else
    echo "Using existing .env file"
fi

echo
echo "=== Setup Complete ==="
echo
echo "To start the development server:"
echo "  make run"
echo "Or:"
echo "  source venv/bin/activate && python local_dev.py"