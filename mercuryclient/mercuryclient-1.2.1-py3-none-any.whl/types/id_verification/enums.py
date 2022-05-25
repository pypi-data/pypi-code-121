from enum import Enum


class IDTypes(Enum):
    PAN_CARD = "PAN_CARD"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    VOTER_ID = "VOTER_ID"
    PASSPORT = "PASSPORT"


class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    TRANSGENDER = "TRANSGENDER"


class PassportTypes(Enum):
    PERSONAL = "PERSONAL"
    SERVICE = "SERVICE"
    DIPLOMATIC = "DIPLOMATIC"


class Countries(Enum):
    INDIA = "INDIA"
