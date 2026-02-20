from app.apis.auth import api as auth_ns
from app.apis.classes import api as classes_ns
from app.config import Config
from app.db import DB

from http import HTTPStatus
from flask import Flask
from flask_restx import Api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    DB.init_app(app)

    api = Api(
        title="Fitness Class Management and Booking System",
        version="1.0",
        description="A simple Fitness Class Management and Booking System  API",
        authorizations = 
        {
            "Bearer Auth": 
            {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Enter: Bearer <JWT code>",
            }
        }
    )

    api.init_app(app)
    api.add_namespace(auth_ns)
    api.add_namespace(classes_ns)

    @api.errorhandler(Exception)
    def handle_input_validation_error(error):
        return {"message": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR

    return app