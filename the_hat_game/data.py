import re
from collections import Counter
from typing import List

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from tqdm.auto import tqdm

STOP_WORDS = stopwords.words("english")
LEMMATIZER = WordNetLemmatizer()


def sent_2_words(sent: str) -> List[str]:
    sent = sent.lower()
    sent = re.sub("[^a-z]+", " ", sent)
    words = word_tokenize(sent)
    words = [LEMMATIZER.lemmatize(word) for word in words if ((word not in STOP_WORDS) and len(word.strip()) > 3)]
    return words


def corpus_to_words(file_path: str):
    my_counter: Counter = Counter()
    with open(file_path, "r", encoding="utf-8") as fl:
        for sent in tqdm(fl, desc="Precess file"):
            my_counter.update(sent_2_words(sent))

    max_cnt = max(count for word, count in my_counter.items()) / 10
    min_count = max([10, max_cnt / 100])

    selected_words = [word for word, count in my_counter.items() if (min_count < count <= max_cnt)]
    return selected_words
