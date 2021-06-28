#!/usr/bin/env python3

# Made by Riggle with regret
# You are welcome to do whatever as long as you credit me

import sys
import re
import unicodedata
import nltk
import requests as req
import bs4
from base64 import b85decode

nltk.download("stopwords", quiet = True)
nltk.download("punkt", quiet = True)
nltk.download("averaged_perceptron_tagger", quiet = True)
nltk.download("vader_lexicon", quiet = True)
nltk.download("wordnet", quiet = True)


from nltk.text import Text
from nltk.probability import FreqDist
from nltk.stem import SnowballStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize

# A list of words to closely analyze
# They only need to be in one of their forms, since they will get stemmed or lemmatized (for example, 'run', 'running' and 'ran' will all convert to 'run')
# Words obfuscated so GitHub won't get mad at me
detect = [b85decode(x).decode() for x in [b"V|8r", b"WpZzHX=4", b"WNBk-", b"aAj_3a{", b"V{c<?", b"c422}Zea", b"aCLKYc>", b"Xm4_Ec>", b"VRLf", b"b8BgGbN", b"Vqt7-a{", b"ZEs<2", b"aA9tAa{", b"aA9tAX=QT", b"Z*pg0b8P", b"b9Z5EY;Sh"]]

# Add your own words here, for example ["cat", "dog", "bird"]
detect.extend([])

def preprocess(s: str) -> str:
    """
    Preprocess string for analisys
    """
    s = unicodedata.normalize("NFKD", s)
    # Remove all extra new lines
    s = re.sub("\n{2,}", "", s)
    # Replace all kinds of special characters
    s = replace_mul(
        s, 
        ('„', '"'),
        ('”', '"'),
        ("’", "'"),
        (".\n", " "),
        ("\n", ". ")
    )

    # Remove empty sentences
    s = re.sub("(\\. \\.)( \\.)*", " ", s)
    # Replace multiple spaces with only one
    s = re.sub(" {2,}", " ", s)

    return s

def replace_mul(s: str, *args: tuple[str, str]) -> str:
    """Perform many string replacements at once

    Arguments:
        s (str): the string to perform replacements on
        args (*tuple[str, str]): tuples in the form of ("prev_value", "desired_value")
    
    Returns a string on which the replacements were performed on
    """
    for t in args:
        s = s.replace(t[0], t[1])
    return s

def lemmatize(word_list: list[str]) -> list[str]:
    """
    Lemmatization: put the word in the so called "dictionary form", also called the lemma (scarves -> scarf) (stemming would do scarves -> scarv)

    Arguments:
        word_list (list[str]): list of words to be lemmatized
    """

    lemmatizer = WordNetLemmatizer()

    pos_tagged = nltk.pos_tag(word_list)
    #print(pos_tagged)

    lemmatized = []
    for t in pos_tagged:
        try: 
            # As this assumes all words as nouns, we need to tag the part of speech and try to relay it to the lemmatizer
            lemmatized.append(lemmatizer.lemmatize(t[0], pos = t[1][0].lower()))
        except:
            pass

    #print(lemmatized)
    return lemmatized

def stem(word_list: list[str]) -> list[str]:
    """
    Perform stemming (helping -> help)

    Arguments:
        word_list (list[str]): list of words to be stemmed
    """
    stemmer = SnowballStemmer("english")
    #stemmer = LancasterStemmer()
    stemmed = [stemmer.stem(word) for word in word_list]

    return stemmed

def frequency_analisys(word_list: list[str]) -> None:
    """
    Analyze the frequency of words
    """
    freq = FreqDist(word_list)
    return freq.most_common(25)

def print_concordence(nltk_text: nltk.text.Text, words_to_check: list[str]):
    """
    Print words in their immediate context
    """
    for word in words_to_check:
        print(f"Concordance for {word}:")
        nltk_text.concordance(word)
        print()

def sentiment_analisys(sentances: list[str]):
    # Sentiment analisys
    sia = SentimentIntensityAnalyzer()
    sentiments: list[dict] = []
    for sentance in sentances:
        sentiments.append(sia.polarity_scores(sentance))

    # Average sentiment
    if len(sentiments) > 1:
        average_sent = {}
        lowest_compound = sentiments[0]["compound"]
        highest_compound = sentiments[0]["compound"]
        for key in sentiments[0].keys():
            average_sent[key] = 0
        for sent in sentiments:
            # Lowest sentiment
            if sent["compound"] < lowest_compound:
                lowest_compound = sent["compound"]
            # Highest sentiment
            elif sent["compound"] > highest_compound:
                highest_compound = sent["compound"]
            # Add sentiment
            for key in sent.keys():
                average_sent[key] += sent[key]
        # Average sentiment is calculated here
        for key in average_sent.keys():
            average_sent[key] = average_sent[key] / len(sentiments)                    

    #print(sentiments)
    return average_sent, lowest_compound, highest_compound


def main(txt: str):
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words("english")) # Get English stopwords only

    # Preprocess: remove newlines, convert some quotes, remove empty sentences, remove double spaces
    to_process = preprocess(txt)

    # Tokenize sentances
    sentances = sent_tokenize(to_process)

    # Tokenize words, remove stopwords (useless words such as 'the')
    word_list = [word for word in word_tokenize(to_process) if word.casefold() not in stopwords]

    print("Length:")
    print(len(to_process))
    print("Meaningful words:")
    print(len(word_list))

    #print(to_process)
    #print(sentances)
    #print(word_list)

    # NOTE: stemming is worse at doing it's job, but lemmatization requires part of speech tagging (see functions 'stem' and 'lemmatize')
    # I believe stemming can be enough in this case, since we don't want the original word, we just want to group words
    # Use lemmatization anyway (it can skip some words, so be careful)

    # Process both sets in the same way
    processed = lemmatize(word_list) #stem(word_list)
    detect_processed = lemmatize(detect) #stem(detect)
    nltk_text = Text(processed) # Wrap text for further analisys (use any list of strings)

    # Concordance (the word with it's immediate context)
    # The two arguments SHOULD be processed in the same way. If not, the script will miss some occurances of certain words
    print_concordence(nltk_text, detect_processed)

    # Common collocations: pairs of words that come up often
    print("Common collocations: ")
    nltk_text.collocations()
    print()

    # Most common words
    # The frequency analisys uses the default word list here
    # To change to stemmed words, just use the 'stem' function (or 'lemmatize' for lemmatized words, word_list to non-processed words if you wish)
    print("25 most common words:")
    print(frequency_analisys(processed))

    average_sent, lowest_compound, highest_compound = sentiment_analisys(sentances)
    print("Average sentence sentiment")
    print(average_sent)
    print(f"Lowest / highest coumpound sentiment: {lowest_compound} / {highest_compound}")

    nltk_text.dispersion_plot(detect)

def extract_text_from_statbus(html: str) -> str:
    """
    Parses StatBus' page and removes clutter, leaving only the book text
    """
    bs = bs4.BeautifulSoup(html, "html.parser")
    bs = bs.find("div", {"class": lambda x: ("card" in x.split()) and ("border-" in x)})
    if not bs:
        raise Exception("Book could not be loaded correctly. Check your PHPSESSID cookie and if the book is available to read.")
    return re.sub("<[^>]*>", " ", str(bs))

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
    main(preprocess(extract_text_from_statbus(req.get(link, cookies={"PHPSESSID": cookie}).text).strip()))
