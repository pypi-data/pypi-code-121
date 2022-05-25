from pathlib import Path
import pkg_resources
import sys
import subprocess
import tempfile
import os
import jinja2
import platform
import warnings
import matplotlib.pyplot as plt
from PIL import Image

from preciso import run
from preciso.HDF5 import HDF5_make

"""This file contains convenience functions to allow use
of PreciSo in an high-level fashion. It consists in a wrapper
to C binaries of the PreciSo code.
"""

def version():
    """Finds the installed version of PreciSo using pkg_resources.
    
    Examples
    --------
    >>> import preciso
    >>> preciso.version()
    '0.1.2'
    """
    return pkg_resources.get_distribution('Preciso').version

def runSimulation(inputFileName, temp=True, write_limit=100, nodes=None, n_samples=2, debug=False, save_title = None, save_target_path = None, save_mode = None):
    """Runs PreciSo in a temporary folder (default), using provided Input File
    and gives results in the form of a PrecisoResults object. **Run in temporary directories is not supported on Windows currently. It will issue a warning and fallback to temp=False.**

    Parameters
    ----------

    inputFileName : pathlib.Path object or str
        The path to the input file to use in Preciso. Can be given either as
        a `pathlib.Path` object (recommended as it is cross-plateform) or as
        a `str` that complies with the computer's filesystem.
    temp : bool
        If True, PreciSo will run in a temporary folder, and its results files will
        be read and outputed. All files will be discarded at the end.
        If false, `run_input_file` is directly called and output files will be created
        in current working directory.
    write_limit : int
        The maximum total size of the files written by PreciSo, in Megabytes. It prevents PreciSo from filling up your computer's hard drive. 
        Default value is 100MB. If `write_limit` is of a type different than `int`, no limit is set. **Windows is not supported**, there will be **no limit on this plateform**.
    nodes : List of int (optional)
        The id of the node(s) for which we want the precipitates distribution. Default is [0].
    
    save_title : str
        Specify if the results and parameters are to be saved in an HDF5 file (for testing purposes for now).
        In that case, this is the name of the saved file. Make sure its extension is '.hdf5'
    save_target_path : str or Pathlib.path
        Specify only if save_title is set.
        The directory where the HDF5 file will be saved. Default is current directory.
    save_mode : char
        Specify only if save_title is set.
        The opening mode for the save file. Default is 'x' to prevent overwritting existing data; use 'w' to bypass.


    Returns
    ----------
    out : preciso.Results object
        An object that stores the results from a PreciSo simulation.

    """
    if nodes is None:
        nodes = [0]

    initial_dir = os.getcwd()
    myres = None
    inputFileName = Path(inputFileName)
    
    if platform.system() == "Windows":
        warnings.warn(
            "Run in temporary directories is not supported on Windows currently. Falling back to temp=False. It means that preciso will write its results files in the current working directory : {}.\n To disable this warning, set temp=False.\n More details : https://arnall.gitlab.io/preciso/preciso.html#preciso.preciso.runSimulation".format(os.getcwd()),stacklevel=2)
        temp = False

    if temp:
        if not Path(inputFileName).is_absolute():
            inputFileName = Path(initial_dir).joinpath(inputFileName)
        try:
            with tempfile.TemporaryDirectory() as tdir:
                os.chdir(tdir)
                myres = run.run_input_file(inputFileName, nodes, n_samples, write_limit, debug)
        finally:
            os.chdir(initial_dir)
    else:
        myres = run.run_input_file(
            inputFileName, nodes, n_samples, write_limit, debug)

    if not(save_title is None):
        HDF5_make(save_title, inputFileName, res = myres, target_path = save_target_path, mode = save_mode, temp = temp, write_limit = write_limit, nodes = nodes, n_samples = n_samples, debug = debug)

    return myres


def fillTemplate(template_string, values):
    """Fills-in a template that complies with Jinja2 convention.
    Variables appear as `{{variable}}` in the template.

    Parameters
    ----------

    template_string : str
        The template to fill-in, in plain-text format.

    values : dict
        A dictionnary containing variables to replace (keys) and
        values to put in place (values).

    Returns
    ----------
    filled_template : str
        The template, with variables replaced by their values. If there are
        keys without matching values, they will be **ignored** (i.e replaced by
        an empty string).

    Examples
    --------
    >>> import preciso
    >>> template = "Hello {{ something }} !"
    >>> variables = {"something":"World"}
    >>> preciso.fillTemplate(template, variables)
    'Hello world !'
    >>> preciso.fillTemplate(template, {"somessshing":"World"})
    'Hello  !'
    """
    if isinstance(values, dict):
        jinja_template = jinja2.Template(template_string)
        return jinja_template.render(**values)
    else:
        raise TypeError("`values` should be `dict`, got {} instead.".format(type(values)))

def logo_path():
    """
    Returns the path to the PreciSo logo as a pathlib.Path object.
    """
    return Path(pkg_resources.resource_filename('preciso','Logo-Figures.png'))

def add_logo(f, x_frac, y_frac, scale=1, alpha=1, path='', dpi=300):
    """
    Add an image to the figure (not the axes)

    Parameters
    ----------

    f: 
        a matplotlib figure instance.
    x_frac: 
        the fraction of the x dimension of the figure to set the offset to. Must be a float.
    y_frac: 
        the fraction of the y dimension of the figure to set the offset to.
        Must be a float.
    scale: 
        The float scale by which to multiply to the image pixel dimensions. Defalut is 1.
    alpha: 
        Sets the opacity (named alpha in matplotlib). Must be a float between 0 and 1. Default is 1 (full opacity).
    path: 
        The path to the image to add to the figure, as a string or a pathlib.Path object. By default, it adds the PreciSo logo image that is included in the python package. 
    dpi: 
        Set the figure resolution in dpi (dots per inch). Default is 300.
    
    Examples
    --------
    To insert a preciso logo at the center of the figure, at half it's original size, with 15% opacity.

    >>> import preciso
    >>> import matplotlib.pyplot as plt
    >>> f = plt.Figure()
    >>> f = add_logo(f, x_frac=0.5, y_frac=0.5, scale=0.5, alpha=0.15)
    """
    assert isinstance(f, plt.Figure), "f must be a matplotlib figure instance"
    assert type(x_frac) == float and type(y_frac) == float,  "x_frac and y_frac must be floats."

    if path == '':
        path = logo_path()
    
    with Image.open(path) as im:
        f.set_dpi(dpi)
        im.thumbnail((int(im.size[0] * scale), int(im.size[1] * scale)), Image.ANTIALIAS)
        img_x, img_y = im.size[0], im.size[1]
        x_offset = int((f.bbox.xmax * x_frac - img_x/2))
        y_offset = int((f.bbox.ymax * y_frac - img_y/2))

        plt.figimage(im, xo=x_offset, yo=y_offset, origin='upper', zorder=10, alpha=alpha)