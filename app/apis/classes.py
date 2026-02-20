from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.apis import MSG
from app.db.fitness_classes import FitnessClassResource
from app.db.fitness_classes import NAME, DESCRIPTION, DATE, START_TIME, END_TIME, LOCATION, TRAINER, CAPACITY, AVAILABLE_SLOTS, PARTICIPANTS, CREATED_BY
from http import HTTPStatus
from flask import request

api = Namespace("classes", description="Endpoint for fitness_class")

_EXAMPLE_CLASS_1 = {
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
    CREATED_BY: "admin",
}

CLASS_CREATE_FLDS = api.model(
    "NewClassEntry",
    {
        NAME: fields.String(example=_EXAMPLE_CLASS_1[NAME]),
        DESCRIPTION: fields.String(example=_EXAMPLE_CLASS_1[DESCRIPTION]),
        DATE: fields.String(example=_EXAMPLE_CLASS_1[DATE]),
        START_TIME: fields.String(example=_EXAMPLE_CLASS_1[START_TIME]),
        END_TIME: fields.String(example=_EXAMPLE_CLASS_1[END_TIME]),
        LOCATION: fields.String(example=_EXAMPLE_CLASS_1[LOCATION]),
        TRAINER: fields.String(example=_EXAMPLE_CLASS_1[TRAINER]),
        CAPACITY: fields.Integer(example=_EXAMPLE_CLASS_1[CAPACITY]),
        AVAILABLE_SLOTS: fields.Integer(example=_EXAMPLE_CLASS_1[AVAILABLE_SLOTS]),
        PARTICIPANTS: fields.List(fields.String, example=_EXAMPLE_CLASS_1[PARTICIPANTS]),
        CREATED_BY: fields.String(example=_EXAMPLE_CLASS_1[CREATED_BY]),
    },
)


@api.route("/")
class FitnessClassList(Resource):
    @api.doc(description=" Returns all fitness classes. Accessible to guests, members, and admins.")
    @api.response(
        HTTPStatus.OK,
        "Success",
        api.model(
            "All Fitness Classes",
            {
                MSG: fields.List(
                    fields.Nested(CLASS_CREATE_FLDS),
                    example=[_EXAMPLE_CLASS_1],
                )
            },
        ),
    )
    def get(self):
        fitness_class_resource = FitnessClassResource()
        class_list = fitness_class_resource.get_fitness_classes()
        return {MSG: class_list}, HTTPStatus.OK

    @api.expect(CLASS_CREATE_FLDS)
    @api.doc(security='Bearer Auth')
    @api.response(
        HTTPStatus.OK,
        "Success",
        api.model(
            "Create Fitness Class",
            {MSG: fields.String("Fitness class created with id: XXXXXXXXXXXXXXXXXXXXXXXX")},
        ),
    )
    @api.response(
        HTTPStatus.NOT_ACCEPTABLE,
        "Invalid Request",
        api.model(
            "Create Fitness Class: Bad Request",
            {MSG: fields.String("Invalid value provided for one of the fields")},
        ),
    )
    @api.response(
        HTTPStatus.UNAUTHORIZED,
        "Unauthorized",
        api.model(
            "Create Fitness Class: Unauthorized",
            {MSG: fields.String("Admin or trainer access required")},
        ),
    )
    @jwt_required()
    def post(self):
        assert isinstance(request.json, dict)
        name = request.json.get(NAME)
        description = request.json.get(DESCRIPTION)
        date = request.json.get(DATE)
        start_time = request.json.get(START_TIME)
        end_time = request.json.get(END_TIME)
        location = request.json.get(LOCATION)
        trainer = request.json.get(TRAINER)
        capacity = request.json.get(CAPACITY)
        if not (
            isinstance(name, str) and len(name) > 0
            and isinstance(description, str) and len(description) > 0
            and isinstance(date, str) and len(date) > 0
            and isinstance(start_time, str) and len(start_time) > 0
            and isinstance(end_time, str) and len(end_time) > 0
            and isinstance(location, str) and len(location) > 0
            and isinstance(trainer, str) and len(trainer) > 0
            and isinstance(capacity, int) and capacity > 0
        ):
            return {
                MSG: "Invalid value provided for one of the fields"
            }, HTTPStatus.NOT_ACCEPTABLE

        current_user = get_jwt_identity()
        fitness_class_resource = FitnessClassResource()
        class_id = fitness_class_resource.create_fitness_class(
            name, description, date, start_time,
            end_time, location, trainer, capacity
        )
        return {MSG: f"Fitness class created with id: {class_id}"}, HTTPStatus.OK


# @api.route("/<email>")
# @api.param("email", "Student email to use for lookup")
# @api.response(
#     HTTPStatus.NOT_FOUND,
#     "Student Not Found",
#     api.model("Student: Not Found", {MSG: fields.String("Student not found")}),
# )
# class Student(Resource):
#     @api.doc("Get a specific student, identified by email")
#     @api.response(HTTPStatus.OK, "Success", STUDENT_CREATE_FLDS)
#     def get(self, email):
#         student_resource = StudentResource()
#         student = student_resource.get_student_by_email(email)

#         if student is None:
#             return {MSG: "Student not found"}, HTTPStatus.NOT_FOUND

#         return {MSG: student}, HTTPStatus.OK

#     @api.expect(STUDENT_CREATE_FLDS)
#     @api.doc("Update a specific student, identified by email")
#     @api.response(
#         HTTPStatus.OK,
#         "Success",
#         api.model("Update Student", {MSG: fields.String("Student updated")}),
#     )
#     @api.response(
#         HTTPStatus.NOT_ACCEPTABLE,
#         "Student Update Information Not Acceptable",
#         api.model(
#             "Update Student: Not Acceptable",
#             {MSG: fields.String("Invalid value provided for one of the fields")},
#         ),
#     )
#     def put(self, email):
#         assert isinstance(request.json, dict)
#         name = request.json.get(NAME)
#         seniority = request.json.get(SENIORITY)
#         new_email = request.json.get(EMAIL)
#         if not (
#             isinstance(name, str)
#             and len(name) > 0
#             and isinstance(new_email, str)
#             and len(new_email) > 0
#             and isinstance(seniority, str)
#             and seniority.lower() in ["first-year", "sophomore", "junior", "senior"]
#         ):
#             return {
#                 MSG: "Invalid value provided for one of the fields"
#             }, HTTPStatus.NOT_ACCEPTABLE

#         student_resource = StudentResource()
#         updated_student = student_resource.update_student(
#             email, name, new_email, seniority
#         )

#         if updated_student is None:
#             return {MSG: "Student not found"}, HTTPStatus.NOT_FOUND

#         return {MSG: "Student updated"}, HTTPStatus.OK
