from typing import TextIO


class CompareLSOutput:

    a1: str
    a2: str
    distance_metric: str
    result: str

    def __init__(self, a1: str, a2: str, distance_metric: str, result: str):
        """

        Parameters
        ----------
        a1 : str
            Name of first latent space
        a2 : str
            Name of second latent space
        distance_metric : str
            Name of distance function
        result : str
            Distance
        """
        self.a1 = a1
        self.a2 = a2
        self.distance_metric = distance_metric
        self.result = result

    def to_stdout(self):
        print(self.distance_metric + ' distance between ' + self.a1 + ' and ' + self.a2 + ': ' + self.result)

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
                outf.write(self.distance_metric + ' distance between ' + self.a1 + ' and ' + self.a2 + ': ' + self.result + '\n')
            else:
                outf.write(self.a1 + ',' + self.a2 + ',' + self.distance_metric + ',' + self.result + '\n')
