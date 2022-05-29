import os
import pandas as pd
import json

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
refdata = os.path.join(path, 'refdata/')


def get_telescope_config():

    dict = {}
    dict['diameter'] = 200
    dict['obscure'] = 0.
    dict['coll_area'] = 31415.926535897932

    # out_file = open(refdata + 'csst/telescope/config.json', "w")
    # json.dump(dict, out_file, indent=2)
    # out_file.close()

    return dict


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


    throughput_file = os.path.join(refdata, 'csst', 'ifs', 'IFU_throughput.dat')
    cat = pd.read_csv(throughput_file,
                      comment='#', sep='\s+', header=None, names=['nm', 'q'])
    throughputwave = cat['nm'].values * 10  # nm to A
    throughputvalue = cat['q'].values       # energe fraction or photon fraction??

    return throughputwave, throughputvalue


def build_default_source():

    dict = {}
    dict['spectrum'] = {'name': 'SFgal_texp_FeH0_tau5_Ew10_AGN1.fits', 'redshift': 0.0, 'ebv': 0.0, 'lines':[]}
    dict['normalization'] = {'value': 17.7, 'unit':'mag/arcsec^2', 'band': 'sdss_g'}

    # out_file = open(refdata + "source/config.json", "w")
    # json.dump(dict, out_file, indent=2)
    # out_file.close()

    return dict



def build_default_calc():

    calc = {}
    calc['configuration'] = get_instrument_config()
    calc['source'] = build_default_source()
    calc['zodiacal_level'] = 'med'
    calc['earthshine_level'] = 'med'
    calc['repn'] = 20.
    calc['obst'] = 300.

    calc['targetsnr'] = 10      # only be used in calculate_type = 'limitmag',
                                # in this case, normalization value is invalid


    return calc


