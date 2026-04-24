from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.db.users import UserResource, VALID_CHANNELS
from http import HTTPStatus


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
    "notification_channels": fields.List(
       fields.String,
       required=False,
       description="Notification channels: email, telegram. Defaults to [email].",
       example=["email"],
    ),
    "telegram_chat_id": fields.String(
        required=False,
        description="Telegram chat ID for Telegram notifications.",
        example="123456789",
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

PREFERENCES_MODEL = api.model("Preferences", {
   "notification_channels": fields.List(
       fields.String,
       required=True,
       description="List of notification channels (email, telegram)",
       example=["email", "telegram"],
   ),
   "telegram_chat_id": fields.String(
       required=False,
       description="Telegram chat ID (required when telegram is in channels)",
       example="123456789",
   ),
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
        notification_channels = data.get("notification_channels") or ["email"]
        telegram_chat_id = data.get("telegram_chat_id") or ""

        if not all([name, email,phone, password]):
            return {"message": "name,email, phone,and password are all required"}, HTTPStatus.BAD_REQUEST

        if role not in ("member", "trainer","admin"):
            return {"message": "role must be one of: member, trainer, admin"}, HTTPStatus.BAD_REQUEST
        
        if not isinstance(notification_channels, list) or not all(c in VALID_CHANNELS for c in notification_channels):
           return {"message": "notification_channels must be a list containing: email, telegram"}, HTTPStatus.BAD_REQUEST

        user_resource = UserResource()
        try:
            user_id = user_resource.register_user(
                name=name,
                email=email,
                phone=phone,
                password=password,
                role=role,
                notification_channels=notification_channels,
                telegram_chat_id=telegram_chat_id,
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

@api.route("/preferences")
class Preferences(Resource):
   @api.expect(PREFERENCES_MODEL)
   @api.doc(description="Update notification preferences for the logged-in user.", security="Bearer Auth")
   @api.response(HTTPStatus.OK, "Preferences updated")
   @api.response(HTTPStatus.BAD_REQUEST, "Validation error")
   @api.response(HTTPStatus.UNAUTHORIZED, "Not authenticated")
   @jwt_required()
   def put(self):
       """Update notification channels and Telegram chat ID (JWT required)"""
       data = request.json
       if not data:
           return {"message": "Request body is required"}, HTTPStatus.BAD_REQUEST


       notification_channels = data.get("notification_channels")
       telegram_chat_id = data.get("telegram_chat_id") or ""


       if not isinstance(notification_channels, list) or not notification_channels:
           return {"message": "notification_channels must be a non-empty list"}, HTTPStatus.BAD_REQUEST


       if not all(c in VALID_CHANNELS for c in notification_channels):
           return {"message": "notification_channels must only contain: email, telegram"}, HTTPStatus.BAD_REQUEST


       email = get_jwt_identity()
       user_resource = UserResource()
       user_resource.update_preferences(email, notification_channels, telegram_chat_id)
       return {"message": "Preferences updated successfully"}, HTTPStatus.OK