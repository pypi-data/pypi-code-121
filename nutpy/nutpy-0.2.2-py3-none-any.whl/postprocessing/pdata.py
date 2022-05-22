def plot_temporal_map(self, map_type="TAT", N=256, units='s', cbar_size=0.064, sensor_id=None):
    """
    Plot temporal analysis results

    Parameters
    ----------
    map_type : str
        Result to be plotted
    N : int
        Mesh for plotting

    Returns
    -------
    fig :  matplotlib figure
        Plotted figure

    """

    factor = 1.

    if map_type in cte.tags_dict:
        pass
    else:
        raise NameError(f"'{map_type}' result does not exist")

    if sensor_id is None:
        data = self.sat.visibility_global_results()[map_type].values
    else:
        data = self.sat.visibility_sensor_results(sensor_id)[map_type].values
    main_label = cte.tags_dict[map_type]
    default_units = cte.units_dict[map_type]

    if default_units is None:
        units_label = ''
    else:
        if units == 's':
            factor = 1.
        elif units == 'min':
            factor = 60.
        elif units == 'h':
            factor = 3600.
        units_label = ' (' + units + ')'
        data = data * 1. / factor

    label = main_label + units_label

    fig = pgraph.plot_map(data, label, N, cbar_size)

    return fig




def numerical_map(mission,
                  quantity,
                  N,
                  fig_flag,
                  units,
                  cbar_size,
                  sensor_id
                  ):
    """
    Calculates numerically the demanded quantity for all the celestial
    sphere and plots it.

    Parameters
    ----------
    mission : Nut class
        Mission with temporal analysis results
    quantity : str
        Quantity to be computed
    N : int
        Resolution of results
    fig_flag : bool
        If True, figure is returned
    delta_detector : float
        Used for detector analysis (deg)
    units : str
        Time units for the output
    cbar_size : float
        Size of the colorbar
    sensor_id : int
        Sensor id number

    Returns
    -------
    fig : matplotlib figure
        Figure of profile
    data : ndarray (N)
        Results of calculations (value per pixel for Healpix scheme)
    """

    factor = 1.

    if quantity in cte.tags_dict:
        pass
    else:
        raise NameError(f"'{quantity}' result does not exist")

    if sensor_id is None:
        data = mission.sat.visibility_global_results()[quantity].values
    else:
        data = mission.sat.visibility_sensor_results(sensor_id)[quantity].values

    main_label = cte.tags_dict[quantity]
    default_units = cte.units_dict[quantity]

    if default_units is None:
        units_label = ''
    else:
        if units == 's':
            factor = 1.
        elif units == 'min':
            factor = 60.
        elif units == 'h':
            factor = 3600.
        units_label = ' (' + units + ')'
        data = data * 1. / factor

    label = main_label + units_label

    fig = pgraph.plot_map(data, label, N, cbar_size)

    return fig


       def numerical_map(mission,
                      N=256,
                      quantity="TAT",
                      fig_flag=True,
                      units='s',
                      cbar_size=0.064,
                      sensor_id=None
                      ):
        """
        Calculates numerically the demanded quantity for all the celestial
        sphere and plots it.

        Parameters
        ----------
        mission : Nut class
            Mission with temporal analysis results
        N : int
            Resolution of results
        quantity : str
            Quantity to be computed
        fig_flag : bool
            If True, figure is returned
        units : str
            Time units for the output
        cbar_size : float
            Size of the colorbar
        sensor_id : int
            Sensor id number

        Returns
        -------
        fig : matplotlib figure
            Figure of profile
        data : ndarray (N)
            Results of calculations (value per pixel for Healpix scheme)
        """

        pass


    cartopy==0.19.0.post1

    import cartopy.crs as ccrs

        if projection == 'orthographic':
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Orthographic(0, 0))

        yaxis = False

        lon_grid_plot = lon_grid.value
        lat_grid_plot = lat_grid.value

        lon_grid, lat_grid = np.meshgrid(lon, lat)

        im = ax.pcolormesh(lon_grid, lat_grid, map_plot, transform=ccrs.PlateCarree())

    else:

