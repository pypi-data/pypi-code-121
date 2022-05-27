
def setup_plot_formatting():
    """set up matplotlib plot formatting"""

    # TODO: load from config

    # adapted from https://stackoverflow.com/a/39566040

    import matplotlib.pyplot as plt

    # plt.rcParams['figure.dpi'] = 96

    # SMALL_SIZE = 12
    # MEDIUM_SIZE = 14
    # BIGGER_SIZE = 16
    SMALL_SIZE = 18
    MEDIUM_SIZE = 20
    BIGGER_SIZE = 24

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    plt.rc('figure', figsize=[12, 12])  # size of plots

    plt.rcParams['figure.facecolor'] = '#FFFFFF'
    plt.rcParams['font.family'] = 'Monospace'

    plt.rc('lines', linewidth=3)  # width of lines

