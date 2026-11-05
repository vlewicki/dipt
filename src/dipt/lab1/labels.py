from enum import StrEnum

class PIILabel(StrEnum):
    EMAIL = "EMAIL"
    BANK_CARD = "BANK_CARD"
    SNILS = "SNILS"
    INN = "INN"
    PHONE = "PHONE"
    PASSPORT = "PASSPORT"
    SURNAME = "SURNAME"
    NAME = "NAME"
    PATRONYMIC = "PATRONYMIC"
    # при необходимости можно добавить O = "O"
