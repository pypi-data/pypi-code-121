from ...libs.io_lib import archive_object, unarchive_object

class AlphaSave():
    root    = None
    ext     = '.ast'
    
    @staticmethod
    def set_root(root):
        AlphaSave.root = root

    @staticmethod
    def get_file_path(filename):
        file_path = AlphaSave.root + os.sep + filename + '.ast'
        return file_path

    @staticmethod
    def save(object_to_save,filename):
        file_path = AlphaSave.get_file_path(filename)
        directory = os.path.dirname(file_path)
        os.makedirs(directory,exist_ok=True)
        archive_object(object_to_save,file_path)

    @staticmethod
    def load(filename):
        file_path = AlphaSave.get_file_path(filename)
        return unarchive_object(file_path)
