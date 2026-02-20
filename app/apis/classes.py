from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.apis import MSG
from app.db.fitness_classes import FitnessClassResource
from app.db.fitness_classes import (
   NAME, DESCRIPTION, DATE, START_TIME, END_TIME,
   LOCATION, TRAINER, CAPACITY, AVAILABLE_SLOTS, PARTICIPANTS, CREATED_BY,
)
from app.db.users import UserResource
from http import HTTPStatus
from flask import request
from datetime import datetime, timedelta


api = Namespace("classes", description="Fitness class management and booking")

_EXAMPLE_CLASS = {
   NAME: "Yoga",
   DESCRIPTION: "A relaxing yoga class",
   DATE: "2025-10-10",
   START_TIME: "10:00",
   END_TIME: "11:00",
   LOCATION: "Gym",
   TRAINER: "Jane Doe",
   CAPACITY: 10,
   AVAILABLE_SLOTS: 10,
   PARTICIPANTS: [],
   CREATED_BY: "admin@example.com",
}


CLASS_CREATE_FLDS = api.model(
    "NewClassEntry",
    {
        NAME: fields.String(required=True, example=_EXAMPLE_CLASS[NAME]),
        DESCRIPTION: fields.String(required=True, example=_EXAMPLE_CLASS[DESCRIPTION]),
        DATE: fields.String(required=True, example=_EXAMPLE_CLASS[DATE]),
        START_TIME: fields.String(required=True, example=_EXAMPLE_CLASS[START_TIME]),
        END_TIME: fields.String(required=True, example=_EXAMPLE_CLASS[END_TIME]),
        LOCATION: fields.String(required=True, example=_EXAMPLE_CLASS[LOCATION]),
        TRAINER: fields.String(required=True, example=_EXAMPLE_CLASS[TRAINER]),
        CAPACITY: fields.Integer(required=True, example=_EXAMPLE_CLASS[CAPACITY]),
    },
)

CLASS_VIEW_FLDS = api.model(
   "ClassView",
   {
       NAME: fields.String,
       DESCRIPTION: fields.String,
       DATE: fields.String,
       START_TIME: fields.String,
       END_TIME: fields.String,
       LOCATION: fields.String,
       TRAINER: fields.String,
       CAPACITY: fields.Integer,
       AVAILABLE_SLOTS: fields.Integer,
   },
)

PARTICIPANT_FLDS = api.model(
   "Participant",
   {
       "name": fields.String(example="John Doe"),
       "email": fields.String(example="john@example.com"),
       "phone": fields.String(example="+1234567890"),
   },
)

def _parse_class_datetime(fitness_class: dict) -> datetime | None:
   try:
       date_str = fitness_class.get(DATE, "")
       time_str = fitness_class.get(START_TIME, "")
       return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
   except (ValueError, TypeError):
       return None



@api.route("/")
class FitnessClassList(Resource):
    @api.doc(description=" Returns all fitness classes. Accessible to guests, members, and admins.")
    @api.response(
        HTTPStatus.OK,
        "Success")

    def get(self):
         """List all upcoming fitness classes (public)"""
         fitness_class_resource = FitnessClassResource()
         class_list = fitness_class_resource.get_fitness_classes()
         return {MSG: class_list}, HTTPStatus.OK

    @api.expect(CLASS_CREATE_FLDS)
    @api.doc(description="Create a new fitness class. Admin only.", security="Bearer Auth")
    @api.response(HTTPStatus.CREATED, "Class created")
    @api.response(HTTPStatus.BAD_REQUEST, "Validation error")
    @api.response(HTTPStatus.UNAUTHORIZED, "Not authenticated")
    @api.response(HTTPStatus.FORBIDDEN, "Admin role required")
    @jwt_required()

    def post(self):
       """Create a new fitness class (admin, Bearer token required)"""
       claims = get_jwt()
       if claims.get("role") != "admin":
           return {MSG: "Admin role required"}, HTTPStatus.FORBIDDEN


       data = request.json
       if not isinstance(data, dict):
           return {MSG: "Request body is required"}, HTTPStatus.BAD_REQUEST


       name = data.get(NAME, "").strip() if isinstance(data.get(NAME), str) else ""
       description = data.get(DESCRIPTION, "").strip() if isinstance(data.get(DESCRIPTION), str) else ""
       date = data.get(DATE, "").strip() if isinstance(data.get(DATE), str) else ""
       start_time = data.get(START_TIME, "").strip() if isinstance(data.get(START_TIME), str) else ""
       end_time = data.get(END_TIME, "").strip() if isinstance(data.get(END_TIME), str) else ""
       location = data.get(LOCATION, "").strip() if isinstance(data.get(LOCATION), str) else ""
       trainer = data.get(TRAINER, "").strip() if isinstance(data.get(TRAINER), str) else ""
       capacity = data.get(CAPACITY)


       if not all([name, description, date, start_time, end_time, location, trainer]):
           return {MSG: "All fields are required: name, description, date, start_time, end_time, location, trainer, capacity"}, HTTPStatus.BAD_REQUEST


       if not isinstance(capacity, int) or capacity <= 0:
           return {MSG: "Capacity must be a positive integer"}, HTTPStatus.BAD_REQUEST


       try:
           class_start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
       except ValueError:
           return {MSG: "Invalid date or start_time format. Use YYYY-MM-DD and HH:MM"}, HTTPStatus.BAD_REQUEST


       if class_start < datetime.now():
           return {MSG: "Cannot create a class in the past"}, HTTPStatus.BAD_REQUEST


       created_by = get_jwt_identity()
       fitness_class_resource = FitnessClassResource()
       class_id = fitness_class_resource.create_fitness_class(
           name, description, date, start_time, end_time,
           location, trainer, capacity, created_by,
       )
       return {MSG: f"Fitness class created with id: {class_id}"}, HTTPStatus.CREATED