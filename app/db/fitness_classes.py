from app.db.utils import serialize_item, serialize_items
from app.db import DB
from app.db.booking_result import BookingResult
from bson import ObjectId
from datetime import datetime, timedelta
import uuid

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
RECURRENCE_GROUP_ID = "recurrence_group_id"

RECURRENCE_DELTAS = {
   "daily": timedelta(days=1),
   "weekly": timedelta(weeks=1),
}

class FitnessClassResource:
   def __init__(self):
       self.collection = DB.get_collection(FITNESS_CLASS)

   def get_fitness_classes(self):
      classes = self.collection.find({})
      classes_without_participants = []
      for c in classes:
          c.pop(PARTICIPANTS, None)
          classes_without_participants.append(c)
      return serialize_items(classes_without_participants)

   def create_fitness_class(self, name: str, description: str, date: str, start_time: str, end_time: str, location: str, trainer: str,
       capacity: int, created_by: str, recurrence_group_id: str = None):

       fitness_class = {NAME: name, DESCRIPTION: description, DATE: date, START_TIME: start_time, END_TIME: end_time, LOCATION: location,
       TRAINER: trainer, CAPACITY: capacity, AVAILABLE_SLOTS: capacity, PARTICIPANTS: [], CREATED_BY: created_by}

       if recurrence_group_id:
           fitness_class[RECURRENCE_GROUP_ID] = recurrence_group_id
       result = self.collection.insert_one(fitness_class)
       return str(result.inserted_id)

   def create_recurring_classes(self, name: str, description: str, date: str, start_time: str, end_time: str, location: str,
       trainer: str, capacity: int, created_by: str, recurrence: str, count: int) -> list:
       delta = RECURRENCE_DELTAS.get(recurrence, timedelta(days=1))
       group_id = str(uuid.uuid4())
       base_date = datetime.strptime(date, "%Y-%m-%d")
       created_ids = []
       for i in range(count):
           class_date = (base_date + delta * i).strftime("%Y-%m-%d")
           class_id = self.create_fitness_class(
               name, description, class_date, start_time, end_time,
               location, trainer, capacity, created_by,
               recurrence_group_id=group_id,
           )
           created_ids.append(class_id)
       return created_ids

   def book_class(self, class_id: str, participant: dict) -> BookingResult:
       fitness_class = self.get_fitness_class_by_id(class_id)
       if fitness_class is None:
           return BookingResult.NOT_FOUND

       email = participant.get("email", "")
       for p in fitness_class.get(PARTICIPANTS, []):
           existing_email = p.get("email", "") if isinstance(p, dict) else p
           if existing_email == email:
               return BookingResult.ALREADY_BOOKED

       if fitness_class.get(AVAILABLE_SLOTS, 0) <= 0:
          return BookingResult.CLASS_FULL

       try:
           oid = ObjectId(class_id)
       except Exception:
           return BookingResult.NOT_FOUND

       self.collection.update_one({"_id": oid},
           {"$push": {PARTICIPANTS: participant}, "$inc": {AVAILABLE_SLOTS: -1}})
       return BookingResult.OK

   def has_participants(self, class_id: str) -> bool:
       fitness_class = self.get_fitness_class_by_id(class_id)
       if fitness_class is None:
           return False
       return len(fitness_class.get(PARTICIPANTS, [])) > 0

   def get_participants(self, class_id: str):
       fitness_class = self.get_fitness_class_by_id(class_id)
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

   def add_multiple_fitness_classes(self, fitness_classes: list):
       if not fitness_classes:
           return
       self.collection.insert_many(fitness_classes)
