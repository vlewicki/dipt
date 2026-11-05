from tqdm import tqdm
from corus import load_factru
from transformers import BatchEncoding
from dipt.lab1.tokenizer import tokenizer
from dipt.lab1.labels import PIILabel

max_tok_len = 512
records = list(load_factru("factRuEval-2016-master"))
types = []
for rec in records:
    for obj in rec.objects:
        for span in obj.spans:
            types.append(span.type.upper())
            # if span.type.upper() == "PATRONYMIC":
            #     print(rec.text[span.start: span.stop])
types = sorted(set(types))
print(types)

types = [PIILabel.SURNAME, PIILabel.NAME, PIILabel.PATRONYMIC]

label_names = ["O"]
for t in types:
    label_names.append("B-" + t)
    label_names.append("I-" + t)

id2label = {i: label for i, label in enumerate(label_names)}
label2id = {v: k for k, v in id2label.items()}

result = {
    'input_ids': [],
    'token_type_ids': [],
    'attention_mask': [],
    'labels': []
}
for rec in tqdm(records):
    labels = []
    tokenized_inputs: BatchEncoding = tokenizer(
        rec.text, truncation=True, max_length=max_tok_len
    )
    enc = tokenized_inputs.encodings[0]
    offsets = enc.offsets
    word_ids = enc.word_ids
    stm = enc.special_tokens_mask
    temp_tags = []
    for i in range(len(offsets)):
        if word_ids[i] is None:
            labels.append(-100)
            temp_tags.append("O")
        elif i > 0 and word_ids[i - 1] == word_ids[i]:
            labels.append(-100)
            offset = offsets[i]
            flg = False
            for obj in rec.objects:
                if flg:
                    break
                for span in obj.spans:
                    if (
                        span.start <= offset[0] < span.stop
                        or span.start < offset[1] <= span.stop
                    ):
                        temp_tags.append(span.type)
                        flg = True
                        break
            if not flg:
                temp_tags.append("O")
        else:
            offset = offsets[i]
            flg = False
            for obj in rec.objects:
                if flg:
                    break
                for span in obj.spans:
                    if (
                        span.start <= offset[0] < span.stop
                        or span.start < offset[1] <= span.stop
                    ):
                        if span.type == temp_tags[-1]:
                            prefix = "I-"
                        else:
                            prefix = "B-"
                        # labels.append(prefix + span.type.upper())
                        labels.append(label2id.get(prefix + span.type.upper(), 0))
                        temp_tags.append(span.type)
                        flg = True
                        break
            if not flg:
                labels.append(0)
                temp_tags.append("O")
    result["input_ids"].append(tokenized_inputs["input_ids"])
    result["token_type_ids"].append(tokenized_inputs["token_type_ids"])
    result["attention_mask"].append(tokenized_inputs["attention_mask"])
    result["labels"].append(labels)
    # if len(labels) != len(offsets) or len(temp_tags) != len(offsets):
    #     break
