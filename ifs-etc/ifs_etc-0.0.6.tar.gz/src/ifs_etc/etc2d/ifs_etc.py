import os
import numpy as np

from .config import get_instrument_config, build_default_scene, build_default_bkg
import pdb

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
refdata_dir = os.path.join(path, 'refdata/')


def check_input(input_message='', input_type=None, input_range=(), input_default=None):

    # input_message:
    # input_type:
    # input_range:
    # input_default:

    tmp = False
    xx = None
    while tmp is False:

        xx_str = input(input_message + ' (default = ' + str(input_default) + '): ')

        if xx_str is '':

            xx = input_type(input_default)
            tmp = True

        else:

            try:
                xx = input_type(xx_str)

                if input_type is float or input_type is int:
                    flag_range = input_range[0] <= xx <= input_range[1]
                elif input_type is str:
                    flag_range = xx in input_range
                else:
                    flag_range = False

                if flag_range is True:
                    tmp = True
                else:
                    err_message = 'The input should be in ' + str(input_range)
                    print(err_message)
                    tmp = False

            except Exception:
                err_message = 'The input should be ' + str(input_type)
                print(err_message)
                tmp = False

    return xx


def build_input_para():

    calc = dict()

    print('######################################################')
    print('#          IFS Exposure Time Calculator              #')
    print('# (Use default value when press enter and no input)  #')
    print('######################################################')

    print('#')
    print('# 1. Spectral Resolution: 3.5 Angstrom per 2 pixels (fixed)')
    print('#    Spectral coverage: 3500-10000 A')

    print('#')
    print('# 2. CCD parameters: ')
    print('#     1. Dispersion axis binning: 1 pixel')
    print('#     2. Spatial axis binning: 1 pixel')
    print('#     3. Gain: 1 e-/ADU')
    print('#     4. Dark: 0.017 e-/s/pixel')

    readout_xbin = 1
    readout_ybin = 1
    gain = 1
    dark = 0.017

    tmp1 = False
    while tmp1 is False:

        flag_change = input('Reset the parameters or use the default value? (r|d): ')

        if flag_change == 'r':

            tmp2 = False
            while tmp2 is False:

                flag_number = input('The parameter index you want to change (1-4): ')
                if flag_number == '1':
                    readout_xbin = check_input(input_message='Dispersion axis binning',
                                input_type=int,
                                input_range=(1, 10),
                                input_default=1)

                    flag_next = input('whether or not change another one ? (y|n): ')
                    if flag_next == 'n':
                        tmp2 = True
                    else:
                        tmp2 = False

                elif flag_number == '2':
                    readout_ybin = check_input(input_message='Spatial axis binning',
                             input_type=int,
                             input_range=(1, 10),
                             input_default=1)

                    flag_next = input('whether or not change another one ? (y|n): ')
                    if flag_next == 'n':
                        tmp2 = True
                    else:
                        tmp2 = False

                elif flag_number == '3':
                    gain = check_input(input_message='Gain value',
                             input_type=float,
                             input_range=(1., 4.),
                             input_default=1)

                    flag_next = input('whether or not change another one ? (y|n): ')
                    if flag_next == 'n':
                        tmp2 = True
                    else:
                        tmp2 = False

                elif flag_number == '4':
                    dark = check_input(input_message='Dark value',
                             input_type=float,
                             input_range=(0., 0.1),
                             input_default=0.017)

                    flag_next = input('whether or not change another one ? (y|n): ')
                    if flag_next == 'n':
                        tmp2 = True
                    elif flag_next == 'y':
                        tmp2 = False
                    else:
                        print('The input needs to be (y|n). Retry.')
                        tmp2 = False

                else:
                    print('The input needs to be (1-4). Retry.')
                    tmp2 = False

            tmp1 = True
            print('#')
            print('# 2. The reseted CCD parameters: ')
            print('#     1. Dispersion axis binning: ' + str(readout_xbin) + ' pixel')
            print('#     2. Spatial axis binning: ' + str(readout_ybin) + ' pixel')
            print('#     3. Gain: ' + str('{:3.1f}'.format(gain)) + ' e-/ADU')
            print('#     4. Dark: ' + str('{:4.3f}'.format(dark)) + ' e-/s/pixel')

        elif flag_change == 'd':

            print('# Use the default CCD parameters. ')
            tmp1 = True

        else:
            print('The input needs to be (r|d). Retry.')
            tmp1 = False


    calc['configuration'] = get_instrument_config(readout_xbin=readout_xbin,
                                                  readout_ybin=readout_ybin,
                                                  gain=gain,
                                                  dark=dark)


    # calculation modes.
    obst = 300.
    print('#')
    print('# 3. Specify the calculation mode: ')
    print('#     1. How many visits needed to obtain a certain SNR.')
    print('#     2. SNR reached in certain visits.')
    print('#     (Set the exposure time = 300 seconds per visit.)')

    calc_mode = check_input(input_message='which calculation mode',
                             input_type=int,
                             input_range=(1, 2),
                             input_default=1)

    if calc_mode == 1:

        targetsnr = check_input(input_message='The target SNR is',
                             input_type=float,
                             input_range=(3, np.inf),
                             input_default=20)
        calc['calc_mode'] = {'mode': calc_mode, 'targetsnr': targetsnr, 'obst': obst}

        print('# Calculate the visits to obtain SNR = ' + str(targetsnr) + '. ')

    elif calc_mode == 2:

        repn = check_input(input_message='How many visits',
                             input_type=int,
                             input_range=(1, np.inf),
                             input_default=20)
        calc['calc_mode'] = {'mode': calc_mode, 'repn': repn, 'obst': obst}

        print('# Calculate the SNR in 300 * '+str(repn)+' seconds. ')



    # scene
    scene = []

    # define the source.
    print('#')
    print('# 4. Define the source (position, shape, spectrum, brightness). ')
    n_source = check_input(input_message='How many sources to be considered',
                             input_type=int,
                             input_range=(1, 10),
                             input_default=1)

    print('# Set the parameters for each source.')
    for i in range(n_source):

        dic = dict()

        # set the source shape
        print('# 4. (1/5) Select the source type for source-' + str(i+1) + ': ')
        print('#    1. point source')
        print('#    2. extended source')
        isource_type = check_input(input_message='Enter the index',
                         input_type=int,
                         input_range=(1, 2),
                         input_default=1)

        # set the central xy-offset
        print('# 4. (2/5) Set the center position for source-' + str(i+1) + ': ')
        x_offset = check_input(input_message='Enter the x-offset [arcsec]',
                                     input_type=float,
                                     input_range=(-3, 3),
                                     input_default=0.0)
        y_offset = check_input(input_message='Enter the y-offset [arcsec]',
                                     input_type=float,
                                     input_range=(-3, 3),
                                     input_default=0.0)
        dic['position'] = {'x_offset': x_offset, 'y_offset': y_offset}


        if isource_type == 1:

            print('# 4. (3/5) Point source is set to have PSF shape with FWHM = 0.2". ')
            dic['geometry'] = {'shape': 'PSF', 'FWHM': 0.2}


        elif isource_type == 2:

            print('# 4. (3/5) Select the shape type for extended source: ')
            print('#    1. Gaussian')
            print('#    2. Sersic')
            print('#    3. flat_box')
            shape_type = check_input(input_message='Enter the index',
                                           input_type=int,
                                           input_range=(1, 3),
                                           input_default=2)

            if shape_type == 1:

                fwhm = check_input(input_message='Enter the gaussian FWHM [arcsec]',
                                       input_type=float,
                                       input_range=(0.5, 6),
                                       input_default=1)

                dic['geometry'] = {'shape': 'gaussian', 'FWHM': fwhm}


            elif shape_type == 2:

                sersic_n = check_input(input_message='Enter the sersic index n',
                                       input_type=float,
                                       input_range=(0.5, 6),
                                       input_default=1)

                re_maj = check_input(input_message='Enter the effective radius [arcsec]',
                                       input_type=float,
                                       input_range=(0, np.inf),
                                       input_default=2)

                b2a = check_input(input_message='Enter the ratio of minor axis and major axis (b/a)',
                                       input_type=float,
                                       input_range=(0, 1),
                                       input_default=0.5)

                pa = check_input(input_message='Enter position angle of major axis (North=0, East=90) [degree]',
                                       input_type=float,
                                       input_range=(0, 180),
                                       input_default=45)

                dic['geometry'] = {'shape': 'sersic', 'sersic_n': sersic_n, 'Re_maj': re_maj,
                                   'PA': pa, 'b2a': b2a}


            elif shape_type == 3:

                xwidth = check_input(input_message='Enter the width in x-axis [arcsec]',
                                       input_type=float,
                                       input_range=(1, 30),
                                       input_default=5.)

                ywidth = check_input(input_message='Enter the width in y-axis [arcsec]',
                                       input_type=float,
                                       input_range=(1, 30),
                                       input_default=5.)

                pa = check_input(input_message='Enter the rotation angle [degree]',
                                       input_type=float,
                                       input_range=(0, 90),
                                       input_default=45)

                dic['geometry'] = {'shape': 'flatbox', 'PA': pa,
                                   'xwidth': xwidth, 'ywidth': ywidth}




        # choose or upload a spectrum template
        print('# 4. (4/5) Choose a spectrum for the source-' + str(i+1) + ': ')
        print('#    1. Elliptical galaxy (bc03_FeH0_tau1_Ewd)')
        print('#    2. Spiral galaxy (bc03_FeH0_tau5_Ew5)')
        print('#    3. Starburst galaxy (bc03_FeH-2_tau10_Ew50)')
        print('#    4. AGN (FeH0_tau5_Ew10_AGN)')
        print('#    5. upload spectrum file [text format only, '
              'with two-columns: wavelength in A and flux in erg/s/cm^2/A]')
        template_index = check_input(input_message='Enter the choise',
                                     input_type=int,
                                     input_range=(1, 5),
                                     input_default=1)

        if template_index == 1:
            template_file = os.path.join(refdata_dir, 'sed', 'SFgal_texp_FeH0_tau1_Ewd.fits')
        elif template_index == 2:
            template_file = os.path.join(refdata_dir, 'sed', 'SFgal_texp_FeH0_tau5_Ew5.fits')
        elif template_index == 3:
            template_file = os.path.join(refdata_dir, 'sed', 'SFgal_texp_FeH-2_tau10_Ew50.fits')
        elif template_index == 4:
            template_file = os.path.join(refdata_dir, 'sed', 'SFgal_texp_FeH0_tau5_Ew10_AGN1.fits')
        else:
            template_file = None
            tmp = False
            while tmp is False:
                template_file = input('Enter the spectrum file: ')
                file_exists = os.path.exists(template_file)
                if file_exists:
                    tmp = True
                else:
                    print('Do not found ' + template_file + ', retry.')
                    tmp = False


        template_redshift = check_input(input_message='Enter the redshift',
                                        input_type=float,
                                        input_range=(0, np.inf),
                                        input_default=0.0)

        template_ebv = check_input(input_message='Enter the E(B-V)',
                                   input_type=float,
                                   input_range=(0, np.inf),
                                   input_default=0.0)

        dic['spectrum'] = {'name': template_file,
                           'redshift': template_redshift, 'ebv': template_ebv}


        # set the normalization
        print('# 4. (5/5) Select the normalization type for source-' + str(i+1) + ': ')
        print('#    1. Normalized at certain wavelength. ')
        print('#    2. Normalized at certain filter. ')
        inormalization_type = check_input(input_message='Select the normalization type',
                                          input_type=int,
                                          input_range=(1, 2),
                                          input_default=2)

        if inormalization_type == 1:

            normal_wave = check_input(input_message='Enter the wavelength [A]',
                                      input_type=float,
                                      input_range=(3500, 10000),
                                      input_default=5500)

            print('# Normalization unit: [add arcsec^-2 for extended source].')
            print('#    1. erg/s/cm^2/A')
            print('#    2. erg/s/cm^2/Hz')
            print('#    3. AB magnitude')
            normal_unit_flag = check_input(input_message='Select the normalization unit',
                                      input_type=int,
                                      input_range=(1, 3),
                                      input_default=1)

            if normal_unit_flag == 1:
                normal_unit = 'erg/s/cm^2/A'
            elif normal_unit_flag == 2:
                normal_unit = 'erg/s/cm^2/Hz'
            else:
                normal_unit = 'AB magnitude'

            normal_value = check_input(input_message='Enter the normalization value',
                                      input_type=float,
                                      input_range=(0, np.inf),
                                      input_default=1e-17)

            dic['normalization'] = {'value': normal_value, 'unit': normal_unit, 'wavelength': normal_wave}


        else:

            print('# Filters: 1. sdss-u, 2. sdss-g, 3. sdss-r, 4. sdss-i, 5. sdss-z. ')
            normal_filter_index = check_input(input_message='Select the normalized filter',
                                      input_type=int,
                                      input_range=(1, 5),
                                      input_default=2)
            if normal_filter_index == 1:
                normal_filter = 'sdss_u'
            elif normal_filter_index == 2:
                normal_filter = 'sdss_g'
            elif normal_filter_index == 3:
                normal_filter = 'sdss_r'
            elif normal_filter_index == 4:
                normal_filter = 'sdss_i'
            else:
                normal_filter = 'sdss_z'

            print('# Normalization unit: [add arcsec^-2 for extended source].')
            print('#    1. AB magnitude')
            print('#    2. erg/s/cm^2/A')
            print('#    3. erg/s/cm^2/Hz')

            normal_unit_flag = check_input(input_message='Select the normalization unit',
                                      input_type=int,
                                      input_range=(1, 3),
                                      input_default=1)

            if normal_unit_flag == 2:
                normal_unit = 'erg/s/cm^2/A'
            elif normal_unit_flag == 3:
                normal_unit = 'erg/s/cm^2/Hz'
            else:
                normal_unit = 'AB magnitude'

            normal_value = check_input(input_message='Enter the normalization value',
                                      input_type=float,
                                      input_range=(0, np.inf),
                                      input_default=17.7)

            dic['normalization'] = {'value': normal_value, 'unit': normal_unit, 'band': normal_filter}


        # append to the scene one-by-one source.
        scene.append(dic)

    calc['source'] = scene


    # set the background level
    print('#')
    print('# 5. Specify the background level: ')
    print('# Zodiacal level: 1. low, 2. median, 3. high.')
    zodiacal_flag = check_input(input_message='Enter the choice',
                           input_type=int, input_range=(1, 3), input_default=2)
    if zodiacal_flag == 1:
        zodiacal = 'low'
    elif zodiacal_flag == 2:
        zodiacal = 'med'
    else:
        zodiacal = 'high'

    print('# Earth shine level: 1. low, 2. median, 3. high.')
    earth_shine_flag = check_input(input_message='Enter the choice',
                           input_type=int, input_range=(1, 3), input_default=2)
    if earth_shine_flag == 1:
        earth_shine = 'low'
    elif earth_shine_flag == 2:
        earth_shine = 'med'
    else:
        earth_shine = 'high'

    calc['background'] = {'zodiacal': zodiacal, 'earth_shine': earth_shine}



    return calc


if __name__ == '__main__':

    config = build_input_para()


