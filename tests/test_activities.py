import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert activities["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"

    def test_get_activities_returns_participant_lists(self, client):
        """Test that activities include participant information."""
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert "participants" in activities[activity_name]
        assert len(activities[activity_name]["participants"]) == 2
        assert "michael@mergington.edu" in activities[activity_name]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_adds_participant(self, client):
        """Test that a valid signup adds the email to the activity's participant list."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was actually added
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert email in updated_activity["participants"]
        assert len(updated_activity["participants"]) == 3

    def test_signup_with_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signing up the same student twice returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_without_email_parameter_fails(self, client):
        """Test that signup fails when email parameter is missing."""
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422  # Unprocessable Entity


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success_removes_participant(self, client):
        """Test that a valid unregister removes the email from the activity's participant list."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was actually removed
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert email not in updated_activity["participants"]
        assert len(updated_activity["participants"]) == 1

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_registered_email_returns_400(self, client):
        """Test that unregistering a non-participant returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"  # Not signed up

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"

    def test_unregister_without_email_parameter_fails(self, client):
        """Test that unregister fails when email parameter is missing."""
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister")

        # Assert
        assert response.status_code == 422  # Unprocessable Entity
