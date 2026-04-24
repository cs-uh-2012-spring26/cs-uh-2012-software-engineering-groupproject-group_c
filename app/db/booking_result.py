from enum import Enum


class BookingResult(str, Enum):
    OK = "ok"
    NOT_FOUND = "not_found"
    ALREADY_BOOKED = "already_booked"
    CLASS_FULL = "class_full"
