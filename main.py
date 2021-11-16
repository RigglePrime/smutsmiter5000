#!/usr/bin/env python3

# Made by Riggle with regret
# You are welcome to do whatever as long as you credit me

import sys

from scraper import extract_text_from_statbus, preprocess_statbus_text
from human_analisys import sentiment_analisys, detect
from preprocessing import lemmatize, stem

import nltk
import requests as req

nltk.download("stopwords", quiet = True)
nltk.download("punkt", quiet = True)
nltk.download("averaged_perceptron_tagger", quiet = True)
nltk.download("vader_lexicon", quiet = True)
nltk.download("wordnet", quiet = True)


if __name__ == "__main__":
    cookie = sys.argv[1] if len(sys.argv) > 1 else input("Log in to StatBus, then get the cookie named PHPSESSID and paste it's value here:\n")
    book_id = sys.argv[2] if len(sys.argv) > 2 else input("Book ID or link:\n")
    base_link = "https://sb.atlantaned.space/library/"

    link = ""
    if book_id.isnumeric():
        link = base_link + book_id
    elif base_link in book_id:
        link = book_id
    else:
        raise Exception("No idea what to do with your data (for now?)\nYour input:\n" + book_id)
        
    cookie = cookie.replace("PHPSESSID=", "")
    from human_analisys import print_human_readable_info
    print_human_readable_info(preprocess_statbus_text(extract_text_from_statbus(req.get(link, cookies={"PHPSESSID": cookie}).text).strip()))
