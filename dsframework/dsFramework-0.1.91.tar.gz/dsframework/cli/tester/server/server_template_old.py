from ast import literal_eval
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS, cross_origin
from dsframework.testable.dataset_base import DatasetSample
from generatedMainDirectory.tester import generatedProjectNameTester
import pandas as pd
import json

class generatedClass():

    def __init__(self):
        self.tester = generatedProjectNameTester()
        self.tester.init_pipeline()
        self.error_df = pd.DataFrame(columns=['signature', 'target'])
        self.report_df = None
        # self.report_col_names = self.tester.get_report_df_cols()
        # self.report_df = pd.DataFrame(columns=self.report_col_names)


    @staticmethod
    def run(debug=False):
        app.run(debug=debug)

    def handle_request(self, action, params,  truth_dataset_id=-1, model_type_id=-1, raw_id=-1):
        if action == 'parse':
            return self.parse_single(params)
        elif action == 'test':
            return self.test_mini_batch(params,  truth_dataset_id, model_type_id, raw_id)
        return {'action':action, 'params':params}

    def parse_single(self, params):
        text   = '' if 'text' not in params else params['text']
        uid    = '1'
        parsed = self.tester.parse(text)
        pred   = parsed['signatures'][0]
        pred['uid'] = uid
        return pred

    def test_mini_batch(self, params, truth_dataset_id=-1, model_type_id=-1, raw_id=-1):
        data = {} if 'data' not in params else params['data']
        data = literal_eval(data) if type(data) == str else data
        _id  = params['id'] if 'id' in params else -1
        signature_text = data['signature']
        target = data['segments']
        parsed = self.tester.parse(signature_text)
        pred   = parsed['signatures'][0]['segments']
        sample = DatasetSample(x=signature_text, y=target, pred=pred)
        results = self.tester.evaluate(sample)
        if self.report_df is None:
            self.report_df = pd.DataFrame(columns=self.tester.report_col_names)
        self.report_df.loc[len(self.report_df.index)] = results
        resp = {}
        try:
            for idx, col_name in enumerate(self.tester.report_col_names):
                if col_name in ['pred', 'target']:
                    results[idx] = json.dumps(results[idx])
                resp[col_name] = results[idx]
        except Exception as e:
            print('error', str(e),  '\n\n\n',signature_text, '\n\n\n', target, '\n\n\n', results , '\n\n\n')
            self.error_df.loc[len(self.error_df.index)] = [signature_text, target]
            self.error_df.to_csv('error_log.csv', index=False)

        resp['truth_id'] = _id
        resp['truth_dataset_id'] = truth_dataset_id
        resp['model_type_id'] = model_type_id
        resp['raw_id'] = raw_id
        if len(self.report_df.index)%100==0:
            self.report_df.to_csv('server_report.csv', index=False)
        return resp


app  = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
web_handler = generatedClass()

@app.route('/parse', methods = ['POST'])
@cross_origin()
def parse():
    if request.is_json:
        req    = request.json
        action = 'parse'
        text   = '' if 'text' not in req else req['text']
        params = {'text': text}
        resp   = [web_handler.handle_request(action, params)]
        return jsonify(resp)


@app.route('/test', methods = ['POST'])
@cross_origin()
def test():
    if request.is_json:
        req    = request.json
        action = 'test'
        truth_dataset_id = req['truth_dataset_id'] if 'truth_dataset_id' in req else -1
        model_type_id = req['model_type_id'] if 'model_type_id' in req else -1
        raw_id = req['raw_id'] if 'raw_id' in req else -1
        rows = req['rows'] if 'rows' in req else []
        resp = [web_handler.handle_request(action, params, model_type_id,truth_dataset_id,raw_id) for params in rows]
        return jsonify(resp)

if __name__ == '__main__':
    web_handler.run()

