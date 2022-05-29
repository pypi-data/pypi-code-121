import os
from shutil import copyfile

cur_file_path = os.path.dirname(os.path.abspath(__file__))
TPL_PATH = f"{cur_file_path}/data/default_template.yml"


class TemplatesGenerator:
    def __init__(self, pipeline_pth='', node_ids=None):
        assert pipeline_pth
        node_ids = node_ids if node_ids else []
        self.pipeline_pth = pipeline_pth
        self.node_ids = node_ids

    def write(self):
        for node_id in self.node_ids:
            dst_file = f'{self.pipeline_pth}/{node_id}_template.yml'
            if os.path.isfile(dst_file):
                print(f'template {dst_file} already exists')
                return
            copyfile(TPL_PATH, dst_file)
