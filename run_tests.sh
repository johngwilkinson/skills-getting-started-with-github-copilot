#!/bin/bash

# Test runner script for the High School Management System API

echo "🧪 Running FastAPI Tests..."
echo "=================================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing -v

echo ""
echo "✅ Test run completed!"
echo ""
echo "To run tests manually:"
echo "  pytest tests/ -v                    # Basic test run"
echo "  pytest tests/ --cov=src            # With coverage"
echo "  pytest tests/test_api.py -v        # Specific test file"
echo "  pytest -k test_signup -v           # Tests matching pattern"