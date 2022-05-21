#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
# Copyright (c) 2017 Hai Liang Wang, All Rights Reserved
#
#
# File: /Users/hain/ai/insuranceqa-corpus-zh/pypi/insuranceqa_data/__init__.py
# Author: Hai Liang Wang
# Date: 2017-07-28:10:47:28
# Modified by Xuming Lin in 2018-01-23 23:50
#
#===============================================================================
from __future__ import print_function

__copyright__ = "Copyright (c) Hai Liang Wang 2017 . All Rights Reserved"
__author__    = "Hai Liang Wang"
__date__      = "2017-07-28:10:47:28"

import os
import sys
import gzip
import json
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, curdir)

import wget

def load(data_path):
    print("\n Project Sponsored by Chatopera\n")
    print("\n  deliver your chatbots with Chatopera Cloud Services --> https://bot.chatopera.com\n")
    if not os.path.exists(data_path):
        data_dir = os.path.split(os.path.split(data_path)[0])[0]
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        if not os.path.exists(os.path.join(data_dir, 'pairs')):
            os.mkdir(os.path.join(data_dir, 'pairs'))
        if not os.path.exists(os.path.join(data_dir, 'pool')):
            os.mkdir(os.path.join(data_dir, 'pool'))
        print('\n Now download data to dir {}'.format(data_dir))
        # download all pair data
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.test.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.test.json.gz", out = os.path.join(data_dir, 'pairs'))
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.train.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.train.json.gz", out = os.path.join(data_dir, 'pairs'))
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.valid.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.valid.json.gz", out = os.path.join(data_dir, 'pairs'))
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.vocab.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pairs/iqa.vocab.json.gz", out = os.path.join(data_dir, 'pairs'))

        # download all pool data
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/answers.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/answers.json.gz", out = os.path.join(data_dir, 'pool'))
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/test.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/test.json.gz", out = os.path.join(data_dir, 'pool'))
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/train.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/train.json.gz", out = os.path.join(data_dir, 'pool'))
        print("\n [insuranceqa_data] downloading data %s ... \n" % "https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/valid.json.gz")
        wget.download("https://github.com/chatopera/insuranceqa-corpus-zh/raw/release/corpus/pool/valid.json.gz", out = os.path.join(data_dir, 'pool'))

    with gzip.open(data_path, 'rb') as f:
        data = json.loads(f.read())
        return data

'''
pool data are translated Chinese data with Google API from original English data
'''

def load_pool_test(data_path=None):
    if data_path is None:
        POOL_TEST_DATA = os.path.join(curdir, 'pool', 'test.json.gz')
    else:
        POOL_TEST_DATA = os.path.join(data_path, 'pool', 'test.json.gz')
    return load(POOL_TEST_DATA)

def load_pool_valid(data_path=None):
    if data_path is None:
        POOL_VALID_DATA = os.path.join(curdir, 'pool', 'valid.json.gz')
    else:
        POOL_VALID_DATA = os.path.join(data_path, 'pool', 'valid.json.gz')
    return load(POOL_VALID_DATA)

def load_pool_train(data_path=None):
    if data_path is None:
        POOL_TRAIN_DATA = os.path.join(curdir, 'pool', 'train.json.gz')
    else:
        POOL_TRAIN_DATA = os.path.join(data_path, 'pool', 'train.json.gz')
        return load(POOL_TRAIN_DATA)

def load_pool_answers(data_path=None):
    if data_path is None:
        POOL_ANS_DATA = os.path.join(curdir, 'pool', 'answers.json.gz')
    else:
        POOL_ANS_DATA = os.path.join(data_path, 'pool', 'answers.json.gz')
    return load(POOL_ANS_DATA)

def __test_qa():
    d = load_train()
    for x in d:
        print('index %s value: %s ++$++ %s ++$++ %s %s' % (x, d[x]['zh'], d[x]['en'], d[x]['answers'], d[x]['negatives']))

def __test_answers():
    d = load_answers()
    for x in d:
        print('index %s: %s ++$++ %s' % (x, d[x]['zh'], d[x]['en']))

'''
pair data are segmented and labeled after pool data
'''

def load_pairs_vocab(data_path=None):
    '''
    Load vocabulary data
    '''
    if data_path is None:
        PAIR_VOCAB_DATA = os.path.join(curdir, 'pairs', 'iqa.vocab.json.gz')
    else:
        PAIR_VOCAB_DATA = os.path.join(data_path, 'pairs', 'iqa.vocab.json.gz')
    return load(PAIR_VOCAB_DATA)

def load_pairs_test(data_path=None):
    if data_path is None:
        PAIR_TEST_DATA = os.path.join(curdir, 'pairs','iqa.test.json.gz')
    else:
        PAIR_TEST_DATA = os.path.join(data_path, 'pairs','iqa.test.json.gz')
    return load(PAIR_TEST_DATA)

def load_pairs_valid(data_path=None):
    if data_path is None:
        PAIR_VALID_DATA = os.path.join(curdir, 'pairs','iqa.valid.json.gz')
    else:
        PAIR_VALID_DATA = os.path.join(data_path, 'pairs','iqa.valid.json.gz')
    return load(PAIR_VALID_DATA)

def load_pairs_train(data_path=None):
    if data_path is None:
        PAIR_TRAIN_DATA = os.path.join(curdir, 'pairs','iqa.train.json.gz')
    else:
        PAIR_TRAIN_DATA = os.path.join(data_path, 'pairs','iqa.train.json.gz')
    return load(PAIR_TRAIN_DATA)

def __test_pair_test():
    d = load_pairs_test()
    for x in d:
        print("index %s question %s utterance %s label %s" % (x['qid'], x['question'], x['utterance'], x['label']))
        break

if __name__ == '__main__':
    # __test_qa()
    # __test_answers()
    __test_pair_test()
    pass
