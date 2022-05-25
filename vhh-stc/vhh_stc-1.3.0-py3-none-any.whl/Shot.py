

class Shot(object):
    """
    This class is representing a shot. Each instance of this class is holding the properties of one shot.
    """

    def __init__(self, sid, movie_name, start_pos, end_pos):
        """
        Constructor

        :param sid [required]: integer value representing the id of a shot
        :param movie_name [required]: string representing the name of the movie
        :param start_pos [required]: integer value representing the start frame position of the shot
        :param end_pos [required]: integer value representing the end frame position of the shot
        """
        #print("create instance of shot ...");
        self.sid = sid
        self.movie_name = movie_name
        self.start_pos = start_pos
        self.end_pos = end_pos

    def convert2String(self):
        """
        Method to convert class member properties in a semicolon separated string.

        :return: string holding all properties of one shot.
        """
        tmp_str = str(self.sid) + ";" + str(self.movie_name) + ";" + str(self.start_pos) + ";" + str(self.end_pos)
        return tmp_str

    def printShotInfo(self):
        """
        Method to a print summary of shot properties.
        """
        print("------------------------")
        print("shot id: " + str(self.sid))
        print("movie name: " + str(self.movie_name))
        print("start frame: " + str(self.start_pos))
        print("end frame: " + str(self.end_pos))