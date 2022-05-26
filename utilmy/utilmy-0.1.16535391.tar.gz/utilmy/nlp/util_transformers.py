# -*- coding: utf-8 -*-
MNAME = "utilmy."
""" utils for




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












###############################################################################
#                      BERT (TRANSFORMERS LANGUAGE MODEL)                     #
###############################################################################

def utils_bert_embedding(txt, tokenizer, nlp, log=False):
    '''
    Word embedding with Bert (equivalent to nlp["word"]).
    Doc::

        txt: string
        tokenizer: transformers tokenizer
        nlp: transformers bert
    :return
        tensor sentences x words x vector (1x3x768)
    '''
    idx = tokenizer.encode(txt)
    if log is True:
        print("tokens:", tokenizer.convert_ids_to_tokens(idx))
        print("ids   :", tokenizer.encode(txt))
    idx = np.array(idx)[None,:]
    embedding = nlp(idx)
    X = np.array(embedding[0][0][1:-1])
    return X



def embedding_bert(x, tokenizer=None, nlp=None, log=False):
    '''
    Creates a feature matrix (num_docs x vector_size)
    Doc::

        x: string or list
        tokenizer: transformers tokenizer
        nlp: transformers bert
        log: bool - print tokens
    :return
        vector or matrix
    '''
    tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-uncased') if tokenizer is None else tokenizer
    nlp = transformers.TFBertModel.from_pretrained('bert-base-uncased') if nlp is None else nlp

    ## single word --> vec (size,)
    if (type(x) is str) and (len(x.split()) == 1):
        X = utils_bert_embedding(x, tokenizer, nlp, log).reshape(-1)

    ## list of words --> matrix (n, size)
    elif (type(x) is list) and (type(x[0]) is str) and (len(x[0].split()) == 1):
        X = utils_bert_embedding(x, tokenizer, nlp, log)

    ## list of lists of words --> matrix (n mean vectors, size)
    elif (type(x) is list) and (type(x[0]) is list):
        lst_mean_vecs = [utils_bert_embedding(lst, tokenizer, nlp, log).mean(0) for lst in x]
        X = np.array(lst_mean_vecs)

    ## single text --> matrix (n words, size)
    elif (type(x) is str) and (len(x.split()) > 1):
        X = utils_bert_embedding(x, tokenizer, nlp, log)

    ## list of texts --> matrix (n mean vectors, size)
    else:
        lst_mean_vecs = [utils_bert_embedding(txt, tokenizer, nlp, log).mean(0) for txt in x]
        X = np.array(lst_mean_vecs)
    return X



# def tokenize_bert(corpus, tokenizer=None, maxlen=None):
#     tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True) if tokenizer is None else tokenizer
#     maxlen = np.max([len(i.split()) for i in corpus]) if maxlen is None else maxlen
#     idx, masks, types = [],[],[]
#     for txt in corpus:
#         dic_tokens = tokenizer.encode_plus(txt, add_special_tokens=True, max_length=maxlen)
#         idx.append(dic_tokens['input_ids'])
#         masks.append(dic_tokens['special_tokens_mask'])
#         types.append(dic_tokens['token_type_ids'])
#     return [np.asarray(idx, dtype='int32'), np.asarray(masks, dtype='int32'), np.asarray(types, dtype='int32')]

def tokenize_bert(corpus, tokenizer=None, maxlen=None):
    '''
    Preprocess corpus to create features for Bert.
    Doc::

        corpus: list - dtf["text"]
        tokenizer: transformer tokenizer
        maxlen: num - max length of the padded sequence
    :return
        tensor/list with idx, masks, segments
    '''
    tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True) if tokenizer is None else tokenizer
    maxlen = np.max([len(txt.split(" ")) for txt in corpus]) if maxlen is None else maxlen
    if maxlen < 20:
        raise Exception("maxlen cannot be less than 20")
    else:
        print("maxlen:", maxlen)

    ## add special tokens: [CLS] my name is mau ##ro [SEP]
    maxqnans = np.int((maxlen-20)/2)
    corpus_tokenized = ["[CLS] "+
                        " ".join(tokenizer.tokenize(re.sub(r'[^\w\s]+|\n', '', str(txt).lower().strip()))[:maxqnans])+
                        " [SEP] " for txt in corpus]

    ## generate masks: [1, 1, 1, 1, 1, 1, 1, | (padding) 0, 0, 0, 0, 0, ...]
    masks = [[1]*len(txt.split(" ")) + [0]*(maxlen - len(txt.split(" "))) for txt in corpus_tokenized]

    ## padding
    #corpus_tokenized = kprocessing.sequence.pad_sequences(corpus_tokenized, maxlen=maxlen, dtype=object, value='[PAD]')
    txt2seq = [txt + " [PAD]"*(maxlen-len(txt.split(" "))) if len(txt.split(" ")) != maxlen else txt for txt in corpus_tokenized]

    ## generate idx: [101, 22, 35, 44, 50, 60, 102, 0, 0, 0, 0, 0, 0, ...]
    idx = [tokenizer.encode(seq.split(" ")) for seq in txt2seq]

    ## generate segments: [0, 0, 0, 0, 0, 0, 1 [SEP], 0, 0, 0, 0, 2 [SEP], 0, ...]
    segments = []
    for seq in txt2seq:
        temp, i = [], 0
        for token in seq.split(" "):
            temp.append(i)
            if token == "[SEP]":
                i += 1
        segments.append(temp)

    ## check
    genLength = set([len(seq.split(" ")) for seq in txt2seq])
    if len(genLength) != 1:
        print(genLength)
        raise Exception("--- texts are not of same size ---")

    X = [np.asarray(idx, dtype='int32'), np.asarray(masks, dtype='int32'), np.asarray(segments, dtype='int32')]
    print("created tensor idx-masks-segments:", str(len(X))+"x "+str(X[0].shape))
    return X



def fit_bert_classif(X_train, y_train, X_test, encode_y=False, dic_y_mapping=None, model=None, epochs=100, batch_size=64):
    '''
    Pre-trained Bert + Fine-tuning (transfer learning) with tf2 and transformers.
    Doc::

        X_train: array of sequence
        y_train: array of classes
        X_test: array of sequence
        model: model object - model to fit (before fitting)
        encode_y: bool - whether to encode y with a dic_y_mapping
        dic_y_mapping: dict - {0:"A", 1:"B", 2:"C"}. If None it calculates
        epochs: num - epochs to run
        batch_size: num - it does backpropagation every batch, the more the faster but it can use all the memory
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
        ### inputs
        idx = layers.Input((X_train[0].shape[1]), dtype="int32", name="input_idx")
        masks = layers.Input((X_train[1].shape[1]), dtype="int32", name="input_masks")
        segments = layers.Input((X_train[2].shape[1]), dtype="int32", name="input_segments")
        ### pre-trained bert
        bert = transformers.TFBertModel.from_pretrained("bert-base-uncased")
        bert_out, _ = bert([idx, masks, segments])
        ### fine-tuning
        x = layers.GlobalAveragePooling1D()(bert_out)
        x = layers.Dense(64, activation="relu")(x)
        y_out = layers.Dense(len(np.unique(y_train)), activation='softmax')(x)
        ### compile
        model = models.Model([idx, masks, segments], y_out)
        for layer in model.layers[:4]:
            layer.trainable = False
        model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())

    ## train
    verbose = 0 if epochs > 1 else 1
    training = model.fit(x=X_train, y=y_train, batch_size=batch_size, epochs=epochs, shuffle=True, verbose=verbose, validation_split=0.3)
    if epochs > 1:
        utils_plot_keras_training(training)

    ## test
    predicted_prob = model.predict(X_test)
    predicted = [dic_y_mapping[np.argmax(pred)] for pred in predicted_prob] if encode_y is True else [np.argmax(pred)]
    return training.model, predicted_prob, predicted
































###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


