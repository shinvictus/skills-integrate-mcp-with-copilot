import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import app

client = TestClient(app.app)


def test_teacher_login_succeeds_with_valid_credentials():
    response = client.post(
        "/login",
        json={"username": "teacher", "password": "school123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["role"] == "teacher"


def test_teacher_login_fails_with_invalid_credentials():
    response = client.post(
        "/login",
        json={"username": "teacher", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_non_teacher_cannot_register_student():
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 403


def test_teacher_can_register_student():
    response = client.post(
        "/login",
        json={"username": "teacher", "password": "school123"},
    )
    token = response.json()["token"]

    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["participants"]

    response = client.delete(
        "/activities/Chess Club/unregister?email=newstudent@mergington.edu",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
