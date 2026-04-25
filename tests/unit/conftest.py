import pytest
import os
import mongomock
import yaml
from unittest.mock import MagicMock
from dotenv import load_dotenv
from pathlib import Path


# to force mock db for tests
os.environ["MOCK_DB"] = "true" 
os.environ["TESTING"] = "true"

from app import create_app
from app.db import DB
import app.apis.classes as classes_module
import app.apis.auth as auth_module
from tests.utils import auth_header, sample_class_data

@pytest.fixture(scope="session", autouse=True)
def mock_db():
    mock_client = mongomock.MongoClient()
    mock_database = mock_client["test_database"]

    DB.client = mock_client
    DB.db = mock_database

    yield mock_database

@pytest.fixture(scope="session", autouse=True)
def app(mock_db):
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture(autouse=True)
def clean_db(app):
    DB.get_collection("users").delete_many({})
    DB.get_collection("fitness_class").delete_many({})
    yield

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def mock_email_service():
    import app.services.email_service as email_module
    original_cls = email_module.EmailService

    mock_cls = MagicMock()
    mock_instance = MagicMock()
    mock_cls.return_value = mock_instance
    mock_instance.send_reminder.return_value = None

    email_module.EmailService = mock_cls
    yield mock_instance
    email_module.EmailService = original_cls


@pytest.fixture(autouse=True)
def mock_telegram_requests():
    import app.services.notifier as notifier_module
    original_post = notifier_module.requests.post
    notifier_module.requests.post = MagicMock(return_value=MagicMock(status_code=200))
    yield notifier_module.requests.post
    notifier_module.requests.post = original_post


def _get_token(client, name, email, phone, password, role="member"):
    client.post("/auth/register", json={
        "name": name,
        "email": email,
        "phone": phone,
        "password": password,
        "role": role,
    })
    resp = client.post("/auth/login", json={
        "email": email,
        "password": password,
    })
    return resp.get_json()["access_token"]


@pytest.fixture
def member_token(client):
    return _get_token(client, "Test Member", "member@test.com",
                      "+1234567890", "pass123", "member")


@pytest.fixture
def admin_token(client):
    return _get_token(client, "Test Admin", "admin@test.com",
                      "+1234567890", "pass123", "admin")


@pytest.fixture
def trainer_token(client):
    return _get_token(client, "Test Trainer", "trainer@test.com",
                      "+1234567890", "pass123", "trainer")


@pytest.fixture
def created_class_id(client, admin_token):
    resp = client.post("/classes/", json=sample_class_data(),
                       headers=auth_header(admin_token))
    return resp.get_json()["message"].split("id: ")[1]