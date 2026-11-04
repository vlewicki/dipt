"""Обёртка над обученной NER-моделью: текст -> [(label, start, end), ...]."""
from typing import List, Tuple

import torch
from transformers import AutoModelForTokenClassification

from dipt.lab1.tokenizer import tokenizer
from dipt.lab1.trycorus import id2label


class ModelNER:
    def __init__(self, model_path: str = "./res_model_base", device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = AutoModelForTokenClassification.from_pretrained(model_path).to(self.device).eval()
        self.tokenizer = tokenizer

    def predict(self, text: str) -> List[Tuple[str, int, int]]:
        enc = self.tokenizer(
            text,
            return_offsets_mapping=True,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        offsets = enc.pop("offset_mapping")[0].tolist()
        enc = {k: v.to(self.device) for k, v in enc.items()}

        with torch.no_grad():
            logits = self.model(**enc).logits
        preds = logits.argmax(dim=-1)[0].tolist()

        spans: List[Tuple[str, int, int]] = []
        cur_label: str | None = None
        cur_start = cur_end = 0

        for (s, e), p in zip(offsets, preds):
            # спецтокены (CLS/SEP/PAD) — offset (0, 0)
            if s == e:
                if cur_label is not None:
                    spans.append((cur_label, cur_start, cur_end))
                    cur_label = None
                continue

            label = id2label[p]
            if label == "O":
                if cur_label is not None:
                    spans.append((cur_label, cur_start, cur_end))
                    cur_label = None
                continue

            prefix, name = label.split("-", 1)
            if prefix == "B" or cur_label != name:
                if cur_label is not None:
                    spans.append((cur_label, cur_start, cur_end))
                cur_label, cur_start, cur_end = name, s, e
            else:  # I- с тем же именем
                cur_end = e

        if cur_label is not None:
            spans.append((cur_label, cur_start, cur_end))
        return spans
