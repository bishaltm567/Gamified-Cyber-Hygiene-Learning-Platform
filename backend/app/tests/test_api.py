import os

os.environ["DATABASE_URL"] = "sqlite:///./test_cyberquest.db"
if os.path.exists("test_cyberquest.db"):
    os.remove("test_cyberquest.db")

from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_auth_register_and_me(client):
    payload = {
        "email": "newlearner@cyberquest.academy",
        "username": "newlearner",
        "full_name": "New Learner",
        "password": "demo123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]


def test_challenges_are_available(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "learner@cyberquest.academy", "password": "demo123"},
    )
    token = login.json()["access_token"]
    response = client.get("/api/challenges", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"]


def test_simulation_and_scoring_flow(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "learner@cyberquest.academy", "password": "demo123"},
    )
    token = login.json()["access_token"]
    challenge_id = 1
    create = client.post(
        "/api/simulations",
        headers={"Authorization": f"Bearer {token}"},
        json={"challenge_id": challenge_id, "persona_name": "Security Coach"},
    )
    assert create.status_code == 200
    sim_id = create.json()["id"]

    decision = client.post(
        f"/api/simulations/{sim_id}/decision",
        headers={"Authorization": f"Bearer {token}"},
        json={"selected_action": "verify", "reasoning": "It is urgent and the sender is not verified.", "suspicious_indicators": ["Urgency", "Fake sender domain"]},
    )
    assert decision.status_code == 200
    body = decision.json()
    assert body["score"] >= 0
    assert body["xp"] >= 0

    complete = client.post(f"/api/simulations/{sim_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert complete.status_code == 200


def test_admin_and_trainer_access(client):
    admin_login = client.post(
        "/api/auth/login",
        json={"email": "admin@cyberquest.academy", "password": "demo123"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_response = client.get("/api/admin/analytics", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_response.status_code == 200

    trainer_login = client.post(
        "/api/auth/login",
        json={"email": "trainer@cyberquest.academy", "password": "demo123"},
    )
    trainer_token = trainer_login.json()["access_token"]
    trainer_response = client.get("/api/trainer/analytics", headers={"Authorization": f"Bearer {trainer_token}"})
    assert trainer_response.status_code == 200
