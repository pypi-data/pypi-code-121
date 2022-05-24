from os import path as ospath


class FTPWalk:
    """
    This class is contain corresponding functions for traversing the FTP
    servers using BFS algorithm.
    """
    def __init__(self, connection):
        self.connection = connection

    def listdir(self, _path):
        """
        return files and directory names within a path (directory)
        """

        file_list, dirs, nondirs = [], [], []
        try:
            self.connection.cwd(_path)
        except Exception as exp:
            print("the current path is : ", self.connection.pwd(),
                   exp.__str__(), _path)
            return [], []
        self.connection.retrlines('LIST', lambda x: file_list.append(x.split()))
        for info in file_list:
            ls_type, name = info[0], info[-1]
            if ls_type.startswith('d'):
                if not name == '.' and not name == '..':
                    dirs.append(name)
                else:
                    pass  # ignore these special directories
            else:
                nondirs.append(name)
        return dirs, nondirs

    def walk(self, path='/'):
        """
        Walk through FTP server's directory tree, based on a BFS algorithm.
        """
        dirs, nondirs = self.listdir(path)
        yield path, nondirs
        for name in dirs:
            path = ospath.join(path, name)
            dirs, nondirs = self.listdir(path)
            yield path, nondirs
            self.connection.cwd('..')
            path = ospath.dirname(path)
