import os
import shutil
from pypers.core.interfaces.storage import get_storage

class STAGE():
    All = "all"
    Images = "imgs"
    Documents = "docs"

    @staticmethod
    def get_choices():
        return [STAGE.All, STAGE.Images, STAGE.Documents]

class StageBase():

    def __init__(self, snapshot, stage_type):
        self.snapshot = snapshot
        self.run_id = snapshot.split('.')[-2]
        self.stage_type = stage_type
        self.manifests = {}
        self.storage = get_storage()

    def _move_object(self, write_root, read_root, file):
        if not file:
            return

        src_file = os.path.join(read_root, file)
        dest_file = os.path.join(write_root, file)

        dest_dir = os.path.dirname(dest_file)
        os.makedirs(dest_dir, exist_ok=True)

        shutil.move(src_file, dest_file)