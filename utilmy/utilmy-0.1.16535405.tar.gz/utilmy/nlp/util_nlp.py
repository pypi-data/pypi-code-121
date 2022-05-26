# -*- coding: utf-8 -*-
MNAME = "utilmy.nlp.util_nlp"
""" utils for NLP processing

### pip install fire

python  utilmy/nlp/util_nlp.py test1


"""
import os,sys, collections, random, numpy as np,  glob, pandas as pd, matplotlib.pyplot as plt ;from box import Box
from copy import deepcopy
from abc import abstractmethod
from tqdm import tqdm


## for plotting
import matplotlib.pyplot as plt
import seaborn as sns

## for analysis
import re, langdetect, nltk, wordcloud, contractions

## for sentiment
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob


## for machine learning
from sklearn import preprocessing, model_selection, feature_extraction, feature_selection, metrics, manifold, naive_bayes, pipeline

## for deep learning
from tensorflow.keras import callbacks, models, layers, preprocessing as kprocessing



## for W2V and textRank
import gensim
import gensim.downloader as gensim_api


## for summarization
import rouge




#############################################################################################
from utilmy import log, log2, help_create
def help():
    """function help.
    Doc::
            
            Args:
            Returns:
                
    """
    print( help_create(MNAME) )


#############################################################################################
def test_all():
    """function test_all.
    Doc::
            
            Args:
            Returns:
                
    """
    log(MNAME)
    test1()
    # test2()



def test1():
    """function test1.
    Doc::
            
            Args:
            Returns:
                
    """
    pass




###############################################################################
#                  TEXT ANALYSIS                                              #
###############################################################################
def text_plot_distributions(df, x, max_cat=20, top=None, y=None, bins=None, figsize=(10,5)):
    '''.
    Doc::
            
            Plot univariate and bivariate distributions.
    '''
    ## univariate
    if y is None:
        fig, ax = plt.subplots(figsize=figsize)
        fig.suptitle(x, fontsize=15)
        ### categorical
        if df[x].nunique() <= max_cat:
            if top is None:
                df[x].reset_index().groupby(x).count().sort_values(by="index").plot(kind="barh", legend=False, ax=ax).grid(axis='x')
            else:
                df[x].reset_index().groupby(x).count().sort_values(by="index").tail(top).plot(kind="barh", legend=False, ax=ax).grid(axis='x')
            ax.set(ylabel=None)
        ### numerical
        else:
            sns.distplot(df[x], hist=True, kde=True, kde_kws={"shade":True}, ax=ax)
            ax.grid(True)
            ax.set(xlabel=None, yticklabels=[], yticks=[])

    ## bivariate
    else:
        fig, ax = plt.subplots(nrows=1, ncols=2, sharex=False, sharey=False, figsize=figsize)
        fig.suptitle(x, fontsize=15)
        for i in df[y].unique():
            sns.distplot(df[df[y]==i][x], hist=True, kde=False, bins=bins, hist_kws={"alpha":0.8}, axlabel="", ax=ax[0])
            sns.distplot(df[df[y]==i][x], hist=False, kde=True, kde_kws={"shade":True}, axlabel="", ax=ax[1])
        ax[0].set(title="histogram")
        ax[0].grid(True)
        ax[0].legend(df[y].unique())
        ax[1].set(title="density")
        ax[1].grid(True)
    plt.show()



def text_add_detect_lang(data, column):
    '''.
    Doc::
            
            Detect language of text.
    '''
    df = data.copy()
    df['lang'] = df[column].apply(lambda x: langdetect.detect(x) if x.strip() != "" else "")
    return df



def text_add_text_length(data, column):
    '''.
    Doc::
            
            Compute different text length metrics.
            Doc::
        
                df: dataframe - df with a text column
                column: string - name of column containing text
            :return
                df: input dataframe with 2 new columns
    '''
    df = data.copy()
    df['word_count'] = df[column].apply(lambda x: len(nltk.word_tokenize(str(x))) )
    df['char_count'] = df[column].apply(lambda x: sum(len(word) for word in nltk.word_tokenize(str(x))) )
    df['sentence_count'] = df[column].apply(lambda x: len(nltk.sent_tokenize(str(x))) )
    df['avg_word_length'] = df['char_count'] / df['word_count']
    df['avg_sentence_lenght'] = df['word_count'] / df['sentence_count']
    print(df[['char_count','word_count','sentence_count','avg_word_length','avg_sentence_lenght']].describe().T[["min","mean","max"]])
    return df



def text_add_sentiment(data, column, algo="vader", sentiment_range=(-1,1)):
    '''.
    Doc::
            
            Computes the sentiment using Textblob or Vader.
            Doc::
        
                df: dataframe - df with a text column
                column: string - name of column containing text
                algo: string - "textblob" or "vader"
                sentiment_range: tuple - if not (-1,1) score is rescaled with sklearn
            :return
                df: input dataframe with new sentiment column
    '''
    df = data.copy()
    ## calculate sentiment
    if algo == "vader":
        vader = SentimentIntensityAnalyzer()
        df["sentiment"] = df[column].apply(lambda x: vader.polarity_scores(x)["compound"])
    elif algo == "textblob":
        df["sentiment"] = df[column].apply(lambda x: TextBlob(x).sentiment.polarity)
    ## rescaled
    if sentiment_range != (-1,1):
        df["sentiment"] = preprocessing.MinMaxScaler(feature_range=sentiment_range).fit_transform(df[["sentiment"]])
    print(df[['sentiment']].describe().T)
    return df




def text_create_stopwords(lst_langs=["english"], lst_add_words=[], lst_keep_words=[]):
    '''.
    Doc::
            
            Creates a list of stopwords.
            Doc::
        
                lst_langs: list - ["english", "italian"]
                lst_add_words: list - list of new stopwords to add
                lst_keep_words: list - list words to keep (exclude from stopwords)
            :return
                stop_words: list of stop words
    '''
    lst_stopwords = set()
    for lang in lst_langs:
        lst_stopwords = lst_stopwords.union( set(nltk.corpus.stopwords.words(lang)) )
    lst_stopwords = lst_stopwords.union(lst_add_words)
    lst_stopwords = list(set(lst_stopwords) - set(lst_keep_words))
    return sorted(list(set(lst_stopwords)))



def text_utils_preprocess_text(txt, lst_regex=None, punkt=True, lower=True, slang=True, lst_stopwords=None, stemm=False, lemm=True):
    '''.
    Doc::
            
            Preprocess a string.
            Doc::
        
                txt: string - name of column containing text
                lst_regex: list - list of regex to remove
                punkt: bool - if True removes punctuations and characters
                lower: bool - if True convert lowercase
                slang: bool - if True fix slang into normal words
                lst_stopwords: list - list of stopwords to remove
                stemm: bool - whether stemming is to be applied
                lemm: bool - whether lemmitisation is to be applied
            :return
                cleaned text
    '''
    ## regex (in case, before processing)
    if lst_regex is not None:
        for regex in lst_regex:
            txt = re.sub(regex, '', txt)

    ## clean
    ### separate sentences with '. '
    txt = re.sub(r'\.(?=[^ \W\d])', '. ', str(txt))
    ### remove punctuations and characters
    txt = re.sub(r'[^\w\s]', '', txt) if punkt is True else txt
    ### strip
    txt = " ".join([word.strip() for word in txt.split()])
    ### lowercase
    txt = txt.lower() if lower is True else txt
    ### slang
    txt = contractions.fix(txt) if slang is True else txt

    ## Tokenize (convert from string to list)
    lst_txt = txt.split()

    ## remove Stopwords
    if lst_stopwords is not None:
        lst_txt = [word for word in lst_txt if word not in lst_stopwords]

    ## Stemming (remove -ing, -ly, ...)
    if stemm is True:
        ps = nltk.stem.porter.PorterStemmer()
        lst_txt = [ps.stem(word) for word in lst_txt]

    ## Lemmatization (convert the word into root word)
    if lemm is True:
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        lst_txt = [lem.lemmatize(word) for word in lst_txt]

    ## remove leftover Stopwords
    if lst_stopwords is not None:
        lst_txt = [word for word in lst_txt if word not in lst_stopwords]

    ## back to string from list
    txt = " ".join(lst_txt)
    return txt



def text_add_preprocessed_text(data, column, lst_regex=None, punkt=False, lower=False, slang=False, lst_stopwords=None, stemm=False, lemm=False, remove_na=True):
    '''.
    Doc::
            
            Adds a column of preprocessed text.
            Doc::
        
                df: dataframe - df with a text column
                column: string - name of column containing text
            :return
                : input dataframe with two new columns
    '''
    df = data.copy()

    ## apply preprocess
    df = df[ pd.notnull(df[column]) ]
    df[column+"_clean"] = df[column].apply(lambda x: text_utils_preprocess_text(x, lst_regex, punkt, lower, slang, lst_stopwords, stemm, lemm))

    ## residuals
    df["check"] = df[column+"_clean"].apply(lambda x: len(x))
    if df["check"].min() == 0:
        print("--- found NAs ---")
        print(df[[column,column+"_clean"]][df["check"]==0].head())
        if remove_na is True:
            df = df[df["check"]>0]

    return df.drop("check", axis=1)



def text_word_freq(corpus, ngrams=[1,2,3], top=10, figsize=(10,7)):
    '''.
    Doc::
            
            Compute n-grams frequency with nltk tokenizer.
            Doc::
        
                corpus: list - df["text"]
                ngrams: int or list - 1 for unigrams, 2 for bigrams, [1,2] for both
                top: num - plot the top frequent words
            :return
                dtf_count: df with word frequency
    '''
    lst_tokens = nltk.tokenize.word_tokenize(corpus.str.cat(sep=" "))
    ngrams = [ngrams] if type(ngrams) is int else ngrams

    ## calculate
    dtf_freq = pd.DataFrame()
    for n in ngrams:
        dic_words_freq = nltk.FreqDist(nltk.ngrams(lst_tokens, n))
        dtf_n = pd.DataFrame(dic_words_freq.most_common(), columns=["word","freq"])
        dtf_n["ngrams"] = n
        dtf_freq = dtf_freq.append(dtf_n)
    dtf_freq["word"] = dtf_freq["word"].apply(lambda x: " ".join(string for string in x) )
    dtf_freq = dtf_freq.sort_values(["ngrams","freq"], ascending=[True,False])

    ## plot
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(x="freq", y="word", hue="ngrams", dodge=False, ax=ax,
                data=dtf_freq.groupby('ngrams')["ngrams","freq","word"].head(top))
    ax.set(xlabel=None, ylabel=None, title="Most frequent words")
    ax.grid(axis="x")
    plt.show()
    return dtf_freq



def text_plot_wordcloud(corpus, max_words=150, max_font_size=35, figsize=(10,10)):
    '''.
    Doc::
            
            Plots a wordcloud from a list of Docs or from a dictionary
            Doc::
        
                corpus: list - df["text"]
    '''
    wc = wordcloud.WordCloud(background_color='black', max_words=max_words, max_font_size=max_font_size)
    wc = wc.generate(str(corpus)) #if type(corpus) is not dict else wc.generate_from_frequencies(corpus)
    fig = plt.figure(num=1, figsize=figsize)
    plt.axis('off')
    plt.imshow(wc, cmap=None)
    plt.show()



def text_add_word_freq(data, column, lst_words, freq="count"):
    '''.
    Doc::
            
            Adds a column with word frequency.
            Doc::
        
                df: dataframe - df with a text column
                column: string - name of column containing text
                lst_words: list - ["donald trump", "china", ...]
                freq: str - "count" or "tfidf"
            :return
                df: input dataframe with new columns
    '''
    df = data.copy()

    ## query
    print("found records:")
    print([word+": "+str(len(df[df[column].str.contains(word)])) for word in lst_words])

    ## vectorizer
    lst_grams = [len(word.split(" ")) for word in lst_words]
    if freq == "tfidf":
        vectorizer = feature_extraction.text.TfidfVectorizer(vocabulary=lst_words, ngram_range=(min(lst_grams),max(lst_grams)))
    else:
        vectorizer = feature_extraction.text.CountVectorizer(vocabulary=lst_words, ngram_range=(min(lst_grams),max(lst_grams)))
    dtf_X = pd.DataFrame(vectorizer.fit_transform(df[column]).todense(), columns=lst_words)

    ## join
    for word in lst_words:
        df[word] = dtf_X[word]
    return df





###############################################################################
#                     BAG OF WORDS (VECTORIZER)                               #
###############################################################################

def bagwords_fit_bow(corpus, vectorizer=None, vocabulary=None):
    '''.
    Doc::
            
            Vectorize corpus with Bag-of-Words (classic Count or Tf-Idf variant), plots the most frequent words.
            Doc::
        
                corpus: list - df["text"]
                vectorizer: sklearn vectorizer object, like Count or Tf-Idf
                vocabulary: list of words or dict, if None it creates from scratch, else it searches the words into corpus
            :return
                sparse matrix, list of text tokenized, vectorizer, dic_vocabulary, X_names
    '''
    ## vectorizer
    vectorizer = feature_extraction.text.TfidfVectorizer(max_features=None, ngram_range=(1,1), vocabulary=vocabulary) if vectorizer is None else vectorizer
    vectorizer.fit(corpus)

    ## sparse matrix
    print("--- creating sparse matrix ---")
    X = vectorizer.transform(corpus)
    print("shape:", X.shape)

    ## vocabulary
    print("--- creating vocabulary ---") if vocabulary is None else print("--- used vocabulary ---")
    dic_vocabulary = vectorizer.vocabulary_   #{word:idx for idx, word in enumerate(vectorizer.get_feature_names())}
    print(len(dic_vocabulary), "words")

    ## text2tokens
    print("--- tokenization ---")
    tokenizer = vectorizer.build_tokenizer()
    preprocessor = vectorizer.build_preprocessor()
    lst_text2tokens = []
    for text in corpus:
        lst_tokens = [dic_vocabulary[word] for word in tokenizer(preprocessor(text)) if word in dic_vocabulary]
        lst_text2tokens.append(lst_tokens)
    print(len(lst_text2tokens), "texts")

    ## plot heatmap
    fig, ax = plt.subplots(figsize=(15,5))
    sns.heatmap(X.todense()[:,np.random.randint(0,X.shape[1],100)]==0, vmin=0, vmax=1, cbar=False, ax=ax).set_title('Sparse Matrix Sample')
    plt.show()
    return {"X":X, "lst_text2tokens":lst_text2tokens, "vectorizer":vectorizer, "dic_vocabulary":dic_vocabulary, "X_names":vectorizer.get_feature_names()}



def bagwords_features_selection(X, y, X_names, top=None, print_top=10):
    '''.
    Doc::
            
            Perform feature selection using p-values (keep highly correlated features)
            Doc::
        
                X: array - like sparse matrix or df.values
                y: array or df - like df["y"]
                X_names: list - like vetcorizer.get_feature_names()
                top: int - ex. 1000 takes the top 1000 features per classes of y. If None takes all those with p-value < 5%.
                print_top: int - print top features
            :return
                df with features and scores
    '''
    ## selection
    dtf_features = pd.DataFrame()
    for cat in np.unique(y):
        chi2, p = feature_selection.chi2(X, y==cat)
        dtf_features = dtf_features.append(pd.DataFrame({"feature":X_names, "score":1-p, "y":cat}))
    dtf_features = dtf_features.sort_values(["y","score"], ascending=[True,False])
    dtf_features = dtf_features[dtf_features["score"]>0.95] #p-value filter
    if top is not None:
        dtf_features = dtf_features.groupby('y')["y","feature","score"].head(top)

    ## print
    print("features selection: from", "{:,.0f}".format(len(X_names)),
          "to", "{:,.0f}".format(len(dtf_features["feature"].unique())))
    print(" ")
    for cat in np.unique(y):
        print("# {}:".format(cat))
        print("  . selected features:", len(dtf_features[dtf_features["y"]==cat]))
        print("  . top features:", ", ".join(dtf_features[dtf_features["y"]==cat]["feature"].values[:print_top]))
        print(" ")
    return dtf_features["feature"].unique().tolist(), dtf_features



def bagwords_sparse2dtf(X, dic_vocabulary, X_names, prefix=""):
    '''.
    Doc::
            
            Transform a sparse matrix into a df with selected features only.
            Doc::
        
                X: array - like sparse matrix or df.values
                dic_vocabulary: dict - {"word":idx}
                X_names: list of words - like vetcorizer.get_feature_names()
                prefix: str - ex. "x_" -> x_word1, x_word2, ..
    '''
    dtf_X = pd.DataFrame()
    for word in X_names:
        idx = dic_vocabulary[word]
        dtf_X[prefix+word] = np.reshape(X[:,idx].toarray(), newshape=(-1))
    return dtf_X



def bagwords_fit_ml_classif(X_train, y_train, X_test, vectorizer=None, classifier=None):
    '''.
    Doc::
            
            Fits a sklearn classification model.
            Doc::
        
                X_train: feature matrix
                y_train: array of classes
                X_test: raw text
                vectorizer: vectorizer object - if None Tf-Idf is used
                classifier: model object - if None MultinomialNB is used
            :return
                fitted model and predictions
    '''
    ## model pipeline
    vectorizer = feature_extraction.text.TfidfVectorizer() if vectorizer is None else vectorizer
    classifier = naive_bayes.MultinomialNB() if classifier is None else classifier
    model = pipeline.Pipeline([("vectorizer",vectorizer), ("classifier",classifier)])

    ## train
    if vectorizer is None:
        model.fit(X_train, y_train)
    else:
        model["classifier"].fit(X_train, y_train)

    ## test
    predicted = model.predict(X_test)
    predicted_prob = model.predict_proba(X_test)
    return model, predicted_prob, predicted




###############################################################################
#                        WORD2VEC (WORD EMBEDDING)                            #
###############################################################################

def word2vec_utils_preprocess_ngrams(corpus, ngrams=1, grams_join=" ", lst_ngrams_detectors=[]):
    '''.
    Doc::
            
            Create a list of lists of grams with gensim:
                [ ["hi", "my", "name", "is", "Tom"],
                ["what", "is", "yours"] ]
            Doc::
        
                corpus: list - df["text"]
                ngrams: num - ex. "new", "york"
                grams_join: string - "_" (new_york), " " (new york)
                lst_ngrams_detectors: list - [bigram and trigram models], if empty doesn't detect common n-grams
            :return
                lst of lists of n-grams
    '''
    ## create list of n-grams
    lst_corpus = []
    for string in corpus:
        lst_words = string.split()
        lst_grams = [grams_join.join(lst_words[i:i + ngrams]) for i in range(0, len(lst_words), ngrams)]
        lst_corpus.append(lst_grams)

    ## detect common bi-grams and tri-grams
    if len(lst_ngrams_detectors) != 0:
        for detector in lst_ngrams_detectors:
            lst_corpus = list(detector[lst_corpus])
    return lst_corpus



def word2vec_create_ngrams_detectors(corpus, grams_join=" ", lst_common_terms=[], min_count=5, top=10, figsize=(10,7)):
    '''.
    Doc::
            
            Train common bigrams and trigrams detectors with gensim
            Doc::
        
                corpus: list - df["text"]
                grams_join: string - "_" (new_york), " " (new york)
                lst_common_terms: list - ["of","with","without","and","or","the","a"]
                min_count: int - ignore all words with total collected count lower than this value
            :return
                list with n-grams models and dataframe with frequency
    '''
    ## fit models
    lst_corpus = word2vec_utils_preprocess_ngrams(corpus, ngrams=1, grams_join=grams_join)
    bigrams_detector = gensim.models.phrases.Phrases(lst_corpus, delimiter=grams_join.encode(), common_terms=lst_common_terms,
                                                     min_count=min_count, threshold=min_count*2)
    bigrams_detector = gensim.models.phrases.Phraser(bigrams_detector)
    trigrams_detector = gensim.models.phrases.Phrases(bigrams_detector[lst_corpus], delimiter=grams_join.encode(), common_terms=lst_common_terms,
                                                      min_count=min_count, threshold=min_count*2)
    trigrams_detector = gensim.models.phrases.Phraser(trigrams_detector)

    ## plot
    dtf_ngrams = pd.DataFrame([{"word":grams_join.join([gram.decode() for gram in k]), "freq":v} for k,v in trigrams_detector.phrasegrams.items()])
    dtf_ngrams["ngrams"] = dtf_ngrams["word"].apply(lambda x: x.count(grams_join)+1)
    dtf_ngrams = dtf_ngrams.sort_values(["ngrams","freq"], ascending=[True,False])

    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(x="freq", y="word", hue="ngrams", dodge=False, ax=ax,
                data=dtf_ngrams.groupby('ngrams')["ngrams","freq","word"].head(top))
    ax.set(xlabel=None, ylabel=None, title="Most frequent words")
    ax.grid(axis="x")
    plt.show()
    return [bigrams_detector, trigrams_detector], dtf_ngrams



def word2vec_fit_w2v(corpus, ngrams=1, grams_join=" ", lst_ngrams_detectors=[], min_count=1, size=300, window=20, sg=1, epochs=100):
    '''.
    Doc::
            
            Fits the Word2Vec model from gensim.
            Doc::
        
                corpus: list - df["text"]
                ngrams: num - ex. "new", "york"
                grams_join: string - "_" (new_york), " " (new york)
                lst_ngrams_detectors: list - [bigram and trigram models], if empty doesn't detect common n-grams
                min_count: num - ignores all words with total frequency lower than this
                size: num - dimensionality of the vectors
                window: num - ( x x x ... x  word  x ... x x x)
                sg: num - 1 for skip-grams, 0 for CBOW
                lst_common_terms: list - ["of","with","without","and","or","the","a"]
            :return
                lst_corpus and the nlp model
    '''
    lst_corpus = word2vec_utils_preprocess_ngrams(corpus, ngrams=ngrams, grams_join=grams_join, lst_ngrams_detectors=lst_ngrams_detectors)
    nlp = gensim.models.word2vec.Word2Vec(lst_corpus, size=size, window=window, min_count=min_count, sg=sg, iter=epochs)
    return lst_corpus, nlp.wv



def word2vec_embedding_w2v(x, nlp=None, value_na=0):
    '''.
    Doc::
            
            Creates a feature matrix (num_docs x vector_size)
            Doc::
        
                x: string or list
                nlp: gensim model
                value_na: value to return when the word is not in vocabulary
            :return
                vector or matrix
    '''
    nlp = gensim_api.load("glove-wiki-gigaword-300") if nlp is None else nlp
    null_vec = [value_na]*nlp.vector_size

    ## single word --> vec (size,)
    if (type(x) is str) and (len(x.split()) == 1):
        X = nlp[x] if x in nlp.vocab.keys() else null_vec

    ## list of words --> matrix (n, size)
    elif (type(x) is list) and (type(x[0]) is str) and (len(x[0].split()) == 1):
        X = np.array([nlp[word] if word in nlp.vocab.keys() else null_vec for word in x])

    ## list of lists of words --> matrix (n mean vectors, size)
    elif (type(x) is list) and (type(x[0]) is list):
        lst_mean_vecs = []
        for lst in x:
            lst_mean_vecs.append(np.array([nlp[word] if word in nlp.vocab.keys() else null_vec for word in lst]
                                          ).mean(0))
        X = np.array(lst_mean_vecs)

    ## single text --> matrix (n words, size)
    elif (type(x) is str) and (len(x.split()) > 1):
        X = np.array([nlp[word] if word in nlp.vocab.keys() else null_vec for word in x.split()])

    ## list of texts --> matrix (n mean vectors, size)
    else:
        lst_mean_vecs = []
        for txt in x:
            lst_mean_vecs.append(np.array([nlp[word] if word in nlp.vocab.keys() else null_vec for word in txt.split()]
                                          ).mean(0))
        X = np.array(lst_mean_vecs)

    return X



def word2vec_plot_w2v(lst_words=None, nlp=None, plot_type="2d", top=20, annotate=True, figsize=(10,5)):
    '''.
    Doc::
            
            Plot words in vector space (2d or 3d).
            Doc::
        
                lst_words: list - ["donald trump","china", ...]. If None, it plots the whole vocabulary
                nlp: gensim model
                plot_type: string - "2d" or "3d"
                top: num - plot top most similar words (only if lst_words is given)
                annotate: bool - include word text
    '''
    nlp = gensim_api.load("glove-wiki-gigaword-300") if nlp is None else nlp
    fig = plt.figure(figsize=figsize)
    if lst_words is not None:
        fig.suptitle("Word: "+lst_words[0], fontsize=12) if len(lst_words) == 1 else fig.suptitle("Words: "+str(lst_words[:5]), fontsize=12)
    else:
        fig.suptitle("Vocabulary")
    try:
        ## word embedding
        tot_words = lst_words + [tupla[0] for tupla in nlp.most_similar(lst_words, topn=top)] if lst_words is not None else list(nlp.vocab.keys())
        X = nlp[tot_words]

        ## pca
        pca = manifold.TSNE(perplexity=40, n_components=int(plot_type[0]), init='pca')
        X = pca.fit_transform(X)

        ## create df
        columns = ["x","y"] if plot_type == "2d" else ["x","y","z"]
        df = pd.DataFrame(X, index=tot_words, columns=columns)
        df["input"] = 0
        if lst_words is not None:
            df["input"].iloc[0:len(lst_words)] = 1  #<--this makes the difference between vocabulary and input words

        ## plot 2d
        if plot_type == "2d":
            ax = fig.add_subplot()
            sns.scatterplot(data=df, x="x", y="y", hue="input", legend=False, ax=ax, palette={0:'black',1:'red'})
            ax.set(xlabel=None, ylabel=None, xticks=[], xticklabels=[], yticks=[], yticklabels=[])
            if annotate is True:
                for i in range(len(df)):
                    ax.annotate(df.index[i], xy=(df["x"].iloc[i],df["y"].iloc[i]),
                                xytext=(5,2), textcoords='offset points', ha='right', va='bottom')

        ## plot 3d
        elif plot_type == "3d":
            from mpl_toolkits.mplot3d import Axes3D
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(df[df["input"]==0]['x'], df[df["input"]==0]['y'], df[df["input"]==0]['z'], c="black")
            ax.scatter(df[df["input"]==1]['x'], df[df["input"]==1]['y'], df[df["input"]==1]['z'], c="red")
            ax.set(xlabel=None, ylabel=None, zlabel=None, xticklabels=[], yticklabels=[], zticklabels=[])
            if annotate is True:
                for label, row in df[["x","y","z"]].iterrows():
                    x, y, z = row
                    ax.text(x, y, z, s=label)

        plt.show()

    except Exception as e:
        print("--- got error ---")
        print(e)
        word = str(e).split("'")[1]
        print("maybe you are looking for ... ")
        print([k for k in list(nlp.vocab.keys()) if 1-nltk.jaccard_distance(set(word),set(k)) > 0.7])



def word2vec_vocabulary_embeddings(dic_vocabulary, nlp=None):
    '''.
    Doc::
            
            Embeds a vocabulary of unigrams with gensim w2v.
            Doc::
        
                dic_vocabulary: dict - {"word":1, "word":2, ...}
                nlp: gensim model
            :return
                Matric and the nlp model
    '''
    nlp = gensim_api.load("glove-wiki-gigaword-300") if nlp is None else nlp
    embeddings = np.zeros((len(dic_vocabulary)+1, nlp.vector_size))
    for word,idx in dic_vocabulary.items():
        ## update the row with vector
        try:
            embeddings[idx] =  nlp[word]
        ## if word not in model then skip and the row stays all zeros
        except:
            pass
    print("vocabulary mapped to", embeddings.shape[0], "vectors of size", embeddings.shape[1])
    return embeddings



def word2vec_text2seq(corpus, ngrams=1, grams_join=" ", lst_ngrams_detectors=[], fitted_tokenizer=None, top=None, oov=None, maxlen=None):
    '''.
    Doc::
            
            Transforms the corpus into an array of sequences of idx (tokenizer) with same length (padding).
            Doc::
        
                corpus: list - df["text"]
                ngrams: num - ex. "new", "york"
                grams_join: string - "_" (new_york), " " (new york)
                lst_ngrams_detectors: list - [bigram and trigram models], if empty doesn't detect common n-grams
                fitted_tokenizer: keras tokenizer - if None it creates one with fit and transorm (train set), if given it transforms only (test set)
                top: num - if given the tokenizer keeps only top important words
                oov: string - how to encode words not in vocabulary (ex. "NAN")
                maxlen: num - dimensionality of the vectors, if None takes the max length in corpus
                padding: string - "pre" for [9999,1,2,3] or "post" for [1,2,3,9999]
            :return
                If training: matrix of sequences, tokenizer, dic_vocabulary. Else matrix of sequences only.
    '''
    print("--- tokenization ---")

    ## detect common n-grams in corpus
    lst_corpus = word2vec_utils_preprocess_ngrams(corpus, ngrams=ngrams, grams_join=grams_join, lst_ngrams_detectors=lst_ngrams_detectors)

    ## bow with keras to get text2tokens without creating the sparse matrix
    ### train
    if fitted_tokenizer is None:
        tokenizer = kprocessing.text.Tokenizer(num_words=top, lower=False, split=' ', char_level=False, oov_token=oov,
                                               filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
        tokenizer.fit_on_texts(lst_corpus)
        dic_vocabulary = tokenizer.word_index if top is None else dict(list(tokenizer.word_index.items())[0:top+1])
        print(len(dic_vocabulary), "words")
    else:
        tokenizer = fitted_tokenizer
    ### transform
    lst_text2seq = tokenizer.texts_to_sequences(lst_corpus)

    ## padding sequence (from [1,2],[3,4,5,6] to [0,0,1,2],[3,4,5,6])
    print("--- padding to sequence ---")
    X = kprocessing.sequence.pad_sequences(lst_text2seq, maxlen=maxlen, padding="post", truncating="post")
    print(X.shape[0], "sequences of length", X.shape[1])

    ## plot heatmap
    fig, ax = plt.subplots(figsize=(15,5))
    sns.heatmap(X==0, vmin=0, vmax=1, cbar=False, ax=ax).set_title('Sequences Overview')
    plt.show()
    return {"X":X, "tokenizer":tokenizer, "dic_vocabulary":dic_vocabulary} if fitted_tokenizer is None else X



def word2vec_fit_dl_classif(X_train, y_train, X_test, encode_y=False, dic_y_mapping=None, model=None, weights=None, epochs=100, batch_size=256):
    '''.
    Doc::
            
            Fits a keras classification model.
            Doc::
        
                dic_y_mapping: dict - {0:"A", 1:"B", 2:"C"}. If None it calculates.
                X_train: array of sequence
                y_train: array of classes
                X_test: array of sequence
                model: model object - model to fit (before fitting)
                weights: array of weights - like embeddings
            :return
                model fitted and predictions
    '''
    ## encode y
    if encode_y is True:
        dic_y_mapping = {n:label for n,label in enumerate(np.unique(y_train))}
        inverse_dic = {v:k for k,v in dic_y_mapping.items()}
        y_train = np.array( [inverse_dic[y] for y in y_train] )
    print(dic_y_mapping)

    ## model
    if model is None:
        ### params
        n_features, embeddings_dim = weights.shape
        max_seq_lenght = X_train.shape[1]
        ### neural network
        x_in = layers.Input(shape=(X_train.shape[1],))
        x = layers.Embedding(input_dim=n_features, output_dim=embeddings_dim, weights=[weights], input_length=max_seq_lenght, trainable=False)(x_in)
        x = layers.Attention()([x,x])
        x = layers.Bidirectional(layers.LSTM(units=X_train.shape[1], dropout=0.2))(x)
        x = layers.Dense(units=64, activation='relu')(x)
        y_out = layers.Dense(len(np.unique(y_train)), activation='softmax')(x)
        ### compile
        model = models.Model(x_in, y_out)
        model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())

    ## train
    verbose = 0 if epochs > 1 else 1
    training = model.fit(x=X_train, y=y_train, batch_size=batch_size, epochs=epochs, shuffle=True, verbose=verbose, validation_split=0.3)

    ## test
    predicted_prob = model.predict(X_test)
    predicted = [dic_y_mapping[np.argmax(pred)] for pred in predicted_prob] if encode_y is True else [np.argmax(predicted_prob )]
    return training.model, predicted_prob, predicted




###############################################################################
#                        TOPIC MODELING                                       #
###############################################################################

def topic_get_similar_words(lst_words, top, nlp=None):
    '''.
    Doc::
            
            Use Word2Vec to get a list of similar words of a given input words list
            Doc::
        
                lst_words: list - input words
                top: num - number of words to return
                nlp: gensim model
            :return
                list with input words + output words
    '''
    nlp = gensim_api.load("glove-wiki-gigaword-300") if nlp is None else nlp
    lst_out = lst_words
    for tupla in nlp.most_similar(lst_words, topn=top):
        lst_out.append(tupla[0])
    return list(set(lst_out))



def topic_word_clustering(corpus, nlp=None, ngrams=1, grams_join=" ", lst_ngrams_detectors=[], n_clusters=3):
    '''.
    Doc::
            
            Clusters a Word2Vec vocabulary with nltk Kmeans using cosine similarity.
            Doc::
        
                corpus: list - df["text"]
                ngrams: num - ex. "new", "york"
                grams_join: string - "_" (new_york), " " (new york)
                lst_ngrams_detectors: list - [bigram and trigram models], if empty doesn't detect common n-grams
                n_clusters: num - number of topics to find
            :return
                df with clusters
    '''
    ## fit W2V
    if nlp is None:
        print("--- training W2V---")
        lst_corpus, nlp = word2vec_fit_w2v(corpus, ngrams=ngrams, grams_join=grams_join, lst_ngrams_detectors=lst_ngrams_detectors,
                                  min_count=1, size=300, window=20, sg=0, epochs=100)

    ## fit K-Means
    print("--- training K-means ---")
    X = nlp[nlp.vocab.keys()]
    kmeans_model = nltk.cluster.KMeansClusterer(n_clusters, distance=nltk.cluster.util.cosine_distance, repeats=50, avoid_empty_clusters=True)
    clusters = kmeans_model.cluster(X, assign_clusters=True)
    dic_clusters = {word:clusters[i] for i,word in enumerate(list(nlp.vocab.keys()))}
    dtf_clusters = pd.DataFrame({"word":word, "cluster":str(clusters[i])} for i,word in enumerate(list(nlp.vocab.keys())))
    dtf_clusters = dtf_clusters.sort_values(["cluster", "word"], ascending=[True,True]).reset_index(drop=True)
    return dtf_clusters



def topic_fit_lda(corpus, ngrams=1, grams_join=" ", lst_ngrams_detectors=[], n_topics=3, figsize=(10,7)):
    '''.
    Doc::
            
            Fits Latent Dirichlet Allocation with gensim.
            Doc::
        
                corpus: list - df["text"]
                ngrams: num - ex. "new", "york"
                grams_join: string - "_" (new_york), " " (new york)
                lst_ngrams_detectors: list - [bigram and trigram models], if empty doesn't detect common n-grams
                n_topics: num - number of topics to find
            :return
                model and df topics
    '''
    ## train the lda
    lst_corpus = word2vec_utils_preprocess_ngrams(corpus, ngrams=ngrams, grams_join=grams_join, lst_ngrams_detectors=lst_ngrams_detectors)
    id2word = gensim.corpora.Dictionary(lst_corpus) #map words with an id
    dic_corpus = [id2word.doc2bow(word) for word in lst_corpus]  #create dictionary Word:Freq
    print("--- training ---")
    lda_model = gensim.models.ldamodel.LdaModel(corpus=dic_corpus, id2word=id2word, num_topics=n_topics,
                                                random_state=123, update_every=1, chunksize=100,
                                                passes=10, alpha='auto', per_word_topics=True)

    ## output
    lst_dics = []
    for i in range(0, n_topics):
        lst_tuples = lda_model.get_topic_terms(i)
        for tupla in lst_tuples:
            lst_dics.append({"topic":i, "id":tupla[0], "word":id2word[tupla[0]], "weight":tupla[1]})
    dtf_topics = pd.DataFrame(lst_dics, columns=['topic','id','word','weight'])

    ## plot
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(y="word", x="weight", hue="topic", data=dtf_topics, dodge=False, ax=ax).set_title('Main Topics')
    ax.set(ylabel="", xlabel="importance")
    plt.show()
    return lda_model, dtf_topics



def topic_plot_w2v_cluster(dic_words=None, nlp=None, plot_type="2d", annotate=True, figsize=(10,5)):
    '''.
    Doc::
            
            Plot word clusters in vector space (2d or 3d).
            Doc::
        
                dic_words: dict - {0:lst_words, 1:lst_words, ...}
                nlp: gensim model
                plot_type: string - "2d" or "3d"
                annotate: bool - include word text
    '''
    nlp = gensim_api.load("glove-wiki-gigaword-300") if nlp is None else nlp
    fig = plt.figure(figsize=figsize)
    fig.suptitle("Word Clusters", fontsize=12)
    try:
        ## word embedding
        tot_words = [word for v in dic_words.values() for word in v]
        X = nlp[tot_words]

        ## pca
        pca = manifold.TSNE(perplexity=40, n_components=int(plot_type[0]), init='pca')
        X = pca.fit_transform(X)

        ## create df
        columns = ["x","y"] if plot_type == "2d" else ["x","y","z"]
        df = pd.DataFrame()
        for k,v in dic_words.items():
            size = len(df) + len(v)
            dtf_group = pd.DataFrame(X[len(df):size], columns=columns, index=v)
            dtf_group["cluster"] = k
            df = df.append(dtf_group)

        ## plot 2d
        if plot_type == "2d":
            ax = fig.add_subplot()
            sns.scatterplot(data=df, x="x", y="y", hue="cluster", ax=ax)
            ax.legend().texts[0].set_text(None)
            ax.set(xlabel=None, ylabel=None, xticks=[], xticklabels=[], yticks=[], yticklabels=[])
            if annotate is True:
                for i in range(len(df)):
                    ax.annotate(df.index[i], xy=(df["x"].iloc[i],df["y"].iloc[i]),
                                xytext=(5,2), textcoords='offset points', ha='right', va='bottom')

        ## plot 3d
        elif plot_type == "3d":
            from mpl_toolkits.mplot3d import Axes3D
            ax = fig.add_subplot(111, projection='3d')
            colors = sns.color_palette(None, len(dic_words.keys()))
            for n,k in enumerate(dic_words.keys()):
                ax.scatter(df[df["cluster"]==k]['x'], df[df["cluster"]==k]['y'], df[df["cluster"]==k]['z'], c=colors[n], label=k)
            ax.set(xlabel=None, ylabel=None, zlabel=None, xticklabels=[], yticklabels=[], zticklabels=[])
            ax.legend()
            if annotate is True:
                for label, row in df[["x","y","z"]].iterrows():
                    x, y, z = row
                    ax.text(x, y, z, s=label)

        plt.show()

    except Exception as e:
        print("--- got error ---")
        print(e)
        word = str(e).split("'")[1]
        print("maybe you are looking for ... ")
        print([k for k in list(nlp.vocab.keys()) if 1-nltk.jaccard_distance(set(word),set(k)) > 0.7])





###############################################################################
#               UNSEPERVISED CLASSIFICATION BY SIMILARITY                     #
###############################################################################

def text_cluster_cosine_sim(a, b, nlp=None):
    '''.
    Doc::
            
            Compute cosine similarity between 2 strings or 2 vectors/matrices: cosine_sim = matrix (rows_a x rows_b)
            Doc::
        
                a: string, vector, or matrix
                b: string, vector, or matrix
                nlp: gensim model - used only if a and b are strings
            :return
                cosine similarity score or matrix
    '''
    ## string vs string = score
    if (type(a) is str) or (type(b) is str):
        nlp = gensim_api.load("glove-wiki-gigaword-300") if nlp is None else nlp
        cosine_sim = nlp.similarity(a,b)

    else:
        ## vector vs vector = score
        if (len(a.shape) == 1) and (len(a.shape) == 1):
            a = a.reshape(1,-1)
            b = b.reshape(1,-1)
            cosine_sim = metrics.pairwise.cosine_similarity(a, b)[0][0]  #np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

        ## matrix vs matrix = matrix (rows_a x rows_b)
        else:
            a = a.reshape(1,-1) if len(a.shape) == 1 else a
            b = b.reshape(1,-1) if len(b.shape) == 1 else b
            cosine_sim = metrics.pairwise.cosine_similarity(a, b)
    return cosine_sim



def text_cluster_predict_similarity_classif(X, dic_y):
    '''.
    Doc::
            
            Clustering of text to specific classes (Unsupervised Classification by similarity).
            Doc::
        
                X: feature matrix (num_docs x vector_size)
                dic_y: dic label:mean_vector - {'finance':mean_vec, 'esg':mean_vec}
            :return
                predicted_prob, predicted
    '''
    predicted_prob = np.array([text_cluster_cosine_sim(X, y).T.tolist()[0] for y in dic_y.values()]).T
    labels = list(dic_y.keys())

    ## adjust and rescale
    for i in range(len(predicted_prob)):
        ### assign randomly if there is no similarity
        if sum(predicted_prob[i]) == 0:
            predicted_prob[i] = [0]*len(labels)
            predicted_prob[i][np.random.choice(range(len(labels)))] = 1
        ### rescale so they sum=1
        predicted_prob[i] = predicted_prob[i] / sum(predicted_prob[i])

    predicted = [labels[np.argmax(pred)] for pred in predicted_prob]
    return predicted_prob, predicted





###############################################################################
#                  STRING MATCHING                                            #
###############################################################################

def string_matching_cossim(a, lst_b, threshold=None, top=None):
    '''.
    Doc::
            
            Matches strings with cosine similarity.
            Doc::
        
                a: string - ex. "my house"
                lst_b: list of strings - ex. ["my", "hi", "house", "sky"]
                threshold: num - similarity threshold to consider the match valid
                top: num - number of matches to return
            :return
                df with 1 column = a, index = lst_b, values = cosine similarity scores
    '''
    ## vectorizer ("my house" --> ["my", "hi", "house", "sky"] --> [1, 0, 1, 0])
    vectorizer = feature_extraction.text.CountVectorizer()
    X = vectorizer.fit_transform([a]+lst_b).toarray()

    ## cosine similarity (scores a vs lst_b)
    lst_vectors = [vec for vec in X]
    cosine_sim = metrics.pairwise.cosine_similarity(lst_vectors)
    scores = cosine_sim[0][1:]

    ## match
    match_scores = scores if threshold is None else scores[scores >= threshold]
    match_idxs = range(len(match_scores)) if threshold is None else [i for i in np.where(scores >= threshold)[0]]
    match_strings = [lst_b[i] for i in match_idxs]

    ## df
    dtf_match = pd.DataFrame(match_scores, columns=[a], index=match_strings)
    dtf_match = dtf_match[~dtf_match.index.duplicated(keep='first')].sort_values(a, ascending=False).head(top)
    return dtf_match



def string_vlookup(lst_left, lst_right, threshold=0.7, top=1):
    '''.
    Doc::
            
            str_vlookup for similar strings.
            Doc::
        
                lst_left - array or lst
                lst_right - array or lst
                threshold: num - similarity threshold to consider the match valid
                top: num or None - number of matches to return
            :return
                dtf_matches - dataframe with matches
    '''
    try:
        dtf_matches = pd.DataFrame(columns=['string','match','similarity'])
        for string in lst_left:
            dtf_match = string_matching_cossim(string, lst_right, threshold, top)
            dtf_match = dtf_match.reset_index().rename(columns={'index':'match', string:'similarity'})
            dtf_match["string"] = string
            for i in range(len(dtf_match)):
                print(string, " --", round(dtf_match["similarity"].values[i], 2), "--> ", dtf_match["match"].values[i])
            dtf_matches = dtf_matches.append(dtf_match, ignore_index=True, sort=False)
        return dtf_matches[['string','match','similarity']]

    except Exception as e:
        print("--- got error ---")
        print(e)



def string_matching_display(a, b, both=True, sentences=True, titles=[]):
    '''.
    Doc::
            
            Highlights the matched strings in text.
            Doc::
        
                a: string - raw text
                b: string - raw text
                both: bool - search a in b and, if True, viceversa
                sentences: bool - if False matches single words
            :return
                text html, it can be visualized on notebook with display(HTML(text))
    '''
    if sentences is True:
        lst_a, lst_b = nltk.sent_tokenize(a), nltk.sent_tokenize(b)
    else:
        lst_a, lst_b = a.split(), b.split()

    ## highlight a
    first_text = []
    for i in lst_a:
        if i.lower() in [z.lower() for z in lst_b]:
            first_text.append('<span style="background-color:rgba(255,215,0,0.3);">' + i + '</span>')
        else:
            first_text.append(i)
    first_text = ' '.join(first_text)

    ## highlight b
    second_text = []
    if both is True:
        for i in lst_b:
            if i in [z.lower() for z in lst_a]:
                second_text.append('<span style="background-color:rgba(255,215,0,0.3);">' + i + '</span>')
            else:
                second_text.append(i)
    else:
        second_text.append(b)
    second_text = ' '.join(second_text)

    ## concatenate
    if len(titles) > 0:
        first_text = "<strong>"+titles[0]+"</strong><br>"+first_text
    if len(titles) > 1:
        second_text = "<strong>"+titles[1]+"</strong><br>"+second_text
    else:
        second_text = "---"*65+"<br><br>"+second_text
    final_text = first_text +'<br><br>'+ second_text
    return final_text



###############################################################################
#                             SEQ2SEQ                                         #
###############################################################################

def seqseq_fit_seq2seq(X_train, y_train, X_embeddings, y_embeddings, model=None, build_encoder_decoder=True, epochs=100, batch_size=64):
    '''.
    Doc::
            
            Fits a keras seq2seq model.
            Doc::
        
                X_train: array of sequences
                y_train: array of sequences
                X_embeddings: array of weights - shape (len_vocabulary x 300)
                y_embeddings: array of weights - shape (len_vocabulary x 300)
                model: model object - model to fit (before fitting)
                build_encoder_decoder: logic - if True returns prediction encoder-decoder
            :return
                fitted model, encoder + decoder (if model is noy given)
    '''
    ## model
    if model is None:
        ### params
        len_vocabulary_X, embeddings_dim_X = X_embeddings.shape
        len_vocabulary_y, embeddings_dim_y = y_embeddings.shape
        lstm_units = 250
        max_seq_lenght = X_train.shape[1]
        ### encoder (embedding + lstm)
        x_in = layers.Input(name="x_in", shape=(max_seq_lenght,))
        layer_x_emb = layers.Embedding(name="x_emb", input_dim=len_vocabulary_X, output_dim=embeddings_dim_X,
                                       weights=[X_embeddings], trainable=False)
        x_emb = layer_x_emb(x_in)
        layer_x_lstm = layers.LSTM(name="x_lstm", units=lstm_units, dropout=0.4, recurrent_dropout=0.4,
                                   return_sequences=True, return_state=True)
        x_out, state_h, state_c = layer_x_lstm(x_emb)
        ### decoder (embedding + lstm + dense)
        y_in = layers.Input(name="y_in", shape=(None,))
        layer_y_emb = layers.Embedding(name="y_emb", input_dim=len_vocabulary_y, output_dim=embeddings_dim_y,
                                       weights=[y_embeddings], trainable=False)
        y_emb = layer_y_emb(y_in)
        layer_y_lstm = layers.LSTM(name="y_lstm", units=lstm_units, dropout=0.4, recurrent_dropout=0.4,
                                   return_sequences=True, return_state=True)
        y_out, _, _ = layer_y_lstm(y_emb, initial_state=[state_h, state_c])
        layer_dense = layers.TimeDistributed(name="dense",
                                             layer=layers.Dense(units=len_vocabulary_y, activation='softmax'))
        y_out = layer_dense(y_out)
        ### compile
        model = models.Model(inputs=[x_in, y_in], outputs=y_out, name="Seq2Seq")
        model.compile(loss='sparse_categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        print(model.summary())

    ## train
    verbose = 0 if epochs > 1 else 1
    training = model.fit(x=[X_train, y_train[:,:-1]],
                         y=y_train.reshape(y_train.shape[0], y_train.shape[1], 1)[:,1:],
                         batch_size=batch_size, epochs=epochs, shuffle=True, verbose=verbose, validation_split=0.3,
                         callbacks=[callbacks.EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=2)])

    ## build prediction enconder-decoder model
    if build_encoder_decoder is True:
        lstm_units = lstm_units*2 if any("Bidirectional" in str(layer) for layer in model.layers) else lstm_units
        ### encoder
        encoder_model = models.Model(inputs=x_in, outputs=[x_out, state_h, state_c], name="Prediction_Encoder")
        ### decoder
        encoder_out = layers.Input(shape=(max_seq_lenght, lstm_units))
        state_h, state_c = layers.Input(shape=(lstm_units,)), layers.Input(shape=(lstm_units,))
        y_emb2 = layer_y_emb(y_in)
        y_out2, new_state_h, new_state_c = layer_y_lstm(y_emb2, initial_state=[state_h, state_c])
        predicted_prob = layer_dense(y_out2)
        decoder_model = models.Model(inputs=[y_in, encoder_out, state_h, state_c],
                                     outputs=[predicted_prob, new_state_h, new_state_c],
                                     name="Prediction_Decoder")
        return training.model, encoder_model, decoder_model
    else:
        return training.model



def seqseq_predict_seq2seq(X_test, encoder_model, decoder_model, fitted_tokenizer, special_tokens=("<START>","<END>")):
    '''.
    Doc::
            
            Predicts text sequences.
            Doc::
        
                x: array - sequence of shape (n x max_seq_lenght)
                encoder_model: keras model - input: x
                                                    output: [(1, max_seq_lenght, lstm_units), state_h, state_c]
                decoder_model: keras model - input: [1 word idx, encoder output, state_h (1 x lstm_units), state_c (1 x lstm_units)]
                                                    output: [probs, new_state_h, new_state_c]
                fitted_tokenizer: fitted tokenizer to convert predicted idx in words
                special_tokens: tuple - start-of-seq token and end-of-seq token
            :return
                list of predicted text
    '''
    max_seq_lenght = X_test.shape[1]
    predicted = []
    for x in X_test:
        x = x.reshape(1,-1)

        ## encode X
        encoder_out, state_h, state_c = encoder_model.predict(x)

        ## prepare loop
        y_in = np.array([fitted_tokenizer.word_index[special_tokens[0]]])
        predicted_text = ""
        stop = False

        while not stop:
            ## predict dictionary probability distribution
            probs, new_state_h, new_state_c = decoder_model.predict([y_in, encoder_out, state_h, state_c])
            ## get predicted word
            voc_idx = np.argmax(probs[0,-1,:])
            pred_word = fitted_tokenizer.index_word[voc_idx] if voc_idx != 0 else special_tokens[1]
            ## check stop
            if (pred_word != special_tokens[1]) and (len(predicted_text.split()) < max_seq_lenght):
                predicted_text = predicted_text +" "+ pred_word
            else:
                stop = True
            ## next
            y_in = np.array([voc_idx])
            state_h, state_c = new_state_h, new_state_c

        predicted_text = predicted_text.replace(special_tokens[0],"").strip()
        predicted.append(predicted_text)

    return predicted



###############################################################################
#                     TEXT SUMMARIZATION                                      #
###############################################################################

def summary_evaluate_summary(y_test, predicted):
    '''.
    Doc::
            
            Calculate ROUGE score.
            Doc::
        
                y_test: string or list
                predicted: string or list
    '''
    rouge_score = rouge.Rouge()
    scores = rouge_score.get_scores(y_test, predicted, avg=True)
    score_1 = round(scores['rouge-1']['f'], 2)
    score_2 = round(scores['rouge-2']['f'], 2)
    score_L = round(scores['rouge-l']['f'], 2)
    print("rouge1:", score_1, "| rouge2:", score_2, "| rougeL:", score_2,
          "--> avg rouge:", round(np.mean([score_1,score_2,score_L]), 2))



def summary_textrank(corpus, ratio=0.2):
    '''.
    Doc::
            
            Summarizes corpus with TextRank.
            Doc::
        
                corpus: list - df["text"]
                ratio: length of the summary (ex. 20% of the text)
            :return
                list of summaries
    '''
    if type(corpus) is str:
        corpus = [corpus]
    lst_summaries = [gensim.summarization.summarize(txt, ratio=ratio) for txt in corpus]
    return lst_summaries



def summary_bart(corpus, ratio=0.2):
    '''.
    Doc::
            
            Summarizes corpus with Bart.
            Doc::
        
                corpus: list - df["text"]
                ratio: length of the summary (ex. 20% of the text)
            :return
                list of summaries
    '''
    import transformers
    nlp = transformers.pipeline("summarization")
    lst_summaries = [nlp(txt, max_length=int(len(txt.split())*ratio),
                              min_length=int(len(txt.split())*ratio)
                        )[0]["summary_text"].replace(" .", ".")
                     for txt in corpus]
    return lst_summaries




if 'utils':

    def pd_train_test_split(df, y, test_size=0.3, shuffle=False):
        '''
        Split the dataframe into train / test
        '''
        dtf_train, dtf_test = model_selection.train_test_split(df, test_size=test_size, shuffle=shuffle)
        print("X_train shape:", dtf_train.drop(y, axis=1).shape, "| X_test shape:", dtf_test.drop(y, axis=1).shape)
        print("y:")
        for i in dtf_train["y"].value_counts(normalize=True).index:
            print(" ", i, " -->  train:", round(dtf_train["y"].value_counts(normalize=True).loc[i], 2),
                              "| test:", round(dtf_test["y"].value_counts(normalize=True).loc[i], 2))
        print(dtf_train.shape[1], "features:", dtf_train.drop(y, axis=1).columns.to_list())
        return dtf_train, dtf_test



    def pd_colstring_encode(df, column):
        '''
        Transform an array of strings into an array of int.
        '''
        df[column+"_id"] = df[column].factorize(sort=True)[0]
        dic_class_mapping = dict( df[[column+"_id",column]].drop_duplicates().sort_values(column+"_id").values )
        return df, dic_class_mapping



    def metric_classifier_multilabel_show(y_test, predicted, predicted_prob, figsize=(15,5)):
        '''
        Evaluates a model performance.
        Doc::

            y_test: array
            predicted: array
            predicted_prob: array
            figsize: tuple - plot setting
        '''
        classes = np.unique(y_test)
        y_test_array = pd.get_dummies(y_test, drop_first=False).values

        ## Accuracy, Precision, Recall
        accuracy = metrics.accuracy_score(y_test, predicted)
        auc = metrics.roc_auc_score(y_test, predicted_prob, multi_class="ovr")
        print("Accuracy:",  round(accuracy,2))
        print("Auc:", round(auc,2))
        print("Detail:")
        print(metrics.classification_report(y_test, predicted))

        ## Plot confusion matrix
        cm = metrics.confusion_matrix(y_test, predicted)
        fig, ax = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', ax=ax, cmap=plt.cm.Blues, cbar=False)
        ax.set(xlabel="Pred", ylabel="True", xticklabels=classes, yticklabels=classes, title="Confusion matrix")
        plt.yticks(rotation=0)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=figsize)
        ## Plot roc
        for i in range(len(classes)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test_array[:,i], predicted_prob[:,i])
            ax[0].plot(fpr, tpr, lw=3, label='{0} (area={1:0.2f})'.format(classes[i], metrics.auc(fpr, tpr)))
        ax[0].plot([0,1], [0,1], color='navy', lw=3, linestyle='--')
        ax[0].set(xlim=[-0.05,1.0], ylim=[0.0,1.05], xlabel='False Positive Rate',
                  ylabel="True Positive Rate (Recall)", title="Receiver operating characteristic")
        ax[0].legend(loc="lower right")
        ax[0].grid(True)

        ## Plot precision-recall curve
        for i in range(len(classes)):
            precision, recall, thresholds = metrics.precision_recall_curve(y_test_array[:,i], predicted_prob[:,i])
            ax[1].plot(recall, precision, lw=3, label='{0} (area={1:0.2f})'.format(classes[i], metrics.auc(recall, precision)))
        ax[1].set(xlim=[0.0,1.05], ylim=[0.0,1.05], xlabel='Recall', ylabel="Precision", title="Precision-Recall curve")
        ax[1].legend(loc="best")
        ax[1].grid(True)
        plt.show()




###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
