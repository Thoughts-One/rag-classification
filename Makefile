# Makefile for RAG Classification Service local development

.PHONY: setup install run test clean verify help

# Default target
help:
	@echo "RAG Classification Service - Development Commands"
	@echo
	@echo "First time setup:"
	@echo "  make setup     - Install dependencies and verify setup (recommended first step)"
	@echo
	@echo "Development:"
	@echo "  make run       - Start local development server"
	@echo "  make test      - Run all tests"
	@echo "  make verify    - Verify local setup is working"
	@echo
	@echo "Maintenance:"
	@echo "  make clean     - Clean temporary files"
	@echo "  make help      - Show this help message"

# First-time setup (recommended)
setup:
	@echo "=== Initial Setup ==="
	@echo "1. Installing dependencies..."
	uv pip install -r requirements.txt
	@echo "2. Running full setup..."
	chmod +x setup_local.sh && ./setup_local.sh
	@echo
	@echo "Setup complete! Run 'make verify' to confirm everything is working, or 'make run' to start the server."

# Alias for backward compatibility
install: setup

# Start development server
run:
	@echo "Starting local development server..."
	source venv/bin/activate && python3 local_dev.py

# Run tests
test:
	@echo "Running tests..."
	source venv/bin/activate && pytest3 test/

# Verify setup
verify:
	@echo "Verifying local setup..."
	@echo "Starting server in background for verification..."
	source venv/bin/activate && python3 local_dev.py &
	SERVER_PID=$$!
	@echo "Waiting for server to start..."
	sleep 1 # Give a moment for the process to register
	@echo "Waiting for server to be ready..."
	./scripts/wait-for-it.sh localhost:8000 -t 30 -- echo "Server is up!" || (echo "Server did not start in time. Exiting." && kill $$SERVER_PID && exit 1)
	@echo "Running verification tests..."
	source venv/bin/activate && python3 test_local_setup.py
	@echo "Stopping server..."
	# Find and kill the process listening on port 8000
	LSOF_PID=$$(lsof -t -i:8000) ; \
	if [ -n "$$LSOF_PID" ]; then \
		kill $$LSOF_PID || true ; \
		echo "Killed process $$LSOF_PID listening on port 8000." ; \
	else \
		echo "No process found listening on port 8000." ; \
	fi
	@echo "Verification complete."

# Clean temporary files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ .pytest_cache
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete