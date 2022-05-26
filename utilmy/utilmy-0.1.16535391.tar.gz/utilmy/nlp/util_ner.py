# -*- coding: utf-8 -*-
MNAME = "utilmy.nlp.util_ner"
""" utils for Name Entity Recognition




"""
import os, sys, glob, time,gc, datetime, numpy as np, pandas as pd
from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box


import spacy

#############################################################################################
from utilmy import log, log2,help_create

def help():
    """function help"""
    print( help_create(MNAME) )



#############################################################################################
def test_all() -> None:
    """function test_all

    """
    log(MNAME)
    test1()
    test2()


def test1() -> None:
    """function test1
    Args:
    Returns:

    """
    pass


def test2() -> None:
    """function test2
    Args:
    Returns:

    """
    pass


#############################################################################################
#                            NER                                              #

def ner_spacy_displacy(txt, ner=None, lst_tag_filter=None, title=None, serve=False):
    '''
    Display the spacy NER model.
    Doc::

        txt: string - text input for the model.
        model: string - "en_core_web_lg", "en_core_web_sm", "xx_ent_wiki_sm"
        lst_tag_filter: list or None - example ["ORG", "GPE", "LOC"], None for all tags
        title: str or None
    '''
    ner = spacy.load("en_core_web_lg") if ner is None else ner
    doc = ner(txt)
    doc.user_data["title"] = title
    if serve == True:
        spacy.displacy.serve(doc, style="ent", options={"ents":lst_tag_filter})
    else:
        spacy.displacy.render(doc, style="ent", options={"ents":lst_tag_filter})



def ner_spacy_text(txt, ner=None, lst_tag_filter=None, grams_join="_"):
    '''
    Find entities in text, replace strings with tags and extract tags:
        Donald Trump --> Donald_Trump
        [Donald Trump, PERSON]
    '''
    ## apply model
    ner = spacy.load("en_core_web_lg") if ner is None else ner
    entities = ner(txt).ents

    ## tag text
    tagged_txt = txt
    for tag in entities:
        if (lst_tag_filter is None) or (tag.label_ in lst_tag_filter):
            try:
                tagged_txt = re.sub(tag.text, grams_join.join(tag.text.split()), tagged_txt) #it breaks with wild characters like *+
            except Exception as e:
                continue

    ## extract tags list
    if lst_tag_filter is None:
        lst_tags = [(tag.text, tag.label_) for tag in entities]  #list(set([(word.text, word.label_) for word in ner(x).ents]))
    else:
        lst_tags = [(word.text, word.label_) for word in entities if word.label_ in lst_tag_filter]

    return tagged_txt, lst_tags



def ner_features(lst_dics_tuples, tag):
    '''
    Creates columns
        lst_dics_tuples: [{('Texas','GPE'):1}, {('Trump','PERSON'):3}]
        tag: string - 'PERSON'
    :return
        int
    '''
    if len(lst_dics_tuples) > 0:
        tag_type = []
        for dic_tuples in lst_dics_tuples:
            for tuple in dic_tuples:
                type, n = tuple[1], dic_tuples[tuple]
                tag_type = tag_type + [type]*n
                dic_counter = collections.Counter()
                for x in tag_type:
                    dic_counter[x] += 1
        return dic_counter[tag]   #pd.DataFrame([dic_counter])
    else:
        return 0



def ner_spacy_add_tag_features(data, column, ner=None, lst_tag_filter=None, grams_join="_", create_features=True):
    '''
    Apply spacy NER model and add tag features.
    Doc::

        dtf: dataframe - dtf with a text column
        column: string - name of column containing text
        ner: spacy object - "en_core_web_lg", "en_core_web_sm", "xx_ent_wiki_sm"
        lst_tag_filter: list - ["ORG","PERSON","NORP","GPE","EVENT", ...]. If None takes all
        grams_join: string - "_", " ", or more (ex. "new york" --> "new_york")
        create_features: bool - create columns with category features
    :return
        dtf
    '''
    ner = spacy.load("en_core_web_lg") if ner is None else ner
    dtf = data.copy()

    ## tag text and exctract tags
    print("--- tagging ---")
    dtf[[column+"_tagged", "tags"]] = dtf[[column]].apply(lambda x: utils_ner_text(x[0], ner, lst_tag_filter, grams_join),
                                                          axis=1, result_type='expand')

    ## put all tags in a column
    print("--- counting tags ---")
    dtf["tags"] = dtf["tags"].apply(lambda x: list_topk(x, top=None))

    ## extract features
    if create_features == True:
        print("--- creating features ---")
        ### features set
        tags_set = []
        for lst in dtf["tags"].tolist():
            for dic in lst:
                for k in dic.keys():
                    tags_set.append(k[1])
        tags_set = list(set(tags_set))
        ### create columns
        for feature in tags_set:
            dtf["tags_"+feature] = dtf["tags"].apply(lambda x: ner_features(x, feature))
    return dtf



def ner_freq_spacy_tag(tags, top=30, figsize=(10,5)):
    '''
    Compute frequency of spacy tags.
    '''
    tags_list = tags.sum()
    map_lst = list(map(lambda x: list(x.keys())[0], tags_list))
    dtf_tags = pd.DataFrame(map_lst, columns=['tag','type'])
    dtf_tags["count"] = 1
    dtf_tags = dtf_tags.groupby(['type','tag']).count().reset_index().sort_values("count", ascending=False)
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle("Top frequent tags", fontsize=12)
    sns.barplot(x="count", y="tag", hue="type", data=dtf_tags.iloc[:top,:], dodge=False, ax=ax)
    ax.set(ylabel=None)
    ax.grid(axis="x")
    plt.show()
    return dtf_tags



def ner_spacy_retrain(train_data, output_dir, model="blank", n_iter=100):
    '''
    Retrain spacy NER model with new tags.
    Doc::

        train_data: list [
                ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
                ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
            ]
        output_dir: string - path of directory to save model
        model: string - "blanck" or "en_core_web_lg", ...
        n_iter: num - number of iteration
    '''
    try:
        ## prepare data
#        train_data = []
#        for name in lst:
#            frase = "ciao la mia azienda si chiama "+name+" e fa business"
#            tupla = (frase, {"entities":[(30, 30+len(name), tag_type)]})
#            train_data.append(tupla)

        ## load model
        if model == "blank":
            ner_model = spacy.blank("en")
        else:
            ner_model = spacy.load(model)

        ## create a new pipe
        if "ner" not in ner_model.pipe_names:
            new_pipe = ner_model.create_pipe("ner")
            ner_model.add_pipe(new_pipe, last=True)
        else:
            new_pipe = ner_model.get_pipe("ner")

        ## add label
        for _, annotations in train_data:
            for ent in annotations.get("entities"):
                new_pipe.add_label(ent[2])

        ## train
        other_pipes = [pipe for pipe in ner_model.pipe_names if pipe != "ner"] ###ignora altre pipe
        with ner_model.disable_pipes(*other_pipes):
            print("--- Training spacy ---")
            if model == "blank":
                ner_model.begin_training()
            for n in range(n_iter):
                random.shuffle(train_data)
                losses = {}
                batches = spacy.util.minibatch(train_data, size=spacy.util.compounding(4., 32., 1.001)) ###batch up data using spaCy's minibatch
                for batch in batches:
                    texts, annotations = zip(*batch)
                    ner_model.update(docs=texts, golds=annotations, drop=0.5, losses=losses)  ###update

        ## test the trained model
        print("--- Test new model ---")
        for text, _ in train_data:
            doc = ner_model(text)
            print([(ent.text, ent.label_) for ent in doc.ents])

        ## save model to output directory
        ner_model.to_disk(output_dir)
        print("Saved model to", output_dir)

    except Exception as e:
        print("--- got error ---")
        print(e)



if 'utils':
    def list_topk(lst, top:int=None):
        '''
        Counts the elements in a list.
        Doc::

            lst: list
            top: num - number of top elements to return
        :return
            lst_top - list with top elements
        '''
        dic_counter = collections.Counter()
        for x in lst:
            dic_counter[x] += 1
        dic_counter = collections.OrderedDict(sorted(dic_counter.items(), key=lambda x: x[1], reverse=True))
        lst_top = [ {key:value} for key,value in dic_counter.items() ]
        if top is not None:
            lst_top = lst_top[:top]
        return lst_top


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


