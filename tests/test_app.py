"""
Tests for the Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their initial state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team with regular practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["marcus@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Recreational and competitive soccer for all skill levels",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media art techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater and performance arts with end-of-year productions",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["sophia@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["rachel@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through hands-on experiments and projects",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["david@mergington.edu", "emily@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_has_correct_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant to an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds participant to activity list"""
        from app import activities
        
        initial_count = len(activities["Chess Club"]["participants"])
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        new_count = len(activities["Chess Club"]["participants"])
        
        assert new_count == initial_count + 1
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        email = "newstudent@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from activity"""
        from app import activities
        
        initial_count = len(activities["Chess Club"]["participants"])
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        new_count = len(activities["Chess Club"]["participants"])
        
        assert new_count == initial_count - 1
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_registered_student(self, client, reset_activities):
        """Test that a student who is not registered cannot unregister"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]


class TestSignupUnregisterFlow:
    """Integration tests for signup and unregister flow"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "testuser@mergington.edu"
        
        # Sign up
        response1 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Verify participant was added
        response_check = client.get("/activities")
        activities_data = response_check.json()
        assert email in activities_data["Programming Class"]["participants"]
        
        # Unregister
        response2 = client.post(
            "/activities/Programming Class/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify participant was removed
        response_check2 = client.get("/activities")
        activities_data2 = response_check2.json()
        assert email not in activities_data2["Programming Class"]["participants"]
    
    def test_signup_then_signup_same_activity_fails(self, client, reset_activities):
        """Test that signup fails if signing up again for the same activity"""
        email = "testuser@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Science Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup for same activity
        response2 = client.post(
            "/activities/Science Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
