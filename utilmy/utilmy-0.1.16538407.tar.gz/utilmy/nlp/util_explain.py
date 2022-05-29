# -*- coding: utf-8 -*-
MNAME = "utilmy.nlp_util_explain"
""" utils for NL explanation






"""
import os, sys, glob, time,gc, datetime, numpy as np, pandas as pd
from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box






#############################################################################################
from utilmy import log, log2

def help():
    """function help"""
    from utilmy import help_create
    print( help_create(__file__) )



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
def explainer_lime(model, y_train, txt_instance, top=10):
    '''
    Use lime to build an a explainer.
    Doc::

        model: pipeline with vectorizer and classifier
        Y_train: array
        txt_instance: string - raw text
        top: num - top features to display
    :return
        dtf with explanations
    '''
    explainer = lime_text.LimeTextExplainer(class_names=np.unique(y_train))
    explained = explainer.explain_instance(txt_instance, model.predict_proba, num_features=top)
    explained.show_in_notebook(text=txt_instance, predict_proba=False)
    dtf_explainer = pd.DataFrame(explained.as_list(), columns=['feature','effect'])
    return dtf_explainer





def explainer_attention(model, tokenizer, txt_instance, lst_ngrams_detectors=[], top=5, figsize=(5,3)):
    '''
    Takes the weights of an Attention layer and builds an explainer.
    Doc::

        model: model instance (after fitting)
        tokenizer: keras tokenizer (after fitting)
        txt_instance: string - raw text
        lst_ngrams_detectors: list - [bigram and trigram models], if empty doesn't detect common n-grams
        top: num - top features to display
    :return
        text html, it can be visualized on notebook with display(HTML(text))
    '''
    ## preprocess txt_instance
    lst_corpus = utils_preprocess_ngrams([re.sub(r'[^\w\s]', '', txt_instance.lower().strip())], lst_ngrams_detectors=lst_ngrams_detectors)
    X_instance = kprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences(lst_corpus),
                                                    maxlen=int(model.input.shape[1]), padding="post", truncating="post")

    ## get attention weights
    layer = [layer for layer in model.layers if "attention" in layer.name][0]
    func = K.function([model.input], [layer.output])
    weights = func(X_instance)[0]
    weights = np.mean(weights, axis=2).flatten()

    ## rescale weights, remove null vector, map word-weight
    weights = preprocessing.MinMaxScaler(feature_range=(0,1)).fit_transform(np.array(weights).reshape(-1,1)).reshape(-1)
    weights = [weights[n] for n,idx in enumerate(X_instance[0]) if idx != 0]
    dic_word_weigth = {word:weights[n] for n,word in enumerate(lst_corpus[0]) if word in tokenizer.word_index.keys()}

    ## plot
    if len(dic_word_weigth) > 0:
        dtf = pd.DataFrame.from_dict(dic_word_weigth, orient='index', columns=["score"])
        dtf.sort_values(by="score", ascending=True).tail(top).plot(kind="barh", legend=False, figsize=figsize).grid(axis='x')
        plt.show()
    else:
        print("--- No word recognized ---")

    ## return html visualization (yellow:255,215,0 | blue:100,149,237)
    text = []
    for word in lst_corpus[0]:
        weight = dic_word_weigth.get(word)
        if weight is not None:
            text.append('<b><span style="background-color:rgba(100,149,237,' + str(weight) + ');">' + word + '</span></b>')
        else:
            text.append(word)
    text = ' '.join(text)
    return text



def explainer_shap(model, X_train, X_instance, dic_vocabulary, class_names, top=10):
    '''
    Use shap to build an a explainer (works only if model has binary_crossentropy).
    Doc::

        model: model instance (after fitting)
        X_train: array
        X_instance: array of size n (n,)
        dic_vocabulary: dict - {"word":0, ...}
        class_names: list - labels
        top: num - top features to display
    :return
        dtf with explanations
    '''
    explainer = shap.DeepExplainer(model, data=X_train[:100])
    shap_values = explainer.shap_values(X_instance.reshape(1,-1))
    inv_dic_vocabulary = {v:k for k,v in dic_vocabulary.items()}
    X_names = [inv_dic_vocabulary[idx] if idx in dic_vocabulary.values() else " " for idx in X_instance]
    shap.summary_plot(shap_values, feature_names=X_names, class_names=class_names, plot_type="bar")




def explainer_similarity_classif(tokenizer, nlp, dic_clusters, txt_instance, token_level=False, top=5, figsize=(20,10)):
    '''
    Plot a text instance into a 2d vector space and compute similarity.
    Doc::

        tokenizer: transformers tokenizer
        nlp: transformers bert
        dic_clusters: dict - dict - {0:lst_words, 1:lst_words, ...}
        txt_instance: string - raw text
        token_level: bool - if True the text is broken down into tokens otherwise the mean vector is taken
        top: num - top similarity to display
    '''
    ## create embedding Matrix
    y = np.concatenate([embedding_bert(v, tokenizer, nlp) for v in dic_clusters.values()])
    X = embedding_bert(txt_instance, tokenizer, nlp) if token_level is True else embedding_bert(txt_instance, tokenizer, nlp).mean(0).reshape(1,-1)
    M = np.concatenate([y,X])

    ## pca
    pca = manifold.TSNE(perplexity=40, n_components=2, init='pca')
    M = pca.fit_transform(M)
    y, X = M[:len(y)], M[len(y):]

    ## create dtf clusters
    dtf = pd.DataFrame()
    for k,v in dic_clusters.items():
        size = len(dtf) + len(v)
        dtf_group = pd.DataFrame(y[len(dtf):size], columns=["x","y"], index=v)
        dtf_group["cluster"] = k
        dtf = dtf.append(dtf_group)

    ## plot clusters
    fig, ax = plt.subplots(figsize=figsize)
    sns.scatterplot(data=dtf, x="x", y="y", hue="cluster", ax=ax)
    ax.legend().texts[0].set_text(None)
    ax.set(xlabel=None, ylabel=None, xticks=[], xticklabels=[], yticks=[], yticklabels=[])
    for i in range(len(dtf)):
        ax.annotate(dtf.index[i], xy=(dtf["x"].iloc[i],dtf["y"].iloc[i]), xytext=(5,2), textcoords='offset points', ha='right', va='bottom')

    ## add txt_instance
    if token_level is True:
        tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(txt_instance))[1:-1]
        dtf = pd.DataFrame(X, columns=["x","y"], index=tokens)
        dtf = dtf[~dtf.index.str.contains("#")]
        dtf = dtf[dtf.index.str.len() > 1]
        X = dtf.values
        ax.scatter(x=dtf["x"], y=dtf["y"], c="red")
        for i in range(len(dtf)):
            ax.annotate(dtf.index[i], xy=(dtf["x"].iloc[i],dtf["y"].iloc[i]), xytext=(5,2), textcoords='offset points', ha='right', va='bottom')
    else:
        ax.scatter(x=X[0][0], y=X[0][1], c="red", linewidth=10)
        ax.annotate("x", xy=(X[0][0],X[0][1]), ha='center', va='center', fontsize=25)

    ## calculate similarity
    sim_matrix = utils_cosine_sim(X,y)

    ## add top similarity
    for row in range(sim_matrix.shape[0]):
        ### sorted {keyword:score}
        dic_sim = {n:sim_matrix[row][n] for n in range(sim_matrix.shape[1])}
        dic_sim = {k:v for k,v in sorted(dic_sim.items(), key=lambda item:item[1], reverse=True)}
        ### plot lines
        for k in dict(list(dic_sim.items())[0:top]).keys():
            p1 = [X[row][0], X[row][1]]
            p2 = [y[k][0], y[k][1]]
            ax.plot([p1[0],p2[0]], [p1[1],p2[1]], c="red", alpha=0.5)
    plt.show()































###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


