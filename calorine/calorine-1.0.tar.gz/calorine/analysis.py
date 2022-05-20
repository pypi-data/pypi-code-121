from typing import Dict, List

from matplotlib import pyplot as plt
from .data_analysis import analyze_data
from pandas import DataFrame


# labels with units for the different properties
labels = {}
labels['temperature'] = 'Temperature (K)'
labels['potential_energy'] = 'Potential energy (eV)'
labels['Px'] = 'Pressure x (GPa)'
labels['Py'] = 'Pressure y (GPa)'
labels['Pz'] = 'Pressure z (GPa)'
labels['kx_tot'] = 'Kappa x (W/m K)'
labels['ky_tot'] = 'Kappa y (W/m K)'
labels['kz_tot'] = 'Kappa z (W/m K)'


def get_run_average(kappas: List[DataFrame],
                    nequil: int) -> dict:
    """Computes averages over several simulations and returns mean, error estimate
    and correlation length in the form of a dictionary.

    Parameters
    ----------
    kappas
        list of dataframes with data read from ``kappa.out`` files
    nequil
        number of data points to drop in the beginning to account for equilibration
    """
    df_avg = None
    for df in kappas.values():
        if df_avg is None:
            df_avg = df[df.index > nequil].copy()
        else:
            df_avg += df
    if len(kappas) == 0:
        return
    df_avg /= len(kappas)
    df_avg.dropna(inplace=True)

    tags = 'kx_tot ky_tot kz_tot'.split()
    data = {}
    for tag in tags:
        data[tag] = analyze_data(df_avg[tag])
    data = DataFrame.from_dict(data).T

    return data


def plot_thermos_split(thermos: Dict[str, DataFrame],
                       nsim_max: int = 10,
                       title: str = '') -> None:
    """Generates an overview figure of the thermodynamic data from a series of runs.

    Parameters
    ----------
    thermos
        dictionary with each entry containing a dataframe read from a ``thermo.out`` file
    nsim_max
        maximum number columns (=runs) to show
    title
        title string (optional)
    """
    tags = 'temperature potential_energy Px Py Pz'.split()
    nsim = min(nsim_max, len(thermos))
    fig, grid = plt.subplots(ncols=nsim, nrows=len(tags),
                             figsize=(12, 9), sharex='col', sharey='row')
    if len(title) > 0:
        fig.suptitle(title)
    for row, (tag, axes) in enumerate(zip(tags, grid)):
        axes[0].set_ylabel(f'{labels[tag]}')
        for ax, (run, df) in zip(axes, thermos.items()):
            ax.plot(df.index, df[tag])
            ax.set_xlabel('Index')
            if row == 0:
                ax.text(0.06, 0.92, run, transform=ax.transAxes)
    plt.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=0)


def plot_kappas_split(kappas: Dict[str, DataFrame],
                      nsim_max: int = 10,
                      title: str = '') -> None:
    """Generates an overview figure of the thermal conductivity data from a series of runs.

    Parameters
    ----------
    kappas
        dictionary with each entry containing a dataframe read from a ``kappa.out``
        or ``hac.out`` file
    nsim_max
        maximum number columns (=runs) to show
    title
        title string (optional)
    """
    tags = 'kx_tot ky_tot kz_tot'.split()
    nsim = min(nsim_max, len(kappas))
    fig, grid = plt.subplots(ncols=nsim, nrows=len(tags),
                             figsize=(12, 6), sharex='col', sharey='row')
    if len(title) > 0:
        fig.suptitle(title)
    for row, (tag, axes) in enumerate(zip(tags, grid)):
        axes[0].set_ylabel(f'{labels[tag]}')
        for ax, (run, df) in zip(axes, kappas.items()):
            ax.plot(df.index, df[tag])
            ax.set_xlabel('Index')
            if row == 0:
                ax.text(0.06, 0.92, run, transform=ax.transAxes)
    plt.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=0)


def plot_thermos_with_average(thermos: Dict[str, DataFrame],
                              title: str = '') -> None:
    """Generates an overview figure of the thermodynamic data from a series of runs.

    Parameters
    ----------
    kappas
        dictionary with each entry containing a dataframe read from a ``thermo.out`` file
    title
        title string (optional)
    """
    df_avg = None
    for df in thermos.values():
        if df_avg is None:
            df_avg = df.copy()
        else:
            df_avg += df
    if len(thermos) == 0:
        print('No data')
        return
    df_avg /= len(thermos)

    tags = 'temperature potential_energy Px Py Pz'.split()
    fig, axes = plt.subplots(ncols=len(tags), figsize=(12, 3), sharex=True)
    if len(title) > 0:
        fig.suptitle(title)
    for tag, ax in zip(tags, axes):
        ax.set_ylabel(f'{labels[tag]}')
        ax.set_xlabel('Index')
        for k, (run, df) in enumerate(thermos.items()):
            ax.plot(df.index, df[tag], color=f'{0.2+0.6*k/len(thermos)}')
        ax.plot(df_avg.index, df_avg[tag], color='red')
    plt.tight_layout()


def plot_kappas_with_average(kappas: Dict[str, DataFrame],
                             title: str = '') -> None:
    """Generates an overview figure of the thermal conductivity data from a series of runs.

    Parameters
    ----------
    kappas
        dictionary with each entry containing a dataframe read from a ``kappa.out``
        or ``hac.out`` file
    title
        title string (optional)
    """
    df_avg = None
    for df in kappas.values():
        if df_avg is None:
            df_avg = df.copy()
        else:
            df_avg += df
    if len(kappas) == 0:
        print('No data')
        return
    df_avg /= len(kappas)

    tags = 'kx_tot ky_tot kz_tot'.split()
    fig, axes = plt.subplots(ncols=len(tags), figsize=(9, 3), sharex=True)
    if len(title) > 0:
        fig.suptitle(title)
    for tag, ax in zip(tags, axes):
        ax.set_ylabel(f'{labels[tag]}')
        ax.set_xlabel('Index')
        for k, (run, df) in enumerate(kappas.items()):
            ax.plot(df.index, df[tag], color=f'{0.2+0.6*k/len(kappas)}')
        ax.plot(df_avg.index, df_avg[tag], color='red')
    plt.tight_layout()


def plot_kappas_distribution(kappas: Dict[str, DataFrame],
                             nequil: int = 0,
                             title: str = '') -> None:
    """Generates an overview figure of the thermal conductivity data from a series of runs.

    Parameters
    ----------
    kappas
        dictionary with each entry containing a dataframe read from a ``kappa.out`` file
    nequil
        number of steps to drop in the beginning of each trajectory to account for equilibration
    title
        title string (optional)
    """
    df_avg = None
    for df in kappas.values():
        if df_avg is None:
            df_avg = df[df.index > nequil].copy()
        else:
            df_avg += df
    if len(kappas) == 0:
        print('No data')
        return
    df_avg /= len(kappas)

    tags = 'kx_tot ky_tot kz_tot'.split()
    fig, axes = plt.subplots(ncols=len(tags), figsize=(9, 3), sharey=True)
    if len(title) > 0:
        fig.suptitle(title)
    for col, (tag, ax) in enumerate(zip(tags, axes)):
        if col == 0:
            ax.set_ylabel('Density')
        ax.set_xlabel(labels[tag])
        for k, (run, df) in enumerate(kappas.items()):
            df = df[df.index > nequil]
            try:
                ax.hist(df[tag], density=True, color=f'{0.2+0.6*k/len(kappas)}')
            except ValueError:
                print(f'Failed to generate histogram for {tag}')
        try:
            ax.hist(df_avg[tag], density=True, color='red')
        except ValueError:
            print('Failed to generate histogram for average')
    plt.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=0)
