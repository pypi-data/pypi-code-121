import os

class FileUtils:
    @staticmethod
    def create_directory_if_not_exists(path):
        # Check whether the specified path exists or not
        isExist = os.path.exists(path)

        if not isExist:
            # Create a new directory because it does not exist
            print("Create new directory {}".format(path))
            os.makedirs(path)
