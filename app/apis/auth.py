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
    @api.expect(REGISTER_MODEL)
    @api.response(HTTPStatus.CREATED, "User registered successfully")
    @api.response(HTTPStatus.BAD_REQUEST, "Missing required fields")
    @api.response(HTTPStatus.CONFLICT, "User already exists")
    def post(self):
        """Register a new user (email, phone, password required)"""
        data = request.json
        if not data:
            return {"message": "Request body is required"}, HTTPStatus.BAD_REQUEST

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()
        password = data.get("password") or ""
        role = (data.get("role") or "member").lower()

        if not all([name, email,phone, password]):
            return {"message": "name,email, phone,and password are all required"}, HTTPStatus.BAD_REQUEST

        if role not in ("member", "trainer","admin"):
            return {"message": "role must be one of: member, trainer, admin"}, HTTPStatus.BAD_REQUEST

        user_resource = UserResource()
        try:
            user_id = user_resource.register_user(
                name=name,
                email=email,
                phone=phone,
                password=password,
                role=role,
            )
            return {"message": "User registered successfully","user_id": user_id}, HTTPStatus.CREATED
        except ValueError as e:
            return {"message": str(e)}, HTTPStatus.CONFLICT
        except Exception as e:
            return {"message": f"Registration failed: {str(e)}"}, HTTPStatus.BAD_REQUEST
       
        
@api.route("/login")
class Login(Resource):
    @api.expect(LOGIN_MODEL)
    @api.response(HTTPStatus.OK, "Login successful", TOKEN_RESPONSE_MODEL)
    @api.response(HTTPStatus.UNAUTHORIZED, "Invalid credentials")
    def post(self):
        """Login with email and password — returns JWT access and refresh tokens"""
        data = request.json
        if not data:
            return {"message": "Request body is required"}, HTTPStatus.BAD_REQUEST

        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not email or not password:
            return {"message": "email and password are required"}, HTTPStatus.BAD_REQUEST

        user_resource = UserResource()
        user = user_resource.authenticate_user(email, password)

        if not user:
            return {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED

        claims = {"id": user["_id"], "email": user["email"], "role": user["role"]}
        access_token = create_access_token(identity=user["email"], additional_claims=claims)
        refresh_token = create_refresh_token(identity=user["email"], additional_claims=claims)

        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.get("_id"),
                "name": user.get("name"),
                "email": user.get("email"),
                "role": user.get("role"),
            },
        }, HTTPStatus.OK