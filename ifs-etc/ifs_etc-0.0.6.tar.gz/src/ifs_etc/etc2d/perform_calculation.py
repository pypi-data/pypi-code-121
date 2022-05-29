import pdb
import pandas as pd
import numpy as np
import os
import h5py
from einops import repeat
import matplotlib.pyplot as plt
from . import source
from .source import filter_mag, read_filter
from .config import get_throughput

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
snpp_refdata = os.path.join(path, 'refdata/')

def flux2electron(spaxel_xsize, spaxel_ysize, wavearr, fluxarr, throughtputwave, throughtputvalue, fluxunit=''):
    """

    Args:
        spaxel_xsize: 
        spaxel_ysize: 
        wavearr: 
        fluxarr: erg/s/cm^2/A/arcsec^2 or erg/s/cm^2/Hz/arcsec^2
        throughtputwave: 
        throughtputvalue: 
        fluxunit: 'erg/s/cm^2/A' or 'erg/s/cm^2/hz'

    Returns:

    """

    # instru = config['configuration']

    cc = 3.0e18   # speed of light, A/s
    spaxel_area = spaxel_xsize * spaxel_ysize     # arcsec^2
    d = 200  # diameter of the telescope, in cm unit
    obscure = 0.0  # effective central obscuration, no unit
    telarea = 3.14159 / 4.0 * d * d * (1.0 - obscure)  # effective area of the telescope, cm^2
    delta_lambda_per_pixel = 1.755555  # per pixel
    delta_hz_per_specpixel = delta_lambda_per_pixel / wavearr**2 * cc  # s^-1
    specsampling = 1.0  # 2 pixels
    planckh = 6.626e-27  # erg*s
    hv = planckh * cc / wavearr  # erg
    QE = 1

    if wavearr.ndim == 3:
        qvalue = np.zeros(shape=wavearr.shape, dtype=float)
        qvalue = np.interp(wavearr[:, 0, 0], throughtputwave, throughtputvalue)
        qvalue = repeat(qvalue, 'h -> h '+str(wavearr.shape[1])+' '+str(wavearr.shape[2]))
    elif wavearr.ndim == 1:
        qvalue = np.interp(wavearr, throughtputwave, throughtputvalue)
    else:
        raise ValueError('check dimension of the input array.')

    if fluxunit=='erg/s/cm^2/A':
        isource1 = fluxarr * wavearr ** 2 / cc * spaxel_area  # erg/s/cm^2/Hz per spaxel
        isource2 = isource1 * telarea  # erg/s/Hz per spaxel
        isource3 = qvalue * isource2 * delta_hz_per_specpixel  # erg/s per spaxel
        isource4 = isource3 * specsampling  # erg/s per spec-element per spaxel
        isource5 = isource4 / hv  # phot/s per spec-element per spaxel
        isource6 = isource5 * QE  # e/s per spec-element per spaxel

        return isource6
    else:

        return np.nan


def electron2flux(config, wavearr, countsarr, throughtputwave, throughtputvalue, fluxunit=''):
    '''
    :param wavearr: A
    :param countsarr: e-/s
    :return:
    '''

    instru = config['configuration']

    cc = 3.0e18   # speed of light, A/s
    spaxel_area = instru['spaxel_xsize'] * instru['spaxel_ysize']    # arcsec^2
    d = 200  # diameter of the telescope, in cm unit
    obscure = 0.0  # effective central obscuration, no unit
    telarea = 3.14159 / 4.0 * d * d * (1.0 - obscure)  # effective area of the telescope, cm^2
    delta_lambda_per_pixel = 1.755555  # per pixel
    delta_hz_per_specpixel = delta_lambda_per_pixel / wavearr**2 * cc  # s^-1
    specsampling = 1.0  # 2 pixels
    planckh = 6.626e-27  # erg*s
    hv = planckh * cc / wavearr  # erg
    QE = 1

    qvalue = np.interp(wavearr, throughtputwave, throughtputvalue)


    if fluxunit=='erg/s/cm^2/A':

        isource5 = countsarr / QE  # phot/s per spec-element per spaxel
        isource4 = isource5 * hv  # erg/s per spec-element per spaxel
        isource3 = isource4 / specsampling  # erg/s per spec-element per spaxel
        isource2 = isource3 / delta_hz_per_specpixel / qvalue  # erg/s per spaxel
        isource1 = isource2 / telarea  # erg/s/Hz per spaxel
        fluxarr = isource1 / wavearr ** 2 * cc / spaxel_area  # erg/s/cm^2/Hz per spaxel

        return fluxarr

    else:

        return np.nan


def get_ms_nsky(wavearr, spaxel_xsize, spaxel_ysize):

    """

    Args:
        wavearr:
        spaxel_xsize:
        spaxel_ysize:

    Returns:
        sky counts (e-/s), in 1d array.


    """

    # know the sky counts in MS ccd per pixel in different bands,
    # Thus convert it to sky spectrum (counts) in IFS ccd per spaxel

    fluxskypp = np.zeros(len(wavearr))

    ii = np.logical_and(wavearr >= 2550, wavearr <= 4000)
    counta = len(np.where(ii == 1)[0])
    if counta > 0:
        fluxskypp[ii] = 0.028 / counta      # e/s/spaxel/pixel
    ii = np.logical_and(wavearr >= 4000, wavearr <= 6000)
    countb = len(np.where(ii == 1)[0])
    if countb > 0:
        fluxskypp[ii] = 0.229 / countb
    ii = np.logical_and(wavearr >= 6000, wavearr <= 9000)
    countc = len(np.where(ii == 1)[0])
    if countc > 0:
        fluxskypp[ii] = 0.301 / countc
    ii = np.where(wavearr >= 9000)[0]
    countd = len(ii)
    if countd > 0:
        fluxskypp[ii] = 0.301 / countd

    ms_pix_area = 0.074**2      # arcsec
    spaxel_area = spaxel_xsize * spaxel_ysize   # arcsec
    factor = 0.9

    fluxskypp = fluxskypp / ms_pix_area * spaxel_area * factor  # e/s/spaxel/spec-elements

    return fluxskypp



def get_background(zodia_level, earthshine_level, wavearr, spaxel_xsize, spaxel_ysize):

    """
    Consider zodiacal background and earth shine background in different levels.

    Args:
        zodia_level:
            zodiacal level, low, median, high, corresponding index from 1-3.
        earthshine_level:
            earth shine level, low, median, high, corresponding index from 1-3.
        wavearr:
            wave array to be returned.

    Returns:
        sky counts (e-/s) in each spaxel element (spaxel_xsize * spaxel_ysize), in 1d array.

    """

    # get IFS throughtput
    throughtputwave, throughtputvalue = get_throughput()

    # get the zodia spectrum, convert to e/s/spaxel/spec-elements
    filename = os.path.join(snpp_refdata, 'csst', 'background', 'zodi_spec.csv')
    cat = pd.read_csv(filename, comment='#')
    zodia_wave = cat['wave']
    zodia_spec = cat['zodi_' + zodia_level]       # erg/s/cm^2/A/arcsec^2
    zodia_spec_interp = np.interp(wavearr, zodia_wave, zodia_spec)
    zodia_counts_interp = flux2electron(spaxel_xsize, spaxel_ysize,
                                       wavearr, zodia_spec_interp,
                                       throughtputwave, throughtputvalue,
                                       fluxunit='erg/s/cm^2/A')

    # get the earth shine spectrum, convert to e/s/spaxel/spec-elements
    filename = os.path.join(snpp_refdata, 'csst', 'background', 'earthshine_spec.csv')
    cat = pd.read_csv(filename, comment='#')
    earthshine_wave = cat['wave']
    earthshine_spec = cat['earthshine_' + earthshine_level]       # erg/s/cm^2/A/arcsec^2
    earthshine_spec_interp = np.interp(wavearr, earthshine_wave, earthshine_spec)
    earthshine_counts_interp = flux2electron(spaxel_xsize, spaxel_ysize,
                                       wavearr, earthshine_spec_interp,
                                       throughtputwave, throughtputvalue,
                                       fluxunit='erg/s/cm^2/A')

    nsky = zodia_counts_interp + earthshine_counts_interp


    return nsky



class DetectorCountsRate(source.ModelCube):

    def __init__(self, config):

        self.config = config

        # pdb.set_trace()

        source.ModelCube.__init__(
            self, config
        )

        throughtputwave, throughtputvalue = get_throughput()

        instru = config['configuration']
        self.source_counts = flux2electron(instru['spaxel_xsize'], instru['spaxel_ysize'],
                                           self.wavecube, self.fluxcube,
                                           throughtputwave, throughtputvalue,
                                           fluxunit='erg/s/cm^2/A')
        self.wavearr = self.wavecube[:, 0, 0]



class DetectorCounts(object):

    def __init__(self, config, signal):

        instru = config['configuration']
        ccdspec_wave = signal.ccdspec_wave
        nw = len(signal.ccdspec_wave)
        nspaxel_x = signal.source_counts.shape[1]
        nspaxel_y = signal.source_counts.shape[2]

        # several count_rates
        nsource_rate_cube = signal.source_counts     # e/s

        ndark_rate = np.zeros(shape=nw, dtype=float) + instru['dark']   # e/s/pix

        nreadout_rate = np.zeros(shape=nw, dtype=float) + instru['readout_noise']**2    # e/pix

        nsky_rate = get_background(config['background']['zodiacal'],
                                   config['background']['earth_shine'],
                                   signal.ccdspec_wave,
                                   instru['spaxel_xsize'],
                                   instru['spaxel_ysize'])

        # read the exptime
        repn = config['calc_mode']['repn']
        obst = config['calc_mode']['obst']
        npixw = 2
        specsampling = 1

        # calculate the counts with exptime and extract_area.
        tot_t = repn * obst
        readout_n = repn
        ndark = (ndark_rate * tot_t * npixw * specsampling)  # e/s/pix * sampling * t * extraction area
        nreadout = nreadout_rate * (repn * npixw * specsampling)  # e/pix * sampling * readout times * extraction area
        nsource_cube = (nsource_rate_cube * tot_t)  # e/s/sampling * t per spaxel
        nsky = (nsky_rate * tot_t)  # e/s/sampling * t per spaxel

        # add 2% of the source counts as straylight, scatter into the entire CCD (b: 4k*2k, r: 6k*3k)
        stray_frac = 0.02
        ind_blue = ccdspec_wave < 5700  # assume the blue/red separate at 5700A
        ind_red = ccdspec_wave > 5700
        tot_source_counts_blue = np.sum(nsource_cube[ind_blue, :, :]) + np.sum(nsky[ind_blue]) * nspaxel_x * nspaxel_y
        tot_source_counts_red = np.sum(nsource_cube[ind_red, :, :]) + np.sum(nsky[ind_red]) * nspaxel_x * nspaxel_y
        nstray_blue = tot_source_counts_blue * stray_frac / (4000 * 2000)
        nstray_red = tot_source_counts_red * stray_frac / (6000 * 3000)
        nstray = np.zeros(shape=nw, dtype=float)
        nstray[ind_blue] = nstray_blue
        nstray[ind_red] = nstray_red


        # make into 3d cube
        ndark_cube = repeat(ndark, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_x))
        nreadout_cube = repeat(nreadout, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_x))
        nsky_cube = repeat(nsky, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_x))
        nstray_cube = repeat(nstray, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_y))

        self.ccdspec_wave = ccdspec_wave
        self.ndark = ndark_cube
        self.nreadout = nreadout_cube
        self.nsky = nsky_cube
        self.nsource = nsource_cube
        self.nstray = nstray_cube


        # consider the binning in x-axis
        if instru['readout_xbin'] > 1:
            ccdspec_wave_xbin = np.array([])
            ndark_bin = np.array([])
            nreadout_bin = np.array([])
            nsky_bin = np.array([])
            nstray_bin = np.array([])
            i = 0
            xbin = instru['readout_xbin']
            while i + xbin < nw:
                ccdspec_wave_xbin = np.append(ccdspec_wave_xbin, np.mean(ccdspec_wave[i:i+xbin]))
                ndark_bin = np.append(ndark_bin, np.mean(ndark[i:i+xbin]))
                nreadout_bin = np.append(nreadout_bin, np.mean(nreadout[i:i+xbin]))
                nsky_bin = np.append(nsky_bin, np.sum(nsky[i:i + xbin]))
                nstray_bin = np.append(nstray_bin, np.sum(nstray[i:i + xbin]))
                i = i + xbin

            # bin the source counts
            nw_bin = len(ccdspec_wave_xbin)
            nsource_bin_cube = np.zeros(shape=(nw_bin, nspaxel_x, nspaxel_y), dtype=float)
            for i in range(nw_bin):
                j = i * xbin
                nsource_bin_cube[i, :, :] = np.sum(nsource_cube[j:j + xbin, :, :], axis=0)

            # make into 3d cube (xbinning)
            ndark_bin_cube = repeat(ndark_bin, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_x))
            nreadout_bin_cube = repeat(nreadout_bin, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_x))
            nsky_bin_cube = repeat(nsky_bin, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_x))  # e/s
            nstray_bin_cube = repeat(nstray_bin, 'h -> h ' + str(nspaxel_x) + ' ' + str(nspaxel_y))

            self.ccdspec_wave = ccdspec_wave_xbin
            self.ndark = ndark_bin_cube
            self.nreadout = nreadout_bin_cube
            self.nsky = nsky_bin_cube
            self.nsource = nsource_bin_cube
            self.nstray = nstray_bin_cube



class calculation_snr(object):

    def __init__(self, config):

        signal_rate = DetectorCountsRate(config)

        counts = DetectorCounts(config, signal_rate)

        self.source = counts.nsource
        self.darknoise = np.sqrt(counts.ndark)
        self.readnoise = np.sqrt(counts.nreadout)
        self.skynoise = np.sqrt(counts.nsky)
        self.sourcenoise = np.sqrt(counts.nsource)
        self.straynoise = np.sqrt(counts.nstray)
        self.saturate_mask = (self.source > 65535)


        self.totnoise = np.sqrt(self.darknoise ** 2 + self.readnoise ** 2 +
                                self.skynoise ** 2 + self.sourcenoise ** 2 +
                                self.straynoise ** 2)
        self.sysnoise = np.sqrt(self.darknoise ** 2 + self.readnoise ** 2 +
                                self.skynoise ** 2 + self.straynoise ** 2)
        self.snr = counts.nsource / self.totnoise


        # model spectrum
        nw, nx, ny = counts.nsource.shape
        self.mockwave = counts.ccdspec_wave
        template_fluxcube = np.zeros(shape=(nw, nx, ny), dtype=float)
        if config['configuration']['readout_xbin'] > 1:
            for i in range(nx):
                for j in range(ny):
                    template_fluxcube[:, i, j] = np.interp(self.mockwave,
                                                  signal_rate.ccdspec_wave,
                                                  signal_rate.fluxcube[:, i, j])
        else:
            template_fluxcube = signal_rate.fluxcube

        self.mockflux = np.random.normal(template_fluxcube, scale=template_fluxcube / self.snr)
        self.mockerror = template_fluxcube / self.snr

        # model image
        self.img2d = signal_rate.mag2d

    def save(self, file):

        f = h5py.File(file, 'w')
        f.create_dataset('source', data=self.source)
        f.create_dataset('darknoise', data=self.darknoise)
        f.create_dataset('readnoise', data=self.readnoise)
        f.create_dataset('skynoise', data=self.skynoise)
        f.create_dataset('sourcenoise', data=self.sourcenoise)
        f.create_dataset('totnoise', data=self.totnoise)
        f.create_dataset('sysnoise', data=self.sysnoise)
        f.create_dataset('straynoise', data=self.straynoise)
        f.create_dataset('snr', data=self.snr)
        f.create_dataset('saturate_mask', data=self.saturate_mask)
        f.create_dataset('mockwave', data=self.mockwave)
        f.create_dataset('mockflux', data=self.mockflux)
        f.create_dataset('mockerror', data=self.mockerror)
        f.create_dataset('img2d', data=self.img2d)
        f.close()


    def plot(self):

        report = self

        fig, axs = plt.subplots(figsize=(12, 9))
        fig.subplots_adjust(hspace=0.35, wspace=0.45,
                            left=0.05, right=0.97, top=0.95, bottom=0.05)
        cm = plt.cm.get_cmap('jet_r')

        ax_recontructed_magmap = plt.subplot2grid((3, 4), (0, 0))
        im = ax_recontructed_magmap.imshow(self.img2d, origin='low', extent=(0, 30, 0, 30),
                                           cmap=cm, picker=True)
        ax_recontructed_magmap.set_xlabel('spaxel')
        ax_recontructed_magmap.set_ylabel('spaxel')
        ax_recontructed_magmap.set_title('reconstructed magmap')
        cbar_ax = fig.add_axes([0.25, 0.75, 0.01, 0.2])
        cbar = plt.colorbar(im, cax=cbar_ax, ticks=np.arange(20, 25, 2), orientation='vertical')
        cbar.set_label(r'mag/arcsec$^{2}$', labelpad=-1)
        cbar.ax.tick_params(labelsize=7)

        ax_recontructed_snr = plt.subplot2grid((3, 4), (1, 0))
        ind = np.argmin(abs(self.mockwave - 5000))
        im = ax_recontructed_snr.imshow(self.snr[ind, :, :], origin='low', extent=(0, 30, 0, 30),
                                        cmap=cm, picker=True)
        ax_recontructed_snr.set_xlabel('spaxel')
        ax_recontructed_snr.set_ylabel('spaxel')
        ax_recontructed_snr.set_title('reconstructed SNR@5000A')
        cbar_ax = fig.add_axes([0.25, 0.41, 0.01, 0.2])
        cbar = plt.colorbar(im, cax=cbar_ax, ticks=np.arange(0, 4, 1), orientation='vertical')
        cbar.set_label('SNR', labelpad=-1)
        cbar.ax.tick_params(labelsize=7)

        k = 0
        i = 15
        j = 15
        ax_snr = plt.subplot2grid((3, 3), (k, 1), colspan=2)
        ax_snr.plot(self.mockwave, self.snr[:, j, i], 'k-')
        ax_snr.annotate('surface brightness: \n' + '{:4.1f}'.format(self.img2d[j, i]) + r' mag/arcsec$^{2}$',
                        xy=(0.75, 0.8), xycoords='axes fraction')
        ax_snr.annotate('SNR@5000A: \n' + '{:4.1f}'.format(self.snr[ind, j, i]),
                        xy=(0.75, 0.65), xycoords='axes fraction')
        ax_snr.annotate('x: ' + str(i) + ', y: ' + str(j),
                        xy=(0.05, 0.78), xycoords='axes fraction')
        ax_snr.set_ylabel('SNR')
        ax_snr.set_xlabel('wavelength')

        ax_noises = plt.subplot2grid((3, 3), (k + 1, 1), colspan=2)
        ax_noises.plot(self.mockwave, self.sourcenoise[:, j, i], label='source_noise')
        ax_noises.plot(self.mockwave, self.skynoise[:, j, i], label='sky_noise')
        ax_noises.plot(self.mockwave, self.readnoise[:, j, i], label='readout_noise')
        ax_noises.plot(self.mockwave, self.darknoise[:, j, i], label='dark_noise')
        ax_noises.plot(self.mockwave, self.straynoise[:, j, i], label='stray_noise')
        ax_noises.legend(loc=1)
        ax_noises.set_ylabel('noise counts (e-/s)')

        ax_recontructed_spec = plt.subplot2grid((3, 3), (k + 2, 1), colspan=2)
        ax_recontructed_spec.plot(self.mockwave, self.mockflux[:, j, i], 'k-', label='mockflux')
        ax_recontructed_spec.plot(self.mockwave, self.mockerror[:, j, i], 'b-', label='mockerr')
        ax_recontructed_spec.set_ylabel(r'mock flux (erg/s/cm$^2$/A)')
        ax_recontructed_spec.set_xlabel('wavelength')


        def onpick(event):

            x = event.mouseevent.xdata
            y = event.mouseevent.ydata
            # print('show spec in x = ' + str(int(np.floor(x))) + ', y = '+ str(int(np.floor(y))))

            xind = int(np.floor(x))
            yind = int(np.floor(y))

            update(xind, yind)

        def update(xind, yind):

            k = 0
            i = xind
            j = yind
            ax_snr = plt.subplot2grid((3, 3), (k, 1), colspan=2)
            ax_snr.plot(self.mockwave, self.snr[:, j, i], 'k-')
            ax_snr.annotate('surface brightness: \n' + '{:4.1f}'.format(self.img2d[j, i]) + r' mag/arcsec$^{2}$',
                            xy=(0.75, 0.8), xycoords='axes fraction')
            ax_snr.annotate('SNR@5000A: \n' + '{:4.1f}'.format(self.snr[ind, j, i]),
                            xy=(0.75, 0.65), xycoords='axes fraction')
            ax_snr.annotate('x: ' + str(i) + ', y: ' + str(j),
                            xy=(0.05, 0.78), xycoords='axes fraction')
            ax_snr.set_ylabel('SNR')
            ax_snr.set_xlabel('wavelength')

            ax_noises = plt.subplot2grid((3, 3), (k + 1, 1), colspan=2)
            ax_noises.plot(self.mockwave, self.sourcenoise[:, j, i], label='source_noise')
            ax_noises.plot(self.mockwave, self.skynoise[:, j, i], label='sky_noise')
            ax_noises.plot(self.mockwave, self.readnoise[:, j, i], label='readout_noise')
            ax_noises.plot(self.mockwave, self.darknoise[:, j, i], label='dark_noise')
            ax_noises.plot(self.mockwave, self.straynoise[:, j, i], label='stray_noise')
            ax_noises.legend(loc=1)
            ax_noises.set_ylabel('noise counts (e-/s)')

            ax_recontructed_spec = plt.subplot2grid((3, 3), (k + 2, 1), colspan=2)
            ax_recontructed_spec.plot(self.mockwave, self.mockflux[:, j, i], 'k-', label='mockflux')
            ax_recontructed_spec.plot(self.mockwave, self.mockerror[:, j, i], 'b-', label='mockerr')
            ax_recontructed_spec.set_ylabel(r'mock flux (erg/s/cm$^2$/A)')
            ax_recontructed_spec.set_xlabel('wavelength')

            fig.canvas.draw()


        fig.canvas.mpl_connect('pick_event', onpick)

        plt.show()


class read_report(object):

    def __init__(self, file):

        f = h5py.File(file, 'r')
        list(f.keys())

        self.source = f['source'].value
        self.darknoise = f['darknoise'].value
        self.readnoise = f['readnoise'].value
        self.skynoise = f['skynoise'].value
        self.sourcenoise = f['sourcenoise'].value
        self.totnoise = f['totnoise'].value
        self.sysnoise = f['sysnoise'].value
        self.straynoise = f['straynoise'].value
        self.snr = f['snr'].value
        self.saturate_mask = f['saturate_mask'].value
        self.mockwave = f['mockwave'].value
        self.mockflux = f['mockflux'].value
        self.mockerror = f['mockerror'].value
        self.img2d = f['img2d'].value
        f.close()


# class calculation_limitmag(object):
#
#     def __init__(self, config):
#
#         instru = config['configuration']
#         targetsnr = config['targetsnr']
#
#         ccdspec_wave = np.arange(3500, 10000, 1.75555)
#         darkc = instru['dark']      # e/s/pix
#         rn = instru['readout_noise']   # e/pix
#         nsky = get_background(ccdspec_wave)
#         repn = config['repn']
#         obst = config['obst']
#         npixw = 2
#         specsampling = 1
#
#         coeff_s2 = (repn * obst) ** 2
#         coeff_s1 = -targetsnr ** 2 * (repn * obst)
#         coeff_s0 = -targetsnr ** 2 * (rn ** 2 * (repn * npixw * specsampling) +
#                                 (darkc * repn * obst * npixw * specsampling) +
#                                 (nsky * repn * obst))
#
#         source_rate = (-coeff_s1 + np.sqrt(coeff_s1 ** 2 - 4 * coeff_s2 * coeff_s0)) / (2 * coeff_s2)
#
#         throughtputwave, throughtputvalue = get_throughput(config)
#         flux = electron2flux(config, ccdspec_wave, source_rate,
#                              throughtputwave, throughtputvalue,
#                              fluxunit='erg/s/cm^2/A')
#
#         filter = read_filter(config['scene'][0]['normalization']['band'])
#         ind_filter = (ccdspec_wave >= filter.wavemin) & (ccdspec_wave <= filter.wavemax)
#         filter_wave = ccdspec_wave[ind_filter]
#         filter_flux = np.interp(filter_wave, filter.wave, filter.throughput)
#         self.limitmag = filter_mag(ccdspec_wave, flux, filter_wave, filter_flux, output='mag')



def perform_calculation(config):


    calculation_mode = config['calc_mode']['mode']

    if calculation_mode == 1:       # known the target SNR, calculate the needed time.

        # report = calculation_exptime(config)
        report = None
        print('This calc_mode is under development. Return none.')

    elif calculation_mode == 2:     # known the exposure time, calculate the reached SNR.

        report = calculation_snr(config)
    #
    # elif calculation_mode == 'snr2limitmag':
    #
    #     report = calculation_limitmag(config)

    else:

        report = None
        print('This calc_mode is not defined. ')



    return report

