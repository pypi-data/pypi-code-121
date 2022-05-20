from typing import TextIO


class SearchSQOutput:
    seq: str
    closest: str
    accuracy: str

    def __init__(self, seq: str, closest: str, accuracy: str):
        """

        Parameters
        ----------
        seq : str
            Name of sequence
        closest : str
            Name of closest protein family
        accuracy : str
            Accuracy
        """
        self.seq = seq
        self.closest = closest
        self.accuracy = accuracy

    def to_stdout(self):
        print('The closest protein family to ' + self.seq + ' is ' + self.closest + ' with average accuracy: ' + self.accuracy)

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
                outf.write('The closest protein family to ' + self.seq + ' is ' + self.closest + ' with average accuracy: ' + self.accuracy + '\n')
            else:
                outf.write(self.seq + ',' + self.closest + ',' + self.accuracy + '\n')
