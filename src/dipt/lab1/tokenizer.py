from transformers import AutoTokenizer, AutoModelForTokenClassification

model_name = "DeepPavlov/rubert-base-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name, fix_mistral_regex=True, local_files_only=False)
