from base64 import b85decode

import nltk
from nltk.text import Text
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from preprocessing import lemmatize, remove_stopwords
from nltk.probability import FreqDist

# A list of words to closely analyze
# They only need to be in one of their forms, since they will get stemmed or lemmatized (for example, 'run', 'running' and 'ran' will all convert to 'run')
# Words obfuscated so GitHub won't get mad at me
detect = [b85decode(x).decode() for x in [b"V|8r", b"WpZzHX=4", b"WNBk-", b"aAj_3a{", b"V{c<?", b"c422}Zea", b"aCLKYc>", b"Xm4_Ec>", b"VRLf", b"b8BgGbN", b"Vqt7-a{", b"ZEs<2", b"aA9tAa{", b"aA9tAX=QT", b"Z*pg0b8P", b"b9Z5EY;Sh"]]

# Add your own words here, for example ["cat", "dog", "bird"]
detect.extend([])


def print_concordence(nltk_text: Text, words_to_check: list[str]):
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

def print_human_readable_info(text):
    from nltk.corpus import stopwords
    
    # Preprocess: remove newlines, convert some quotes, remove empty sentences, remove double spaces
    stopwords = set(stopwords.words("english"))
    # Tokenize words, remove stopwords (useless words such as 'the')
    word_list = remove_stopwords(word_tokenize(text))
    # Tokenize sentances
    sentances = sent_tokenize(text)

    print("Length:")
    print(len(text))
    print("Meaningful words:")
    print(len(word_list))

    # Process both sets in the same way
    processed = lemmatize(word_list) #stem(word_list)
    detect_processed = lemmatize(detect) #stem(detect)

    #print(to_process)
    #print(sentances)
    #print(word_list)

    # NOTE: stemming is worse at doing it's job, but lemmatization requires part of speech tagging (see functions 'stem' and 'lemmatize')
    # I believe stemming can be enough in this case, since we don't want the original word, we just want to group words
    # Use lemmatization anyway (it can skip some words, so be careful)

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
    freq = FreqDist(word_list)
    print("25 most common words:")
    print(freq.most_common(25))

    average_sent, lowest_compound, highest_compound = sentiment_analisys(sentances)
    print("Average sentence sentiment")
    print(average_sent)
    print(f"Lowest / highest coumpound sentiment: {lowest_compound} / {highest_compound}")

    nltk_text.dispersion_plot(detect)