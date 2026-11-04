"""Генерация синтетических текстов с ПДн и разметкой через Faker.

Каждый пример: {"text": str, "entities": [[label, start, end], ...]}
Разметка совместима с выходом PIIExtractor.
"""

import random
from typing import Dict, List, Tuple

from faker import Faker

from regex_rules import (
    validate_inn,
    validate_luhn,
    validate_passport,
    validate_phone,
    validate_snils,
)

fake = Faker("ru_RU")
Faker.seed(42)  # воспроизводимость

# -------------------- Генераторы валидных значений --------------------


def gen_name() -> str:
    return fake.first_name()


def gen_surname() -> str:
    return fake.last_name()


def gen_patronymic() -> str:
    return fake.middle_name()


def gen_email() -> str:
    return fake.email()


def gen_phone() -> str:
    while True:
        value = fake.phone_number()  # формат +7 (XXX) XXX-XX-XX
        if validate_phone(value):
            return value


def gen_bank_card() -> str:
    # Faker гарантирует Luhn-валидность (см. документацию credit_card провайдера)
    return fake.credit_card_number()


def gen_inn() -> str:
    while True:
        value = fake.individuals_inn()  # 12 цифр, с контрольными разрядами
        if validate_inn(value):
            return value


def gen_snils() -> str:
    while True:
        value = fake.snils()  # 11 цифр, контрольная сумма по алгоритму ПФР
        if validate_snils(value):
            # Приводим к привычному формату XXX-XXX-XXX YY
            digits = "".join(c for c in value if c.isdigit())
            if len(digits) == 11:
                return f"{digits[:3]}-{digits[3:6]}-{digits[6:9]} {digits[9:]}"
            return value


def gen_passport() -> str:
    """Серия (2+2) + номер (6), регион 1–99."""
    while True:
        region = fake.random_int(1, 99)
        series = f"{region:02d} {fake.random_int(0, 99):02d}"
        number = f"{fake.random_int(0, 999999):06d}"
        value = f"{series} {number}"
        if validate_passport(value):
            return value


GENERATORS = {
    "NAME": gen_name,
    "SURNAME": gen_surname,
    "PATRONYMIC": gen_patronymic,
    "EMAIL": gen_email,
    "PHONE": gen_phone,
    "BANK_CARD": gen_bank_card,
    "INN": gen_inn,
    "SNILS": gen_snils,
    "PASSPORT": gen_passport,
}

# -------------------- Шаблоны предложений --------------------

TEMPLATES = [
    "Меня зовут {NAME} {SURNAME} {PATRONYMIC}, мой email: {EMAIL}.",
    "Клиент {SURNAME} {NAME} {PATRONYMIC}, телефон: {PHONE}.",
    "Для перевода используйте карту {BANK_CARD}.",
    "ИНН физического лица: {INN}.",
    "СНИЛС сотрудника: {SNILS}.",
    "Паспорт: серия и номер {PASSPORT}.",
    "{SURNAME} {NAME} {PATRONYMIC}, email {EMAIL}, тел. {PHONE}.",
    "Реквизиты: ИНН {INN}, СНИЛС {SNILS}, карта {BANK_CARD}.",
    "Прошу связаться с {NAME} {SURNAME} по телефону {PHONE} или email {EMAIL}.",
    "Документ: паспорт {PASSPORT}, ИНН {INN}.",
    # ... можно добавить ещё шаблоны
]


def _fill_template(template: str) -> Tuple[str, List[List]]:
    """Подставляет сущности в шаблон и возвращает (text, entities)."""
    entities: List[List] = []
    parts: List[str] = []
    cursor = 0
    i = 0
    while i < len(template):
        if template[i] == "{":
            end = template.index("}", i)
            label = template[i + 1 : end]
            value = GENERATORS[label]()
            start = cursor
            parts.append(value)
            cursor += len(value)
            entities.append([label, start, cursor])
            i = end + 1
        else:
            parts.append(template[i])
            cursor += 1
            i += 1
    return "".join(parts), entities


def generate_dataset(
    num_texts: int = 200,
    min_per_entity: int = 50,
    seed: int | None = None,
) -> List[Dict]:
    """Генерирует тексты, гарантируя ≥ min_per_entity на каждый атрибут."""
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    samples: List[Dict] = []
    counts = {label: 0 for label in GENERATORS}

    # Генерируем, пока все атрибуты не наберут минимум
    while len(samples) < num_texts or any(c < min_per_entity for c in counts.values()):
        template = random.choice(TEMPLATES)
        text, entities = _fill_template(template)
        samples.append({"text": text, "entities": entities})
        for label, _, _ in entities:
            counts[label] += 1

    return samples


if __name__ == "__main__":
    data = generate_dataset(num_texts=200, min_per_entity=50)
    print(f"Всего текстов: {len(data)}")
    print("Первый пример:")
    print(data[0])
