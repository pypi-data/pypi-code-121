import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from astropy import units as u
from astropy_healpix import HEALPix

from nutpy.constants import plot_options


def plot_map(data, cbarlabel, N, **kwargs):
    """
    Plot temporal analysis results

    Parameters
    ----------
    data : 1D-array
        Data to plot (value per pixel for Healpix scheme))
    cbarlabel : str
        Label for the colorbar
    N : int
        Size of plotting mesh (2NxN)
    cbar_size : float
        Size of the colorbar
    projection_type : str
        Type of projection (Hammer, mollweide or orthographic)

    Returns
    -------
    fig :  matplotlib figure
        Plotted figure
    """

    map_options = {**kwargs, **plot_options}

    cbar_size = map_options['cbar_size']
    projection = map_options['projection']

    lon = np.linspace(-180., 180., 2 * N) * u.deg
    lat = np.linspace(-90., 90., N) * u.deg
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    npix = len(data)
    hp = HEALPix(nside=int(np.sqrt(npix/12)))

    map_plot = data[hp.lonlat_to_healpix(lon_grid.ravel(), lat_grid.ravel())]

    map_plot = map_plot.reshape((N, 2 * N))

    fig = plt.figure()

    ax = plt.axes(projection=projection)
    yaxis = True

    lon_grid_plot = lon_grid.to(u.radian).value
    lat_grid_plot = lat_grid.to(u.radian).value

    im = ax.pcolormesh(lon_grid_plot, lat_grid_plot, map_plot, cmap=plt.cm.jet, rasterized=True, shading='auto')

    cbar = plt.colorbar(im, fraction=cbar_size)

    cbar.set_label(cbarlabel)

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(yaxis)

    return fig


def plot_focal_plane(xd, yd, r, cases_dict=None, case_id=None, quantity='Viewed', numbered=False):
    """
    Plots focal plane results for a given case

    Parameters
    ----------
    xd : float
        X coordinates of detectors in focal plane
    yd : float
        Y coordinates of detectors in focal plane
    nd : int
        Number of detectors
    r : float
        Half-angle of the detector fov (degrees)
    cases_dict : dict
        Temporal results for point in the sky
    case_id : str
        Id of case to be plotted
    quantity : str
        Quantity to be shown
    numbered : bool
        If True, sensors Id is plotted

    Returns
    -------
    fig : matplotlib figure
        Figure of profile
    ax : axes
        Matplotlib figure axes of sensor array and FOV
    """

    fig, ax = plt.subplots(figsize=(10, 10))

    nd = len(xd)

    if case_id is None:
        sensor_data = np.zeros(nd)
        vmin_mod = 0
    else:
        case_df = cases_dict[case_id]

        sensor_data = case_df[quantity].values

        if quantity == 'Viewed' and sensor_data.min() == 1:
            vmin_mod = 0
        else:
            vmin_mod = 1

    ax.set_aspect('equal', 'box')

    cmap = matplotlib.cm.get_cmap('viridis')

    vmin = sensor_data.min() * vmin_mod
    vmax = sensor_data.max()

    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)

    for i in range(nd):
        a_circle = plt.Circle((xd[i], yd[i]), r, color=cmap(norm(sensor_data[i])))
        ax.add_artist(a_circle)
        ax.text(xd[i], yd[i], str(i), fontsize=7, color='w', horizontalalignment='center', verticalalignment='center',)

    t = np.linspace(0, 2 * np.pi, 100)
    ax.plot(np.cos(t), np.sin(t))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    if case_id is None:
        pass
    else:
        plt.colorbar(sm)

    ax.set_axis_off()

    return fig, ax
