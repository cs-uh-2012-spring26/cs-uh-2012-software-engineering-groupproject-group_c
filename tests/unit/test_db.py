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
