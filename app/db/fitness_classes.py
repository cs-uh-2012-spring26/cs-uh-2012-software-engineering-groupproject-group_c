from app.db.utils import serialize_item, serialize_items
from app.db import DB
from bson import ObjectId

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

   def get_fitness_classes(self):
       classes = self.collection.find({})
       return serialize_items(list(classes))

   def create_fitness_class(self, name: str, description: str, date: str, start_time: str, end_time: str, location: str, trainer: str,
       capacity: int,created_by: str):

       fitness_class = {NAME: name, DESCRIPTION: description, DATE: date, START_TIME: start_time, END_TIME: end_time, LOCATION: location,
       TRAINER: trainer, CAPACITY: capacity, AVAILABLE_SLOTS: available_slots, PARTICIPANTS: [], CREATED_BY: created_by}

       result = self.collection.insert_one(fitness_class)
       return str(result.inserted_id)

   def book_class(self, class_id: str, user_id: str, is_trainer: bool = False):
       fitness_class = self.get_class_by_id(class_id)
       if fitness_class is None:
           return "not_found"

       participants = fitness_class.get(PARTICIPANTS, [])
       if user_id in participants:
           return "already_booked"

       if not is_trainer and fitness_class[AVAILABLE_SLOTS] <= 0:
           return "class_full"

       try:
           oid = ObjectId(class_id)
       except Exception:
           return "not_found"

       update: dict = {"$push": {PARTICIPANTS: user_id}}
       if not is_trainer:
           update["$inc"] = {AVAILABLE_SLOTS: -1}

       self.collection.update_one({"_id": oid}, update)
       return "ok"

   def get_participants(self, class_id: str):
       fitness_class = self.get_class_by_id(class_id)
       if fitness_class is None:
           return None
       return fitness_class.get(PARTICIPANTS, [])

   def get_fitness_class_by_id(self, fitness_class_id: str):
       try:
           oid = ObjectId(fitness_class_id)
       except Exception:
           return None
       fitness_class = self.collection.find_one({"_id": oid})
       return serialize_item(fitness_class)

   def add_multiple_fitness_classes(self, fitness_classes: list[dict]):
       if not fitness_classes:
           return
       self.collection.insert_many(fitness_classes)