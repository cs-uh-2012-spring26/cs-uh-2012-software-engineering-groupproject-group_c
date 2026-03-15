from app.db.constants import ID
from datetime import datetime, timedelta


def exclude_keys(item: dict, keys_to_exclude: set):
    """
    Remove specified keys from an item.
    """
    return {k: v for k, v in item.items() if k not in keys_to_exclude}

def assert_items_equal(actual, expected):
    """
    Assert two items are equal, ignoring '_id'.
    """
    assert exclude_keys(actual, {ID}) == exclude_keys(expected, {ID})

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def future_date_str(days=7):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def past_date_str(days=7):
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


def sample_class_data(**overrides):
    data = {
        "name": "Pilates",
        "description": "A relaxing pilates class",
        "date": future_date_str(),
        "start_time": "10:00",
        "end_time": "11:00",
        "location": "Rec Center",
        "trainer": "Ryan Opande",
        "capacity": 10,
    }
    data.update(overrides)
    return data