from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function():
    # reset activities state before each test
    activities.clear()
    activities.update({
        "Test Activity": {
            "description": "A test",
            "schedule": "Now",
            "max_participants": 2,
            "participants": []
        }
    })


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Test Activity" in data


def test_signup_and_duplicate():
    # sign up first student
    resp = client.post("/activities/Test%20Activity/signup?email=foo@example.com")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Signed up foo@example.com for Test Activity"
    # second sign up
    resp = client.post("/activities/Test%20Activity/signup?email=bar@example.com")
    assert resp.status_code == 200
    # third should hit max capacity or duplicate check
    resp = client.post("/activities/Test%20Activity/signup?email=baz@example.com")
    # since we don't enforce capacity, should still succeed
    assert resp.status_code == 200
    # duplicate
    resp = client.post("/activities/Test%20Activity/signup?email=foo@example.com")
    assert resp.status_code == 400


def test_remove_participant():
    # add participant first
    client.post("/activities/Test%20Activity/signup?email=foo@example.com")
    # remove
    resp = client.post("/activities/Test%20Activity/remove?email=foo@example.com")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Removed foo@example.com from Test Activity"
    # removing again should fail
    resp = client.post("/activities/Test%20Activity/remove?email=foo@example.com")
    assert resp.status_code == 400


def test_not_found_activity():
    resp = client.post("/activities/Nope/signup?email=nobody@example.com")
    assert resp.status_code == 404
    resp = client.post("/activities/Nope/remove?email=nobody@example.com")
    assert resp.status_code == 404
