from seqeval.metrics import classification_report
from seqeval.scheme import IOB2
from transformers import TrainingArguments, Trainer, DataCollatorForTokenClassification
import numpy as np

from dipt.lab1.model import model
from dipt.lab1.dataset import dsd
from dipt.lab1.tokenizer import tokenizer
from dipt.lab1.trycorus import id2label


def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=-1)

    y_true = [
        [id2label[l] for l, p in zip(label, pred) if l != -100]
        for label, pred in zip(labels, predictions)
    ]
    y_pred = [
        [id2label[p] for l, p in zip(label, pred) if l != -100]
        for label, pred in zip(labels, predictions)
    ]

    res = classification_report(
        y_true=y_true, y_pred=y_pred, scheme=IOB2, output_dict=True
    )["weighted avg"]
    res.pop("support", None)
    return res


data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

training_args = TrainingArguments(
    output_dir="./train_result",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=16,  # надо подобрать оптимальное значение с т.з. качества
    logging_steps=50,
    weight_decay=0.01,
    load_best_model_at_end=True,
    report_to=[],
    # save_safetensors=False
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dsd["train"],
    eval_dataset=dsd["valid"],
    # tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)


def train():
    trainer.train()
    model_path = "./res_model_base"
    trainer.save_model(model_path)
