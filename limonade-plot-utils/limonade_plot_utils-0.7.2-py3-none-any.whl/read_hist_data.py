import numpy as np
import pathlib as pl
import pathlib
# import PyQt5
from types import SimpleNamespace
# matplotlib.use('Qt5Agg')
print('Loading Qt5 frontend!')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import limonade.histo_utils as hut
from limonade.data import load_config
from limonade.utils import get_limonade_config


def read_hist_data(**kwargs):
    """
    Histoplot takes a list of ascii histogram paths as input and plots them to the same figure.

    The ascii files have to be in comma separated format and contain two, three or four columns.
    First column is the left edge of the bin, next is the value of the bin and if present the next two columns are the
    lower and upper errors. The error is taken to be symmetric if only three columns are present.

    :param data_in: a list of paths to ascii histogram files or a list of data in a 2d np arrays
    :param errplot: A string controlling error plot style. Either one character code to set all plots or a string with
                    one character per input file. If the string is too short, error plots will be dropped for the last
                    files, if the string is too long the excess characters are ignored. Valid characters are:
                    :b: Standard error bar plot
                    :B: Error bands.
                    :x: No error plot for this input file
    :param style:   Name of a Matplotlib style sheet located in config/style

    :return:
    """
    # setup path config with global configuration directory
    path_cfg = get_limonade_config()

    if len(kwargs) == 0:
        args = parse_args()
    else:
        print(kwargs)
        args = SimpleNamespace(**kwargs)

    data_in = args.file

    if args.plotstyle is not None:
        # style should be a style dict or path to matplotlib stylesheet. In practice it is a stylesheet saved in
        # config/stylecfg dir
        plt.style.use(pl.Path(path_cfg['cfg_dir']) / 'style' / (args.plotstyle + '.mplstyle'))
    else:
        try:  # try to load default style
            plt.style.use(pl.Path(path_cfg['cfg_dir']) / 'style' / ('default' + '.mplstyle'))
        except (FileNotFoundError, OSError):
            pass

    # Stupid dirty tricks to not mess up...
    if isinstance(data_in, str):
        datas = hut.read_histo([data_in], unpack=False)
    elif isinstance(data_in, np.ndarray):
        datas = [data_in]
    elif isinstance(data_in[0], np.ndarray):
        datas = []
        for inp in data_in:
            datas.append(inp)
    else:  # I guess this is a list of strings or paths then
        datas = hut.read_histo(data_in, unpack=False)

    # parsing errplot. Note that if the data file lacks error columns, no error plots are defined even if the
    # string here is set correctly.
    err_str = ''
    for achar in args.errorplot:
        if achar in ('bBx'):
            err_str += achar
        else:
            raise SyntaxError('Illegal error plot character {}.'.format(achar))
    if len(err_str) == 1:  # all plots share the same
        err_str = err_str * len(datas)
    elif len(err_str) < len(datas):  # last ones plotted without errors
        err_str = err_str + ('-' * (len(datas) - len(err_str)))

    fig, ax = plt.subplots()
    for err_type, ahisto in zip(err_str, datas):
        # check if error data
        if err_type == 'b' and ahisto.shape[1] > 2:

            if ahisto.shape[1] == 3:
                plt.errorbar(ahisto[:, 0], ahisto[:, 1], yerr=np.abs(ahisto[:, 2]), capsize=2, elinewidth=1,
                             linewidth=1, linestyle='None', marker='.', markersize=3, color='k')
            else:
                plt.errorbar(ahisto[:, 0], ahisto[:, 1], yerr=np.abs(ahisto[:, 2:4].T))

        elif err_type == 'B' and ahisto.shape[1] > 2:

            if ahisto.shape[1] == 3:
                bandplot(ahisto[:, 0], ahisto[:, 1], np.abs(ahisto[:, 2:].T), ax)
            else:
                bandplot(ahisto[:, 0], ahisto[:, 1], np.abs(ahisto[:, 2:4].T), ax)
        else:

            plt.plot(ahisto[:, 0], ahisto[:, 1], linewidth=0.5, drawstyle='steps-pre')

    plt.show()

def bandplot(x, y, yerr, ax):
    # end points of errors
    yp = y + yerr[0, :]
    yn = y - yerr[-1, :]
    print('error verts')
    print(yp)
    print(yn)
    
    vertices = np.block([[x, x[::-1], x[-1]],
                         [yp, yn[::-1], yn[-1]]]).T  # add a vertice for the final closepoly

    codes = Path.LINETO * np.ones(len(vertices), dtype=Path.code_type)
    codes[0] = Path.MOVETO
    codes[len(vertices)-1] = Path.CLOSEPOLY

    path = Path(vertices, codes)
    #print(vertices)
    #print(codes)
    patch = PathPatch(path, facecolor='C0', edgecolor='none', alpha=0.3)
    
    ax.plot(x, y)
    ax.add_patch(patch)

    print('Done')

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Read and plot csv histogram files.')
    parser.add_argument('file', metavar='datafile', type=str, nargs='*',
                        help='Path to histogram file. Several can be supplied and will be plotted to same figure.')
    parser.add_argument('-p', '--plotstyle', metavar='plot', type=str, default=None,
                        help='A matplotlib stylesheet file name located in config/style.')
    parser.add_argument('-e', '--errorplot', type=str, default='b',
                        help='String that defines error plot type. "b" for bar plot, "B" for band plot or "x" for no error plot. Either one type or one for each input file.')
    parser.add_argument('-c', '--custom', action='store_true',
                        help='Custom histogram with no metadata.')
    args = parser.parse_args()
    print(args.file)
    #paths = [pl.Path(fil).parent for fil in args.file]
    paths = [pl.Path(fil) for fil in args.file]
    # here we read the local configuration of the first file, but add other paths to the config. This information is not
    # really used anywhere though and is skipped on -c flag
    if not args.custom:
        confd = load_config(paths, det_name='histogram', from_global_conf=False)
        args.cfg = confd
    return args

if __name__ == '__main__':

    read_hist_data()
