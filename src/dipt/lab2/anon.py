from .labels import PIILabel
from .generators import GENERATORS

def anon(text: str, entities: list[list[str | int]]) -> str:
    if not entities:
        return text

    # Сортируем по убыванию start, чтобы замены не сдвигали индексы
    sorted_entities = sorted(entities, key=lambda e: e[1], reverse=True)

    result = text
    for label, start, end in sorted_entities:
        try:
            pii_label = PIILabel(label)
        except ValueError:
            continue  # неизвестная метка — пропускаем

        generator = GENERATORS.get(pii_label)
        if generator is None:
            continue

        replacement = generator()
        result = result[:start] + replacement + result[end:]

    return result