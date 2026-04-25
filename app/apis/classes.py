from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.apis import MSG
from app.db.fitness_classes import FitnessClassResource
from app.db.fitness_classes import (
   NAME, DESCRIPTION, DATE, START_TIME, END_TIME,
   LOCATION, TRAINER, CAPACITY, AVAILABLE_SLOTS, PARTICIPANTS, CREATED_BY,
)
from app.db.users import UserResource
from app.db.booking_result import BookingResult
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

VALID_RECURRENCES = {"daily", "weekly"}
MAX_RECURRENCE_COUNT = 10
BOOKING_DEADLINE_MINUTES = 30

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
        "recurrence": fields.String(
            required=False,
            description="Recurrence type: daily or weekly",
            enum=["daily", "weekly"],
            example="weekly",
        ),
        "recurrence_count": fields.Integer(
            required=False,
            description=f"Number of recurring instances (2–{MAX_RECURRENCE_COUNT})",
            example=4,
        ),
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


def _fetch_class_or_404(class_id: str):
    fitness_class = FitnessClassResource().get_fitness_class_by_id(class_id)
    if fitness_class is None:
        return None, ({MSG: "Class not found"}, HTTPStatus.NOT_FOUND)
    return fitness_class, None


def _validate_class_fields(data: dict):
    name = data.get(NAME, "").strip() if isinstance(data.get(NAME), str) else ""
    description = data.get(DESCRIPTION, "").strip() if isinstance(data.get(DESCRIPTION), str) else ""
    date = data.get(DATE, "").strip() if isinstance(data.get(DATE), str) else ""
    start_time = data.get(START_TIME, "").strip() if isinstance(data.get(START_TIME), str) else ""
    end_time = data.get(END_TIME, "").strip() if isinstance(data.get(END_TIME), str) else ""
    location = data.get(LOCATION, "").strip() if isinstance(data.get(LOCATION), str) else ""
    trainer = data.get(TRAINER, "").strip() if isinstance(data.get(TRAINER), str) else ""
    capacity = data.get(CAPACITY)

    if not all([name, description, date, start_time, end_time, location, trainer]):
        return None, ({MSG: "All fields are required: name, description, date, start_time, end_time, location, trainer, capacity"}, HTTPStatus.BAD_REQUEST)

    if not isinstance(capacity, int) or capacity <= 0:
        return None, ({MSG: "Capacity must be a positive integer"}, HTTPStatus.BAD_REQUEST)

    try:
        class_start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None, ({MSG: "Invalid date or start_time format. Use YYYY-MM-DD and HH:MM"}, HTTPStatus.BAD_REQUEST)

    if class_start < datetime.now():
        return None, ({MSG: "Cannot create a class in the past"}, HTTPStatus.BAD_REQUEST)

    return {
        "name": name, "description": description, "date": date,
        "start_time": start_time, "end_time": end_time,
        "location": location, "trainer": trainer, "capacity": capacity,
    }, None


@api.route("/")
class FitnessClassList(Resource):
    @api.doc(description=" Returns all fitness classes. Accessible to guests, members, and admins.")
    @api.response(
        HTTPStatus.OK,
        "Success")

    def get(self):
         """List all upcoming fitness classes (public)"""
         class_list = FitnessClassResource().get_fitness_classes()
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

       fields, error = _validate_class_fields(data)
       if error:
           return error

       recurrence = data.get("recurrence")
       recurrence_count = data.get("recurrence_count")

       if recurrence is not None:
           if recurrence not in VALID_RECURRENCES:
               return {MSG: "recurrence must be 'daily' or 'weekly'"}, HTTPStatus.BAD_REQUEST
           if not isinstance(recurrence_count, int) or not (2 <= recurrence_count <= MAX_RECURRENCE_COUNT):
               return {MSG: f"recurrence_count must be an integer between 2 and {MAX_RECURRENCE_COUNT}"}, HTTPStatus.BAD_REQUEST

       created_by = get_jwt_identity()
       fc_resource = FitnessClassResource()

       if recurrence:
           class_ids = fc_resource.create_recurring_classes(
               fields["name"], fields["description"], fields["date"],
               fields["start_time"], fields["end_time"], fields["location"],
               fields["trainer"], fields["capacity"], created_by,
               recurrence=recurrence, count=recurrence_count,
           )
           return {MSG: f"{len(class_ids)} recurring classes created", "class_ids": class_ids}, HTTPStatus.CREATED

       class_id = fc_resource.create_fitness_class(
           fields["name"], fields["description"], fields["date"],
           fields["start_time"], fields["end_time"], fields["location"],
           fields["trainer"], fields["capacity"], created_by,
       )
       return {MSG: f"Fitness class created with id: {class_id}"}, HTTPStatus.CREATED

@api.route("/<string:class_id>/book")
@api.param("class_id", "The fitness class identifier")
class BookClass(Resource):
   @api.doc(description="Book a fitness class. Member only.", security="Bearer Auth")
   @api.response(HTTPStatus.OK, "Booking successful")
   @api.response(HTTPStatus.BAD_REQUEST, "Validation error")
   @api.response(HTTPStatus.UNAUTHORIZED, "Not authenticated")
   @api.response(HTTPStatus.FORBIDDEN, "Member role required")
   @api.response(HTTPStatus.NOT_FOUND, "Class not found")
   @jwt_required()
   def post(self, class_id):
       """Book a fitness class (member, Bearer token required)"""
       claims = get_jwt()
       if claims.get("role") != "member":
           return {MSG: "Member role required to book a class"}, HTTPStatus.FORBIDDEN

       fitness_class, error = _fetch_class_or_404(class_id)
       if error:
           return error

       class_start = _parse_class_datetime(fitness_class)
       if class_start is not None:
           booking_deadline = class_start + timedelta(minutes=BOOKING_DEADLINE_MINUTES)
           if datetime.now() > booking_deadline:
               return {MSG: "Booking deadline has passed (30 minutes after class start)"}, HTTPStatus.BAD_REQUEST

       user_email = claims.get("email", "")
       user_resource = UserResource()
       user = user_resource.get_user_by_email(user_email)
       if user is None:
           return {MSG: "User not found"}, HTTPStatus.NOT_FOUND

       participant = {
           "name": user.get("name", ""),
           "email": user.get("email", ""),
           "phone": user.get("phone", ""),
       }

       result = FitnessClassResource().book_class(class_id, participant)

       if result == BookingResult.NOT_FOUND:
           return {MSG: "Class not found"}, HTTPStatus.NOT_FOUND
       if result == BookingResult.ALREADY_BOOKED:
           return {MSG: "You have already booked this class"}, HTTPStatus.BAD_REQUEST
       if result == BookingResult.CLASS_FULL:
           return {MSG: "Class is full, no available spots"}, HTTPStatus.BAD_REQUEST

       return {MSG: "Class booked successfully"}, HTTPStatus.OK

@api.route("/<string:class_id>/participants")
@api.param("class_id", "The fitness class identifier")
class ClassParticipants(Resource):
   @api.doc(description="View participants of a fitness class. Admin only.", security="Bearer Auth")
   @api.response(HTTPStatus.OK, "Success")
   @api.response(HTTPStatus.UNAUTHORIZED, "Not authenticated")
   @api.response(HTTPStatus.FORBIDDEN, "Admin role required")
   @api.response(HTTPStatus.NOT_FOUND, "Class not found")
   @jwt_required()
   def get(self, class_id):
       """View participants of a fitness class (admin, Bearer token required)"""
       claims = get_jwt()
       if claims.get("role") != "admin":
           return {MSG: "Admin role required"}, HTTPStatus.FORBIDDEN


       fitness_class_resource = FitnessClassResource()
       participants = fitness_class_resource.get_participants(class_id)


       if participants is None:
           return {MSG: "Class not found"}, HTTPStatus.NOT_FOUND


       return {MSG: participants}, HTTPStatus.OK

@api.route("/<string:class_id>/remind")
@api.param("class_id", "The fitness class identifier")
class ClassReminder(Resource):
  @api.doc(description="Send reminders to class participants via their chosen channels. Trainer/Admin only.", security="Bearer Auth")
  @api.response(HTTPStatus.OK, "Reminders sent")
  @api.response(HTTPStatus.NOT_FOUND, "Class not found")
  @api.response(HTTPStatus.BAD_REQUEST, "No participants or class already started")
  @api.response(HTTPStatus.FORBIDDEN, "Trainer or Admin role required")
  @jwt_required()
  def post(self, class_id):
      """Send reminders to all participants via their chosen channels (trainer/admin, Bearer token required)"""
      claims = get_jwt()
      if claims.get("role") not in ("trainer", "admin"):
          return {MSG: "Trainer or Admin role required"}, HTTPStatus.FORBIDDEN

      fitness_class, error = _fetch_class_or_404(class_id)
      if error:
          return error

      class_start = _parse_class_datetime(fitness_class)
      if class_start is not None and datetime.now() > class_start:
          return {MSG: "Cannot send reminders for a class that has already started"}, HTTPStatus.BAD_REQUEST

      fc_resource = FitnessClassResource()
      if not fc_resource.has_participants(class_id):
          return {MSG: "No participants to remind"}, HTTPStatus.BAD_REQUEST

      from app.services.email_service import EmailService
      from app.services.notifier import EmailNotifier, TelegramNotifier
      from app.config import Config

      notifier_registry = {
          "email": EmailNotifier(EmailService()),
          "telegram": TelegramNotifier(Config.TELEGRAM_BOT_TOKEN),
      }

      user_resource = UserResource()
      participants = fitness_class.get(PARTICIPANTS, [])
      participants_reached = 0

      for participant in participants:
          email = participant.get("email", "") if isinstance(participant, dict) else participant
          user = user_resource.get_user_by_email(email)
          channels = user.get("notification_channels", ["email"]) if user else ["email"]
          recipient = {
              **(participant if isinstance(participant, dict) else {"email": participant}),
              "telegram_chat_id": user.get("telegram_chat_id", "") if user else "",
          }
          participant_notified = False
          for channel in channels:
              notifier = notifier_registry.get(channel)
              if notifier is None:
                  continue
              try:
                  notifier.send_reminder(recipient, fitness_class)
                  participant_notified = True
              except Exception:
                  continue
          if participant_notified:
              participants_reached += 1

      return {MSG: f"Reminders sent to {participants_reached} participants"}, HTTPStatus.OK
