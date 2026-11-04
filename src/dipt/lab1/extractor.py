"""Интеграционный модуль: текст -> [[label, start, end], ...].

Правила:
  1. Валидная регулярка имеет приоритет над моделью.
  2. Если регулярка не прошла контрольную проверку — она отбрасывается,
     на этом участке остаётся результат модели (или O, если модель ничего не нашла).
  3. Пересечения между регулярками разрешаются по приоритету (см. RULES).
"""

from typing import List

from dipt.lab1.regex_rules import find_regex_matches
from dipt.lab1.model_ner import ModelNER


def _overlaps(a, b) -> bool:
    return not (a[2] <= b[1] or b[2] <= a[1])


class PIIExtractor:
    def __init__(self, model_path: str = "./res_model_base", device: str | None = None):
        self.ner = ModelNER(model_path, device)

    def extract(self, text: str) -> List[List]:
        # --- 1. Кандидаты от регулярок, оставляем только прошедших валидацию ---
        candidates = find_regex_matches(text)  # (label, s, e, valid, priority)
        valid = [(l, s, e, pr) for l, s, e, v, pr in candidates if v]
        # сначала высокий приоритет, затем более длинные совпадения, затем левее
        valid.sort(key=lambda x: (x[3], -(x[2] - x[1]), x[1]))

        # --- 2. Разрешаем пересечения между регулярками ---
        regex_spans: List[tuple] = []
        for label, s, e, _ in valid:
            span = (label, s, e)
            if not any(_overlaps(span, r) for r in regex_spans):
                regex_spans.append(span)

        # --- 3. Предсказания модели; отбрасываем те, что накладываются на валидные регулярки ---
        model_spans: List[tuple] = []
        for label, s, e in self.ner.predict(text):
            span = (label, s, e)
            if not any(_overlaps(span, r) for r in regex_spans):
                model_spans.append(span)

        # --- 4. Объединяем и сортируем ---
        merged = regex_spans + model_spans
        merged.sort(key=lambda x: x[1])
        return [[label, s, e] for label, s, e in merged]
