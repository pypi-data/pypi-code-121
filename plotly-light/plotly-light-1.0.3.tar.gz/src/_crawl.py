from typing import List
from os import listdir, remove
from os.path import basename
import json
import ipynb_path


def _get_html_list_jupyter(fname: str) -> List[str]:
    """Get the list of plotly HTML file names in a jupyter notebook.
    """
    data = json.load(open(fname, 'r'))
    plotly_htmls = []
    if "cells" in data:
        for cell in data["cells"]:
            if "outputs" not in cell:
                continue
            for output in cell["outputs"]:
                if "data" in output and "text/html" in output["data"]:
                    for html in output["data"]["text/html"]:
                        if (html.startswith(f"src=\"{basename(fname)}.iframe_figures/")
                                and html.endswith(".html\"\n")):
                            plotly_htmls.append(html.split('"')[1].strip())
    return plotly_htmls


def _remove_unused_htmls() -> None:
    """Remove plot HTML files that are no longer used in the Notebook currently opened.
    """
    jupyter_fname = basename(ipynb_path.get())   # Notebook must be running in CWD
    plot_dname = f"{jupyter_fname}.iframe_figures/"

    htmls_jupyter = set(_get_html_list_jupyter(jupyter_fname))
    htmls_exist = [f"{plot_dname}{html}" for html in listdir(plot_dname) if html.endswith(".html")]

    for html in htmls_exist:
        if html not in htmls_jupyter:
            remove(html)
