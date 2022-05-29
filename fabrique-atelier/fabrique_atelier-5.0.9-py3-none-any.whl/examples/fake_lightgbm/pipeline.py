from fabrique_atelier.actors import Processor, Pipeline

import json
import numpy as np
import fake_lightgbm as lgb

np.seterr(all='raise')


class ExtractFeatures(Processor):
    def __init__(self):
        self.classes = ["about", "services", "contacts", "roaming", "tariffs",
                        "simcards", "balance", "internet", "messaging", "support"]

    def get_result(self, body):
        mes = json.loads(body['data'])
        features = np.array([mes['traffic'][cls] for cls in self.classes]).flatten()

        data = dict(ts=mes['ts'], uid=mes['uid'], number=mes['number'], features=features.tolist())

        return {'data': data}


class ScoringModel(Processor):
    def __init__(self):
        self.classes = ["about", "services", "contacts", "roaming", "tariffs",
                        "simcards", "balance", "internet", "messaging", "support"]

        self.bst = lgb.Booster(model_file='./model.txt')  # init model

    def get_batch_result(self, batch):
        # prediction
        features_batch = np.array([body['data']['features'] for body in batch])
        pred_batch = self.bst.predict(features_batch)

        out_batch = []
        for i, body in enumerate(batch):
            in_data = body['data']
            scores = pred_batch[i]

            try:
                scores = scores / scores.sum() # try to normalize
            except:
                pass

            reason_num = scores.argmax()
            reason = self.classes[reason_num]

            scores_dict = {cls: round(scores[i], 2) for i, cls in enumerate(self.classes)}
            out_data = dict(ts=in_data['ts'], uid=in_data['uid'], number=in_data['number'],
                            classes=scores_dict, reason=reason)
            out_body = dict(data=json.dumps(out_data).encode(), metrics={"reason_num": int(reason_num)})
            out_batch.append(out_body)

        return out_batch


# topology
pipeline = Pipeline(['extractor', 'model'])

ids = pipeline.ids
nodes = pipeline.nodes

nodes.extractor = ExtractFeatures.to(ids.model)
nodes.model = ScoringModel.to(ids.end)
