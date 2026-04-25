from http import HTTPStatus
from tests.utils import auth_header

def test_update_preferences_email_only(client, member_token):
   resp = client.put("/auth/preferences", json={
       "notification_channels": ["email"],
   }, headers=auth_header(member_token))
   assert resp.status_code == HTTPStatus.OK
   assert "updated" in resp.get_json()["message"]

def test_update_preferences_telegram_only(client, member_token):
   resp = client.put("/auth/preferences", json={
       "notification_channels": ["telegram"],
       "telegram_chat_id": "654321",
   }, headers=auth_header(member_token))
   assert resp.status_code == HTTPStatus.OK

def test_update_preferences_both_channels(client, member_token):
   resp = client.put("/auth/preferences", json={
       "notification_channels": ["email", "telegram"],
       "telegram_chat_id": "123456",
   }, headers=auth_header(member_token))
   assert resp.status_code == HTTPStatus.OK

def test_update_preferences_invalid_channel(client, member_token):
   resp = client.put("/auth/preferences", json={
       "notification_channels": ["sms"],
   }, headers=auth_header(member_token))
   assert resp.status_code == HTTPStatus.BAD_REQUEST
   assert "notification_channels" in resp.get_json()["message"]

def test_update_preferences_empty_channels(client, member_token):
   resp = client.put("/auth/preferences", json={
       "notification_channels": [],
   }, headers=auth_header(member_token))
   assert resp.status_code == HTTPStatus.BAD_REQUEST

def test_update_preferences_non_list_channels(client, member_token):
   resp = client.put("/auth/preferences", json={
       "notification_channels": "email",
   }, headers=auth_header(member_token))
   assert resp.status_code == HTTPStatus.BAD_REQUEST

def test_update_preferences_no_auth(client):
   resp = client.put("/auth/preferences", json={
       "notification_channels": ["email"],
   })
   assert resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.INTERNAL_SERVER_ERROR)

def test_update_preferences_empty_body(client, member_token):
   resp = client.put("/auth/preferences", data="",
                     content_type="application/json",
                     headers=auth_header(member_token))
   assert resp.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR)
