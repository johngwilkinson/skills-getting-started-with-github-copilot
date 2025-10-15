import pytest
from fastapi.testclient import TestClient


class TestActivityValidation:
    """Test class for activity validation and edge cases."""

    @pytest.fixture(autouse=True)
    def setup(self, client, reset_activities):
        """Setup for each test method."""
        self.client = client

    def test_activity_name_with_spaces(self):
        """Test activity names with spaces are handled correctly."""
        activity_name = "Programming Class"  # Has space
        email = "spacetest@mergington.edu"
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

    def test_activity_name_url_encoding(self):
        """Test activity names are properly URL encoded."""
        import urllib.parse
        
        activity_name = "Chess Club"
        encoded_name = urllib.parse.quote(activity_name)
        email = "urltest@mergington.edu"
        
        response = self.client.post(f"/activities/{encoded_name}/signup?email={email}")
        assert response.status_code == 200

    def test_case_sensitivity(self):
        """Test case sensitivity of activity names."""
        email = "casetest@mergington.edu"
        
        # Test with different case
        response = self.client.post(f"/activities/chess club/signup?email={email}")
        assert response.status_code == 404  # Should not find lowercase version

    def test_special_characters_in_email(self):
        """Test emails with special characters."""
        activity_name = "Chess Club"
        emails = [
            "test+tag@mergington.edu",
            "test.dot@mergington.edu", 
            "test_underscore@mergington.edu"
        ]
        
        for email in emails:
            response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200

    def test_concurrent_operations_simulation(self):
        """Test simulated concurrent operations."""
        activity_name = "Math Olympiad"
        base_email = "concurrent"
        
        # Simulate multiple quick signups
        for i in range(5):
            email = f"{base_email}{i}@mergington.edu"
            response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        
        for i in range(5):
            email = f"{base_email}{i}@mergington.edu"
            assert email in participants

    def test_activity_data_structure(self):
        """Test activity data structure is consistent."""
        response = self.client.get("/activities")
        activities = response.json()
        
        # Check each activity has expected structure
        for name, activity in activities.items():
            assert "max_participants" in activity
            assert "participants" in activity
            assert "description" in activity
            assert "schedule" in activity
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)
            # Note: No capacity checking is currently implemented

    def test_empty_activity_signup(self):
        """Test signing up for activity with no current participants."""
        activity_name = "Gym Class"  # Has empty participants list
        email = "firstsignup@mergington.edu"
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify it was added
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 1