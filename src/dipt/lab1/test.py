import argparse
from collections import Counter

import numpy as np
from sklearn.metrics import classification_report

from tokenizer import tokenizer
from extractor import PIIExtractor
from synthetic_data import generate_dataset


def spans_to_token_labels(text, spans, max_length=512):
    """
    Преобразует спаны [[label, start, end], ...] в BIO-разметку по токенам.

    Возвращает список тегов ("O", "B-NAME", "I-EMAIL", ...) длиной = числу
    токенов; None — на местах спецтокенов (CLS/SEP/PAD) и продолжений subword.
    """
    enc = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=max_length,
    )
    offsets = enc["offset_mapping"]
    word_ids = enc.word_ids()

    labels = []
    prev_wid = None
    for (s, e), wid in zip(offsets, word_ids):
        if wid is None or wid == prev_wid:
            labels.append(None)
            prev_wid = wid
            continue

        tag = "O"
        for label, ss, se in spans:
            if s < se and e > ss:  # токен пересекает спан
                prefix = "B-" if ss >= s else "I-"
                tag = prefix + label
                break
        labels.append(tag)
        prev_wid = wid
    return labels


def rm_bi(tag):
    """B-NAME -> NAME, I-EMAIL -> EMAIL, O -> O."""
    return tag[2:] if tag.startswith(("B-", "I-")) else tag


def evaluate(num_texts=300, min_per_entity=50, seed=42, max_length=512):
    extractor = PIIExtractor()
    dataset = generate_dataset(
        num_texts=num_texts,
        min_per_entity=min_per_entity,
        seed=seed,
    )

    # Диагностика: сколько текстов реально пришлось на каждый атрибут
    text_counts = Counter()
    for sample in dataset:
        for label in {e[0] for e in sample["entities"]}:
            text_counts[label] += 1
    print(f"Сгенерировано текстов: {len(dataset)}")
    print("Текстов на атрибут:", dict(text_counts))
    print()

    y_true, y_pred = [], []

    for sample in dataset:
        text = sample["text"]
        gold_spans = sample["entities"]

        gold_tags = spans_to_token_labels(text, gold_spans, max_length)
        pred_spans = extractor.extract(text)
        pred_tags = spans_to_token_labels(text, pred_spans, max_length)

        for gt, pt in zip(gold_tags, pred_tags):
            if gt is None:  # спецтокен / subword — не оцениваем
                continue
            y_true.append(rm_bi(gt))
            y_pred.append(rm_bi(pt))

    all_labels = sorted(set(y_true) | set(y_pred))

    return classification_report(
        y_true=y_true,
        y_pred=y_pred,
        labels=all_labels,
        output_dict=False,
        digits=4,
        zero_division=0,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Оценка PIIExtractor на синтетике")
    parser.add_argument(
        "--num-texts",
        type=int,
        default=300,
        help="Число тестовых текстов (по умолчанию 300)",
    )
    parser.add_argument(
        "--min-per-entity",
        type=int,
        default=50,
        help="Минимум текстов на каждый атрибут ПДн (по умолчанию 50)",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print(
        evaluate(
            num_texts=args.num_texts,
            min_per_entity=args.min_per_entity,
            seed=args.seed,
        )
    )
