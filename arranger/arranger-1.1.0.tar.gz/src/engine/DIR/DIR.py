from os import mkdir
from os.path import abspath


class DIR:
    def __init__(self, directory_path):
        self.dir_path = abspath(directory_path)
        self.dir_name = self.dir_path.split('/')[-1]
        self.dir_parent = '/'.join(self.dir_path.split('/')[:-1])

    @property
    def dir_ancestors(self):
        directory = self.dir_parent.split('/')
        ancestors = {'/'.join(directory[:n + 4:]) for n in range(len(directory) - 3)}

        return ancestors

    def create_directory(self):
        try:
            mkdir(self.dir_path)
        except FileExistsError:
            pass
