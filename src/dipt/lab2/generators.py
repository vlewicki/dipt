from .labels import PIILabel

def generate_surname() -> str:
    """Возвращает случайную фамилию."""
    pass


def generate_name() -> str:
    """Возвращает случайное имя."""
    pass


def generate_email() -> str:
    """Возвращает случайный e-mail."""
    pass


def generate_inn() -> str:
    """Возвращает случайный ИНН с валидной контрольной суммой."""
    pass


def generate_phone() -> str:
    """Возвращает случайный российский номер телефона."""
    pass


def generate_bank_card() -> str:
    """Возвращает случайный номер банковской карты, проходящий алгоритм Луна."""
    pass


GENERATORS: dict[PIILabel, callable] = {
    PIILabel.SURNAME: generate_surname,
    PIILabel.NAME: generate_name,
    PIILabel.EMAIL: generate_email,
    PIILabel.INN: generate_inn,
    PIILabel.PHONE: generate_phone,
    PIILabel.BANK_CARD: generate_bank_card,
}