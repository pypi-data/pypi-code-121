import glob
import pandas as pd

def import_file(prefix_file: str, names: list, separator="\t", header=0) -> list:
    """
    Function that given a prefix file composed by path and prexif can import
    all files with that prefix in the given folder.
    

    Parameters
    ----------
    prefix_file : string
        common prexif of files that have to be imported
    names : list of string
        vector of names of file columns
    sep : string, optional
        Separator of each column. The default is "\t".
    header : int, optional
        Number of line of the header. The default is 0.

    Returns
    -------
    char : 
        List with imported files.

    """
    
    files_char = glob.glob(prefix_file)
    char = []
    for j in files_char:
        csv = pd.read_csv(j, sep = separator, header = header, names=names)
        char.append(csv)
        print(j)
    return char


def s4(a):
    return '{:.4e}'.format(a)

def s0(a):
    return '{:.0e}'.format(a)

def s1(a):
    return '{:.1e}'.format(a)
