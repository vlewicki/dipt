import random
import string

from faker import Faker

from .labels import PIILabel
from .morphology import inflect_to_match
from .validators import validate_bank_card

_faker = Faker("ru_RU")


# ---------- Фамилия / Имя ----------

def generate_surname(original: str) -> str:
    from .morphology import _morph  # локальный импорт, чтобы избежать циклов
    tag = _morph.parse(original)[0].tag
    if tag.gender == "femn":
        base = _faker.last_name_female().ca
    else:
        base = _faker.last_name_male()
    return inflect_to_match(base, original)


def generate_name(original: str) -> str:
    from .morphology import _morph
    tag = _morph.parse(original)[0].tag
    if tag.gender == "femn":
        base = _faker.first_name_female()
    else:
        base = _faker.first_name_male()
    return inflect_to_match(base, original)


# ---------- E-mail ----------

def generate_email(original: str) -> str:
    if "@" not in original:
        return original
    _, domain = original.split("@", 1)
    alphabet = string.ascii_lowercase + string.digits
    local = "".join(random.choices(alphabet, k=random.randint(6, 12)))
    return f"{local}@{domain}"


# ---------- ИНН ----------

def _inn_check_digit(digits: list[int], weights: list[int]) -> int:
    s = sum(d * w for d, w in zip(digits, weights))
    return s % 11 % 10


def generate_inn(original: str) -> str:
    digits = [c for c in original if c.isdigit()]
    if len(digits) not in (10, 12):
        return original

    if len(digits) == 10:
        # первые 4 сохраняем, 5 случайных, затем контрольный
        prefix = digits[:4]
        middle = [str(random.randint(0, 9)) for _ in range(5)]
        base = [int(d) for d in prefix + middle]
        w = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        check = _inn_check_digit(base, w)
        return "".join(prefix + middle) + str(check)

    # 12-значный ИНН
    prefix = digits[:4]
    middle = [str(random.randint(0, 9)) for _ in range(6)]
    base10 = [int(d) for d in prefix + middle]  # 10 цифр
    w11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    d11 = _inn_check_digit(base10, w11)

    base11 = base10 + [d11]
    w12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    d12 = _inn_check_digit(base11, w12)

    return "".join(prefix + middle) + str(d11) + str(d12)


# ---------- Телефон ----------

def generate_phone(original: str) -> str:
    out: list[str] = []
    digit_idx = 0
    for ch in original:
        if ch.isdigit():
            if digit_idx < 4:
                out.append(ch)
            else:
                out.append(str(random.randint(0, 9)))
            digit_idx += 1
        else:
            out.append(ch)
    return "".join(out)


# ---------- Банковская карта ----------
def generate_bank_card(original: str) -> str:
    digits = [c for c in original if c.isdigit()]
    if len(digits) != 16:
        return original

    first6 = digits[:6]
    last4 = digits[12:]

    # Перебор случайных 6 цифр в середине до валидного Luhn
    for _ in range(200):
        middle = [str(random.randint(0, 9)) for _ in range(6)]
        card = first6 + middle + last4
        if validate_bank_card(card):
            return "".join(card)

    # теоретически недостижимая ветка — оставляем для безопасности
    return original


GENERATORS: dict[PIILabel, callable] = {
    PIILabel.SURNAME: generate_surname,
    PIILabel.NAME: generate_name,
    PIILabel.EMAIL: generate_email,
    PIILabel.INN: generate_inn,
    PIILabel.PHONE: generate_phone,
    PIILabel.BANK_CARD: generate_bank_card,
}