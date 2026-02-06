"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities(self):
        """Test that we can retrieve all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of activity
        activity = next(iter(data.values()))
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_known_activity(self):
        """Test that we can access a known activity"""
        response = client.get("/activities")
        data = response.json()
        
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Art Studio" in data


class TestSignupEndpoint:
    """Tests for the /signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_duplicate_student(self):
        """Test that duplicate signups are rejected"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self):
        """Test signup for a non-existent activity"""
        email = "newstudent@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_updates_participant_list(self):
        """Test that signup actually adds participant to list"""
        email = "newsignup@mergington.edu"
        activity = "Art Studio"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Check updated count
        response = client.get("/activities")
        updated_count = len(response.json()[activity]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in response.json()[activity]["participants"]


class TestUnregisterEndpoint:
    """Tests for the /unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_not_registered(self):
        """Test unregistration for someone not registered"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self):
        """Test unregistration from a non-existent activity"""
        email = "anyemail@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_updates_participant_list(self):
        """Test that unregister actually removes participant from list"""
        email = "daniel@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Check updated count
        response = client.get("/activities")
        updated_count = len(response.json()[activity]["participants"])
        
        assert updated_count == initial_count - 1
        assert email not in response.json()[activity]["participants"]


class TestIntegration:
    """Integration tests for signup and unregister flows"""

    def test_signup_then_unregister(self):
        """Test the full flow of signing up and then unregistering"""
        email = "integrationtest@mergington.edu"
        activity = "Music Band"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
