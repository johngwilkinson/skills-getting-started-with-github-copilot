import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestErrorHandling:
    """Test class for error handling and edge cases."""

    @pytest.fixture(autouse=True)
    def setup(self, client, reset_activities):
        """Setup for each test method."""
        self.client = client

    def test_missing_email_parameter(self):
        """Test signup without email parameter."""
        activity_name = "Chess Club"
        
        # Missing email parameter should cause an error
        response = self.client.post(f"/activities/{activity_name}/signup")
        assert response.status_code == 422  # Unprocessable Entity

    def test_invalid_http_methods(self):
        """Test using wrong HTTP methods on endpoints."""
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        
        # Try GET on signup endpoint
        response = self.client.get(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 405  # Method Not Allowed
        
        # Try POST on unregister endpoint  
        response = self.client.post(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 405  # Method Not Allowed

    def test_malformed_urls(self):
        """Test malformed URLs."""
        # Missing activity name
        response = self.client.post("/activities//signup?email=test@mergington.edu")
        assert response.status_code in [404, 422]
        
        # Extra slashes
        response = self.client.post("/activities/Chess%20Club//signup?email=test@mergington.edu")
        assert response.status_code in [404, 422]

    def test_very_long_activity_name(self):
        """Test with very long activity name."""
        long_name = "A" * 1000  # Very long activity name
        email = "test@mergington.edu"
        
        response = self.client.post(f"/activities/{long_name}/signup?email={email}")
        assert response.status_code == 404  # Activity not found

    def test_very_long_email(self):
        """Test with very long email."""
        activity_name = "Chess Club"
        long_email = "a" * 1000 + "@mergington.edu"
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={long_email}")
        assert response.status_code == 200  # Should still work

    def test_unicode_characters(self):
        """Test with unicode characters in parameters."""
        activity_name = "Chess Club"
        unicode_email = "tëst@mergington.edu"
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={unicode_email}")
        assert response.status_code == 200

    def test_response_format_consistency(self):
        """Test that all responses have consistent format."""
        activity_name = "Chess Club"
        email = "formattest@mergington.edu"
        
        # Test successful signup response format
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert isinstance(result["message"], str)
        
        # Test error response format
        response = self.client.post(f"/activities/NonExistent/signup?email={email}")
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert isinstance(result["detail"], str)

    def test_multiple_sequential_operations(self):
        """Test multiple operations in sequence on same activity."""
        activity_name = "Drama Society"
        emails = [f"seq{i}@mergington.edu" for i in range(10)]
        
        # Sign up multiple students
        for email in emails:
            response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are registered
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        
        for email in emails:
            assert email in participants
        
        # Unregister all students
        for email in emails:
            response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
            assert response.status_code == 200
        
        # Verify all are unregistered
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        
        for email in emails:
            assert email not in participants