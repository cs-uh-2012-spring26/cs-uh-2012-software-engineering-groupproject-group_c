"""Direct tests for DB resource classes to cover methods not hit by API tests."""
import os

import bcrypt
import pytest

from app.db.users import UserResource
from app.db.fitness_classes import FitnessClassResource
from app.config import get_required_environ


def test_get_users_no_filter():
    ur = UserResource()
    ur.create_user("Alice", "alice@test.com", "+1", "member", "pass123")
    ur.create_user("Bob", "bob@test.com", "+2", "admin", "pass456")
    users = ur.get_users()
    assert len(users) == 2


def test_get_users_filter_by_name():
    ur = UserResource()
    ur.create_user("Alice", "alice@test.com", "+1", "member", "pass123")
    ur.create_user("Bob", "bob@test.com", "+2", "admin", "pass456")
    users = ur.get_users(name="Alice")
    assert len(users) == 1
    assert users[0]["name"] == "Alice"


def test_get_users_filter_by_role():
    ur = UserResource()
    ur.create_user("Alice", "alice@test.com", "+1", "member", "pass123")
    ur.create_user("Bob", "bob@test.com", "+2", "admin", "pass456")
    users = ur.get_users(role="admin")
    assert len(users) == 1
    assert users[0]["role"] == "admin"


def test_get_user_by_id():
    ur = UserResource()
    user_id = ur.create_user("Alice", "alice@test.com", "+1", "member", "pass123")
    user = ur.get_user_by_id(str(user_id))
    assert user is not None
    assert user["email"] == "alice@test.com"

def test_get_user_by_id_not_found():
    ur = UserResource()
    user = ur.get_user_by_id("000000000000000000000000")
    assert user is None


def test_get_user_by_id_invalid():
    ur = UserResource()
    user = ur.get_user_by_id("bad-id")
    assert user is None


def test_delete_all_users():
    ur = UserResource()
    ur.create_user("Alice", "alice@test.com", "+1", "member", "pass123")
    ur.delete_all_users()
    assert ur.get_users() == []


def test_add_multiple_users():
    ur = UserResource()
    ur.add_multiple_users([
        {"name": "A", "email": "a@t.com", "phone": "+1", "role": "member"},
        {"name": "B", "email": "b@t.com", "phone": "+2", "role": "admin"},
    ])
    assert len(ur.get_users()) == 2


def test_add_multiple_users_empty():
    ur = UserResource()
    ur.add_multiple_users([])
    assert ur.get_users() == []


def test_create_user_with_optional_fields():
    ur = UserResource()
    user_id = ur.create_user("Alice", "alice@test.com", "+1", "member",
                             "pass123", birthdate="2000-01-01", gender="female")
    user = ur.get_user_by_id(str(user_id))
    assert user["birthdate"] == "2000-01-01"
    assert user["gender"] == "female"
