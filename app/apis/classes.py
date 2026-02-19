from flask_restx import Namespace, Resource, fields
from app.apis import MSG
from app.db.fitness_class import FitnessClassResource
from app.db.fitness_class import NAME, DESCRIPTION, DATE, START_TIME, END_TIME, LOCATION, TRAINER, CAPACITY
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
    },
)


@api.route("/")
class FitnessClassList(Resource):
    @api.doc(
        params={
            "name": "Filter class list by class name (partial matches allowed)",
            "description": "Filter class list by class description (partial matches allowed)",
            "date": "Filter class list by class date (Exact date match)",
            "start_time": "Filter class list by class start time (Exact time match)",
            "end_time": "Filter class list by class end time (Exact time match)",
            "location": "Filter class list by class location (partial matches allowed)",
            "trainer": "Filter class list by class trainer (partial matches allowed)",
            "capacity": "Filter class list by class capacity (Exact capacity match)",
            "available_slots": "Filter class list by class available slots (Exact available slots match)",
            "participants": "Filter class list by class participants (partial matches allowed)",
            "created_by": "Filter class list by class created by (partial matches allowed)",
        }
    )
    @api.response(
        HTTPStatus.OK,
        "Success",
        api.model(
            "All Students",
            {
                MSG: fields.List(
                    fields.Nested(STUDENT_CREATE_FLDS),
                    example=[_EXAMPLE_STUDENT_1, _EXAMPLE_STUDENT_2],
                )
            },
        ),
    )
    def get(self):
        name = request.args.get("name")
        seniority = request.args.get("seniority")
        student_resource = StudentResource()
        student_list = student_resource.get_students(name, seniority)
        return {MSG: student_list}, HTTPStatus.OK

    @api.expect(FITNESS_CLASS_CREATE_FLDS)
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

        current_user = get_current_user()
        fitness_class_resource = FitnessClassResource()
        class_id = fitness_class_resource.create_fitness_class(
            name, description, date, start_time,
            end_time, location, trainer, capacity
        )
        return {MSG: f"Fitness class created with id: {class_id}"}, HTTPStatus.OK


@api.route("/<email>")
@api.param("email", "Student email to use for lookup")
@api.response(
    HTTPStatus.NOT_FOUND,
    "Student Not Found",
    api.model("Student: Not Found", {MSG: fields.String("Student not found")}),
)
class Student(Resource):
    @api.doc("Get a specific student, identified by email")
    @api.response(HTTPStatus.OK, "Success", STUDENT_CREATE_FLDS)
    def get(self, email):
        student_resource = StudentResource()
        student = student_resource.get_student_by_email(email)

        if student is None:
            return {MSG: "Student not found"}, HTTPStatus.NOT_FOUND

        return {MSG: student}, HTTPStatus.OK

    @api.expect(STUDENT_CREATE_FLDS)
    @api.doc("Update a specific student, identified by email")
    @api.response(
        HTTPStatus.OK,
        "Success",
        api.model("Update Student", {MSG: fields.String("Student updated")}),
    )
    @api.response(
        HTTPStatus.NOT_ACCEPTABLE,
        "Student Update Information Not Acceptable",
        api.model(
            "Update Student: Not Acceptable",
            {MSG: fields.String("Invalid value provided for one of the fields")},
        ),
    )
    def put(self, email):
        assert isinstance(request.json, dict)
        name = request.json.get(NAME)
        seniority = request.json.get(SENIORITY)
        new_email = request.json.get(EMAIL)
        if not (
            isinstance(name, str)
            and len(name) > 0
            and isinstance(new_email, str)
            and len(new_email) > 0
            and isinstance(seniority, str)
            and seniority.lower() in ["first-year", "sophomore", "junior", "senior"]
        ):
            return {
                MSG: "Invalid value provided for one of the fields"
            }, HTTPStatus.NOT_ACCEPTABLE

        student_resource = StudentResource()
        updated_student = student_resource.update_student(
            email, name, new_email, seniority
        )

        if updated_student is None:
            return {MSG: "Student not found"}, HTTPStatus.NOT_FOUND

        return {MSG: "Student updated"}, HTTPStatus.OK
