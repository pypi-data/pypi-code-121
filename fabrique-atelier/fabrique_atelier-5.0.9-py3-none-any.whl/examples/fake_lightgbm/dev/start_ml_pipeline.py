import sys
import os
import json
import numpy as np


sys.path.append('..')
import fake_lightgbm as lgb
from pipeline import pipeline

samp_dir = './samples'
filenames = [f for f in os.listdir(samp_dir) if os.path.isfile(f'{samp_dir}/{f}')]
samples = []
for filename in filenames:
    with open(f'{samp_dir}/{filename}') as fp:
        samples.append(fp.read())

pipeline.start_emulation(samples)




# load model
bst = lgb.Booster(model_file='../model.txt')  # init model
classes = ["about", "services", "contacts", "roaming", "tariffs",
           "simcards", "balance", "internet", "messaging", "support"]

# simple inference code
reference_results = []  # we will use this results for tests
for sample in samples:
    ## 1. extract features from json message
    # 1.1. parse message and get features
    mes = json.loads(sample)
    features = np.array([mes['traffic'][cls] for cls in classes]).flatten()
    ## 2. make prediction result
    # 2.1 get prediction
    pred_vals = bst.predict([features, ])[0]
    # 2.2 normalize scores, get class
    try:
        scores = pred_vals / pred_vals.sum()
    except:
        scores = pred_vals
    reason = classes[scores.argmax()]
    # 2.3 make and serialize message
    scores_dict = {cls: round(scores[i], 2) for i, cls in enumerate(classes)}
    res = dict(ts=mes['ts'], uid=mes['uid'], number=mes['number'], classes=scores_dict, reason=reason)
    reference_results.append(json.dumps(res))



# load results of emulation
result_dir = './out/data'
filenames = [f for f in os.listdir(result_dir) if os.path.isfile(f'{result_dir}/{f}')]
results = []
for filename in filenames:
    with open(f'{result_dir}/{filename}') as fp:
        results.append(fp.read())

#check if results are equal
assert set(results) == set(reference_results)
