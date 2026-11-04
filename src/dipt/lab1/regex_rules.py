"""Регулярные выражения и проверки контрольных разрядов для структурированных ПДн.

Каждое правило возвращает кандидатов (label, start, end, valid, priority).
`start`/`end` — индексы в исходном тексте (end — эксклюзивный).
"""

import re
from typing import List, Tuple


# -------------------- Валидаторы контрольных разрядов --------------------


def validate_inn(value: str) -> bool:
    d = re.sub(r"\D", "", value)
    if len(d) == 10:
        w = (2, 4, 10, 3, 5, 9, 4, 6, 8)
        ctrl = sum(int(a) * b for a, b in zip(d, w)) % 11 % 10
        return ctrl == int(d[9])
    if len(d) == 12:
        w1 = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
        w2 = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
        c1 = sum(int(a) * b for a, b in zip(d, w1)) % 11 % 10
        c2 = sum(int(a) * b for a, b in zip(d, w2)) % 11 % 10
        return c1 == int(d[10]) and c2 == int(d[11])
    return False


def validate_snils(value: str) -> bool:
    d = re.sub(r"\D", "", value)
    if len(d) != 11:
        return False
    s = sum(int(d[i]) * (9 - i) for i in range(9))
    if s < 100:
        ctrl = s
    elif s in (100, 101):
        ctrl = 0
    else:
        ctrl = s % 101
        if ctrl == 100:
            ctrl = 0
    return ctrl == int(d[9:11])


def validate_luhn(value: str) -> bool:
    d = [int(c) for c in re.sub(r"\D", "", value)]
    if not (13 <= len(d) <= 19):
        return False
    total = 0
    parity = len(d) % 2
    for i, n in enumerate(d):
        if i % 2 == parity:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def validate_phone(value: str) -> bool:
    d = re.sub(r"\D", "", value)
    if len(d) == 11:
        return d[0] in ("7", "8")
    if len(d) == 10:
        return d[0] in "34589"
    return False


def validate_passport(value: str) -> bool:
    d = re.sub(r"\D", "", value)
    if len(d) != 10:
        return False
    region = int(d[:2])
    return 1 <= region <= 99


# -------------------- Сами регулярные выражения --------------------

EMAIL_RE = re.compile(
    r"(?<![\w.])"
    r"(?P<v>[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})"
    r"(?!\w)"
)

# 16–19 цифр с необязательными разделителями между 4-значными группами
BANK_CARD_RE = re.compile(
    r"(?<!\w)"
    r"(?P<v>"
    r"\d{4}[ \-]?\d{4}[ \-]?\d{4}[ \-]?\d{4,7}"  # 16–19: 4-4-4-4..7
    r"|\d{4}[ \-]?\d{6}[ \-]?\d{5}"  # 15: 4-6-5 (Amex)
    r"|\d{4}[ \-]?\d{6}[ \-]?\d{4}"  # 14: 4-6-4 (Diners)
    r")"
    r"(?!\w)"
)

# СНИЛС в формате XXX-XXX-XXX YY (дефисы обязательны — отсекает пересечения с телефоном)
SNILS_RE = re.compile(
    r"(?<!\w)"
    r"(?P<v>\d{3}-\d{3}-\d{3}\s?\d{2})"
    r"(?!\w)"
)

# ИНН 10 или 12 цифр подряд
INN_RE = re.compile(
    r"(?<!\w)"
    r"(?P<v>\d{12}|\d{10})"
    r"(?!\w)"
)

# Телефон РФ: +7/8 + 10 цифр, допускаются пробелы, скобки, дефисы
PHONE_RE = re.compile(
    r"(?<![\w+])"
    r"(?P<v>(?:\+7|8)[\s\-()]{0,3}\d{3}[\s\-()]{0,3}\d{3}[\s\-]{0,2}\d{2}[\s\-]{0,2}\d{2})"
    r"(?!\w)"
)

# Паспорт РФ: серия dd dd и номер dddddd, между серией и номером есть пробел
PASSPORT_RE = re.compile(
    r"(?<!\d)"
    r"(?P<v>\d{2}\s?\d{2}\s\d{6})"
    r"(?!\d)"
)


# (label, pattern, validator, priority — меньше = важнее при пересечении)
RULES = [
    ("EMAIL", EMAIL_RE, None, 0),
    ("BANK_CARD", BANK_CARD_RE, validate_luhn, 1),
    ("SNILS", SNILS_RE, validate_snils, 2),
    ("INN", INN_RE, validate_inn, 3),
    ("PHONE", PHONE_RE, validate_phone, 4),
    ("PASSPORT", PASSPORT_RE, validate_passport, 5),
]


def find_regex_matches(text: str) -> List[Tuple[str, int, int, bool, int]]:
    """Возвращает список (label, start, end, valid, priority) по всем правилам."""
    out: List[Tuple[str, int, int, bool, int]] = []
    for label, pattern, validator, priority in RULES:
        for m in pattern.finditer(text):
            value = m.group("v")
            valid = validator(value) if validator else True
            out.append((label, m.start("v"), m.end("v"), valid, priority))
    return out
