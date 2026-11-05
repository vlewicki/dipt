def validate_inn(inn: str) -> bool:
    digits = [c for c in inn if c.isdigit()]
    if len(digits) == 10:
        w = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        s = sum(int(digits[i]) * w[i] for i in range(9))
        return s % 11 % 10 == int(digits[9])
    if len(digits) == 12:
        w1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        w2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        s1 = sum(int(digits[i]) * w1[i] for i in range(10))
        s2 = sum(int(digits[i]) * w2[i] for i in range(11))
        return s1 % 11 % 10 == int(digits[10]) and s2 % 11 % 10 == int(digits[11])
    return False


def validate_bank_card(card: str) -> bool:
    digits = [int(c) for c in card if c.isdigit()]
    if not digits:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def validate_phone(phone: str) -> bool:
    digits = [c for c in phone if c.isdigit()]
    return len(digits) == 11 and digits[0] in ("7", "8")
