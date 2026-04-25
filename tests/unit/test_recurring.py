from http import HTTPStatus
from datetime import datetime, timedelta

from app.db.fitness_classes import FitnessClassResource
from tests.utils import auth_header, sample_class_data, future_date_str


def test_create_recurring_daily(client, admin_token):
    data = sample_class_data(recurrence="daily", recurrence_count=3)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))

    assert resp.status_code == HTTPStatus.CREATED
    body = resp.get_json()
    assert "3 recurring classes created" in body["message"]
    assert len(body["class_ids"]) == 3


def test_create_recurring_weekly(client, admin_token):
    data = sample_class_data(recurrence="weekly", recurrence_count=4)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))

    assert resp.status_code == HTTPStatus.CREATED
    assert len(resp.get_json()["class_ids"]) == 4


def test_create_recurring_max_count(client, admin_token):
    data = sample_class_data(recurrence="daily", recurrence_count=10)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.CREATED
    assert len(resp.get_json()["class_ids"]) == 10


def test_create_recurring_invalid_type(client, admin_token):
    data = sample_class_data(recurrence="monthly", recurrence_count=3)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_recurring_count_too_small(client, admin_token):
    data = sample_class_data(recurrence="daily", recurrence_count=1)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_recurring_count_too_large(client, admin_token):
    data = sample_class_data(recurrence="daily", recurrence_count=11)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_recurring_without_count(client, admin_token):
    data = sample_class_data(recurrence="daily")
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_recurring_count_not_integer(client, admin_token):
    data = sample_class_data(recurrence="daily", recurrence_count="three")
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_recurring_classes_appear_in_list(client, admin_token):
    data = sample_class_data(recurrence="daily", recurrence_count=3)
    client.post("/classes/", json=data, headers=auth_header(admin_token))

    resp = client.get("/classes/")
    assert len(resp.get_json()["message"]) == 3


def test_recurring_daily_classes_have_consecutive_dates(client, admin_token):
    base_date = future_date_str(days=10)
    data = sample_class_data(date=base_date, recurrence="daily", recurrence_count=3)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))

    class_ids = resp.get_json()["class_ids"]
    fc = FitnessClassResource()
    dates = [fc.get_fitness_class_by_id(cid)["date"] for cid in class_ids]

    base = datetime.strptime(base_date, "%Y-%m-%d")
    expected = [(base + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]
    assert dates == expected


def test_recurring_weekly_classes_have_weekly_dates(client, admin_token):
    base_date = future_date_str(days=10)
    data = sample_class_data(date=base_date, recurrence="weekly", recurrence_count=3)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))

    class_ids = resp.get_json()["class_ids"]
    fc = FitnessClassResource()
    dates = [fc.get_fitness_class_by_id(cid)["date"] for cid in class_ids]

    base = datetime.strptime(base_date, "%Y-%m-%d")
    expected = [(base + timedelta(weeks=i)).strftime("%Y-%m-%d") for i in range(3)]
    assert dates == expected


def test_recurring_classes_share_recurrence_group_id(client, admin_token):
    data = sample_class_data(recurrence="daily", recurrence_count=3)
    resp = client.post("/classes/", json=data, headers=auth_header(admin_token))

    class_ids = resp.get_json()["class_ids"]
    fc = FitnessClassResource()
    group_ids = [fc.get_fitness_class_by_id(cid).get("recurrence_group_id") for cid in class_ids]

    assert all(g is not None for g in group_ids)
    assert len(set(group_ids)) == 1


def test_single_class_has_no_recurrence_group_id(client, admin_token):
    resp = client.post("/classes/", json=sample_class_data(),
                       headers=auth_header(admin_token))
    class_id = resp.get_json()["message"].split("id: ")[1]
    fc = FitnessClassResource()
    fitness_class = fc.get_fitness_class_by_id(class_id)
    assert "recurrence_group_id" not in fitness_class


def test_recurring_class_forbidden_for_member(client, member_token):
    data = sample_class_data(recurrence="daily", recurrence_count=3)
    resp = client.post("/classes/", json=data, headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.FORBIDDEN
