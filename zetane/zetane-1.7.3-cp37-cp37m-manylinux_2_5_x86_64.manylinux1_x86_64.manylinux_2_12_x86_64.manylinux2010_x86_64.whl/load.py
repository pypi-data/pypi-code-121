

class Load:
    def __init__(self, nsocket, filepath, panel_location=None, send_absolute_path=True):
        pass


    def add_tag(self, tag):
        """ Updates the load command with list of objects to update

        :param json_objects: list of all the tags and ids to send to Zetane
        :return: self.
        """
        return self


    def objects(self):
        """ returns a dictionary of python object handles keyed to their unique object names
        .. example:: `zimg = zcontext.load(filename).objects()['unique_img_name']`

        :return: dictionary of object handles keyed to their unique names
        """
        return self


    def get_objects_sorted_by_name(self):
        """ Returns a list of all objects loaded from file, sorted alphabetically by their unique names.
        .. example:: `zimg, zmodel, zmodel = zcontext.load(filename).get_objects_sorted_by_name()`
        """
        return self
