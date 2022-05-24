from pathlib import Path
import sys
import time
from matplotlib import pyplot as plt
#try:
#    import PyQt5
#    matplotlib.use('Qt5Agg')
#    print('Loading Qt5 frontend!')

#except:
#    pass

from limonade.data import load_config, Data
from limonade.loaders import loader_dict
from limonade.utils import load_plot_config
from limonade.misc import parse_time, parse_file, natural_keys
from limonade import histo_utils as hut
from limonade_plot_utils.utils import unfold_plot_cfg, sort_data, collate_plots, plot_data


def read_list_data():
    #cfg, data_dirs, data_names, plot, time_slice=None, reset=False, calibrate=True,
    #          save=False, saveall=False, phd=False, effcal=None, style=None):

    """
    The arguments:

    :param cfg:         Configuration dict
    :param data_dirs:   Path to data dir, one per loaded datafile.
    :param data_names:  Base names of the data, one for each path.
    :param plot:        Name of the plot configuration file without the _plotcfg.json.
    :param time:        Time interval in nanoseconds
    :param reset:       Flag to read data again from raw files
    :param calibrate:   Plot data with calibrated or raw axes
    :param save:        Plotted data as .csv files
    :param saveall:     Plotted data as .csv files, but including empty channels (for math operations)
    :param phd:         Plotted data as .phd files
    :param effcal:      Efficiency calibration for phd file
    :param plotstyle:   Name of the style configuration file without the _stylecfg.json.
    :return:


    """
    #cfg, data_dirs, data_names, plot, time_slice=None, reset=False, calibrate=True,
    #          save=False, saveall=False, phd=False, effcal=None, style=None
    start_time = time.time()
    arg_dict = parse_inputs()
    print(arg_dict)
    canvas_cfg = load_plot_config(arg_dict.cfg, arg_dict.plot)

    # data_paths = [data_dirs[idx] / data_names[idx] for idx in range(len(data_dirs))]

    data = Data(arg_dict.cfg)
    data.load_data(arg_dict.data_dirs, arg_dict.data_names, reset=arg_dict.reset)

    stop_time = time.time()
    print('Full data processing took {} seconds.'.format(stop_time - start_time))

    data_path = data.config.path['home']
    time_slice = arg_dict.time
    if time_slice is not None:
        if time_slice[1] is None:
            time_slice = (time_slice[0], data.get_end_time())
    else:
        time_slice = [0, data.get_end_time()]

    if arg_dict.plotstyle is not None:
        # style should be a style dict or path to matplotlib stylesheet. In practise it is a stylesheet saved in
        # config/stylecfg dir
        print(Path(arg_dict.cfg.path['cfg_dir'])/'style'/arg_dict.plotstyle)
        plt.style.use(Path(arg_dict.cfg.path['cfg_dir'])/'style'/arg_dict.plotstyle)

    # plotting setup part
    plot_list = []

    plot_cfg_list = unfold_plot_cfg(canvas_cfg)
    #print(plot_cfg_list)
    # plot_list = [Plot(x, cfg, time_slice) for x in plot_cfg_list]

    # filling plots
    # data: Data, cfg_list: list, time_slice: Optional[list], plot_list: Optional[list]
    plot_list = sort_data(data, plot_cfg_list, time_slice)

    # bunching similar plots in the same axis.
    figlist = collate_plots(plot_list)

    # set up the plot
    ax_list = []
    for subplot_list in figlist:
        # Create a figure
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        # We cannot touch the config in a command line tool, so the canvas config is just read from the 
        # first Plot instance
        plot_data(subplot_list, subplot_list[0].canvas_cfg, ax)

    plt.show()

    # Now saving data in ASCII if asked:
    if arg_dict.save:
        print('Saving histograms to disk!')
        for aplot in plot_list:
            title, legend, labels = aplot.get_plot_labels()
            hut.write_ascii(aplot, out_path=data_path, out_name=legend, calibrate=arg_dict.uncalibrate, saveall=arg_dict.save_full)
    if arg_dict.save_phd:
        print('Saving .phd file to disk!')
        for aplot in plot_list:
            title, legend, labels = aplot.get_plot_labels()
            hut.write_phd(aplot, out_path=data_path, out_name=legend+'_phd', effcal=arg_dict.effcal)


def parse_inputs():
    import argparse

    parser = argparse.ArgumentParser(description='Read and plot data.')

    parser.add_argument('directory', metavar='datadir', type=str,
                        help='Data directory. A wildcard expression can be given for chainloading several directories.')
    parser.add_argument('plot', metavar='plot', type=str, help='plot macro name')
    parser.add_argument('-f', '--filename', metavar='file', type=str,
                        help='name of datafile if not the same as datadir. Wildcards can be used, but the file name'
                             'has to be unique.')
    parser.add_argument('-t', '--time', metavar=('t'), type=str, nargs='+',
                        help='Start and optionally end time of histogram. The base unit of time (s, m, h, or d) can '
                             'be given as last argument (default minutes). ')
    parser.add_argument('-r', '--reload', metavar='reload', type=str, nargs='?',
                        help='Reread the data from binary file using given configuration. If no argument is given the '
                             'local configuration file will be used.')
    parser.add_argument('-u', '--uncalibrate', action='store_false',
                        help='skip energy calibration')
    parser.add_argument('-s', '--save', action='store_true',
                        help='Save a csv file of the plot')
    parser.add_argument('-ss', '--save_full', action='store_true',
                        help='Save a csv file of the plot including empty bins for math')
    parser.add_argument('-S', '--save_phd', action='store_true',
                        help='Save a phd file of the plot')
    parser.add_argument('-p', '--plotstyle', metavar='style_name', type=str,
                        help='name of mplstyle file for plot.')
    parser.add_argument('-e', '--effcal', metavar='effcal_name', type=str,
                        help='name of effcal file for phd.')
    parser.add_argument('--profile', action='store_true',
                        help='Run with profiling enabled.')
    args = parser.parse_args()
    '''
    :param cfg:         Configuration
    :param data_dirs:   Path to data dir, one per loaded datafile.
    :param data_names:  Base names of the data, one for each path.
    :param plot:        Name of the plot configuration file without the _plotcfg.json.
    :param time:        Time interval in given
    :param reset:       Flag to read data again from raw files
    :param calibrate:   Plot data with calibrated or raw axes
    :param save:        Plotted data as .csv files
    :param saveall:     Plotted data as .csv files, but including empty channels (for math operations)
    :param style:       Name of the style configuration file without the _stylecfg.json.
    '''

    # check if a wildcard was given and use it
    path_str = args.directory
    if any([wc in path_str for wc in ('*', '?')]):
        apath = Path(path_str).parent
        expression = Path(path_str).name
        paths = [str(x) for x in apath.glob(expression) if x.is_dir()]

        # and now the stupid natural sorting thing
        #pathnames = [str(x) for x in paths]
        #print(paths)
        paths.sort(key=natural_keys)
        print('Paths')
        for p in paths:
            print(p)
        paths = [Path(x) for x in paths]
    else: 
        apath = Path(path_str)
        if apath.is_dir():
            paths = [apath]

        else:
            errstr = 'Invalid path! {}'.format(path_str)
            raise FileNotFoundError(errstr)
    print('Loading from paths:', paths)
    args.data_dirs = paths
    # detector configuration is loaded preferably from data directory. If this fails, data must be read with -r option
    # giving the detector name as input.
    if args.reload is not None:
        det_name = args.reload
        args.reset = True
    else:
        det_name = None
        args.reset = False
    confd = load_config(paths, det_name=det_name, from_global_conf=args.reset)
    args.cfg = confd
    # Currently several data files in a single directory is not implemented.
    # It will not be implemented in the future either.
    # Names has a single base name per directory in paths.
    names = []
    for adir in paths:
        base_name = parse_file(adir, args.filename, confd)  # data_type=confd.det['data_type'],
                               #index_var=confd.det['index_variable']['name'])
        print('base_name:', base_name)
        if len(base_name) > 1:
            print('too many data files!')
            sys.exit()
        else:
            names.append(base_name[0])
    args.data_names = names
    if args.time is not None:
        args.time = parse_time(args.time, confd)

    if args.plotstyle is not None:
        args.plotstyle = args.plotstyle + '.mplstyle'
    else:
        args.plotstyle = None

    if args.save_full:  # full csv switch sets csv saves on automatically
        args.save = True
    
    return args
        

if __name__ == '__main__':

    read_list_data()
