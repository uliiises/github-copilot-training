import copy

from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def setup_function():
    # Preserve in-memory activities data between tests.
    app_module._activities_backup = copy.deepcopy(app_module.activities)


def teardown_function():
    app_module.activities.clear()
    app_module.activities.update(app_module._activities_backup)
    del app_module._activities_backup


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

    chess = activities["Chess Club"]
    assert chess["description"].startswith("Learn strategies")
    assert chess["max_participants"] == 12
    assert isinstance(chess["participants"], list)


def test_signup_for_activity_adds_new_participant():
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"

    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    activity_name = "Chess Club"
    duplicate_email = app_module.activities[activity_name]["participants"][0]

    response = client.post(f"/activities/{activity_name}/signup?email={duplicate_email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    activity_name = "Programming Class"
    participant_email = app_module.activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{activity_name}/participants/{participant_email}"
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"

    assert participant_email not in app_module.activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    activity_name = "Gym Class"
    missing_email = "notfound@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants/{missing_email}"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
