import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def reset_activities():
    """Reset activities data before each test."""
    # Import here to avoid circular imports
    from app import activities
    
    # Store original state
    original_activities = {}
    for name, activity in activities.items():
        original_activities[name] = {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy()
        }
    
    yield
    
    # Reset to original state after test
    activities.clear()
    activities.update(original_activities)