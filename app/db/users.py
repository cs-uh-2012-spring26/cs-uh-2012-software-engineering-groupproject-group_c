from app.db.utils import serialize_item, serialize_items
from app.db import DB
import bcrypt

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
NOTIFICATION_CHANNELS = "notification_channels"
TELEGRAM_CHAT_ID = "telegram_chat_id"
DEFAULT_CHANNELS = ["email"]
VALID_CHANNELS = {"email", "telegram"}

class UserResource:

    def __init__(self):
        self.collection = DB.get_collection(USER_COLLECTION)

    def get_users(self, name: str = None, role: str = None):
        query = {}
        if name is not None:
            query[NAME] = {"$regex": name}
        if role is not None:
            query[ROLE] = role

        users = self.collection.find(query)
        return serialize_items(list(users))

    def create_user(self, name: str, email: str, phone: str, role: str,
                   password: str, birthdate: str = None, gender: str = None,
                   notification_channels: list = None, telegram_chat_id: str = None):
        
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = {
            NAME: name,
            EMAIL: email,
            PHONE: phone,
            ROLE: role,
            PASSWORD: hashed_password,
            BIRTHDATE: birthdate,
            GENDER: gender,
            NOTIFICATION_CHANNELS: notification_channels or list(DEFAULT_CHANNELS),
            TELEGRAM_CHAT_ID: telegram_chat_id or "",
        }

        result = self.collection.insert_one(user)
        return result.inserted_id

    def get_user_by_id(self, user_id: str):
        from bson import ObjectId
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        user = self.collection.find_one({"_id": oid})
        return serialize_item(user)

    def register_user(self, name: str, email: str, phone: str, password: str,
                     role: str = "member", notification_channels: list = None,
                     telegram_chat_id: str = None):
        existing = self.get_user_by_email(email)
        if existing:
            raise ValueError("A user with this email already exists")

        user_id = self.create_user(name, email, phone, role, password,
                                  notification_channels=notification_channels,
                                  telegram_chat_id=telegram_chat_id)
        return str(user_id)

    def authenticate_user(self, email: str, password: str):
        user = self.collection.find_one({EMAIL: email})
        if not user:
            return None

        stored_password = user.get(PASSWORD)
        if isinstance(stored_password, str):
            stored_password = stored_password.encode("utf-8")

        if bcrypt.checkpw(password.encode("utf-8"), stored_password):
            return serialize_item(user)
        return None

    def get_user_by_email(self, email: str):
        user = self.collection.find_one({EMAIL: email})
        return serialize_item(user)
    
    def update_preferences(self, email: str, notification_channels: list,
                          telegram_chat_id: str):
       self.collection.update_one(
           {EMAIL: email},
           {"$set": {
               NOTIFICATION_CHANNELS: notification_channels,
               TELEGRAM_CHAT_ID: telegram_chat_id,
           }},
       )

    def delete_all_users(self):
        self.collection.delete_many({})

    def add_multiple_users(self, users: list):
        if not users:
            return

        self.collection.insert_many(users)
