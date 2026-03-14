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
