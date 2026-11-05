from dipt.lab1.extractor import PIIExtractor
from dipt.lab2.anon import anon
def main():
    extractor = PIIExtractor()
    while True:
        text = input("Enter document: ")
        print(anon(text, extractor.extract(text)))
    
