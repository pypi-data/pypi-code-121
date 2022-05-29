import numpy as np
import pandas as pd
import os
import astropy.io.fits as fits
from scipy.integrate import simps
import extinction
import pdb

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
refdata = os.path.join(path, 'refdata/')



class read_template(object):

    r"""
    get spectrum template using the input parameters

    .. todo::
        enable to add emission lines


    Args:
        isource (dict, including 3 keys):
            name:
                the spectrum filename
            redshift:
                the redshift applied to the template
            ebv:
                the extinction applied to the template

    Attributes:

        wave (`numpy.ndarray`, unit in Angstrom):
            the wavelength of the spectrum, redshift applied.
        flux (`numpy.ndarray`, unit in erg/s/cm^2/A)
            the flux of the spectrum, redshift and extinction considered.

    """

    def __init__(self, isource):

        # self.source = isource
        # self.line_definitions = self.source['lines']

        # snpp_path = '/Users/linlin/Pro/snpp_v1_05/refdata/'
        # template_filename = snpp_refdata + 'sed/' + self.source['name']
        # filtera = snpp_path + 'normalization/filters/sdss_g0.par'
        # result = input_mag_model(self.source['normalization']['value'],
        #                          galtpl, filtera)  # scale the template to given brightness

        template_filename = isource['name']
        template_redshift = isource['redshift']
        template_ebv = isource['ebv']

        if template_filename.endswith('.fits'):

            if template_filename in ['SFgal_texp_FeH0_tau5_Ew10_AGN1.fits',
                                     'SFgal_texp_FeH0_tau1_Ewd.fits',
                                     'SFgal_texp_FeH0_tau5_Ew5.fits',
                                     'SFgal_texp_FeH-2_tau10_Ew50.fits']:
                template_filename = os.path.join(refdata, 'sed', template_filename)

            hdu = fits.open(template_filename)
            template_wave = hdu[1].data['wavelength']   # A
            template_flux = hdu[1].data['flux'] * 1e-12         # erg/s/A/cm2

            # If the data is big endian, swap the byte order to make it little endian
            if template_wave.dtype.byteorder == '>':
                template_wave = template_wave.byteswap().newbyteorder()

        elif template_filename.endswith('.txt'):

            cat = pd.read_csv(template_filename, sep='\s+', header=None)
            template_wave = cat[0]      # unit should be in Angstrom
            template_flux = cat[1]      # unit should be in erg/s/cm^2/A

        else:
            raise ValueError("File name need to be ended with '.fits' or '.txt'. ")

        # extinction require the dtype should be double.
        template_wave = np.array(template_wave, dtype='float64')

        # extinction correction
        # assuming Calzetti-00 extinction law.
        r_v = 4.5
        extinction_mag = extinction.calzetti00(template_wave,
                                               template_ebv * r_v,
                                               r_v, unit='aa')
        template_flux = extinction.apply(extinction_mag, template_flux)

        # redshift correction
        template_wave = template_wave * (1 + template_redshift)
        template_flux = template_flux / (1 + template_flux)

        self.wave = template_wave
        self.flux = template_flux


def get_wavearr(config):

    instr_par = config['configuration']
    wave_start = instr_par['wave_start']
    wave_end = instr_par['wave_end']
    wave_delta = instr_par['ccd_xsize'] * instr_par['readout_xbin']

    ccdspec_wave = np.arange(wave_start, wave_end, wave_delta)

    return ccdspec_wave


class read_filter(object):

    def __init__(self, filter_name=''):
        """

        Args:
            filter_name:
        """

        filter_file = os.path.join(refdata, 'normalization', 'filters', filter_name+'.par')
        band = pd.read_csv(filter_file, sep='\s+', header=None, comment='#')
        self.wave = band[0].values  # A
        self.throughput = band[1].values  # vaccum_pass
        self.wavemin = self.wave[0]
        self.wavemax = self.wave[-1]

        # find the central wavelength, effective wavelength, and FWHM of the given filter
        filtermid = (self.wavemax - self.wavemin) * 0.5  # A, central wavelength
        dwave = self.wave[1:] - self.wave[:-1]
        self.waveeff = np.nansum(dwave * self.wave[1:] * self.throughput[1:]) / \
                       np.nansum(dwave * self.throughput[1:])
                                                                            # A, effective wavelength
        rmax = np.max(self.throughput)
        nnn = np.where(self.throughput > 0.5 * rmax)[0]
        self.FWHMmin = self.wave[nnn[0]]      # wave range at FWHM
        self.FWHMmax = self.wave[nnn[-1]]
        self.wavefwhm = self.FWHMmax - self.FWHMmin  # A, FWHM


def filter_mag(objwave, objflux, filterwave, filterthroughtput, output='mag'):
    """
    Get AB magnitude in a certain filter.

    Args:
        objwave: unit as A
        objflux: unit as erg/s/cm^2/A
        filterwave: unit as A
        filterthroughtput: unit as detector signal per photon (use vaccum_pass for space telescope,
                              otherwise select a given airmass)

    Return:
        AB magnitude in this band

    """

    # resample the throughtput to objwave
    ind = (objwave >= np.min(filterwave)) & (objwave <= np.max(filterwave))
    wavetmp = objwave[ind]
    phot_frac = np.interp(wavetmp, filterwave, filterthroughtput)  # phot fraction (/s/A/cm^2?)

    # convert to energy fraction
    # E_frac = E0/hv * N_frac / E0 ~ N_frac/nu ~ N_frac * lambda
    energy_frac = phot_frac * wavetmp  # convert to energy fraction

    # convert the objflux to erg/s/cm^2/Hz
    c = 3e18  # A/s
    objflux_hz = objflux[ind] * (objwave[ind] ** 2) / c  # erg/s/scm^2/Hz

    from scipy.integrate import simps
    integrate_flux = simps(objflux_hz * energy_frac, c / wavetmp) / simps(energy_frac, c / wavetmp)

    if output == 'mag':
        mag = -2.5 * np.log10(integrate_flux) - 48.6
        return mag
    elif output == 'flux':
        return integrate_flux
    else:
        print('Error: output need to be "mag" or "flux". ')
        return np.nan



def normalized(template_wave, template_flux, config):

    source = config['source']

    normalize = source['normalization']

    filter = read_filter(normalize['band'])

    ind_filter = (template_wave >= filter.wavemin) & (template_wave <= filter.wavemax)
    filter_wave = template_wave[ind_filter]
    filter_flux = np.interp(filter_wave, filter.wave, filter.throughput)
    filter_constant = simps(filter_flux * filter_wave, filter_wave)

    template_constant = simps(filter_flux * template_wave[ind_filter] * template_flux[ind_filter],
                              template_wave[ind_filter])

    u0 = normalize['value']
    u0 = 10**((u0 + 48.6)/(-2.5))         # target flux in erg/s/cm^2/Hz unit
    u0 = u0 * 3e18 / filter.waveeff**2    # erg/s/cm^2/A

    factor = u0 * filter_constant / template_constant

    norm_wave = template_wave                  # A
    norm_flux = template_flux * factor         # erg/s/cm^2/A


    # check the normalized magnitude should be normalized.value - 2.5*log(0.04)
    mag = filter_mag(norm_wave, norm_flux,
                     filter_wave, filter_flux, output='mag')


    return norm_wave, norm_flux, mag


class ModelCube(object):

    def __init__(self, config):

        self.ccdspec_wave = get_wavearr(config)
        self.ccdspec_nw = len(self.ccdspec_wave)


        # grid = get_grid(config)

        object = config['source']['spectrum']


        template = read_template(object)
        template_wave_interp = self.ccdspec_wave
        template_flux_interp = np.interp(template_wave_interp, template.wave, template.flux)

        # self.ccdspec_flux = np.zeros(shape=(self.ccdspec_nw, grid.ny, grid.nx), dtype=np.float32)

        self.wavecube, self.fluxcube, self.mag2d = normalized(template_wave_interp, template_flux_interp, config)

