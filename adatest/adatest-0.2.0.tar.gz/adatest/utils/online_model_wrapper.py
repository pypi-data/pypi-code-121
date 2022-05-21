import sys
from tqdm.auto import tqdm
import os
import pickle
import urllib
import json
import http
import numpy as np
import time
# from google.cloud import language
# from google.cloud.language import enums
# from google.cloud.language import types
from google.cloud import language_v1
import boto3
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

class OnlinePredictor:
    def __init__(self, pred_file, batch_size=1000, wait_time=1, model='azure3'):
        self.preds = {}
        self.post_fn = None
        if os.path.exists(pred_file):
            self.preds = pickle.load(open(pred_file, 'rb'))
        self.pred_file = pred_file
        if model == 'azure3':
            self.pp_fn = self.predict_proba_azure3
        if model == 'azure2':
            self.pp_fn = self.predict_proba_azure2
            self.post_fn = self.binary_to_three
        if model == 'google':
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/slundberg/.google_cloud_key.json'
            self.pp_fn = self.predict_proba_google
            self.post_fn = self.binary_to_three
            # self.gclient = language.LanguageServiceClient()
            self.gclient = language_v1.LanguageServiceClient()
        if model == 'amazon':
            self.pp_fn = self.predict_proba_amazon
            self.client = boto3.client('comprehend', region_name='us-west-2')

        self.batch_size = batch_size
        self.wait_time = wait_time

    def binary_to_three(self, pr):
        # This is what google recommends
        margin_neutral = 0.25
        mn = margin_neutral / 2.
        pp = np.zeros((pr.shape[0], 3))
        neg = pr < 0.5 - mn
        pp[neg, 0] = 1 - pr[neg]
        pp[neg, 2] = pr[neg]
        pos = pr > 0.5 + mn
        pp[pos, 0] = 1 - pr[pos]
        pp[pos, 2] = pr[pos]
        neutral_pos = (pr >= 0.5) * (pr < 0.5 + mn)
        pp[neutral_pos, 1] = 1 - (1 / margin_neutral) * np.abs(pr[neutral_pos] - 0.5)
        pp[neutral_pos, 2] = 1 - pp[neutral_pos, 1]
        neutral_neg = (pr < 0.5) * (pr > 0.5 - mn)
        pp[neutral_neg, 1] = 1 - (1 / margin_neutral) * np.abs(pr[neutral_neg] - 0.5)
        pp[neutral_neg, 0] = 1 - pp[neutral_neg, 1]
        return (pp.T / pp.sum(1)).T # normalize to sum to 1

    def predict_proba(self, exs, silent=True):
        to_pred = [x for x in exs if x not in self.preds]
        chunked = list(chunks(to_pred, self.batch_size))
        for docs in chunked:
            pps = self.pp_fn(docs)
            for x, pp in zip(docs, pps):
                self.preds[x] = pp
            pickle.dump(self.preds, open(self.pred_file, 'wb'))
            time.sleep(self.wait_time)
        ret = np.array([self.preds.get(x) for x in exs])
        if self.post_fn:
            ret = self.post_fn(ret)
        return ret

    def predict_and_confidences(self, exs):
        confs = self.predict_proba(exs)
        preds = np.argmax(confs, axis=1)
        return preds, confs


    def predict_proba_amazon(self, exs):
#         print('amazon: predicting %d examples' % len(exs))
        scores = []
        for text in exs:
            ret = self.client.detect_sentiment(Text=text, LanguageCode='en')
            r = np.zeros(3)
            r[0] = ret['SentimentScore']['Negative']
            r[1] = ret['SentimentScore']['Neutral'] + ret['SentimentScore']['Mixed']
            r[2] = ret['SentimentScore']['Positive']
            scores.append(r)
        return np.array(scores)


    def predict_proba_azure3(self, exs):
        print('Azure: predicting %d examples' % len(exs))
        headers = {
        # Request headers
        'Content-Type': 'application/json',
        #         'Ocp-Apim-Subscription-Key': '3045416f7b4e4e73a58209761510341b',
        # 'Ocp-Apim-Subscription-Key': '1ddbdc586002484f8d4ad20c1ef092c5',
            # 'Ocp-Apim-Subscription-Key': 'c7c3c9d329aa49639d5706d11b313721'
            'Ocp-Apim-Subscription-Key': '94990b170d4c47c29c8a23facf39a22d'
        }
        params = urllib.parse.urlencode({
            # Request parameters
            'showStats': 'false',
        })
        body = json.dumps({'documents': [{'id': str(i), 'text': x, 'language': 'en'} for i, x in enumerate(exs)]})
        try:
            conn = http.client.HTTPSConnection('westus2.api.cognitive.microsoft.com')
#             conn.request("POST", "/text/analytics/v2.1/sentiment?%s" % params, body, headers)
            conn.request("POST", "/text/analytics/v3.0-preview.1/sentiment?%s" % params, body, headers)
            response = conn.getresponse()
            azureresp = response.read()
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            print(exs)
        try:
            pps = np.array([[x['documentScores'][a] for a in ['negative', 'neutral', 'positive']] for x in json.loads(azureresp)['documents']])
        except:
            print(json.loads(azureresp))
            raise Exception()
        return pps
    def predict_proba_azure2(self, exs):
        print('Azure: predicting %d examples' % len(exs))
        headers = {
        # Request headers
        'Content-Type': 'application/json',
        #         'Ocp-Apim-Subscription-Key': '3045416f7b4e4e73a58209761510341b',
        # 'Ocp-Apim-Subscription-Key': '1ddbdc586002484f8d4ad20c1ef092c5',
            # 'Ocp-Apim-Subscription-Key': 'c7c3c9d329aa49639d5706d11b313721'
            'Ocp-Apim-Subscription-Key': '94990b170d4c47c29c8a23facf39a22d'
        }
        params = urllib.parse.urlencode({
            # Request parameters
            'showStats': 'false',
        })
        body = json.dumps({'documents': [{'id': str(i), 'text': x, 'language': 'en'} for i, x in enumerate(exs)]})
        try:
            conn = http.client.HTTPSConnection('westus2.api.cognitive.microsoft.com')
            conn.request("POST", "/text/analytics/v2.1/sentiment?%s" % params, body, headers)
            # conn.request("POST", "/text/analytics/v3.0-preview.1/sentiment?%s" % params, body, headers)
            response = conn.getresponse()
            azureresp = response.read()
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            print(exs)
        pps = [x['score'] for x in json.loads(azureresp)['documents']]
        return np.array(pps)
    def predict_proba_google(self, exs):
        type_ = language_v1.Document.Type.PLAIN_TEXT
        language = "en"
        encoding_type = language_v1.EncodingType.UTF8
        scores = []
        for text in exs:
            document = {"content": text, "type_": type_, "language": language}
            annotations = self.gclient.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})
            score = 0.5 + annotations.document_sentiment.score / 2.
            scores.append(score)
        return np.array(scores)




    # def predict_proba_google(self, exs):
    #     print('Google: predicting %d examples' % len(exs))
    #     scores = []
    #     for text in exs:
    #         document = types.Document(
    #         content=text,
    #         language='en',
    #         type=enums.Document.Type.PLAIN_TEXT)
    #         annotations = self.gclient.analyze_sentiment(document=document)
    #         score = 0.5 + annotations.document_sentiment.score / 2.
    #         scores.append(score)
    #     return np.array(scores)
