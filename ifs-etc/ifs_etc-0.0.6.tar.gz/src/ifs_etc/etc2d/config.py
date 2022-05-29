import os
import json
import pandas as pd
import numpy as np
import pdb

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
snpp_refdata = os.path.join(path, 'refdata/')

def get_telescope_config():

    dic = dict()
    dic['diameter'] = 200
    dic['obscure'] = 0.
    dic['coll_area'] = 31415.926535897932



def get_instrument_config(readout_xbin=1, readout_ybin=1, gain=1, dark=0.017):

    dic = dict()
    # user parameter
    dic['readout_xbin'] = readout_xbin
    dic['readout_ybin'] = readout_ybin
    dic['gain'] = gain                            # e/ADU
    dic['dark'] = dark                        # e/s/pix
    dic['readout_noise'] = 4.0                 # e/pix
    dic['QE'] = 1.0                            # e/pix
    dic['efficiency_file'] = 'IFU_throughput.dat'

    # hidden parameters
    dic['ccd_xsize'] = 1.755555            # A, delta_lambda_per_pixel
    dic['ccd_ysize'] = 0.1                 # arcsec, spatial axis
    dic['extract_aper_width'] = 2 * dic['readout_ybin']   # extract spectrum with aperture of 2 pixels
    dic['spaxel_xsize'] = 0.2              # arcsec
    dic['spaxel_ysize'] = dic['extract_aper_width'] * 0.1   # arcsec
    dic['fov_xsize'] = 6                 # arcsec
    dic['fov_ysize'] = 6                 # arcsec
    dic['wave_start'] = 3500
    dic['wave_end'] = 10000
    dic['wave_delta'] = dic['ccd_xsize'] * dic['readout_xbin']


    # out_file = open(refdata + "csst/ifs/config.json", "w")
    # json.dump(dict, out_file, indent=2)
    # out_file.close()

    return dic




def get_throughput():

    """
    read IFS throughput file

    Returns:
        throughputwave: unit in Angstrom
        throughputvalue: unit in energy fraction or photon fraction ?

    """

    # throughput_file = os.path.join(os.getenv('SNPP_refdata'), 'csst', 'ifs', 'IFU_throughput.dat')
    # throughput = pd.read_csv(throughput_file,
    #                          sep='\s+', skiprows=1, header=None, names=['nm', 'q'])
    # lambdaq = throughput.nm.values * 10  # nm to A
    # qifs = throughput.q.values  # ; throughput of the whole system,
    # # ;assuming the total throughput cannot reach the theory value, 0.3 is the upper limit.
    # qifs[qifs >= 0.3] = 0.3
    # qinput = 1.0                    # the throughput of the telescope
    # qtot = qifs * qinput            # *qe ;qtot of CSST already includes the CCD efficiency


    throughput_file = os.path.join(snpp_refdata, 'csst', 'ifs', 'IFU_throughput.dat')
    cat = pd.read_csv(throughput_file,
                      comment='#', sep='\s+', header=None, names=['nm', 'q'])
    throughputwave = cat['nm'].values * 10  # nm to A
    throughputvalue = cat['q'].values       # energe fraction or photon fraction??

    return throughputwave, throughputvalue





def build_default_source(source_type='', shape_type='', normalization_type=''):

    dic = dict()

    # creat an point source or an extended source
    dic['source_type'] = source_type
    dic['x_offset'] = 0.0
    dic['y_offset'] = 0.0

    if source_type == 'point':

        dic['geometry'] = {'shape': 'PSF', 'FWHM': 0.2}

    elif source_type == 'extended':

        # shape_type = 'gaussian', 'sersic', 'box',
        # only valid for extended source.
        if shape_type == 'gaussian':

            dic['geometry'] = {'shape': 'gaussian', 'FWHM': 0.2}

        elif shape_type == 'sersic':

            dic['geometry'] = {'shape': 'sersic', 'PA': 45, 'b2a': 0.5,
                                'sersic_n': 1, 'Re_maj': 2}

        elif shape_type == 'box':

            dic['geometry'] = {'shape': 'box', 'PA': 45,
                                'xwidth': 5, 'ywidth': 5}

        else:

            raise ValueError('shape_type for extended source need to be '
                             '"gaussian", "sersic" or "box". ')

    else:

        raise ValueError('source_type need to be "point" or "extended". ')

    # normalized at certain wavelength or filter.
    dic['normalization_type'] = normalization_type

    if normalization_type == 'wavelength':

        dic['normalization'] = {'value': 17.7, 'unit': 'mag/arcsec^2', 'wavelength': 5500}

    elif normalization_type == 'filter':

        dic['normalization'] = {'value': 17.7, 'unit': 'mag/arcsec^2', 'band': 'SDSS-g'}

    else:

        raise ValueError('normalization_type need to be "wavelength" or "filter". ')


    # specify the spectrum template
    dic['spectrum'] = {'name': 'SFgal_texp_FeH0_tau5_Ew10_AGN1.fits',
                        'redshift': 0.0, 'ebv': 0.0}





    # out_file = open(snpp_refdata + "source/config.json", "w")
    # json.dump(dict, out_file, indent=2)
    # out_file.close()

    return dic


def build_default_scene(n_source=1, source_type=(), shape_type=(), normalization_type=()):

    scene = []

    for i in range(n_source):

        scene.append(build_default_source(source_type=source_type,
                                          shape_type=shape_type,
                                          normalization_type=normalization_type))

    return scene


def build_default_bkg():

    dic = dict()

    dic['zodiacal_level'] = 'median'
    dic['earth_shine'] = 'median'

    return dic



# def build_default_calc(n_source=1, source_type=(), normalization_type=()):
#
#     calc = dict()
#     calc['configuration'] = get_instrument_config()
#     calc['source'] = build_default_scene(n_source=n_source,
#                                          source_type=source_type,
#                                          normalization_type=normalization_type)
#     calc['background'] = build_default_bkg()
#     calc['repn'] = 20.
#     calc['obst'] = 300.
#
#     calc['targetsnr'] = 10      # only be used in calculate_type = 'limitmag',
#                                 # in this case, normalization value is invalid
#
#
#     return calc






