import os
import shutil

class FSStorage:
    def __init__(self):
        self.protocol = 'file'
        # get an env variable
        self.storage_dir = os.environ.get("GBD_FS_STORAGE_PATH", os.getcwd())

    def do_store(self, file, root, location):
        dest = os.path.join(self.storage_dir, root, location)
        os.makedirs(os.path.split(dest)[0], exist_ok=True)

        shutil.copyfile(file, dest)

        storage_location = self.protocol + '://' + dest
        return storage_location

    def get_file(self, source_file, dest_file):
        if self.storage_dir not in source_file:
            source_file = os.path.join(self.storage_dir, source_file)
        source_file = source_file.replace("%s://"% self.protocol, '')
        shutil.copyfile(source_file, dest_file)

    def remove_old(self, root, key, current_version, delete_all=False):
        all_versions = os.listdir(os.path.join(self.storage_dir, root, key))
        for version in all_versions:
            if current_version not in version or delete_all:
                os.remove(os.path.join(self.storage_dir, root, key, version))
