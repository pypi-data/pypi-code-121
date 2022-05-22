import os

import pandas as pd
import torch
import all2graph as ag
os.chdir(os.path.dirname(os.path.abspath(__file__)))


if __name__ == '__main__':
    df = pd.read_csv('test_data/0.zip', nrows=32)

    processes = os.cpu_count()
    json_parser = ag.JsonParser(
        json_col='data', time_col='time', time_format='%Y-%m-%d', targets=['target'])

    meta_info = json_parser.analyse('test_data', chunksize=100, nrows=100, processes=processes)  # 15s
    graph_parser = ag.GraphParser.from_data(meta_info)
    parser_wrapper = ag.ParserWrapper(json_parser, graph_parser)
    model = ag.nn.GATFM(d_model=8, num_layers=6, num_heads=2, parser=parser_wrapper)
    model.build_module()
    print(model)
    print(model(df))
    torch.save(model, 'no_cython_model.th')