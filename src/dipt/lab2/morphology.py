import pymorphy3

_morph = pymorphy3.MorphAnalyzer()


def parse_word(word: str) -> pymorphy3.tag.Tag:
    parses = _morph.parse(word)
    if not parses:
        raise ValueError(f"Не удалось разобрать слово: {word!r}")
    return parses[0].tag


def inflect_to_match(candidate: str, original: str) -> str:
    """Склоняет candidate под род/число/падеж original."""
    orig_parses = _morph.parse(original)
    if not orig_parses:
        return candidate

    orig_tag = orig_parses[0].tag
    target_gender = orig_tag.gender
    target_number = orig_tag.number
    target_case = orig_tag.case

    grammemes: set[str] = set()
    if target_case:
        grammemes.add(target_case)
    if target_number:
        grammemes.add(target_number)

    cand_parses = _morph.parse(candidate)

    # 1) сначала ищем разбор с совпадающим родом
    if target_gender:
        for p in cand_parses:
            if p.tag.gender and p.tag.gender != target_gender:
                continue
            inflected = p.inflect(grammemes)
            if inflected is not None:
                return inflected.word

    # 2) fallback — без фильтра по роду
    for p in cand_parses:
        inflected = p.inflect(grammemes)
        if inflected is not None:
            return inflected.word

    return candidate