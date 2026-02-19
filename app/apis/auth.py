from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from app.db.users import UserResource
from http import HTTPStatus
import json


api = Namespace("auth", description="Authentication operations")

REGISTER_MODEL = api.model("Register", {
    "name": fields.String(required=True, description="User's full name", example="Paulo Opande"),
    "email": fields.String(required=True, description="User's email address", example="paulo@upande.ea"),
    "phone": fields.String(required=True, description="User's phone number", example="+1234567890"),
    "password": fields.String(required=True, description="User's password", example="secret123"),
    "role": fields.String(
        required=False,
        description="User's role: member, trainer, or admin. Defaults to member.",
        enum=["member", "trainer", "admin"],
        example="member",
    ),
})


LOGIN_MODEL = api.model("Login", {
    "email": fields.String(required=True, description="User's email address", example="paulo@upande.ea"),
    "password": fields.String(required=True, description="User's password", example="abc123"),
})

TOKEN_RESPONSE_MODEL = api.model("TokenResponse", {
    "message": fields.String(example="Login successful"),
    "access_token": fields.String(description="JWT access token"),
    "refresh_token": fields.String(description="JWT refresh token"),
    "user": fields.Nested(api.model("UserInfo", {
        "id": fields.String(description="User ID"),
        "name": fields.String(description="User's full name"),
        "email": fields.String(description="Email"),
        "role": fields.String(description="Role"),
    })),
})


@api.route("/register")
class Register(Resource):
    @api.expect(AUTH_MODEL)
    def post(self):
        return {"message": "Register endpoint initialized"}, 200

@api.route("/login")
class Login(Resource):
    @api.expect(AUTH_MODEL)
    def post(self):
        return {"message": "Login endpoint initialized"}, 200