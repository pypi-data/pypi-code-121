import os

import numpy as np
import pandas as pd

"""
ic modules provides a class (icCMS) handling ic operation based on a pandas dataframe
The ic DataFrame is based on geom which contains several information on the ecal
geometry.
The variable ic.geom (pandas dataframe) contains all the ecal mapping (electronic, geometry...)
"""


#######################################################################################
# -- The main geometry pandas DataFrame
geomDefFile = os.path.dirname(__file__) + '/data/ecalMapping.v1.0.0.txt'
# geom = pd.read_csv(geomDefFile, sep='\t').rename(columns=lambda x: x.strip())  # remove trailing whitespaces
geom = pd.read_csv(geomDefFile)

# -- add some variables
geom['eta'] = geom.groupby('ieta')['eta'].transform('mean')  # redefined eta
geom['producer'] = geom['fabric'].replace({1: 'BCTP', 2: 'SIC', 3: 'BCTP'})


# -- add geom variables for IC computation is required
def add_ic_geom():
    geom['eta_module'] = geom['ieta'].apply(eta_module)  # module number in eta
    geom['phi_module'] = np.where(np.abs(geom['eta_module']) < 4.5, (geom['iy'] - 1) // 20 + 1, 99)  # module number in phi
    geom['ieta_range'] = geom['ieta'].apply(ieta_range)  # ieta range as defined for IC combination


#######################################################################################
# -- helper function for plotting ICs
# -- based on older numpy functions from Fabrice (might not be the most adequate)
def plot2D_eb(axis, data, title='', zAxis=(0.95, 1.05), cmap='terrain'):
    import matplotlib.pyplot as plt
    ics = np.full((171, 360), np.nan)
    ics[data['ix'] + 85, data['iy'] - 1] = data[data.columns[2]]
    eb = axis.pcolormesh(np.linspace(0.5, 360.5, num=361), np.linspace(-85.5, 85.5, num=172),
                         ics, cmap=cmap, vmin=zAxis[0], vmax=zAxis[1])
    axis.set_xlabel('i$\phi$')
    axis.set_ylabel('i$\eta$')
    axis.set_title(title)
    plt.colorbar(eb, ax=axis)
    return eb


def plot2D_ee(axis, data, title='', zAxis=(0.95, 1.05), cmap='terrain'):
    import matplotlib.pyplot as plt
    ics = np.full((100, 100), np.nan)
    ics[data['ix'] - 1, data['iy'] - 1] = data[data.columns[2]]

    ee = axis.pcolormesh(np.linspace(0.5, 100.5, num=101), np.linspace(0.5, 100.5, num=101),
                         ics.T, cmap=cmap, vmin=zAxis[0], vmax=zAxis[1])
    axis.set_xlabel('i$_x$')
    axis.set_ylabel('i$_y$')
    axis.set_title(title)
    plt.colorbar(ee, ax=axis)
    return ee


#######################################################################################
def join_eb_ee(eb, ee, name=''):
    """
    combined 2 icCMS (one for EB, one for EE) into a single one for all Ecal
    """
    out = eb.copy()
    out = out.where(out['iz'] == 0, ee)
    return icCMS(out)


def icCovCor(ic1, ic2, var='ic', groupby='ieta'):
    """
    Compute correlation (and covariance) between 2 icCMS
    var  : reference variable in ics
    group: used in groupby (directly passed to groupby)
    returns the covariance and the correlation as pandas Series (ic.geom style)
    """

    rel = [i[var] - i.groupby(groupby)[var].transform('mean') for i in [ic1, ic2]]
    std = [i.groupby(groupby)[var].transform('std') for i in [ic1, ic2]]
    ic1['tmp_cov'] = (rel[0] * rel[1])
    cov = ic1.groupby(groupby)['tmp_cov'].transform('mean')
    cor = cov / (std[0] * std[1])
    del ic1['tmp_cov']

    return cov, cor


#######################################################################################
class icCMS(pd.DataFrame):
    def __init__(self, iov=None, name='ICs', error=True):
        """
        class icCMS allows for ic computation and visualisation. It is based on the geom variable
        to allow for plotting, averaging other any variable available in geom.
        It can also plot any variable in geom.
        Parameters:
        -----------
        iov      : input file (None implies ic = 1).
            - name of simple txt input file under the format ix iy iz ic eic (eic is optional)
            - pandas dataframe containing hashedId and  ic column (assuming it is from iov.xml_file.payload)
        name     : optional name
        error: is False set eic = 1,
                   use when the txt input file includes error = 0
                    (default True)
        """

        if isinstance(iov, icCMS):
            super(icCMS, self).__init__(iov)
        elif isinstance(iov, pd.DataFrame):
            super(icCMS, self).__init__(iov)
        elif isinstance(iov, str):
            try:
                data = pd.read_csv(iov, delim_whitespace=True, header=None, names=['ix', 'iy', 'iz', 'ic', 'eic'], usecols=[0, 1, 2, 3, 4])
            except pd.errors.ParserError:
                data = pd.read_csv(iov, delim_whitespace=True, header=None, names=['ix', 'iy', 'iz', 'ic'], usecols=[0, 1, 2, 3])
                data['eic'] = 1
            data.drop_duplicates(inplace=True)
            if not error:
                data['eic'] = 1

            # trick to remove points when the error is 999, i.e. crystal IC not measured by this method
            data['eic'].where(data['eic'] < 99, 0, inplace=True)
            data['ic'].where(data['eic'] > 1e-8, np.nan, inplace=True)
            super(icCMS, self).__init__(pd.merge(geom, data, on=['ix', 'iy', 'iz'], how='left'))
        else:
            super(icCMS, self).__init__(geom)

        self.name = name

    # -- backward compatibility
    @property
    def iov(self):
        return self

    def reset(self, ic_def=np.nan, eic_def=0):
        """
        Reset ic
        Parameters:
        -----------
        ic_def : init ic val (default np.nan)
        eic_def: init eic val (default np.nan)
        """
        self['ic'] = ic_def
        self['eic'] = eic_def

    def __add__(self, ic):
        out = self.copy(deep=True)
        out['ic'] = self['ic'] + ic['ic']
        out['eic'] = np.sqrt(self['eic'] * self['eic'] + ic['eic'] * ic['eic'])
        return icCMS(out)

    def __mul__(self, ic):
        out = self.copy(deep=True)
        out['ic'] = self['ic'] * ic['ic']
        out['eic'] = np.sqrt(self['eic'] * self['eic'] * ic['ic'] * ic['ic'] +
                             ic['eic'] * ic['eic'] * self['ic'] * self['ic'])
        return icCMS(out)

    def __div__(self, ic):
        out = self.copy(deep=True)
        out['ic'] = self['ic'] / ic['ic']
        out['eic'] = np.sqrt((self['eic'] / self['ic']) ** 2 +
                             (ic['eic'] / ic['ic']) ** 2) * out['ic']
        return icCMS(out)

    def __truediv__(self, ic):
        return self.__div__(ic)

    def __sub__(self, ic):
        out = self.copy(deep=True)
        out['ic'] = self['ic'] - ic['ic']
        out['eic'] = np.sqrt(self['eic'] * self['eic'] + ic['eic'] * ic['eic'])
        return icCMS(out)

    def maskTTs(self, tts):
        """
        Mask a list of trigger towers specified as ['Module','ccu']
        (expert only function)
        """
        for tt in tts:
            print(' Masking TT %s - %d' % (tt[0], tt[1]))
            self['ic'].where((self['Module'] != tt[0]) | (self['ccu'] != tt[1]), np.nan, inplace=True)
            self['eic'].where((self['Module'] != tt[0]) | (self['ccu'] != tt[1]), 0, inplace=True)

    def average(self, xtal_mask=None, ic_name='ic', trim=None, groupby='harness'):
        """
        average: average ICs per pre-defined regions
        groupby   : pre-defined region or used defined
                    user defined region are regular (list of) pandas series
                    predefined regions are:
                    - harness
                    - TT: trigger
                    - foldModule: folding EB modules in phi
        xtal_mask : mask to remove some crystals from average
        ic_name   : name of the parameter used for average (default: ic)
        trim      : remove <trim> percent of tail events on both left and right
        """
        tmptab = self.iov
        if xtal_mask is not None:
            tmptab = self.iov.mask(xtal_mask)
        gby = groupby
        if type(groupby) == str:
            if groupby.lower() == 'harness':
                gby = [self['LME'], self['PNA']]
            elif groupby.lower() == 'tt':
                gby = [self['ccu'], self['Module']]
            elif groupby.lower() == 'foldmodule':
                gby = [self['eta_module'], self['phi_module']]

        def trimming(x, cutfrac=None):
            if cutfrac is None:
                return x.mean()
            i = int(x.count() * cutfrac)
            return x.dropna().sort_values()[i:-i].mean()

        return tmptab.groupby(gby)[ic_name].transform(lambda x: trimming(x, trim))

    def etaRingNorm(self, xtal_mask=None, ic_name='ic'):
        """
        eta ring normalization: normalize ic average per eta ring to one
        Parameters:
        -----------
        xtal_mask: a list of crystal to mask from the average (series of [boolean] )
        ic_name  : name of the variable used as ic (default 'ic')
        """

        # need a trick to avoid having nan for masked crystals (when a mask is applied)
        mean = self.groupby('ieta')[ic_name].transform('mean') if xtal_mask is None else \
            self[['ieta']].join(self.mask(xtal_mask).groupby('ieta')[ic_name].mean(), on='ieta')[ic_name]

        self[ic_name] = self[ic_name] / mean
        self['eic'] = self['eic'] / mean

    def plot(self, var='ic', title=None, zRange_eb=None, zRange_ee=None, cmap='RdYlBu', ecalpart=None):
        """
        Plot an ecal variable in 2D (EB, EE+, EE-)
        Parameters:
        -----------
        var: variable to plot (default ic)
        title    : title of the figure (canvas name), if none use icCMS.name
        zRange_eb: specify the z axis range in for EB plot
        zRange_ee: specify the z axis range in for EE plot
        cmap     : color map (matplotlib name)
        ecalpart : part of ecal to plot
                - ecalpart = None : EB , EE+, EE- (default)
                - ecalpart = EB : EB only
                - ecalpart = EE : EE only
        """
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec

        if zRange_eb is None:
            zRange_eb = [self[self['iz'] == 0][var].min(), self[self['iz'] == 0][var].max()]
        if zRange_ee is None:
            zRange_ee = [self[self['iz'] != 0][var].min(), self[self['iz'] != 0][var].max()]
        if title is None:
            title = self.name
        if var == 'eic':
            title, cmap = ('Errors ' + self.name, 'afmhot')

        if ecalpart is None:
            plt.figure(num=title + self.name, figsize=[12, 9])
            gs = gridspec.GridSpec(2, 2)
            plot2D_eb(plt.subplot(gs[0, 0:]), self[self['iz'] == 0][['ix', 'iy', var]], 'EB  ' + title, zRange_eb, cmap)
            plot2D_ee(plt.subplot(gs[1, 0]), self[self['iz'] == -1][['ix', 'iy', var]], 'EE- ' + title, zRange_ee, cmap)
            plot2D_ee(plt.subplot(gs[1, 1]), self[self['iz'] == +1][['ix', 'iy', var]], 'EE+ ' + title, zRange_ee, cmap)
        elif ecalpart.lower() == 'eb':
            plt.figure(num=title + self.name + 'EB', figsize=[10, 4.5])
            plot2D_eb(plt.gca(), self[self['iz'] == 0][['ix', 'iy', var]], 'EB  ' + title, zRange_eb, cmap)
        elif ecalpart.lower() == 'ee':
            plt.figure(num=title + self.name + 'EE', figsize=[10, 4])
            plot2D_ee(plt.subplot(1, 2, 1), self[self['iz'] == -1][['ix', 'iy', var]], 'EE- ' + title, zRange_ee, cmap)
            plot2D_ee(plt.subplot(1, 2, 2), self[self['iz'] == +1][['ix', 'iy', var]], 'EE+ ' + title, zRange_ee, cmap)

    def plotEtaScale(self, var='ic', xtal_mask=None, legend=None, yZoom=(0.90, 1.10),
                     yLarge=(0.5, 1.5), axis=None, linestyle='None',
                     marker='.'):
        """
        Plot function along eta using eta-scale convention, i.e. 1/ic (rather than ic)
        The plot is devided in 3 sub ranges ( VF-EE-,  full ECAL, VF-EE+) where
        VF == very forward means |ieta| > 110.
        Return the central matplotlib axis (3 are defined)
        Parameters:
        -----------
        var       : variable to average vs ieta
        xtal_mask : list of crystals to mask
        yZoom     : y axis range for full ECAL plot (central region)
        yLarge    : y axis range for both VF regions
        legend    : name of the curve in the legend
        axis      : matplotlib axis (default None).
                    if None create a new figure.
                    if specified, must be a list of 3 axis [axisLeft, axisCentral, axisRight]
        linestyle : matplotlib line style (default None)
        marker    : matplotlib marker style (default '.')
        """
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec

        x, y, yerr = self.profile1D(yvar=var, xtal_mask=xtal_mask)
        plt.close(plt.gcf())
        if axis is None:
            plt.figure(num='Eta scale ' + self.name, figsize=[15, 5])
            gs = gridspec.GridSpec(1, 5)
            axis = [plt.subplot(gs[0, 0]), plt.subplot(gs[0, 1:4]), plt.subplot(gs[0, 4])]

        for iecal, ax in enumerate(axis):
            ax.errorbar(x, 1 / y, yerr=0, marker=marker, linestyle=linestyle,
                        markersize=6, label=legend)
            ax.set_xlabel('SC i$\eta$')
            ax.axhline(1, color='k', linewidth=2)
            ax.set_ylim(yLarge[0], yLarge[1])
            ax.grid(which='both', linestyle='--', linewidth=0.9)
            for xmodule in [-85, -65, -45, -25, 0, 25, 45, 65, 85]:
                ax.axvline(xmodule, color='k', linestyle='--')
        axis[0].set_xlim(-125, -110)
        axis[1].set_xlim(-125, +125)
        axis[2].set_xlim(+110, +125)

        axis[0].set_ylabel('r($\eta$)', horizontalalignment='right', y=1)
        axis[1].set_ylim(yZoom[0], yZoom[1])
        axis[1].legend(frameon=True, framealpha=1, loc=8)
        return axis[1]

    def plotEtaEBEE(self, xvar='ieta', yvar='ic', yerr='std', xtal_mask=None, legend=None,
                    yRangeEB=None, yRangeEE=None, yTitle=None,
                    axis=None, linestyle='None', marker='.'):
        """
        Plot function along eta using eta-scale convention, i.e. 1/ic (rather than ic)
        The plot is devided in 2 or 3 sub ranges (EB, EE) or ( EE-, EB, EE+)
        Return the list of 3 axis
        Parameters:
        -----------
        xvar      : x variable (supported eta, ieta, abs_eta, abs_ieta)
        yvar      : y variable to average along eta
        yerr      : y error (std = RMS of y along eta, None: no error)
        xtal_mask : list of crystals to mask
        yRangeEB  : y axis range for full EB region
        yRangeEE  : y axis range for both EE region
        legend    : name of the curve in the legend
        axis      : matplotlib axis (default None).
                    if None create a new figure.
                    if specified, must be a list of 3 axis [axisCentral, axisRight, axisLeft (or None)]
                    axisLeft must be None is xvar is absolute
        linestyle : matplotlib line style (default None)
        marker    : matplotlib marker style (default '.')
        """
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec

        custom_ieta = {'figsize': [15, 5], 'xTitle': 'Crystal i$\eta$', 'xEB': [-85, 85], 'xEE+': [85, 125], 'xEE-': [-125, -85]}
        custom_aieta = {'figsize': [10, 5], 'xTitle': 'Crystal |i$\eta$|', 'xEB': [0, 85], 'xEE+': [85, 125], 'xEE-': None}
        custom_eta = {'figsize': [15, 5], 'xTitle': 'Crystal $\eta$', 'xEB': [-1.5, 1.5], 'xEE+': [1.5, 3.0], 'xEE-': [-3.0, -1.5]}
        custom_aeta = {'figsize': [10, 5], 'xTitle': 'Crystal |$\eta$|', 'xEB': [0, 1.5], 'xEE+': [1.5, 3.0], 'xEE-': None}

        if xvar == 'abs_ieta':
            custom = custom_aieta
        elif xvar == 'ieta':
            custom = custom_ieta
        elif xvar == 'abs_eta':
            custom = custom_aeta
        else:
            custom = custom_eta

        if xvar == 'abs_ieta':
            myx = np.abs(geom['ieta'])
        elif xvar == 'ieta':
            myx = geom['ieta']
        elif xvar == 'abs_eta':
            myx = self.iov.groupby(np.abs(geom['ieta']))['eta'].transform(lambda xl: np.abs(xl).mean())
        else:
            myx = geom['eta']

        x, y, error = self.profile1D(xvar=myx, yvar=yvar, xtal_mask=xtal_mask)
        if yerr is None:
            error = None
        plt.close(plt.gcf())

        if axis is None:
            plt.figure(num='Eta plot ' + self.name, figsize=custom['figsize'])
            gs = gridspec.GridSpec(1, 5)
            if xvar.find('abs') >= 0:
                axis = [plt.subplot(gs[0, 0:3]), plt.subplot(gs[0, 3:]), None]
            else:
                axis = [plt.subplot(gs[0, 1:4]), plt.subplot(gs[0, 4]), plt.subplot(gs[0, 0])]

        for iecal, ax in enumerate(list(filter(None, axis))):
            if ax is None:
                continue
            ax.errorbar(x, y, yerr=error, marker=marker, linestyle=linestyle,
                        markersize=6, label=legend)
            ax.set_xlabel(custom['xTitle'])
            ax.grid(which='both', linewidth=0.9)

        if axis[0] is not None:
            axis[0].set_xlim(custom['xEB'][0], custom['xEB'][1])
        if axis[1] is not None:
            axis[1].set_xlim(custom['xEE+'][0], custom['xEE+'][1])
        if axis[2] is not None:
            axis[2].set_xlim(custom['xEE-'][0], custom['xEE-'][1])
        if axis[0] is not None and yRangeEB is not None:
            axis[0].set_ylim(yRangeEB[0], yRangeEB[1])
        if axis[1] is not None and yRangeEE is not None:
            axis[1].set_ylim(yRangeEE[0], yRangeEE[1])
        if axis[2] is not None and yRangeEE is not None:
            axis[2].set_ylim(yRangeEE[0], yRangeEE[1])

        for ax in list(filter(None, axis)):
            ax.set_xlabel(custom['xTitle'], horizontalalignment='right', x=1)
        if yTitle is not None:
            for ax in list(filter(None, axis)):
                ax.set_ylabel(yTitle, horizontalalignment='right', y=1)

        return axis

    def profile1D(self, xvar='ieta', yvar='ic', xtal_mask=None, title=None, legend=None,
                  axis=None, color=None, yRange=None, xTitle=None, yTitle=None):
        """
        1D profile of the variable y as a function of variable x (both variables should be in the iov dataframe)
        Return numpy arrays of the plotted points:  x,y,yerr
        Parameters:
        -----------
        xvar: variable to define group for average
        yvar: variable to average
        xtal_mask : list of crystals to mask
        yRange    : y axis range
        axis      : matplotlib axis (default None).
                    if None create a new figure.
                    if specified, must be a list of 3 axis [axisLeft, axisCentral, axisRight]
        legend    : name of the curve in the legend
        title     : title used for figure (for saving purposes) - should not be used in principle
        """
        import matplotlib.pyplot as plt

        iov = self.iov if xtal_mask is None else self.iov.mask(xtal_mask)
        proj = iov.groupby(xvar).agg({yvar: ['mean', 'std']})

        if title is None:
            title = 'Mean%s vs %s ' % (yvar, xvar)
        if axis is None:
            axis = plt.figure(num=title + ' ' + self.name, figsize=[7, 4]).gca()

        axis.errorbar(proj.index, proj[yvar, 'mean'], yerr=proj[yvar, 'std'],
                      color=color, linestyle='None', markersize=6, marker='.', label=legend)

        if xTitle is not None:
            axis.set_xlabel(xTitle, horizontalalignment='right', x=1)
        if yTitle is not None:
            axis.set_ylabel(yTitle, horizontalalignment='right', y=1)

        if yRange is not None:
            axis.set_ylim(yRange[0], yRange[1])

        return proj.index, proj[yvar, 'mean'], proj[yvar, 'std']

    def profile1D_groupY(self, xvar='ieta', yvar='ic', xtal_mask=None, title=None, legend=None, axis=None, color='k', yRange=None):
        """
        1D profile of the variable y as a function of variable x (both variables should be in the iov dataframe)
        It differs from profile1D by grouping variable according to Y, adding all events with the same Y to a single
        x-bin (length adjusted to includes all events with same Y).
        Return numpy arrays of the plotted points:  x,y,xerr,yerr
        Parameters:
        -----------
        xvar: variable to define group for average
        yvar: variable to average
        xtal_mask : list of crystals to mask
        yRange    : y axis range
        axis      : matplotlib axis (default None).
                    if None create a new figure.
                    if specified, must be a list of 3 axis [axisLeft, axisCentral, axisRight]
                    legend    : name of the curve in the legend
                    title     : title used for figure (for saving purposes) - should not be used in principle
        """
        import matplotlib.pyplot as plt

        iov = self.iov if xtal_mask is None else self.iov.mask(xtal_mask)
        proj = iov.groupby(yvar).agg({xvar: ['mean', 'min', 'max']})

        if title is None:
            title = '<%s> vs %s ' % (yvar, xvar)
        if axis is None:
            axis = plt.figure(num=title + ' ' + self.name, figsize=[7, 4]).gca()

        x, y, xerr = (proj[xvar, 'max'] + proj[xvar, 'min']) / 2, proj.index, (proj[xvar, 'max'] - proj[xvar, 'min']) / 2
        yerr = np.zeros(y.size)
        axis.errorbar(x, y, xerr=xerr,
                      color=color, linestyle='None', markersize=6, marker='.', label=legend)

        axis.set_xlabel(xvar, horizontalalignment='right', x=1)
        axis.set_ylabel('<%s>' % yvar, horizontalalignment='right', y=1)

        if yRange is not None:
            axis.set_ylim(yRange[0], yRange[1])

        return x.values, y.values, xerr.values, yerr

    def dump(self, output):
        """
        dump the ICs into a regular txt file (csv style) under the format ix iy iz ic eic
        Parameters:
        -----------
        output: name of the output txt file
        """
        print('Dumping iov file to: ' + output)
        # -- replace nan ic with 1 and nan eic with 0 (the latter should not exist)
        self.replace({'ic': {np.nan: 1}, 'eic': {np.nan: 0}}).to_csv(output,
                                                                     columns=['ix', 'iy', 'iz', 'ic', 'eic'],
                                                                     header=False, index=False, sep=' ', float_format='%+6.5f')


#######################################################################################
# -- ecal eb module defintion along ieta
def eta_module(x):
    imod = +99
    if np.abs(x) < 0.5:
        return -999
    elif np.abs(x) < 5.5:
        imod = 0.5
    elif np.abs(x) < 25.5:
        imod = 1
    elif np.abs(x) < 45.5:
        imod = 2
    elif np.abs(x) < 65.5:
        imod = 3
    elif np.abs(x) < 85.5:
        imod = 4
    return imod * np.sign(x)


#######################################################################################
# -- ieta range definition, this can be customized
# -- the present definition matches the one used for ic combination
def ieta_range(x):
    if np.abs(x) < 0.5:
        return -100
    elif np.abs(x) < 10.5:
        return 0
    elif np.abs(x) < 25.5:
        return 1
    elif np.abs(x) < 45.5:
        return 2
    elif np.abs(x) < 65.5:
        return 3
    elif np.abs(x) < 85.5:
        return 5
    elif np.abs(x) < 95.5:
        return 6
    elif np.abs(x) < 105.5:
        return 7
    elif np.abs(x) < 117.5:
        return 8
    elif np.abs(x) < 125.5:
        return 9
    return -1
