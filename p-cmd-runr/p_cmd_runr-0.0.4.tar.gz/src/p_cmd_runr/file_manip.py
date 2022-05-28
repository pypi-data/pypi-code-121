
import sys
import functools
import math



def flatten(lines):
    """
    Description:
        Removes white spaces that may be part of a list of strings, specificaly "\n" characters.
        The result will be that there will be no more than one "\n" between lines.
    Parameters:
        - lines list of strings.
    Returns:
        List of strings without the strings made up of only whitespaces.
    """
    return [l for l in lines if l.strip()]

 

def flatten_file(filename):
    """
    Desription:
        Transforms a text file so that there is only a single "\n" character between lines.
        The file must be a text file and it is overwritten with the change.
    Parameters:
        - filename name of the file.
    """
    with open(filename, mode="rt", encoding="utf-8") as fp:
        lines = fp.readlines()
        lines = flatten(lines)
    with open(filename, mode="wt", encoding="utf-8") as fp:
        for l in lines:
            fp.write(l)



def squeeze(s1, s2):
    """
    Description:
        Takes two strings and returns a concatenation of those strings such that there are no consecutive "\n" characters between them.
        The result will be that there will be no more than two "\n" between lines.
    """
    s3 = s2.strip("\n")
    s4 = s1.strip("\n") + s3
    if not s4:
        return "\n\n"
    if s1.endswith("\n\n") and not s2:
        return s1.rstrip() + "\n\n"
    if s1.endswith("\n") and not s2:
        return s1.rstrip() + "\n\n"
    if s1.endswith("\n\n") and s2:
        return s1.rstrip() + "\n\n" + s2
    return s1.rstrip() + "\n" + s2



def squeeze_file(filename):
    """
    Description:
        Removes multiple consecutive "\n" characters that may be in a file.
        The file must be a text file and it is overwritten with the change.
    Parameters:
        - filename name of the file.
    """
    with open(filename, mode="rt", encoding="utf-8") as fp:
        lines = fp.readlines()
        res = functools.reduce(squeeze, lines)
    with open(filename, mode="wt", encoding="utf-8") as fp:
        fp.write(res)



def count_from_end(s):
    """
    Definition:
        Counts and returns the number of "\n" charecters at the end of a string.
    """
    if s.rfind("\n") == -1:
        return 0
    i = s.rfind("\n")
    if i == 0:
        return 1
    if i == len(s) - 1:
        return 1 + count_from_end(s[0:-1])
    return 0



def deflate(s1, s2):
    """
    Description:
        Takes two strings and returns a concatenation of those strings such that there are no excessive "\n" characters between them.
        The result will be that there will be no duplication of "\n" characters between lines.
    """
    if not s2.strip():
        return s1 + "\n"
    count = count_from_end(s1)
    count = math.ceil(count / 2)
    return s1.rstrip() + count * "\n" + s2



def deflate_file(filename):
    """
    Description:
        Removes duplication of "\n" characters that may be in a file.
        The file must be a text file and it is overwritten with the change.
    Parameters:
        - filename name of the file.
    """
    with open(filename, mode="rt", encoding="utf-8") as fp:
        lines = fp.readlines()
        res = functools.reduce(deflate, lines)
    with open(filename, mode="wt", encoding="utf-8") as fp:
        fp.write(res)



if __name__ == "__main__":
    del sys.argv[0]
    op = sys.argv.pop(0).lower()
    print(op)
    if "f" in op:
        func = flatten_file
    elif "d" in op:
        func = deflate_file
    else:
        func = squeeze_file
    for fn in sys.argv:
        func(fn)
