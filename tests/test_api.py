import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test class for API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, client, reset_activities):
        """Setup for each test method."""
        self.client = client

    def test_root_redirect(self):
        """Test that root endpoint redirects to static index.html."""
        response = self.client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self):
        """Test getting all activities."""
        response = self.client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check if expected activities exist
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        
        # Check activity structure
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity."""
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist."""
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404
        
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_signup_duplicate_student(self):
        """Test signup for a student already registered."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        result = response.json()
        assert result["detail"] == "Student already signed up for this activity"



    def test_unregister_from_activity_success(self):
        """Test successful unregistration from an activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_from_nonexistent_activity(self):
        """Test unregistration from an activity that doesn't exist."""
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 404
        
        result = response.json()
        assert result["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self):
        """Test unregistration for a student not registered for the activity."""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        result = response.json()
        assert result["detail"] == "Student is not registered for this activity"

    def test_signup_and_unregister_flow(self):
        """Test complete signup and unregister flow."""
        activity_name = "Art Club"
        email = "testflow@mergington.edu"
        
        # First, signup
        signup_response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        
        # Then, unregister
        unregister_response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_multiple_signups_different_activities(self):
        """Test signing up for multiple different activities."""
        email = "multisignup@mergington.edu"
        activities_to_signup = ["Chess Club", "Programming Class", "Art Club"]
        
        for activity_name in activities_to_signup:
            response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all signups
        activities_response = self.client.get("/activities")
        activities = activities_response.json()
        
        for activity_name in activities_to_signup:
            assert email in activities[activity_name]["participants"]

    def test_activity_data_integrity(self):
        """Test that activity data maintains integrity across operations."""
        # Get initial state
        initial_response = self.client.get("/activities")
        initial_activities = initial_response.json()
        initial_chess_participants = len(initial_activities["Chess Club"]["participants"])
        
        # Sign up a new student
        email = "integrity@mergington.edu"
        self.client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Check that only Chess Club was modified
        updated_response = self.client.get("/activities")
        updated_activities = updated_response.json()
        
        assert len(updated_activities["Chess Club"]["participants"]) == initial_chess_participants + 1
        assert email in updated_activities["Chess Club"]["participants"]
        
        # Check other activities were not affected
        for activity_name, activity_data in updated_activities.items():
            if activity_name != "Chess Club":
                assert activity_data["participants"] == initial_activities[activity_name]["participants"]