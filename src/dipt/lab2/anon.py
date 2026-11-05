import random

from faker import Faker

from .labels import PIILabel
from .generators import GENERATORS


def anon(
    text: str,
    entities: list[list[str | int]],
    seed: int | None = None,
) -> str:
    """Синонимически обезличивает ПДн в ``text``.

    Parameters
    ----------
    text : str
        Исходный текст.
    entities : list[list[str | int]]
        Список ``[label, start, end]``. Например ``["NAME", 0, 4]``.
    seed : int | None
        Опциональный сид (для воспроизводимости в тестах). При ``None``
        каждое обращение даёт новые значения.

    Returns
    -------
    str
        Обезличенный текст с сохранением морфологии и структуры.
    """
    if not entities:
        return text

    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    # Обрабатываем справа налево, чтобы не сдвигать индексы
    sorted_entities = sorted(entities, key=lambda e: int(e[1]), reverse=True)

    result = text
    for label, start, end in sorted_entities:
        try:
            pii_label = PIILabel(label)
        except ValueError:
            continue

        generator = GENERATORS.get(pii_label)
        if generator is None:
            continue

        original = text[int(start):int(end)]
        if not original:
            continue

        replacement = generator(original)
        result = result[:int(start)] + replacement + result[int(end):]

    return result