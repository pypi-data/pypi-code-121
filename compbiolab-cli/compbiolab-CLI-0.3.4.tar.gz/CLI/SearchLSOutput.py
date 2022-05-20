from typing import TextIO


class SearchLSOutput:

    ls: str
    distance_metric: str
    closest: str
    distance: str

    def __init__(self, ls: str, distance_metric: str, closest: str, distance: str):
        """

        Parameters
        ----------
        ls : str
            Name of latent space
        distance_metric : str
            Name of distance function
        closest : str
            Name of closest protein family
        distance : str
            Distance from closest protein family
        """
        self.ls = ls
        self.distance_metric = distance_metric
        self.closest = closest
        self.distance = distance

    def to_stdout(self):
        print('The closest protein family to ' + self.ls + ' is ' + self.closest + ' with ' + self.distance_metric + ' distance: ' + self.distance)

    def to_file(self, fname: str, ftype: str, mode: str):
        """

        Parameters
        ----------
        fname : str
            Output filename
        ftype : str
            Output format
        mode : str
            Output mode
        """
        outf: TextIO
        with open(fname, mode) as outf:
            if ftype == "text":
                outf.write('The closest protein family to ' + self.ls + ' is ' + self.closest + ' with ' + self.distance_metric + ' distance: ' + self.distance + '\n')
            else:
                outf.write(self.ls + ',' + self.distance_metric + ',' + self.closest + ',' + self.distance + '\n')
