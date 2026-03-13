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
    