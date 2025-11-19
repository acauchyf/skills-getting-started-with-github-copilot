import copy
import urllib.parse

from fastapi.testclient import TestClient

import src.app as app_module


def setup_module(module):
    # ensure we start from the module's in-memory DB (already initialized in app_module)
    pass


def teardown_module(module):
    pass


def test_get_activities_contains_expected_key():
    client = TestClient(app_module.app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # keep a deep copy of original state and restore afterwards
    original = copy.deepcopy(app_module.activities)
    client = TestClient(app_module.app)

    try:
        activity = "Chess Club"
        email = "testuser@mergington.edu"

        # ensure not present
        resp = client.get("/activities")
        assert resp.status_code == 200
        data = resp.json()
        assert email not in data[activity]["participants"]

        # signup
        resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup", params={"email": email})
        assert resp.status_code == 200
        assert "Signed up" in resp.json().get("message", "")

        # verify present
        resp = client.get("/activities")
        data = resp.json()
        assert email in data[activity]["participants"]

        # duplicate signup -> 400
        resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup", params={"email": email})
        assert resp.status_code == 400

        # unregister
        resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants", params={"email": email})
        assert resp.status_code == 200
        assert "Unregistered" in resp.json().get("message", "")

        # verify removed
        resp = client.get("/activities")
        data = resp.json()
        assert email not in data[activity]["participants"]

    finally:
        # restore original in-memory DB to avoid side-effects for other tests
        app_module.activities.clear()
        app_module.activities.update(original)
