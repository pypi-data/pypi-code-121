from generatedDirectory.pipeline import generatedProjectNamePipeline
from dsframework.testable.dataset_base import DatasetBase
import pathlib

class generatedClass(DatasetBase):
    
    @staticmethod
    def get_defaults():
        dir_path = pathlib.Path(__file__).parent.absolute()

        cfg = {}
        cfg['use_local_storage']   = True
        cfg['local_storage_path']  = dir_path/'tests'
        cfg['remote_storage_path'] = ''
        cfg['dataset_name']        = 'annotated_set_round_a_sample.csv'
        return cfg

    def __init__(self, name:str="generatedClassName", path='', load_samples=False,  **kwargs):
        self.pipeline = generatedProjectNamePipeline.getInstance()
        DatasetBase.__init__(self, name, path, False, load_samples, generatedClass.get_defaults(), **kwargs)

    def init_path(self, path=''):
        if not path:
            path = self.local_storage_path/self.dataset_name if self.use_local_storage else self.remote_storage_path/self.dataset_name
        self.path = path

    def set_model_prediction(self):
        # TODO: figure out how to neutralize pre and post processing
        self.pipeline.__dir__()

        raise NotImplementedError


    def set_pipeline_prediction(self):

        raise NotImplementedError

    def set_df_prediction(self, pred_df):

        raise NotImplementedError



    # def get_data_sample_from_row(self, row, i=None):
    #     text               = row.iloc[0]
    #     gt_segments        = row.iloc[1]
    #     # print(text)
    #     gt_segments_dict   = literal_eval(gt_segments) if type(gt_segments) == str else gt_segments
    #     return DatasetSample(x=text, y=gt_segments_dict)
