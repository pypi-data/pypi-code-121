# -*- coding: utf-8 -*-
MNAME = "utilmy.nlp.util_embedding"
""" utils for text emedding


https://github.com/fidelity/PhraseExtraction




"""
import os,sys, collections, random, numpy as np,  glob, pandas as pd
from box import Box ; from copy import deepcopy ;from tqdm import tqdm

## for plotting
import matplotlib.pyplot as plt; seaborn as sns

## for sentiment
from textblob import TextBlob

## for machine learning
from sklearn import preprocessing, model_selection, feature_extraction, feature_selection, metrics, manifold, naive_bayes, pipeline


#############################################################################################
from utilmy import log, log2, help_create
def help():
    print( help_create(__file__) )



#############################################################################################
def test_all():
    log(MNAME)
    test1()
    # test2()


def test1():
    pass



def test_text_get_embedding():
  """ retrieve text embedding from various models
       https://github.com/arita37/textwiser

  """
  # Conceptually, TextWiser is composed of an Embedding, potentially with a pretrained model,
  # that can be chained into zero or more Transformations
  from textwiser import TextWiser, Embedding, Transformation, WordOptions, PoolOptions

  # Data
  documents = ["Some document", "More documents. Including multi-sentence documents."]

  # Model: TFIDF `min_df` parameter gets passed to sklearn automatically
  emb = TextWiser(Embedding.TfIdf(min_df=1))

  # Model: TFIDF followed with an NMF + SVD
  emb = TextWiser(Embedding.TfIdf(min_df=1), [Transformation.NMF(n_components=30), Transformation.SVD(n_components=10)])

  # Model: Word2Vec with no pretraining that learns from the input data
  emb = TextWiser(Embedding.Word(word_option=WordOptions.word2vec, pretrained=None), Transformation.Pool(pool_option=PoolOptions.min))

  # Model: BERT with the pretrained bert-base-uncased embedding
  emb = TextWiser(Embedding.Word(word_option=WordOptions.bert), Transformation.Pool(pool_option=PoolOptions.first))

  # Features
  vecs = emb.fit_transform(documents)



def test_text_sentence_extraction():
  """ Extract Key phrases from Text as summary
     pip install PhraseExtraction
    https://github.com/fidelity/PhraseExtraction

  """
  ###### It contains text pre-processing methods. The sample code for usage is provided below.

  # Load stopwords
  # Load stopwords
  from phraseextraction.utility import nltk_stopwords, spacy_stopwords, gensim_stopwords, smart_stopwords, all_stopwords
  print(nltk_stopwords, spacy_stopwords, gensim_stopwords, smart_stopwords, all_stopwords)

  # Remove Non-ASCII characters/symbols
  from phraseextraction.utility import filter_nonascii
  nonascii_text = filter_nonascii(text)

  # Remove punctuation & digits
  from phraseextraction.utility import remove_punct_num
  text_with_punc_digit_removed = remove_punct_num(text, remove_num=True)

  # Remove Non-english words (junks like website, url etc)
  from phraseextraction.utility import remove_non_english
  english_text = remove_non_english(text)

  # Remove entities using list of entities to removes
  from phraseextraction import remove_named_entities
  ent_list=['DATE','GPE','PERSON','CARDINAL','ORDINAL','LAW','LOC','PERCENT','QUANTITY']
  ents_removed_text = utility.remove_named_entities(text, ent_list)

  # Check if a token is digit
  from phraseextraction import is_number
  num_bool = is_number(token)


  ###### Candidate Phrase Generation ########################################
  from rule import grammar
  from candidate_generation import Grammar_Keyphrase
  grammar_model = Grammar_Keyphrase(grammar)
  key_phrases = grammar_model.get_keyphrases(text)



  from candidate_generation import Rake_Keyphrase
  # ngram_ : The lower and upper boundary of the range of n-values for different word n-grams (2,4) means bi, tri and quad grams only.
  rake_model = Rake_Keyphrase(ngram_ = (2,4), custom_stop_words=custom_stop_words)
  key_phrases = rake_model.get_keyphrases(text)


  ### Phrase Ranking
  #### RAKE/Degree Scoring: Method can take RAKE or Degree scoring. 
  from ranking import RakeRank
  rakeRank = ranking.RakeRank(method='degree')
  ranked_df = rakeRank.rank_phrases(key_phrases)

  ### TextRank: TextRank has two methods: Window based (WindowSize) 
  from ranking import TextRank
  TR_WordEmbedding= ranking.TextRank(method= "WordEmbeddings")
  ranked_df = TR_WordEmbedding.rank_phrases(key_phrases)



#########Core #######################################################################################














###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
















=======
# -*- coding: utf-8 -*-
MNAME = "utilmy.nlp.util_embedding"
HELP = """ utils for text emedding


https://github.com/fidelity/PhraseExtraction




"""
import os,sys, collections, random, numpy as np,  glob, pandas as pd
from box import Box ; from copy import deepcopy ;from tqdm import tqdm

## for plotting
import matplotlib.pyplot as plt; seaborn as sns

## for sentiment
from textblob import TextBlob

## for machine learning
from sklearn import preprocessing, model_selection, feature_extraction, feature_selection, metrics, manifold, naive_bayes, pipeline


#############################################################################################
from utilmy import log, log2, help_create
def help():
    print( HELP + help_create(__file__) )



#############################################################################################
def test_all():
    log(MNAME)
    test1()
    # test2()


def test1():
    pass



def test_text_get_embedding():
  """ retrieve text embedding from various models
       https://github.com/arita37/textwiser

  """
  # Conceptually, TextWiser is composed of an Embedding, potentially with a pretrained model,
  # that can be chained into zero or more Transformations
  from textwiser import TextWiser, Embedding, Transformation, WordOptions, PoolOptions

  # Data
  documents = ["Some document", "More documents. Including multi-sentence documents."]

  # Model: TFIDF `min_df` parameter gets passed to sklearn automatically
  emb = TextWiser(Embedding.TfIdf(min_df=1))

  # Model: TFIDF followed with an NMF + SVD
  emb = TextWiser(Embedding.TfIdf(min_df=1), [Transformation.NMF(n_components=30), Transformation.SVD(n_components=10)])

  # Model: Word2Vec with no pretraining that learns from the input data
  emb = TextWiser(Embedding.Word(word_option=WordOptions.word2vec, pretrained=None), Transformation.Pool(pool_option=PoolOptions.min))

  # Model: BERT with the pretrained bert-base-uncased embedding
  emb = TextWiser(Embedding.Word(word_option=WordOptions.bert), Transformation.Pool(pool_option=PoolOptions.first))

  # Features
  vecs = emb.fit_transform(documents)



def test_text_sentence_extraction():
  """ Extract Key phrases from Text as summary
     pip install PhraseExtraction
    https://github.com/fidelity/PhraseExtraction

  """
  ###### It contains text pre-processing methods. The sample code for usage is provided below.

  # Load stopwords
  # Load stopwords
  from phraseextraction.utility import nltk_stopwords, spacy_stopwords, gensim_stopwords, smart_stopwords, all_stopwords
  print(nltk_stopwords, spacy_stopwords, gensim_stopwords, smart_stopwords, all_stopwords)

  # Remove Non-ASCII characters/symbols
  from phraseextraction.utility import filter_nonascii
  nonascii_text = filter_nonascii(text)

  # Remove punctuation & digits
  from phraseextraction.utility import remove_punct_num
  text_with_punc_digit_removed = remove_punct_num(text, remove_num=True)

  # Remove Non-english words (junks like website, url etc)
  from phraseextraction.utility import remove_non_english
  english_text = remove_non_english(text)

  # Remove entities using list of entities to removes
  from phraseextraction import remove_named_entities
  ent_list=['DATE','GPE','PERSON','CARDINAL','ORDINAL','LAW','LOC','PERCENT','QUANTITY']
  ents_removed_text = utility.remove_named_entities(text, ent_list)

  # Check if a token is digit
  from phraseextraction import is_number
  num_bool = is_number(token)


  ###### Candidate Phrase Generation ########################################
  from rule import grammar
  from candidate_generation import Grammar_Keyphrase
  grammar_model = Grammar_Keyphrase(grammar)
  key_phrases = grammar_model.get_keyphrases(text)



  from candidate_generation import Rake_Keyphrase
  # ngram_ : The lower and upper boundary of the range of n-values for different word n-grams (2,4) means bi, tri and quad grams only.
  rake_model = Rake_Keyphrase(ngram_ = (2,4), custom_stop_words=custom_stop_words)
  key_phrases = rake_model.get_keyphrases(text)


  ### Phrase Ranking
  #### RAKE/Degree Scoring: Method can take RAKE or Degree scoring. 
  from ranking import RakeRank
  rakeRank = ranking.RakeRank(method='degree')
  ranked_df = rakeRank.rank_phrases(key_phrases)

  ### TextRank: TextRank has two methods: Window based (WindowSize) 
  from ranking import TextRank
  TR_WordEmbedding= ranking.TextRank(method= "WordEmbeddings")
  ranked_df = TR_WordEmbedding.rank_phrases(key_phrases)



#########Core #######################################################################################














###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
















