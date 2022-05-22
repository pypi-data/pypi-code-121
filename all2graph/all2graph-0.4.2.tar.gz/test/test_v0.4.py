import os
import shutil

import numpy as np
import pandas as pd
import torch
import all2graph as ag
import dgl.nn.pytorch
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def gen_data():
    import string
    import json
    data = []
    for _ in ag.tqdm(range(10000)):
        one_sample = []
        for _ in range(np.random.randint(1, 200)):
            item = {
                k: list(np.random.choice(list(string.ascii_letters)+list(string.digits), size=np.random.randint(1, 10)))
                for k in np.random.choice(list(string.ascii_letters), size=np.random.randint(1, 10))
            }
            one_sample.append(item)
        data.append(json.dumps(one_sample))
    df = pd.DataFrame({'data': data, 'target': np.random.choice([0, 1], size=len(data)), 'time': None})
    if os.path.exists('test_data'):
        shutil.rmtree('test_data')
    ag.split_csv(pd.concat([df] * 10), 'test_data', chunksize=100)


if __name__ == '__main__':
    # gen_data()
    # df = pd.read_csv('test_data2/0.zip')
    # print(df)
    # print(json.loads(df.data[0]))
    processes = os.cpu_count()
    json_parser = ag.JsonParser(
        json_col='data', time_col='time', time_format='%Y-%m-%d', targets=['target'])

    meta_info = json_parser.analyse('test_data', chunksize=100, nrows=100, processes=processes)  # 15s
    graph_parser = ag.GraphParser.from_data(meta_info)
    parser_wrapper = ag.ParserWrapper(json_parser, graph_parser)

    path_df = pd.read_csv('test_data_path.csv')
    path_df['path'] = path_df['path'].str.replace('\\', '/')
    
    data = ag.data.CSVDataset(path_df, parser_wrapper, index_col=[0, 1])
    data = data.dataloader(processes, shuffle=True, batch_size=32, pin_memory=False)

    d_model = 8
    num_layers = 6
    module = ag.nn.Framework(
        key_emb=torch.nn.LSTM(d_model, d_model//2, 2, bidirectional=True, batch_first=True),
        str_emb=torch.nn.Embedding(graph_parser.num_tokens, d_model),
        num_emb=ag.nn.NumEmb(d_model),
        bottle_neck=ag.nn.BottleNeck(d_model),
        body=ag.nn.Body(
            num_layers,
            conv_layer=dgl.nn.pytorch.GATConv(d_model, d_model, 1, residual=True),
            ff=ag.nn.FeedForward(d_model, pre=torch.nn.BatchNorm1d(d_model)),
        ),
        head=ag.nn.Head((num_layers+1)*d_model),
        seq_degree=(10, 10)
    )
    if torch.cuda.is_available():
        module.cuda()

    trainer = ag.nn.Trainer(
        module=module,
        loss=ag.nn.DictLoss(torch.nn.BCEWithLogitsLoss()),
        data=data,
        valid_data=[data]
    )
    print(trainer)
    trainer.fit(1)  # 3m16/2m40  cython:3m12/1m48
