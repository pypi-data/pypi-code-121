from typing import Union
from . import CompareLSOutput, SearchLSOutput, SearchSQOutput


def output_result(res: Union[
    SearchLSOutput.SearchLSOutput, SearchSQOutput.SearchSQOutput, CompareLSOutput.CompareLSOutput], fname: str, form: str, mode: str):
    """

    Parameters
    ----------
    res : Union[SearchLSOutput.SearchLSOutput, SearchSQOutput.SearchSQOutput, CompareLSOutput.CompareLSOutput]
        Result
    fname : str
        Output filename
    form : str
        Output format
    mode : str
        Output mode
    """
    if fname != "":
        res.to_file(fname, form, mode)
    else:
        res.to_stdout()
