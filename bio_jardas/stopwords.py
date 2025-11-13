import csv
from functools import lru_cache
from pathlib import Path

from unidecode import unidecode

MIN_WORD_LEN = 4
STOPWORDS_PATH = Path("resources/stopwords.csv")


@lru_cache
def stopwords() -> set[str]:
    words = set()
    with STOPWORDS_PATH.open() as file:
        reader = csv.DictReader(file)
        for row in reader:
            words.add(row["word"])
    return words


def tokenize(text: str) -> list[str]:
    text = text.replace("'\",", "")
    all_stopwords = stopwords()
    return list(
        {
            word
            for word in text.split()
            if len(word) > MIN_WORD_LEN and unidecode(word) not in all_stopwords
        }
    )
