# FastAPI Tests

Tests for the High School Management System API.

## Running Tests

```bash
# Basic run
pytest tests/ -v

# With coverage
pytest tests/ --cov=src

# Using script
./run_tests.sh
```

## Test Files

- **`test_api.py`** - Core API endpoints (GET /activities, POST signup, DELETE unregister)
- **`test_validation.py`** - Input validation and edge cases
- **`test_error_handling.py`** - Error scenarios and robustness

## Coverage

27 tests, 100% code coverage of implemented features.

## Notes

Tests only cover currently implemented functionality. Features like activity capacity limits and email validation are not yet implemented in the API.