from dipt.lab1.extractor import PIIExtractor


def main():
    extractor = PIIExtractor()

    # text = (
    #     "Петров Иван Ивановича, e-mail: ivan.petrov@example.com, тел. +7 (900) 123-45-67. "
    #     "ИНН 7707083893, СНИЛС 112-233-445 95, паспорт 45 06 123456. "
    #     "Карта 4111 1111 1111 1111. "
    #     "Обращаться к Анне Сидоровой."
    # )
    while True:
        text = input("Enter document: ")
        for item in extractor.extract(text):
            print(item)
