from http import HTTPStatus
from unittest.mock import MagicMock

import app.apis.auth as auth_module


def test_register_success(client):
    resp = client.post("/auth/register", json={
        "name": "John", "email": "john@test.com",
        "phone": "+123", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.get_json()
    assert "user_id" in data
    assert data["message"] == "User registered successfully"


def test_register_with_role(client):
    resp = client.post("/auth/register", json={
        "name": "Admin", "email": "admin2@test.com",
        "phone": "+123", "password": "pass123", "role": "trainer",
    })
    assert resp.status_code == HTTPStatus.CREATED


def test_register_default_role(client):
    resp = client.post("/auth/register", json={
        "name": "Jane", "email": "jane@test.com",
        "phone": "+123", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.CREATED


def test_register_missing_email(client):
    resp = client.post("/auth/register", json={
        "name": "John", "phone": "+123", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.BAD_REQUEST
