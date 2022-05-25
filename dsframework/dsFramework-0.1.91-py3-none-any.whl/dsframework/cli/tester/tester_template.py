from dsframework.utils.regex_handler import RegexHandler
from generatedMainDirectory.pipeline import generatedProjectNamePipeline
from dsframework.testable.tester_base import TesterBase
# from generatedMainDirectory.tester import generatedProjectNameDataset
from generatedMainDirectory.tester import generatedProjectNameReporter
import pandas as pd
import string
from tqdm import tqdm
import os
import json
import copy
import numpy as np


class generatedClass(TesterBase):
    @staticmethod
    def get_defaults():
        cfg = {}
        return cfg

    def __init__(self, name:str="generatedClassName",  **kwargs):
        TesterBase.__init__(self, name, generatedClass.get_defaults(),  **kwargs)
        self.ready = False

    def build(self, path:str='', load_samples=False):
        path, _ = self.convert_dataset_to_seg_format(path)
        self.init_pipeline()
        # self.init_dataset(path=path, load_samples=load_samples)
        self.init_reporter()
        self.ready = True

    def init_pipeline(self, *args, **kwargs):
        self.pipeline = generatedProjectNamePipeline.getInstance()

    # def init_dataset(self, path='',  do_convert=False, load_samples=False, *args, **kwargs):
    #     self.dataset = generatedProjectNameDataset(path=path, load_samples=load_samples)

    def init_reporter(self, path='', report_header='Signature Parser Analysis Report'):
        self.set_report_header(report_header)
        self.set_report_path(path)
        self.reporter = generatedProjectNameReporter()

    def parse(self, signature = ''):
        return self.pipeline(signature)

    def test(self, prediction_path = None, **kwargs):
        self.pre_test(**kwargs)
        if prediction_path:
            _, pred_df = self.convert_dataset_to_seg_format(prediction_path)
            self.dataset.set_df_prediction(pred_df)
        else:
            self.dataset.set_pipeline_prediction()
        report_col_names = self.get_report_df_cols()
        self.report_col_names = report_col_names
        self.report_df = pd.DataFrame(columns=report_col_names)
        for sample in tqdm(self.dataset.samples):
            sample_evaluations = self.evaluate(sample)
            if sample_evaluations:
                self.report_df.loc[len(self.report_df.index)] = sample_evaluations
        if self.reporter is not None:
            self.reporter(self.report_df, report_path=self.report_path, report_header=self.report_header)

    def pre_test(self):
        if not len(self.dataset.samples):
            self.dataset.populate()

    def get_report_df_cols(self):
        # def get_cols_per_attr(attr):
        #     return [f'{attr}_pred', f'{attr}_target', f'{attr}_prob', f'{attr}_tp',  f'{attr}_fp',  f'{attr}_tn', f'{attr}_fn']
        #
        # cols = []
        # cols+= ['name_prefix', 'name_first', 'name_middle', 'name_last', 'name_suffix', 'name_credentials']
        # cols+= ['tc_title', 'tc_company']
        # cols+= ['connections_phones', 'connections_mobiles', 'connections_faxes', 'connections_urls', 'connections_emails']
        # cols+= ['location_address', 'location_city', 'location_state', 'location_zip', 'location_country']
        #
        # self.report_base_cols = cols
        # cols_per_attr = [get_cols_per_attr(attr) for attr in cols]
        # flatten = lambda l: [item for sublist in l for item in sublist]
        # cols_as_list = flatten(cols_per_attr)
        # report_cols = ['text', 'pred', 'target'] + cols_as_list
        # return report_cols
        raise NotImplementedError

    def evaluate(self, sample):
        # def get_metrics(pred='', target=''):
        #     TP = 1*all([len(pred), len(target), pred==target])
        #     FP = 1*all([len(pred), pred!=target])
        #     TN = 1*all([not len(pred), not len(target), pred==target])
        #     FN = 1*all([not len(pred), len(target), pred!=target])
        #     return [TP, FP, TN, FN]
        #
        # text   = sample.x
        # pred   = sample.pred
        # target = sample.y
        #
        # pred_copy = copy.deepcopy(pred)
        # target_copy = copy.deepcopy(target)
        #
        # connections_pred   = self.convert_lists_to_str(pred_copy.get('connections', {}))
        # connections_target = self.convert_lists_to_str(target_copy.get('connections', {}))
        #
        # pred_copy['connections'] = connections_pred
        # target_copy['connections'] = connections_target
        #
        # # pred['connections'] = connections_pred
        # # target['connections'] = connections_target
        #
        # preds_dict  = self.F.flatten(pred)
        # target_dict = self.F.flatten(target)
        # pred_copy_dict  = self.F.flatten(pred_copy)
        # target_copy_dict = self.F.flatten(target_copy)
        #
        # # if not self.is_valid_signature(target_dict):
        # #     return None
        # row = [text, pred, target]
        #
        # if not self.report_base_cols:
        #     self.report_col_names = self.get_report_df_cols()
        #
        # for key in self.report_base_cols:
        #     prob       = -1
        #     pred_val   = preds_dict.get(key, '')
        #     target_val = target_dict.get(key, '')
        #     pred_val_c   = self.normalize_val_for_compare(pred_copy_dict.get(key, ''))
        #     target_val_c = self.normalize_val_for_compare(target_copy_dict.get(key, ''))
        #     metrices     = [pred_val, target_val, prob] + get_metrics(pred_val_c, target_val_c)
        #     row+=metrices
        #
        # return row
        raise NotImplementedError

    def convert_lists_to_str(self, d={}):
        # def list_to_str(k, v):
        #     val = [RegexHandler.remove_punct(str(t)).lower().replace(' ','') for t in v]
        #     val = list(set(val))
        #     val.sort()
        #     s = ''.join(val).strip()
        #     s = ''.join(list(set(s)))
        #     s = ''.join(sorted(s))
        #     if 'phone' in k :
        #         s = ''.join([c for c in s if c.isdigit()])
        #     else:
        #         s=s.replace('w','') # to ensure no www is considered + no order matters and no duplicates
        #     return s
        #
        # for k, v in d.items():
        #     if type(v) is list:
        #         d[k] = list_to_str(k, v)
        #
        # return d
        raise NotImplementedError

    def is_valid_signature(self, target_dict):
        company_exist    = len(target_dict.get('tc_company', ''))>0
        first_name_exist = len(target_dict.get('name_first', ''))>0
        last_name_exist  = len(target_dict.get('name_last', ''))>0
        return any([company_exist ,all([first_name_exist, last_name_exist])])

    def normalize_val_for_compare(self, val=''):
        if not val:
            return ''
        if not type(val) is str:
            val = str(val).lower()
        val = val.replace('\n', ' ')
        # s = RegexHandler.remove_punct(val, middle=False).lower()
        s = RegexHandler.remove_punct(val).lower()
        s = ''.join(filter(lambda x: x in string.printable, s)).strip()
        s = s.replace(' ','').replace('0', '')
        return s

    def convert_dataset_to_seg_format(self, path):
        """
        Convert dataset file from expanded format (each attribute as a column) to a segment format. Segment format has
        at least 2 columns: signature and segments. signature is the raw signature text column and segments is a string
        representation of the embedded attributes under the meta attributes: name, tc, connections and locations. In
        case the dataset is in expended format, the dataset is converted and saved locally and the new path is returned.
        In case the dataset file is already in segment format, its path is returned.
        @param path: path to dataset file
        @return: path to dataset file in segment format
        """
        df = pd.read_csv(path)
        if 'signature' in df.columns and 'segments' in df.columns:
            return path, df
        else:  # convert to segment format
            df_new = pd.DataFrame()
            df = df.replace({np.nan: ''})
            df_new['signature'] = df.signature
            df_new['segments'] = [json.dumps(self.convert_gt_to_seg(df.iloc[i])) for i in range(len(df))]
            path_new = os.path.join(os.path.dirname(path), os.path.basename(path).replace('.csv', '_seg_format.csv'))
            df_new.to_csv(path_new, index=False)
            return path_new, df_new

    @staticmethod
    def convert_gt_to_seg(entry):
        """
        Convert a dataframe entry into embedded segment attribute dictionary format.
        @param entry: dataframe entry
        @return: dictionary representation of embedded segment format.
        """
        d = {'name': {'first': entry['first'],
                      'last': entry['last'],
                      'middle': entry['middle'],
                      'prefix': entry['prefix'],
                      'suffix': entry['suffix'],
                      'credentials': entry['credentials']},
             'tc': {
                 'title': entry['title'],
                 'company': entry['company']
             },
             'connections': {
                 'emails': [entry['emails']],
                 'phones': [entry['phones']],
                 'faxes': [entry['faxes']],
                 'mobiles': [entry['mobiles']],
                 'urls': [entry['urls']],
             },
             'location': {
                 'address': entry['address'],
                 'city': entry['city'],
                 'state': entry['state'],
                 'zip': entry['zip'],
                 'country': entry['country'],
             }
             }
        return d

    @staticmethod
    def clear_df_before_saving(report_df):
        """
        Helper function clearing illegal characters in dataframe before saving as csv.
        @param report_df: a report dataframe to be stripped of illegal characters.
        @return: cleared dataframe (note some characters may be lost in the process.
        """
        for col in report_df.columns:
            if report_df[col].dtype == object and col.split('_')[-1] not in ['tp', 'tn', 'fp', 'fn']:
                report_df[col] = report_df[col].apply(
                    lambda x: np.nan if x == np.nan else str(x).encode('utf-8', 'replace').decode('utf-8'))
        return report_df

    @staticmethod
    def get_f1_precision_recall(var_name, df):
        """
        Calculate from detailed output report the f1, precision and recall scores per attribute.
        @param var_name: variable name to calculate the scores for.
        @param df: detailed results dataframe with per attribute confusion matrix as outputted by tester.
        @return: f1, precision and recall scores.
        """
        tp = df[var_name + '_tp']
        fp = df[var_name + '_fp']
        tn = df[var_name + '_tn']
        fn = df[var_name + '_fn']
        recall = 0
        precision = 0
        f1 = 0
        if len(np.where(tp + fp + tn + fn != 1)[0]) > 0:
            print(f'{len(np.where(tp + fp + tn + fn != 1)[0])} examples have errors')
        if (tp.sum() + fn.sum()) != 0:
            recall = tp.sum() / (tp.sum() + fn.sum())
        if (tp.sum() + fp.sum()) != 0:
            precision = tp.sum() / (tp.sum() + fp.sum())
        if (precision + recall) != 0:
            f1 = 2 * ((precision * recall) / (precision + recall))
        return f1, precision, recall

    def get_model_performance(self, df):
        """
        Generate aggregated performance report per model. The aggregated report provides per attribute f1, precision and
        recall scores.
        @param df: detailed output report as provided by tester test output.
        @return: aggregated results report
        """
        var_names = ['_'.join(var.split('_')[:-1]) for var in df.columns if var.endswith('_tp')]
        d_l = []
        for var in var_names:
            d = {}
            d['attribute'] = var
            f1, precision, recall = self.get_f1_precision_recall(var, df)
            d['f1'] = f1
            d['precision'] = precision
            d['recall'] = recall
            d_l.append(d)
        res_df = pd.DataFrame(d_l)
        res_df = res_df.set_index('attribute')
        return res_df

    def test_sigparser(self, ground_truth_path):
        """
        Run current local pipeline version test. Each example from the ground truth dataset will be predicted via the
        pipeline and evaluated for accuracy. The output is saved locally with sigparser prefix and stored as a member of
        the tester instance. The outputs are both detailed and aggregated results dataframes.
        @param ground_truth_path: ground truth labeled file path in segment format or expanded format.
        """
        self.build(ground_truth_path)
        self.test()
        report_df = self.report_df
        report_df = self.clear_df_before_saving(report_df)
        report_df.to_csv('local-pipeline_results22_2_21.csv')
        res_df = self.get_model_performance(report_df)
        res_df.to_csv('local-pipeline_aggregated_results_22_2_21.csv')
        self.add_results_to_report(report_df, res_df, 'local-pipeline')

    def add_results_to_report(self, report_df, res_df, algorithm_name):
        self.reports[algorithm_name] = {'detailed': report_df, 'aggregated': res_df}

    def test_from_file(self, ground_truth_path, prediction_path, algorithm_name=None):
        """
        Run a performance test from file output. The file output is compared with the ground truth to produce detailed
        and aggregated result datasets. Both are saved locally with from file prefix and saved as members of the tester
        object reports attribute.
        @param ground_truth_path: ground truth labeled file path in segment of expanded format.
        @param prediction_path: prediction file path in segment of expanded format.
        """
        if self.dataset is None:
            self.build(ground_truth_path)
        if algorithm_name is None:
            algorithm_name = os.path.basename(prediction_path)
        self.test(prediction_path=prediction_path)
        report_df = self.report_df
        report_df = self.clear_df_before_saving(report_df)
        report_df.to_csv(algorithm_name + '_results.csv')
        res_df = self.get_model_performance(report_df)
        res_df.to_csv(algorithm_name + '_aggregated_results.csv')

        self.add_results_to_report(report_df, res_df, algorithm_name)

    def generate_comparative_results(self):
        """
        Use the tester object reports to generate a comparative report between 2 versions. The output are detailed
        results of both versions as in:
        https://docs.google.com/spreadsheets/d/1rMJHHxAU5E0MVkuk5N2JOIh8qi0LeDr4LMiNmqYu8WE/edit#gid=1045120250
        The results provides a comparative aggregated and detailed reoports for both versions together.
        @return: merged datasets for detailed and aggregated results
        """
        def entry_to_dict(entry, prefix):
            d = {}
            for key, val in entry.items():
                d[prefix + key] = val
            return d
        compared_versions = list(self.reports.keys())
        assert len(compared_versions) == 2, 'comparing more than 2 versions is currently not supported'
        # reference version
        v1 = self.reports[compared_versions[0]]['detailed']
        v1_agg = self.reports[compared_versions[0]]['aggregated']
        # compared version
        v2 = self.reports[compared_versions[1]]['detailed']
        v2_agg = self.reports[compared_versions[1]]['aggregated']
        missing_entries = 0  # count missing entries in compared version
        d_l = []
        for i in range(len(v1)):
            v1_entry = v1.iloc[i]
            sig = v1_entry['text']
            match_i = self.dataset.find_signature_in_df(sig, v2, sig_colname='text')
            d = entry_to_dict(v1_entry, compared_versions[0] + '_')
            if match_i:
                v2_entry = v2.iloc[match_i]
                d.update(entry_to_dict(v2_entry, compared_versions[1] + '_'))
            else:
                missing_entries += 1
            d_l.append(d)
        print(f'total missing entries in compared version file: {missing_entries}')
        merged_df = pd.DataFrame(d_l)
        merged_df.to_csv('merged.csv')
        merged_agg = v1_agg.join(v2_agg, on='attribute', lsuffix='_'+compared_versions[0],
                                 rsuffix='_'+compared_versions[1])
        merged_agg.to_csv('merged_agg.csv')
        return merged_df, merged_agg


# usage example for comparing pipeline and file outputs. Note each step can be run independently- so if you wish only to
# test you own local version- just run: tester.test_sigparsr
if __name__ == '__main__':
    ground_truth_path = '/Users/doron.ariav/Desktop/sigparser-dataset/Clean_test_set_10K - Clean_test_set.csv'
    sigparser_file = '/Users/doron.ariav/Desktop/sigparser-dataset/Clean_test_set_10K - 27.12.2020-sigparser.csv'
    cogilex_file = '/Users/doron.ariav/Desktop/sigparser-dataset/Clean_test_set_10K - Parsed with cogilex.csv'
    tester = generatedClass()
    # tester.test_sigparser(ground_truth_path)  # the results are now in tester.reports['sigparser']
    tester.test_from_file(ground_truth_path, sigparser_file)
    tester.test_from_file(ground_truth_path, cogilex_file, algorithm_name='cogilex')  # the results are now in tester.reports['cogilex']
    merged_df, merged_agg_df = tester.generate_comparative_results()  # results are also saved locally (for all steps)

    tester.reports.keys()
