from enum import Enum


class PetType(str, Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    FISH = "fish"


class PaymentMethod(str, Enum):
    COD = "cod"
    BANK_TRANSFER = "bank_transfer"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPING = "shipping"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
