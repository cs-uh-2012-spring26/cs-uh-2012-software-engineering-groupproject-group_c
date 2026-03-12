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

def test_authenticate_user_string_password():
    ur = UserResource()
    ur.create_user("Alice", "alice@test.com", "+1", "member", "pass123")
    user = ur.authenticate_user("alice@test.com", "pass123")
    assert user is not None
    assert user["email"] == "alice@test.com"


def test_add_multiple_fitness_classes():
    fc = FitnessClassResource()
    fc.add_multiple_fitness_classes([
        {"name": "Yoga", "date": "2026-04-01", "capacity": 10},
        {"name": "Pilates", "date": "2026-04-02", "capacity": 5},
    ])
    classes = fc.get_fitness_classes()
    assert len(classes) == 2


def test_add_multiple_fitness_classes_empty():
    fc = FitnessClassResource()
    fc.add_multiple_fitness_classes([])
    assert fc.get_fitness_classes() == []


def test_book_class_string_participant_duplicate():
    fc = FitnessClassResource()
    class_id = fc.create_fitness_class(
        "Yoga", "desc", "2026-04-01", "10:00", "11:00",
        "Gym", "Jane", 10, "admin@test.com",
    )
    from bson import ObjectId
    fc.collection.update_one(
        {"_id": ObjectId(class_id)},
        {"$push": {"participants": "user@test.com"}},
    )
    result = fc.book_class(class_id, {"email": "user@test.com"})
    assert result == "already_booked"


def test_book_class_invalid_id():
    fc = FitnessClassResource()
    result = fc.book_class("bad-id", {"email": "user@test.com"})
    assert result == "not_found"


def test_authenticate_user_with_string_stored_password():
    ur = UserResource()
    hashed = bcrypt.hashpw(b"pass123", bcrypt.gensalt()).decode("utf-8")
    ur.collection.insert_one({
        "name": "Legacy", "email": "legacy@test.com",
        "phone": "+1", "role": "member", "password": hashed,
    })
    user = ur.authenticate_user("legacy@test.com", "pass123")
    assert user is not None
    assert user["email"] == "legacy@test.com"


def test_get_required_environ_missing_key():
    os.environ.pop("_TEST_NONEXISTENT_VAR_", None)
    with pytest.raises(KeyError):
        get_required_environ("_TEST_NONEXISTENT_VAR_")


def test_get_required_environ_empty_value():
    os.environ["_TEST_EMPTY_VAR_"] = "   "
    try:
        with pytest.raises(ValueError, match="cannot be empty"):
            get_required_environ("_TEST_EMPTY_VAR_")
    finally:
        os.environ.pop("_TEST_EMPTY_VAR_", None)
