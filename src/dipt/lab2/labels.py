from enum import StrEnum

class PIILabel(StrEnum):
    """Метки атрибутов ПДн, поддерживаемые пакетом."""
    SURNAME = "SURNAME"
    NAME = "NAME"
    EMAIL = "EMAIL"
    INN = "INN"
    PHONE = "PHONE"
    BANK_CARD = "BANK_CARD"