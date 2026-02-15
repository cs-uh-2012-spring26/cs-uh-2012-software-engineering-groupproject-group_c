from app.db.utils import serialize_item, serialize_items
from app.db import DB

# User Collection Name
USER_COLLECTION = "users"

# User fields
NAME = "name"
EMAIL = "email"
PHONE = "phone"
ROLE = "role"
BIRTHDATE = "birthdate"
GENDER = "gender"
PASSWORD = "password"



class UserResource:

    def __init__(self):
        self.collection = DB.get_collection(USER_COLLECTION)

    def get_users(self, name: str | None = None, role: str | None = None):
        query = {}
        if name is not None:
            query[NAME] = {"$regex": name}
        if role is not None:
            query[ROLE] = role

        users = self.collection.find(query)
        return serialize_items(list(users))

    def create_user(self, name: str, email: str, role: str, password: str,phone: str | None = None,
                    birthdate: str | None = None, gender: str | None = None):
        
        user = {NAME: name, EMAIL: email, ROLE: role, PASSWORD: password}
        if phone is not None:
            user[PHONE] = phone
        if birthdate is not None:
            user[BIRTHDATE] = birthdate
        if gender is not None:
            user[GENDER] = gender

        result = self.collection.insert_one(user)
        return result.inserted_id

    def update_user(self, lookupemail: str, name: str, email: str, role: str):
        user_record = self.get_user_by_email(lookupemail)

        if user_record is None:
            return None

        new_data = {NAME: name, EMAIL: email, ROLE: role}
        result = self.collection.update_one({EMAIL: lookupemail}, {"$set": new_data})

        return result

    def get_user_by_email(self, email: str):
        user = self.collection.find_one({EMAIL: email})
        return serialize_item(user)

    def delete_all_users(self):
        self.collection.delete_many({})

    def add_multiple_users(self, users: list[dict]):
        if not users:
            return

        self.collection.insert_many(users)
