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

def test_register_missing_name(client):
    resp = client.post("/auth/register", json={
        "email": "x@test.com", "phone": "+123", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_register_missing_email(client):
    resp = client.post("/auth/register", json={
        "name": "John", "phone": "+123", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_register_missing_password(client):
    resp = client.post("/auth/register", json={
        "name": "John", "email": "x@test.com", "phone": "+123",
    })
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_register_duplicate_email(client):
    data = {
        "name": "John", "email": "dup@test.com",
        "phone": "+123", "password": "pass123",
    }
    client.post("/auth/register", json=data)
    resp = client.post("/auth/register", json=data)
    assert resp.status_code == HTTPStatus.CONFLICT


def test_register_invalid_role(client):
    resp = client.post("/auth/register", json={
        "name": "John", "email": "john2@test.com",
        "phone": "+123", "password": "pass123", "role": "superadmin",
    })
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_register_empty_name(client):
    resp = client.post("/auth/register", json={
        "name": "  ", "email": "x@test.com",
        "phone": "+123", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_register_empty_body(client):
    """Covers auth.py line 52: request body is None/empty."""
    resp = client.post("/auth/register",
                       data="", content_type="application/json")
    assert resp.status_code in (HTTPStatus.BAD_REQUEST,
                                HTTPStatus.INTERNAL_SERVER_ERROR)

def test_login_success(client):
    client.post("/auth/register", json={
        "name": "John", "email": "login@test.com",
        "phone": "+123", "password": "pass123",
    })
    resp = client.post("/auth/login", json={
        "email": "login@test.com", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.OK
    data = resp.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "login@test.com"
    assert data["message"] == "Login successful"


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "name": "John", "email": "wrong@test.com",
        "phone": "+123", "password": "pass123",
    })
    resp = client.post("/auth/login", json={
        "email": "wrong@test.com", "password": "wrongpass",
    })
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_login_nonexistent_user(client):
    resp = client.post("/auth/login", json={
        "email": "nobody@test.com", "password": "pass123",
    })
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_login_missing_email(client):
    resp = client.post("/auth/login", json={"password": "pass123"})
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_login_missing_password(client):
    resp = client.post("/auth/login", json={"email": "x@test.com"})
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_login_empty_body(client):
    """Covers auth.py line 91: request body is None/empty for login."""
    resp = client.post("/auth/login",
                       data="", content_type="application/json")
    assert resp.status_code in (HTTPStatus.BAD_REQUEST,
                                HTTPStatus.INTERNAL_SERVER_ERROR)

def test_register_unexpected_exception(client):
    """Covers auth.py lines 78-79: generic Exception during registration.
    Uses MagicMock + fixture injection — no @patch."""
    original = auth_module.UserResource
    mock_ur_cls = MagicMock()
    mock_ur_cls.return_value.register_user.side_effect = Exception("DB crash")
    auth_module.UserResource = mock_ur_cls

    try:
        resp = client.post("/auth/register", json={
            "name": "John", "email": "john@test.com",
            "phone": "+123", "password": "pass123",
        })
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert "Registration failed" in resp.get_json()["message"]
    finally:
        auth_module.UserResource = original
        