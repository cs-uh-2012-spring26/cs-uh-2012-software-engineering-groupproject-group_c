from app.db.utils import serialize_item, serialize_items
from app.db import DB

# Fitness Class Collection Name
FITNESS_CLASS = "fitness_class"

# Fitness Class fields
NAME = "name"
DESCRIPTION = "description"
DATE = "date"
START_TIME = "start_time"
END_TIME = "end_time"
LOCATION = "location"
TRAINER = "trainer"
CAPACITY = "capacity"
AVAILABLE_SLOTS = "available_slots"
PARTICIPANTS = "participants"
CREATED_BY = "created_by"

class FitnessClassResource:

    def __init__(self):
        self.collection = DB.get_collection(FITNESS_CLASS)

    def get_fitness_classes(self, name: str | None = None, description: str | None = None,
            date: str | None = None, start_time: str | None = None, end_time: str | None = None,
            location: str | None = None, trainer: str | None = None, capacity: int | None = None,
            available_slots: int | None = None, participants: list[str] | None = None,
            created_by: str | None = None):
        query = {}
        if name is not None:
            query[NAME] = {"$regex": name}
        if description is not None:
            query[DESCRIPTION] = description
        if date is not None:
            query[DATE] = date
        if start_time is not None:
            query[START_TIME] = start_time
        if end_time is not None:
            query[END_TIME] = end_time
        if location is not None:
            query[LOCATION] = location
        if trainer is not None:
            query[TRAINER] = trainer
        if capacity is not None:
            query[CAPACITY] = capacity
        if available_slots is not None:
            query[AVAILABLE_SLOTS] = available_slots
        if participants is not None:
            query[PARTICIPANTS] = participants
        if created_by is not None:
            query[CREATED_BY] = created_by

        fitness_classes = self.collection.find(query)
        return serialize_items(list(fitness_classes))

    def create_fitness_class(self, name: str, description: str, date: str, start_time: str, end_time: str, location: str, trainer: str, capacity: int, available_slots: int, participants: list[str], created_by: str):
        fitness_class = {NAME: name, DESCRIPTION: description, DATE: date, START_TIME: start_time, END_TIME: end_time, LOCATION: location, TRAINER: trainer, CAPACITY: capacity, AVAILABLE_SLOTS: available_slots, PARTICIPANTS: participants, CREATED_BY: created_by}
        result = self.collection.insert_one(fitness_class)
        return result.inserted_id

    def update_fitness_class(self, lookup_name: str, name: str, description: str, date: str, start_time: str, end_time: str, location: str, trainer: str, capacity: int, available_slots: int, participants: list[str], created_by: str):
        fitness_class_record = self.get_fitness_class_by_name(lookup_name)

        if fitness_class_record is None:
            return None

        new_data = {NAME: name, DESCRIPTION: description, DATE: date, START_TIME: start_time, END_TIME: end_time, LOCATION: location, TRAINER: trainer, CAPACITY: capacity, AVAILABLE_SLOTS: available_slots, PARTICIPANTS: participants, CREATED_BY: created_by}
        result = self.collection.update_one({NAME: lookup_name}, {"$set": new_data})

        return result

    def get_fitness_class_by_name(self, name: str):
        fitness_class = self.collection.find_one({NAME: name})
        return serialize_item(fitness_class)

    def delete_all_fitness_classes(self):
        self.collection.delete_many({})

    def add_multiple_fitness_classes(self, fitness_classes: list[dict]):
        if not fitness_classes:
            return

        self.collection.insert_many(fitness_classes)
