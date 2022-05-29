import re
import pandas as pd
import bs4
import requests
import spacy
from spacy import displacy
nlp = spacy.load('en_core_web_sm')
from spacy.matcher import Matcher 
from spacy.tokens import Span 
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import networkx as nx
import matplotlib.pyplot as plt
from summarizer.sbert import SBertSummarizer
from tqdm import tqdm
import pandas as pd
from pymed import PubMed
import os
import gensim
from gensim.utils import simple_preprocess
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import pyLDAvis.gensim_models
import pickle 
import pyLDAvis
stop_words = stopwords.words('english')
stop_words.extend(stop_words)
import gensim.corpora as corpora
from pprint import pprint
pd.set_option('display.max_colwidth', 200)


## ===================================================
## ===================================================
## ===================================================
## ===================================================


stop_words = '''
i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does did doing a an the and but if or because as until while of at by for with about against between into through during before after above below to from up down in out on off over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very can will just don should now
'''
stop_words = stop_words.split(" ")
stop_words

## ===================================================
## ===================================================
## ===================================================
## ===================================================


def get_entities(sent):
  ## chunk 1
  ent1 = ""
  ent2 = ""

  prv_tok_dep = ""    # dependency tag of previous token in the sentence
  prv_tok_text = ""   # previous token in the sentence

  prefix = ""
  modifier = ""

  #############################################################
  
  for tok in nlp(sent):
    ## chunk 2
    # if token is a punctuation mark then move on to the next token
    if tok.dep_ != "punct":
      # check: token is a compound word or not
      if tok.dep_ == "compound":
        prefix = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          prefix = prv_tok_text + " "+ tok.text
      
      # check: token is a modifier or not
      if tok.dep_.endswith("mod") == True:
        modifier = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          modifier = prv_tok_text + " "+ tok.text
      
      ## chunk 3
      if tok.dep_.find("subj") == True:
        ent1 = modifier +" "+ prefix + " "+ tok.text
        prefix = ""
        modifier = ""
        prv_tok_dep = ""
        prv_tok_text = ""      

      ## chunk 4
      if tok.dep_.find("obj") == True:
        ent2 = modifier +" "+ prefix +" "+ tok.text
        
      ## chunk 5  
      # update variables
      prv_tok_dep = tok.dep_
      prv_tok_text = tok.text
  #############################################################

  return [ent1.strip(), ent2.strip()]



def get_relation(sent):
  doc = nlp(sent)
  #We initialise matcher with the vocab
  matcher = Matcher(nlp.vocab)
  #Defining the pattern
  pattern = [{'DEP':'ROOT'},{'DEP':'prep','OP':'?'},{'DEP':'agent','OP':'?'},{'DEP':'ADJ','OP':'?'}]
  #Adding the pattern to the matcher
  matcher.add("matcher_1",None,pattern)
  #Applying the matcher to the doc
  matches = matcher(doc)

  #The matcher returns a list of (match_id, start, end). The start to end in our doc contains the relation. We capture that relation in a variable called span
  span = doc[matches[0][1]:matches[0][2]]
  return span.text




def draw_kg1(pairs):
    G=nx.from_pandas_edgelist(pairs, "source", "target", 
                edge_attr="relation", create_using=nx.MultiDiGraph())
    plt.figure(figsize=(10,10))
    pos = nx.spring_layout(G)
    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
    plt.savefig("Simple_Knowledge_Graph_part.png")
    plt.close()


def draw_kg2(pairs):
    k_graph = nx.from_pandas_edgelist(pairs, 'source', 'target',
            create_using=nx.MultiDiGraph())
    node_deg = nx.degree(k_graph)
    layout = nx.spring_layout(k_graph, k=0.25, iterations=80)
    plt.figure(num=None, figsize=(10, 10), dpi=80)
    nx.draw_networkx(
        k_graph,
        node_size=[int(deg[1]) * 500 for deg in node_deg],
        arrowsize=20,
        linewidths=1.5,
        pos=layout,
        edge_color='red',
        edgecolors='black',
        node_color='white',
        )
    labels = dict(zip(list(zip(pairs.source, pairs.target)),
                  pairs['relation'].tolist()))
    nx.draw_networkx_edge_labels(k_graph, pos=layout, edge_labels=labels,
                                 font_color='red')
    plt.axis('off')
    plt.savefig("high_resolution_Knowledge_Graph.png")
    plt.close()


def analyze_tex(text):

    entity_pairs = []
    for i in tqdm(text):
      entity_pairs.append(get_entities(i))
    relations = [get_relation(i) for i in tqdm(text)]  

    source = [i[0] for i in entity_pairs]
    target = [i[1] for i in entity_pairs]

    kg_df = pd.DataFrame({'source':source, 'target':target, 'relation':relations})
    kg_df.drop(kg_df.index[kg_df['source'] == ''], inplace=True) 
    kg_df.drop(kg_df.index[kg_df['target'] == ''], inplace=True) 
    kg_df.drop(kg_df.index[kg_df['relation'] == ''], inplace=True)
    return kg_df, len(entity_pairs)



def sent_to_words(sentences):
    for sentence in sentences:
        # deacc=True removes punctuations
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))
def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) 
             if word not in stop_words] for doc in texts]




def t_model(text, num_topics):
    data = text.split(".")
    data_words = list(sent_to_words(data))
    data_words = remove_stopwords(data_words)
    id2word = corpora.Dictionary(data_words)
    texts = data_words
    corpus = [id2word.doc2bow(text) for text in texts]


    num_topics = num_topics

    lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                          id2word=id2word,
                                          num_topics=num_topics)

    pprint(lda_model.print_topics())
    doc_lda = lda_model[corpus]
    LDAvis_data_filepath = os.path.join('./'+str(num_topics))
    if 1 == 1:
        LDAvis_prepared = pyLDAvis.gensim_models.prepare(lda_model, corpus, id2word)
        with open(LDAvis_data_filepath, 'wb') as f:
            pickle.dump(LDAvis_prepared, f)
    with open(LDAvis_data_filepath, 'rb') as f:
        LDAvis_prepared = pickle.load(f)
    pyLDAvis.save_html(LDAvis_prepared, './'+ "Topic_Model_" +str(num_topics) +'.html')




## ===================================================
## ===================================================
## ===================================================
## ===================================================





def all_in_one(query, max_results=5, summery_ratio=.3, num_topics=5):

    model = SBertSummarizer('paraphrase-MiniLM-L6-v2')
    pubmed = PubMed(tool="MyTool", email="my@email.address")
    results = pubmed.query(query, max_results=max_results)
    results = list(results)

    text = ''
    os.system("mkdir 'Open Medical'") 
    os.chdir("Open Medical")
    os.system("mkdir '{}'".format(query)) 
    os.chdir("{}".format(query))
    for i in range(max_results):
      try:     
            sum_dic = {}
            text = results[i].abstract + "\n"
            os.system("mkdir '{}'".format(results[i].title))
            os.chdir(results[i].title)
            txt1 = text.split(".")
            txt1 = [i for i in txt1 if len(i)>10]
            kg_df, _ = analyze_tex(txt1)
            summery = model(results[i].abstract, ratio=summery_ratio)
            sum_dic[results[i].abstract] = [summery]
            Summarized_data = pd.DataFrame(sum_dic.items(), columns=['Original', 'Summarized'])
            Summarized_data.to_csv("Summary.csv".format(results[i].title))
            draw_kg1(kg_df) 
            draw_kg2(kg_df)
            t_model(results[i].abstract,num_topics)
            os.chdir("..")
      except:
            pass 
    os.chdir("../..")





