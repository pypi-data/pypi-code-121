import numpy as np
import pandas as pd
# For visualizations
import matplotlib.pyplot as plt
# For regular expressions
import re
# For handling string
import string
# For performing mathematical operations
import math
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text

from wordcloud import WordCloud
from textwrap import wrap

def create_word_cloud(import_file_path,stop_words):
    """
    The function will create Word Cloud using Document Term Matrix.
    
    Parameters:
        import_file_path (string): File Path to export the data.  
                                   Please enter file path with double backslash "\\\\" with file name. 
                                   There should be two columns in the file: "use_case", "all_text".
                                   File name should be .csv extension.
        stop_words (list/string): Enter the list of stop words, which should be avoided while creating word cloud. Example: "mother, mom, mum"
    """
    # Importing dataset
    df = pd.read_csv(
        import_file_path,
        low_memory=False,
    )
    df = df[["use_case", "all_text"]]

    print("File Read!")

    # remove nulls
    df = df.dropna(how="any", axis=0)
    df.dropna(inplace=True)
    # convert ASCII to Unicode Emojis
    def deEmojify(inputString):
        return inputString.encode("ascii", "ignore").decode("ascii")


    df["all_text"] = df["all_text"].apply(lambda x: deEmojify(x))
    # remove commas
    df["all_text"] = df["all_text"].apply(lambda x: x.split(",,,")[0])
    # lower case
    df["cleaned"] = df["all_text"].apply(lambda x: x.lower())
    # remove digits
    df["cleaned"] = df["cleaned"].apply(lambda x: re.sub("\w*\d\w*", "", x))
    # remove punctuation
    df["cleaned"] = df["cleaned"].apply(
        lambda x: re.sub("[%s]" % re.escape(string.punctuation), "", x)
    )
    # Removing extra spaces
    df["cleaned"] = df["cleaned"].apply(lambda x: re.sub(" +", " ", x))
    df["cleaned"] = df["cleaned"].str.encode("ascii", "ignore").str.decode("ascii")
    # Remove unwanted words like I, will, you etc.
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    # Normalizing the data like Played, Playing, Play should fall under Play
    df["lemmatized"] = df["cleaned"].apply(
        lambda x: " ".join(
            [token.lemma_ for token in list(nlp(x)) if (token.is_stop == False)]
        )
    )

    # Group the data by Use Case
    df_grouped = (
        df[["use_case", "lemmatized"]].groupby(by="use_case").agg(lambda x: " ".join(x))
    )

    print("Data Cleaning and Grouping Done!")

    # Create Document Term Matrix
    stop_words = stop_words + (",xx,xxxx,xxx,day,dear")
    stop_words_list = list(stop_words.split(","))
    stop_words_list = [x.lstrip(" ").lower() for x in stop_words_list]
    print(stop_words_list)
    cv = CountVectorizer(analyzer="word", stop_words=stop_words_list, min_df=0.10)
    data = cv.fit_transform(df_grouped["lemmatized"])
    df_dtm = pd.DataFrame(data.toarray(), columns=cv.get_feature_names_out())
    df_dtm.index = df_grouped.index

    print("Document Term Matrix created!")
    
    ## Function for generating word clouds
    def generate_wordcloud(data, title):
        wc = WordCloud(
            width=400, height=330, max_words=150, colormap="Dark2"
        ).generate_from_frequencies(data)
        plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title("\n".join(wrap(title, 60)), fontsize=13)
        plt.show()


    # Transposing document term matrix
    df_dtm = df_dtm.transpose()


    # Plotting word cloud for each product
    for index, product in enumerate(df_dtm.columns):
        generate_wordcloud(df_dtm[product].sort_values(ascending=False), product)
