from flask_restx import Namespace, Resource, fields
from app.db.utils import serialize_item
from app.db import DB

api = Namespace("auth", description="Authentication operations")

AUTH_MODEL = api.model("Auth", {
    "email": fields.String(required=True),
    "password": fields.String(required=True)
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