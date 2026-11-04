import torch
from dipt.lab1.tokenizer import model_name, AutoModelForTokenClassification
from dipt.lab1.trycorus import label_names, id2label, label2id

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model = AutoModelForTokenClassification.from_pretrained(
    model_name,
    num_labels=len(label_names),
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True,
).to(device)
