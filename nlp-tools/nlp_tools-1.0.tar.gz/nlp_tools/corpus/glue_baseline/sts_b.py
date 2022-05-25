#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sts_b.py    
@Contact :   544855237@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2022/4/18 下午7:46   qiufengfeng      1.0         None
'''

# import lib
import os

class STSBenchmarkReader:
    """
    STS Benchmark reader to prep the data for evaluation.
    """

    @classmethod
    def load_data( cls,data_path: str = None):
        assert data_path != None and os.path.isfile(data_path)
        data_dict = dict(sent1=[], sent2=[], scores=[])

        with open(data_path) as fopen:
            dataset = list(filter(None, fopen.read().split('\n')))

        sent1 = []
        sent2 = []
        scores = []

        for data in dataset:
            data_list = data.split('\t')
            sent1.append(data_list[5])
            sent2.append(data_list[6])
            scores.append(data_list[4])

        data_dict['sent1'] = sent1
        data_dict['sent2'] = sent2
        data_dict['scores'] = scores
        # sanity check
        assert len(data_dict['sent1']) == len(data_dict['sent2'])
        assert len(data_dict['sent1']) == len(data_dict['scores'])

        x_union = [(x, y) for x, y in zip(sent1, sent2)]
        data_union = [(x,y) for x,y in zip(x_union,scores)]
        return data_union

if __name__ == '__main__':
    data_path = '/home/fanfanfeng/working_data/nlp_data/baseline/glue_data/STS-B/original/sts-dev.tsv'
    stsb = STSBenchmarkReader.load_data(data_path)
    print(stsb)