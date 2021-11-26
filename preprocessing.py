from nltk import pos_tag
from nltk.stem import SnowballStemmer, LancasterStemmer, WordNetLemmatizer

def remove_stopwords(word_list: list[str], language = "english", remove_punctuation = True):
    """
    Takes a list of words and removes all stopwords and punctuation (optional) from that list
    """
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words(language))

    if remove_punctuation:
        from string import punctuation
        stopwords.update(punctuation)
        stopwords.update(["``", "''", "...", "..", "--"])

    return [word for word in word_list if word.casefold() not in stopwords]

def lemmatize(word_list: list[str]) -> list[str]:
    """
    Lemmatization: put the word in the so called "dictionary form", also called the lemma (scarves -> scarf) (stemming would do scarves -> scarv)

    Arguments:
        word_list (list[str]): list of words to be lemmatized
    """

    lemmatizer = WordNetLemmatizer()

    pos_tagged = pos_tag(word_list)
    #print(pos_tagged)

    lemmatized = []
    for word, pos in pos_tagged:
        try: 
            # As this assumes all words as nouns, we need to tag the part of speech and try to relay it to the lemmatizer
            lemmatized.append(lemmatizer.lemmatize(word, pos = pos[0].lower()))
        except:
            pass

    #print(lemmatized)
    return lemmatized

def stem(word_list: list[str], language = "english") -> list[str]:
    """
    Perform stemming (helping -> help)

    Arguments:
        word_list (list[str]): list of words to be stemmed
    """
    stemmer = SnowballStemmer(language)
    #stemmer = LancasterStemmer()
    stemmed = [stemmer.stem(word) for word in word_list]

    return stemmed