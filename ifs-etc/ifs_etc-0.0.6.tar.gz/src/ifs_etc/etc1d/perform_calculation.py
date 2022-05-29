import pandas as pd
import numpy as np
import os
import h5py
import matplotlib.pyplot as plt
from einops import repeat
from . import source
from .source import filter_mag, read_filter
from .config import get_throughput
import pdb

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
refdata = os.path.join(path, 'refdata/')


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

    cc = 3.0e18   # speed of light, A/s
    spaxel_area = spaxel_xsize * spaxel_ysize    # arcsec^2
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



def get_nsky(wavearr):

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
    spaxel_area = 0.02**2
    factor = 0.9

    fluxskypp = fluxskypp / ms_pix_area * spaxel_area * factor  # e/s/spaxel/spec-elements

    return fluxskypp


def get_background(zodia_level, earthshine_level, wavearr, spaxel_xsize, spaxel_ysize):

    """
    Consider zodiacal background and earth shine background in different levels.

    Args:
        zodia_level:
            zodiacal level, 'low', 'med', 'high', corresponding index from 1-3.
        earthshine_level:
            earth shine level, 'low', 'med', 'high', corresponding index from 1-3.
        wavearr:
            wave array to be returned.

    Returns:
        sky counts (e-/s) in each spaxel element (spaxel_xsize * spaxel_ysize), in 1d array.

    """

    # get IFS throughtput
    throughtputwave, throughtputvalue = get_throughput()

    # get the zodia spectrum, convert to e/s/spaxel/spec-elements
    filename = os.path.join(refdata, 'csst', 'background', 'zodi_spec.csv')
    cat = pd.read_csv(filename, comment='#')
    zodia_wave = cat['wave']
    zodia_spec = cat['zodi_' + zodia_level]       # erg/s/cm^2/A/arcsec^2
    zodia_spec_interp = np.interp(wavearr, zodia_wave, zodia_spec)
    zodia_counts_interp = flux2electron(spaxel_xsize, spaxel_ysize,
                                       wavearr, zodia_spec_interp,
                                       throughtputwave, throughtputvalue,
                                       fluxunit='erg/s/cm^2/A')

    # get the earth shine spectrum, convert to e/s/spaxel/spec-elements
    filename = os.path.join(refdata, 'csst', 'background', 'earthshine_spec.csv')
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
        self.wavearr = self.wavecube



class DetectorCounts(object):

    def __init__(self, config, signal, obst=300, repn=20):

        instru = config['configuration']

        darkcube = np.zeros(shape=signal.source_counts.shape, dtype=float) + instru['dark']      # e/s/pix

        readnoisecube = np.zeros(shape=signal.source_counts.shape, dtype=float) + instru['readout_noise']   # e/pix

        # nskycube = get_nsky(signal.ccdspec_wave)        # e/s/specsampling
        nskycube = get_background(config['zodiacal_level'],
                                   config['earthshine_level'],
                                   signal.ccdspec_wave,
                                   instru['spaxel_xsize'],
                                   instru['spaxel_ysize'])

        # repn = config['repn']
        # obst = config['obst']
        npixw = 2
        specsampling = 1

        tot_t = repn * obst
        readout_n = repn
        self.darkn = (darkcube * tot_t * npixw * specsampling)  # e/s/pix * sampling * t * extraction area
        self.rnn2 = readnoisecube**2 * (repn * npixw * specsampling)  # e/pix * sampling * readout times * extraction area
        self.sourcenn = (signal.source_counts * tot_t)  # e/s/sampling * t per spaxel
        self.skynn = (nskycube * tot_t)  # e/s/sampling * t per spaxel



class calculation_snr(object):

    def __init__(self, config, straylight=False):

        signal_rate = DetectorCountsRate(config)
        noise = DetectorCounts(config, signal_rate, obst=config['obst'], repn=config['repn'])

        self.source = noise.sourcenn
        self.darknoise = np.sqrt(noise.darkn)
        self.readnoise = np.sqrt(noise.rnn2)
        self.skynoise = np.sqrt(noise.skynn)
        self.sourcenoise = np.sqrt(noise.sourcenn)
        self.saturate_mask = (self.source > 65535)

        if straylight == False:
            self.straylight = np.zeros(shape=self.source.shape, dtype=float)
        else:
            # add 2% of the brightest source counts as straylight
            surface_brightness = np.sum(self.source, 0)
            ind_ycen, ind_xcen = np.where(surface_brightness == np.max(surface_brightness))
            nstraylight = self.source[:, ind_ycen[0], ind_xcen[0]] * 0.02

            self.straylight = nstraylight


        self.totnoise = np.sqrt(self.darknoise ** 2 + self.readnoise ** 2 +
                                self.skynoise ** 2 + self.sourcenoise ** 2 +
                                self.straylight ** 2)
        self.sysnoise = np.sqrt(self.darknoise ** 2 + self.readnoise ** 2 +
                                self.skynoise ** 2 + self.straylight ** 2)
        self.snr = noise.sourcenn / self.totnoise


        # model spectrum
        self.mockwave = signal_rate.wavearr
        self.mockflux = np.random.normal(signal_rate.fluxcube, scale=signal_rate.fluxcube / self.snr)
        self.mockerror = signal_rate.fluxcube / self.snr

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
        f.create_dataset('straylight', data=self.straylight)
        f.create_dataset('snr', data=self.snr)
        f.create_dataset('saturate_mask', data=self.saturate_mask)
        f.create_dataset('mockwave', data=self.mockwave)
        f.create_dataset('mockflux', data=self.mockflux)
        f.create_dataset('mockerror', data=self.mockerror)
        f.create_dataset('img2d', data=self.img2d)
        f.close()

    def plot(self, outfile):

        report = self

        fig, axs = plt.subplots(figsize=(7, 9))
        fig.subplots_adjust(hspace=0.35, wspace=0.45,
                            left=0.10, right=0.97, top=0.97, bottom=0.05)
        cm = plt.cm.get_cmap('jet_r')

        # ax_recontructed_magmap = plt.subplot2grid((3, 4), (0, 0))
        # im = ax_recontructed_magmap.imshow(self.img2d, origin='low', cmap=cm)
        # ax_recontructed_magmap.set_xlabel('spaxel')
        # ax_recontructed_magmap.set_ylabel('spaxel')
        # ax_recontructed_magmap.set_title('reconstructed magmap')
        # cbar_ax = fig.add_axes([0.25, 0.75, 0.01, 0.2])
        # cbar = plt.colorbar(im, cax=cbar_ax, ticks=np.arange(20, 25, 2), orientation='vertical')
        # cbar.set_label(r'mag/arcsec$^{2}$', labelpad=-1)
        # cbar.ax.tick_params(labelsize=7)

        # ax_recontructed_snr = plt.subplot2grid((3, 4), (1, 0))
        # ind = np.argmin(abs(self.mockwave - 5000))
        # im = ax_recontructed_snr.imshow(self.snr[ind, :, :], origin='low', cmap=cm)
        # ax_recontructed_snr.set_xlabel('spaxel')
        # ax_recontructed_snr.set_ylabel('spaxel')
        # ax_recontructed_snr.set_title('reconstructed SNR@5000A')
        # cbar_ax = fig.add_axes([0.25, 0.41, 0.01, 0.2])
        # cbar = plt.colorbar(im, cax=cbar_ax, ticks=np.arange(0, 4, 1), orientation='vertical')
        # cbar.set_label('SNR', labelpad=-1)
        # cbar.ax.tick_params(labelsize=7)

        # points = [[15, 15], [15, 20], [15, 25]]
        # npoints = len(points)

        # for k in range(npoints):

        k = 0
        # i = points[k][0]
        # j = points[k][1]
        ax_snr = plt.subplot2grid((3, 3), (k, 0), colspan=3)
        ax_snr.plot(self.mockwave, self.snr, 'k-')
        ax_snr.set_ylabel('SNR')
        ax_snr.set_xlabel('wavelength')

        ax_noises = plt.subplot2grid((3, 3), (k + 1, 0), colspan=3)
        ax_noises.plot(self.mockwave, self.sourcenoise, label='source_noise')
        ax_noises.plot(self.mockwave, self.skynoise, label='sky_noise')
        ax_noises.plot(self.mockwave, self.readnoise, label='readout_noise')
        ax_noises.plot(self.mockwave, self.darknoise, label='dark_noise')
        ax_noises.legend(loc=1)
        ax_noises.set_ylabel('different counts')

        ax_recontructed_spec = plt.subplot2grid((3, 3), (k + 2, 0), colspan=3)
        ax_recontructed_spec.plot(self.mockwave, self.mockflux, 'k-', label='mockflux')
        ax_recontructed_spec.plot(self.mockwave, self.mockerror, 'b-', label='mockerr')
        ax_recontructed_spec.set_ylabel('mock spec')
        ax_recontructed_spec.set_xlabel('wavelength')

        plt.savefig(outfile)
        plt.close()


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
        self.straylight = f['straylight'].value
        self.snr = f['snr'].value
        self.saturate_mask = f['saturate_mask'].value
        self.mockwave = f['mockwave'].value
        self.mockflux = f['mockflux'].value
        self.mockerror = f['mockerror'].value
        self.img2d = f['img2d'].value
        f.close()


class calculation_limitmag(object):

    def __init__(self, config, straylight=False):

        instru = config['configuration']
        targetsnr = config['targetsnr']

        ccdspec_wave = np.arange(3500, 10000, 1.75555)
        darkc = instru['dark']      # e/s/pix
        rn = instru['readout_noise']   # e/pix
        nsky = get_nsky(ccdspec_wave)
        repn = config['repn']
        obst = config['obst']
        npixw = 2
        specsampling = 1

        coeff_s2 = (repn * obst) ** 2
        coeff_s1 = -targetsnr ** 2 * (repn * obst)
        coeff_s0 = -targetsnr ** 2 * (rn ** 2 * (repn * npixw * specsampling) +
                                (darkc * repn * obst * npixw * specsampling) +
                                (nsky * repn * obst))

        source_rate = (-coeff_s1 + np.sqrt(coeff_s1 ** 2 - 4 * coeff_s2 * coeff_s0)) / (2 * coeff_s2)

        throughtputwave, throughtputvalue = get_throughput(config)
        flux = electron2flux(config, ccdspec_wave, source_rate,
                             throughtputwave, throughtputvalue,
                             fluxunit='erg/s/cm^2/A')

        filter = read_filter(config['source']['normalization']['band'])
        ind_filter = (ccdspec_wave >= filter.wavemin) & (ccdspec_wave <= filter.wavemax)
        filter_wave = ccdspec_wave[ind_filter]
        filter_flux = np.interp(filter_wave, filter.wave, filter.throughput)
        self.limitmag = filter_mag(ccdspec_wave, flux, filter_wave, filter_flux, output='mag')



class calculation_exptime(object):

    def __init__(self, config, straylight=False):

        instru = config['configuration']
        snr = config['targetsnr']

        ccdspec_wave = np.arange(3500, 10000, 1.75555)
        darkc = instru['dark']      # e/s/pix
        rn = instru['readout_noise']   # e/pix
        obst = config['obst']
        # nsky = get_nsky(ccdspec_wave)
        nsky = get_background(config['zodiacal_level'],
                                  config['earthshine_level'],
                                  ccdspec_wave,
                                  instru['spaxel_xsize'],
                                  instru['spaxel_ysize'])

        npixw = 2
        specsampling = 1

        signal_rate = DetectorCountsRate(config)
        isource = signal_rate.source_counts

        # need to do loop, to limit the continous time per orbit and solve the repeat number.
        # in current situation, the exptime is larger than 300s, which is not relistic.
        repn = 1
        tmp_obst = obst * 2

        while tmp_obst / obst > 1.1:

            coeff_t2 = (isource * repn) ** 2
            coeff_t1 = -snr ** 2 * ((darkc * repn * npixw * specsampling) + (nsky * repn) + (isource * repn))
            coeff_t0 = -snr ** 2 * rn ** 2 * (repn * npixw * specsampling)

            obst_arr = (-coeff_t1 + np.sqrt(coeff_t1 ** 2 - 4 * coeff_t2 * coeff_t0)) / (2 * coeff_t2)

            filter = read_filter(config['source']['normalization']['band'])
            ind_filter = (ccdspec_wave >= filter.wavemin) & (ccdspec_wave <= filter.wavemax)
            tmp_obst = np.median(obst_arr[ind_filter])
            repn = tmp_obst * repn / obst

        self.exptime = tmp_obst * repn

        #--------
        noise = DetectorCounts(config, signal_rate, obst=config['obst'], repn=repn)

        self.source = noise.sourcenn
        self.darknoise = np.sqrt(noise.darkn)
        self.readnoise = np.sqrt(noise.rnn2)
        self.skynoise = np.sqrt(noise.skynn)
        self.sourcenoise = np.sqrt(noise.sourcenn)
        self.saturate_mask = (self.source > 65535)

        if straylight == False:
            self.straylight = np.zeros(shape=self.source.shape, dtype=float)
        else:
            # add 2% of the brightest source counts as straylight
            surface_brightness = np.sum(self.source, 0)
            ind_ycen, ind_xcen = np.where(surface_brightness == np.max(surface_brightness))
            nstraylight = self.source[:, ind_ycen[0], ind_xcen[0]] * 0.02

            self.straylight = nstraylight

        self.totnoise = np.sqrt(self.darknoise ** 2 + self.readnoise ** 2 +
                                self.skynoise ** 2 + self.sourcenoise ** 2 +
                                self.straylight ** 2)
        self.sysnoise = np.sqrt(self.darknoise ** 2 + self.readnoise ** 2 +
                                self.skynoise ** 2 + self.straylight ** 2)
        self.snr = noise.sourcenn / self.totnoise


        # model spectrum
        self.mockwave = signal_rate.wavearr
        self.mockflux = np.random.normal(signal_rate.fluxcube, scale=signal_rate.fluxcube / self.snr)
        self.mockerror = signal_rate.fluxcube / self.snr

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
        f.create_dataset('straylight', data=self.straylight)
        f.create_dataset('snr', data=self.snr)
        f.create_dataset('saturate_mask', data=self.saturate_mask)
        f.create_dataset('mockwave', data=self.mockwave)
        f.create_dataset('mockflux', data=self.mockflux)
        f.create_dataset('mockerror', data=self.mockerror)
        f.create_dataset('img2d', data=self.img2d)
        f.close()


    def plot(self, outfile):

        report = self

        fig, axs = plt.subplots(figsize=(7, 9))
        fig.subplots_adjust(hspace=0.35, wspace=0.45,
                            left=0.10, right=0.97, top=0.97, bottom=0.05)
        cm = plt.cm.get_cmap('jet_r')

        k = 0
        # i = points[k][0]
        # j = points[k][1]
        ax_snr = plt.subplot2grid((3, 3), (k, 0), colspan=3)
        ax_snr.plot(self.mockwave, self.snr, 'k-')
        ax_snr.set_ylabel('SNR')
        ax_snr.set_xlabel('wavelength')

        ax_noises = plt.subplot2grid((3, 3), (k + 1, 0), colspan=3)
        ax_noises.plot(self.mockwave, self.sourcenoise, label='source_noise')
        ax_noises.plot(self.mockwave, self.skynoise, label='sky_noise')
        ax_noises.plot(self.mockwave, self.readnoise, label='readout_noise')
        ax_noises.plot(self.mockwave, self.darknoise, label='dark_noise')
        ax_noises.legend(loc=1)
        ax_noises.set_ylabel('different counts')

        ax_recontructed_spec = plt.subplot2grid((3, 3), (k + 2, 0), colspan=3)
        ax_recontructed_spec.plot(self.mockwave, self.mockflux, 'k-', label='mockflux')
        ax_recontructed_spec.plot(self.mockwave, self.mockerror, 'b-', label='mockerr')
        ax_recontructed_spec.set_ylabel('mock spec')
        ax_recontructed_spec.set_xlabel('wavelength')

        plt.savefig(outfile)
        plt.close()


def perform_calculation(config, calculation_mode='exptime2snr'):

    if calculation_mode == 'exptime2snr':

        report = calculation_snr(config)

    elif calculation_mode == 'snr2exptime':

        report = calculation_exptime(config)

    elif calculation_mode == 'snr2limitmag':

        report = calculation_limitmag(config)

    else:

        print('calculation_mode need to be " exptime2snr | snr2exptime | snr2limitmag "')
        report = None
        pdb.set_trace()


    return report