from http import HTTPStatus
from unittest.mock import MagicMock

from app.db import DB
from app.db.fitness_classes import FitnessClassResource
import app.apis.classes as classes_module
from tests.utils import auth_header, sample_class_data, past_date_str, future_date_str


def test_book_class_success(client, member_token, created_class_id):
    resp = client.post(f"/classes/{created_class_id}/book",
                    headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.OK
    assert resp.get_json()["message"] == "Class booked successfully"


def test_book_class_decrements_slots(client, member_token, admin_token, created_class_id):
    client.post(f"/classes/{created_class_id}/book",
                headers=auth_header(member_token))
    resp = client.get(f"/classes/{created_class_id}/participants",
                    headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp.get_json()["message"]) == 1

def test_book_class_forbidden_admin(client, admin_token, created_class_id):
    resp = client.post(f"/classes/{created_class_id}/book",
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_book_class_forbidden_trainer(client, trainer_token, created_class_id):
    resp = client.post(f"/classes/{created_class_id}/book",
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.FORBIDDEN

def test_book_class_not_found(client, member_token):
    resp = client.post("/classes/000000000000000000000000/book",
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_book_class_invalid_id(client, member_token):
    resp = client.post("/classes/bad-id/book",
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_book_class_already_booked(client, member_token, created_class_id):
    client.post(f"/classes/{created_class_id}/book",
                headers=auth_header(member_token))
    resp = client.post(f"/classes/{created_class_id}/book",
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "already booked" in resp.get_json()["message"]


def test_book_class_full(client, admin_token):
    resp = client.post("/classes/", json=sample_class_data(capacity=1),
                       headers=auth_header(admin_token))
    class_id = resp.get_json()["message"].split("id: ")[1]

    from tests.unit.conftest import _get_token
    token1 = _get_token(client, "Member1", "m1@test.com",
                        "+111", "pass123", "member")
    client.post(f"/classes/{class_id}/book", headers=auth_header(token1))


    token2 = _get_token(client, "Member2", "m2@test.com",
                        "+222", "pass123", "member")
    resp = client.post(f"/classes/{class_id}/book", headers=auth_header(token2))
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "full" in resp.get_json()["message"]

def test_book_class_deadline_passed(client, member_token):
    fc = FitnessClassResource()
    class_id = fc.create_fitness_class(
        "Old Yoga", "desc", past_date_str(), "10:00", "11:00",
        "Gym", "Jane", 10, "admin@test.com",
    )
    resp = client.post(f"/classes/{class_id}/book",
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "deadline" in resp.get_json()["message"].lower()


def test_book_class_no_auth(client, created_class_id):
    resp = client.post(f"/classes/{created_class_id}/book")
    assert resp.status_code in (HTTPStatus.UNAUTHORIZED,
                                HTTPStatus.INTERNAL_SERVER_ERROR)


def test_book_class_user_deleted(client, member_token, created_class_id):
    DB.get_collection("users").delete_many({"email": "member@test.com"})
    resp = client.post(f"/classes/{created_class_id}/book",
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert "User not found" in resp.get_json()["message"]


def test_book_class_with_invalid_stored_datetime(client, member_token):
    fc = FitnessClassResource()
    class_id = fc.create_fitness_class(
        "Bad Date", "desc", "not-a-date", "not-a-time", "11:00",
        "Gym", "Jane", 10, "admin@test.com",
    )
    resp = client.post(f"/classes/{class_id}/book",
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.OK
    assert resp.get_json()["message"] == "Class booked successfully"


def test_book_class_returns_not_found_from_book_method(client, member_token):
    original = classes_module.FitnessClassResource
    mock_fc_cls = MagicMock()
    mock_instance = mock_fc_cls.return_value
    mock_instance.get_fitness_class_by_id.return_value = {
        "date": future_date_str(), "start_time": "10:00",
        "participants": [],
    }
    mock_instance.book_class.return_value = "not_found"
    classes_module.FitnessClassResource = mock_fc_cls
    try:
        resp = client.post("/classes/000000000000000000000000/book",
                           headers=auth_header(member_token))
        assert resp.status_code == HTTPStatus.NOT_FOUND
    finally:
        classes_module.FitnessClassResource = original