#+
# Name:
#	snpp
# PURPOSE:
#	calculate the S/N per pixel for CSST and simulate a noisy spectrum for any given template.
# CALLING SEQUENCE:
#   snpp,limitmag, repeatnum=10,obstime=300,targetmag=18,/skyperpixel,$
#         galtpl=,wavearr=wavearr,mockgal=mockgal,galflux=galflux
#   plot, wavearr, galflux  ; the input galaxy template
#   plot, wavearr, mockgal  ; the output spectrum with noise
#     
# INPUTS:
# OPTIONAL IUTPUTS:
#   darkcurrent    dark current, in e/s/pix, (defult: 0.0017)
#   deltal         the delta lambda per pixel, in unit of nm (defult: 0.1755555 nm)
#   fovp           diameter of fiber (or spaxel) in arcsec (defult: 0.2 arcsec)
#   filtera         the filter you chosed to estimate the S/N (defult: bessell_V)
#   galtpl         the filename of star-forming galaxy template you want to use. 
#                  They are in the ../obs/SFgal_tpl/ folder (default: SFgal_texp_FeH0_tau5_Ew10.fits)
#   lambdac        the noise at this wavelength wanted (defult: 550 nm)
#   npixel_width   the width of the spectrum on the CCD (defult: 3.0)
#   obstime        in seconds, single integration time (defult: 300s)
#   outfile        the output file name (defult: '../results/noise.dat' )
#   qinput         the throughput correct factor (defult: 1.0)
#   readnoise      read noise, in e/pix. (defult: 4.0)
#   redshift       the redshift of the target spectrum. (defult: 0.0)
#   repeatnum      repeat number (defult: 1.0)
#   skyperpixel    a second way of estimating the Sky, if know the sky photon number per pixel
#   skyv           V band sky brightness in Johnson V mag/arcsec^2 unit (defult: 22.5 mag/arcsec^2)
#  slitwidth      suit to the slit case. the length assumed to be 0.15 arcsec
#   snlimit        S/N limit (defult: 1.0)
#   specsample     pixels per spectral resolution element (defult: 2)
#   targetmag      the surface brightness of the target you want to calculate the S/N (defult: 22 .5 mag/arcsec^2)
#   teld           diameter of the telescope, in cm unit. (defult: d=200 cm)
# OUTPUTS:
#   limitmag       the Vband surface brightness needed to achieve the S/N limit (defult: 1.0)
# OPTIONAL OUTPUTS:
#   limitemi       the medien of Flambda*dlambda*sampling value of Ha line
#   limitemif      the limit detection of Ha flux 
#   snmean         the median S/N of the whole input target spectrum (mag_v=targetmag)
#   wavearr        the wave array (nm)
#   galflux        the input galaxy flux  (1e-13 erg/s/cm2/nm)
#   mockgal        the mocked galaxy flux  with noise (1e-13 erg/s/cm2/nm)
#
# v5: 15 August 2018      writen by Lei Hao, rivised by Jun Yin
# v7: 10 Sep 2019  by Jun Yin
#     1) remove the function im_filtermag, so do not need the Kcorrect package anymore.
#     2) 
#python 
# v7: 22 Sep 2019 by Mengting Ju
#1.02alpha : 26 Sep 2019 
#1.03alpha: 29 Sep 2019
#1.03beta: 14 Oct 2019
#-
#####################################################################################
#####################################################################################

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from scipy import interpolate
from sympy import *
import os
import pdb

####################################################################################
################################################################################
class read_filter(object):
    # load the filters
    # filterfile = filtera  # '../sdss_g0.par'
    # filterpath='./'
    # filterfile=filterpath+filtersel   # ;fluxfilter: max=1, min=0, no particular unit
    def __init__(self, filterfile=''):

        # print('Filter File:', filterfile)

        band = pd.read_csv(filterfile, sep='\s+', header=None, comment='#')
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

####################################################################################
#select input parameters
def input_mag_model(targetmag, galtpl, filtera):

    #filter
    resulte = read_filter(filterfile=filtera)
    wavefilter = resulte[0]
    fluxfilter = resulte[1]
    vmin = resulte[2]
    vmax = resulte[3]
    filtereff = resulte[4]

    ####################################################################################
    # define wavelength array,
    #cover the range of 350nm to 1050nm, depend on the spectral resolution wanted.

    delta_lambda = 1.755555 # has to be in unit of A
    print('delta_lambda:', delta_lambda)

    narray = int((10000.0-3500.0) / delta_lambda)
    wavearr = 3500.0 + delta_lambda * np.float64(np.arange(narray))
    # select out the array of V band filter
    ii = np.logical_and(wavearr >= vmin, wavearr <= vmax)
    wavetmp2 = wavearr[ii]
    x = np.interp(wavetmp2,wavefilter, fluxfilter)
    integratef4 = x * wavetmp2
    integconst = simps(integratef4, wavetmp2) # int(lambda*Rlambda*dlambda)

    lambdav = filtereff #A
    ###############################################################
    # define basic target brightness, parameters constantly change
    itarget = targetmag    # in Johnson V mag/arcsec^2 unit
    print('itarget:', itarget)

    itarget_jy = 3631.0 * 10**(-itarget/2.5 + 3.0)  # target flux in V in mJy/arcsec^2 unit
    itarget_nm = itarget_jy*3.0 / (lambdav / 100.0)**2 # target flux in V in 10^(-12)erg/s/cm^2/A (/arcsec^2 ?)

    galtpl = galtpl
    tplfile = galtpl
    print('tplfile:',tplfile)

    sfgal = fits.open(tplfile)
    wavegal = sfgal[1].data['wavelength'] # A
    galflux2 = sfgal[1].data['flux']
    galflux1 = np.interp(wavearr, wavegal, galflux2)

    #;normalize the galaxy spectrum to the V band magnitude specified.
    ii = np.logical_and(wavegal >= vmin, wavegal <= vmax)
    wavetmp = wavegal[ii]
    fluxtmp = galflux2[ii]
    x = np.interp(wavetmp, wavefilter, fluxfilter)
    vfluxtmp = x * wavetmp * fluxtmp #bandpass*lambda*F_gal_lambda
    galintegrate = simps(vfluxtmp, wavetmp)
    galnorm = itarget_nm * integconst / galintegrate
    galflux = galnorm * galflux1   # the unit should now be in 10^(-12)erg/s/A/cm^2 (/arcsec^2 ?)

    return wavearr, galflux

#######################################################################################################
# select put in wave and flux
def input_wave_flux(wave,flux):

    wave=wave
    flux=flux
    delta_lambda=1.755555
    narray=int((wave[-1]-wave[0])/delta_lambda)
    wavearr=wave[0]+delta_lambda*np.float64(np.arange(narray))

    galflux=np.interp(wavearr,wave,flux)      #erg/s/A/cm2

    return wavearr, galflux*10**12

###############################################################################
def filter_mag(objwave, objflux, filterwave, filterthroughtput, output='mag'):
    '''
    :param objwave: unit as A
    :param objflux: unit as erg/s/cm^2/A
    :param filterwave: unit as A
    :param filterthroughtput: unit as detector signal per photon (use vaccum_pass for space telescope,
                              otherwise select a given airmass)
    :return: AB magnitude in this band
    '''

    # resample the throughtput to objwave
    ind = (objwave >= np.min(filterwave)) & (objwave <= np.max(filterwave))
    wavetmp = objwave[ind]
    phot_frac = np.interp(wavetmp, filterwave, filterthroughtput)  # phot fraction (/s/A/cm^2?)
    # convert to energy fraction
    # E_frac = E0/hv * N_frac / E0 ~ N_frac/nu ~ N_frac * lambda
    energy_frac = phot_frac * wavetmp  # convert to energy fraction

    # convert the objflux to erg/s/cm^2/Hz
    c = 3e18    # A/s
    objflux_hz = objflux[ind] * (objwave[ind]**2) / c    # erg/s/scm^2/Hz

    from scipy.integrate import simps
    integrate_flux = simps(objflux_hz * energy_frac, c/wavetmp) / simps(energy_frac, c/wavetmp)

    if output == 'mag':
        mag = -2.5 * np.log10(integrate_flux) - 48.6
        return mag
    elif output == 'flux':
        return integrate_flux
    else:
        print('Error: output need to be "mag" or "flux". ')
        return np.nan


def get_snr(darkc=None, repn=None, obst=None, npixw=None, specsampling=None,
            rn=None, nsky=None, isource=None):

    darkn = isource.copy() * 0.0
    darkn = darkn + (darkc * repn * obst * npixw * specsampling)  # e/s/pix * sampling * t * extraction area
    rnn2 = isource.copy() * 0.0
    rnn2 = rnn2 + rn ** 2 * (repn * npixw * specsampling)  # e/pix * sampling * readout times * extraction area
    sourcenn = (isource * repn * obst)  # e/s/sampling * t per spaxel
    skynn = (nsky * repn * obst)  # e/s/sampling * t per spaxel

    noise = np.sqrt(rnn2 + darkn + skynn + sourcenn)  # total noise
    snr = sourcenn / noise  # S/N
    # snarray[i] = sn1
    # nn = np.sqrt(rnn2 + darkn + skynn)  # system noise

    return snr


def get_expt(darkc=None, repn=None, snr=None, npixw=None, specsampling=None,
            rn=None, nsky=None, isource=None):

    coeff_t2 = (isource * repn)**2
    coeff_t1 = -snr**2 * ((darkc * repn * npixw * specsampling) + (nsky * repn) + (isource * repn))
    coeff_t0 = -snr**2 * rn ** 2 * (repn * npixw * specsampling)

    t1 = (-coeff_t1 + np.sqrt(coeff_t1**2 - 4 * coeff_t2 * coeff_t0)) / (2 * coeff_t2)
    t2 = (-coeff_t1 - np.sqrt(coeff_t1**2 - 4 * coeff_t2 * coeff_t0)) / (2 * coeff_t2)

    if max(t1, t2) > 0 and min(t1, t2) < 0:
        return max(t1, t2)
    else:
        print('check the solution of t1, t2!')
        return np.nan


def get_isource(darkc=None, repn=None, snr=None, npixw=None, specsampling=None,
            rn=None, nsky=None, obst=None):

    coeff_s2 = (repn * obst)**2
    coeff_s1 = -snr**2 * (repn * obst)
    coeff_s0 = -snr**2 * (rn ** 2 * (repn * npixw * specsampling) +
                          (darkc * repn * obst * npixw * specsampling) +
                          (nsky * repn * obst))

    s1 = (-coeff_s1 + np.sqrt(coeff_s1**2 - 4 * coeff_s2 * coeff_s0)) / (2 * coeff_s2)
    s2 = (-coeff_s1 - np.sqrt(coeff_s1**2 - 4 * coeff_s2 * coeff_s0)) / (2 * coeff_s2)

    if max(s1, s2) > 0 and min(s1, s2) < 0:
        return max(s1, s2)
    else:
        print('check the solution of s1, s2!')
        return np.nan


def flux2electron(wavearr, fluxarr, throughtputwave, throughtputvalue, fluxunit=''):
    '''
    :param wavearr: A
    :param fluxarr: erg/s/cm^2/A
    :return:
    '''

    cc = 3.0e18   # speed of light, A/s
    spaxel_area = 0.2**2    # arcsec^2
    d = 200  # diameter of the telescope, in cm unit
    obscure = 0.0  # effective central obscuration, no unit
    telarea = 3.14159 / 4.0 * d * d * (1.0 - obscure)  # effective area of the telescope, cm^2
    delta_lambda_per_pixel = 1.755555  # per pixel
    delta_hz_per_specpixel = delta_lambda_per_pixel / wavearr**2 * cc  # s^-1
    specsampling = 2.0  # 2 pixels
    planckh = 6.626e-27  # erg*s
    hv = planckh * cc / wavearr  # erg
    QE = 1

    qvalue = np.interp(wavearr, throughtputwave, throughtputvalue)

    if fluxunit=='erg/s/cm^2/A':
        isource = fluxarr * wavearr ** 2 / cc * spaxel_area  # erg/s/cm^2/Hz per spaxel
        isource2 = isource * telarea  # erg/s/Hz per spaxel
        isource3 = qvalue * isource2 * delta_hz_per_specpixel  # erg/s per spaxel
        isource4 = isource3 * specsampling  # erg/s per spec-element per spaxel
        isource5 = isource4 / hv  # phot/s per spec-element per spaxel
        isource6 = isource5 * QE  # e/s per spec-element per spaxel

        return isource6
    else:

        return np.nan


####################################################################################
class snpp(object):

    def __init__(self, wavearr=False, galflux=False,
                 calculate_type=1, readnoise=4.0,
                 fovp=0.2, npixel_width=2.0, snlimit=10, targetmaglimit=None,
                 obstime=300, repeatnum=1.0, skyr=22.5, qinput=1.0,
                 skyperpixel=False, bb=0.):

        # wavearr need to be in unit as A, delta_wavearr need to be 1.755A
        # galflux need to be in unit as erg/s/cm^2/A/arcsec^2

        # Do extensive checking of possible input errors
        #
         
        self.qinput = qinput
        self.fovp = fovp
        self.obstime = obstime
        self.skyr = skyr
        self.repeatnum = repeatnum
        self.readnoise = readnoise
        self.npixel_width = npixel_width
        self.skyperpixel = skyperpixel
        # self.filename = filename
        ###########################################################################
        #some basic unchanged parameters     
        d = 200        # diameter of the telescope, in cm unit
        obscure = 0.0  #effective central obscuration, no unit
        telarea = 3.14159 / 4.0 * d * d * (1.0 - obscure)  #effective area of the telescope, cm^2
        darkc = 0.017   #dark current, in e/s/pix
        planckh = 6.626e-27    # erg*s
        cc = 3.0e18   # speed of light, A/s
        slitunit = 0.074  # arcsec. pixelscale on 主巡天 CCD
        
        rn = readnoise  #read noise, in e/pix
        print('readnoise:', rn)
                       
        npixw = npixel_width
        print('npixel_width:', npixw)
               
        obst = obstime  # in seconds, single integration time
        print('obstime:', obst)
        
        repn = repeatnum   # repeating time
        print('repeatnum:', repn)

        iskyr0 = skyr  # in Johnson V mag/arcsec^2 unit
        print('skyv:', iskyr0)
        
        specsampling = 2.0
        #print('specsample:', sampling)
        
        delta_lambda_per_pixel = 1.755555     # per pixel
        
        #####################################################################

        # some less basic parameters, may change, but not often
        
        throughput = pd.read_csv(os.getenv('SNPP_PATH') + 'obs/IFU_throughput.dat',
                               sep='\s+', skiprows=1, header=None, names=['nm','q'])
        lambdaq = throughput.nm.values * 10    # nm to A
        qtot = throughput.q.values             #; throughput of the whole system,
 

        #;assuming the total throughput cannot reach the theory value, 0.3 is the upper limit. 
        qtot[qtot>=0.3] = 0.3
        
        qinput = qinput
        print('qinput:', qinput)
        
        tot_efficiency = qtot * qinput #*qe ;qtot of CSST already includes the CCD efficiency
        

        spaxel_area = (fovp)**2  # 1 spaxel in IFU, arcsec^2
        print('spaxel_area:', spaxel_area)
        ##############################################################################
        
        # SKY
 
        if self.skyperpixel==True :
            # print(1)
            # since the numbers are given by the main survey,
            # our detected Sky electron will be less, so scale a rough factor of 0.9
            fluxskypp = np.zeros(len(wavearr))
            scaletemp = 0.9

            ii = np.logical_and(wavearr >= 2550, wavearr <= 4000)
            counta = len(np.where(ii==1)[0])
            if counta > 0:
                fluxskypp[ii] = 0.028/counta     # e/s/spaxel/pixel
            ii = np.logical_and(wavearr >= 4000, wavearr <= 6000)
            countb = len(np.where(ii==1)[0])
            if countb > 0:
                fluxskypp[ii] = 0.229/countb
            ii = np.logical_and(wavearr >= 6000, wavearr <= 9000)
            countc = len(np.where(ii==1)[0])
            if countc > 0:
                fluxskypp[ii] = 0.301/countc
            ii = np.where(wavearr >= 9000)[0]
            countd = len(ii)
            if countd > 0:
                fluxskypp[ii] = 0.301/countd

            fluxskypp = fluxskypp / slitunit**2 * spaxel_area * scaletemp  # e/s/spaxel/spec-elements

        else:
            # print(2)
            filter = read_filter(os.getenv('SNPP_PATH')+'obs/filters/sdss_r0.par')
            # wavefilter = resulte[0]  # A
            # fluxfilter = resulte[1]  # vaccum_pass per photon
            # vmin = resulte[2]
            # vmax = resulte[3]
            # filtereff = resulte[4]
            # FWHMmin = resulte[5]
            # FWHMmax = resulte[6]

            # select out the array of r band filter
            ii = np.logical_and(wavearr >= filter.wavemin, wavearr <= filter.wavemax)
            wavetmp2 = wavearr[ii]
            x = np.interp(wavetmp2, filter.wave, filter.throughput)     # phot fraction (/s/A/cm^2?)
            integratef4 = x * wavetmp2      # convert to energy fraction
            integconst = simps(integratef4, wavetmp2)   # int(lambda*Rlambda*dlambda)

            #####################################################################

            #define r band sky brightness

            lambdar = filter.waveeff   #in A

            #sky brightness corresponding to this sky magnitude
            iskyr0_mjy = 3631.0 * 10**(-iskyr0 / 2.5 + 3.0)  # sky flux in V in mJy/arcsec^2 unit
            iskyr0_A = iskyr0_mjy * 3.0 / (lambdar/100.0)**2   # sky flux in V in 10^(-12)erg/s/cm^2/A/arcsec^2
                                                            # sky flux in V in 10^(-12)erg/s/cm^2/nm/arcsec^2

            #readin the ground sky spectrum 
            skybg_50 = pd.read_csv(os.getenv('SNPP_PATH')+'obs/skybg_50_10.dat',sep='\s+',header=None,skiprows=14)
            wavesky = np.array(skybg_50[0]) * 10 # in A
            fluxsky1 = np.array(skybg_50[1]) / 10 # phot/s/A/arcsec^2/m^2
            fluxsky2 = fluxsky1 / wavesky * 1.98 # change the sky flux unit to 10^(-12)erg/s/cm^2/A/arcsec^2


            # This fluxsky is in unit of phot/s/A/arcsec^2/m^2, to convert it to F_lambda/arcsec^2,
            # need to do fluxsky(phot/s/A/arcsec^2/m^2) * h(6.625*10^{-27}erg.s) * nu(1/s) * 10{-4}(m^2/cm^2)
            # = fluxsky * c(3.0*10^{18}A/s)/lambda(A)*6.6*10{-31} erg/s/cm^2/A/arcsec^2
            # = fluxsky / lambda * 1.98 * 10^{-12} erg/s/cm^2/A/arcsec^2

            # find out the normalization of the sky,
            ii = np.logical_and(wavesky >= vmin, wavesky <= vmax)
            wavetmp = wavesky[ii]
            fluxtmp = fluxsky1[ii]  # phot/s/A/arcsec^2/m

            x = np.interp(wavetmp, wavefilter, fluxfilter)
            vfluxtmp = x * fluxtmp * 1.98                 # 10^(-12) erg/s/cm^2/A/arcsec^2 * A
            skyintegrate = simps(vfluxtmp, wavetmp)
            skynorm = iskyr0_A * integconst / skyintegrate
            fluxsky3 = np.interp(wavearr, wavesky, fluxsky2)
            fluxsky = fluxsky3 * skynorm
            # get the sky spectrum in wavearr grid, the unit should now be the same as fluxvega:
            # 10^(-12) erg/s/A/cm^2  (/arcsec^2 ?)

            fluxskypp = fluxsky


        ##########################################################################
        
        #define observation information, parameters constantly change
       
        nwave = len(wavearr)   # per delta_wavearr
        expf2 = np.zeros(nwave)
        QE = 1

        # 'lambda', 'S/N', 'tar_flux', 'tot_noise', 'sc_noise', \
        # 'sys_noise', 'readnoise', 'dark_noise', 'sky_noise', 'mockgal'
        snarray = np.zeros(nwave)
        tot_noise = np.zeros(nwave)
        sc_noise = np.zeros(nwave)
        sys_noise = np.zeros(nwave)
        read_noise = np.zeros(nwave)
        dark_noise = np.zeros(nwave)
        sky_noise = np.zeros(nwave)
        mockflux = np.zeros(nwave)
        mockerror = np.zeros(nwave)
        mockgal = np.zeros(nwave)
        isource6 = np.zeros(nwave)

        tmp = np.zeros(nwave)
        lista = np.zeros(shape=(nwave, 10), dtype=float)


        isource = flux2electron(wavearr, galflux, lambdaq, tot_efficiency, fluxunit='erg/s/cm^2/A')    # e/s
        if self.skyperpixel:
            nsky = fluxskypp * specsampling  # e/s in npixw * sampling pixels


        snr = get_snr(darkc=darkc, repn=repn, obst=obst, npixw=npixw, specsampling=specsampling,
                      rn=rn, nsky=nsky, isource=isource)



        pdb.set_trace()



        for i in range(nwave):     # for each spec-pixel

            ilambda = wavearr[i]
            iqlambda = np.interp(ilambda, lambdaq, tot_efficiency)
            hv = planckh * cc / ilambda     # erg
            delta_hz_per_specpixel = cc * delta_lambda_per_pixel / ilambda / ilambda    # s^-1
            delta_hz_per_specelement = delta_hz_per_specpixel * specsampling
            
            # now that many fluxes are in 10^(-12)erg/s/A/cm^2, to convert it to Jy, need to multiple:
            # lambda0^2/c(in A) = lambda0^2(A)/(3.*10^(18))*10^(-12)erg/s/Hz/cm^2
            # = lambda^2(A)*3.33*10^(-31)erg/s/Hz/cm^2=lambda^2(A)*3.33*10^(-8)Jy
            # = lambda^2(A)*0.0333uJy

            if self.skyperpixel :
                nsky = fluxskypp[i] * specsampling    # e/s in npixw * sampling pixels
            else:
                #find out sky value at lambda0
                #calculate n_sky/pixel
                isky = fluxskypp[i] * lambda0**2 * 0.0333 * spaxel_area   #in uJy/spaxel unit
                iskyall = isky * telarea / 1000.0   #in 10-26 erg/s/Hz /spaxel
                fsky = qlambda * iskyall * delta_hz   #10^{-8} erg/s /spaxel
                fsky = fsky * specsampling
                nsky = fsky / hv * 10.0   #in unit of #e/s /spaxel

            #calculate n_source/pixel
            # isource = galflux[i] * lambda0**2 * 0.0333 * spaxel_area   #in uJy/spaxel unit
            # isall = isource * telarea / 1000.0   #in 10-26 erg/s/Hz /spaxel
            # fs = qlambda * isall * delta_hz   #10^{-8} erg/s /spaxel
            # fs = fs * specsampling
            # ns = fs / hv * 10.0         # photon/s/spaxel, need to consider QE curve
            #                             # in unit of #e/s /spaxel

            isource = galflux[i] * ilambda**2/cc * spaxel_area          # erg/s/cm^2/Hz per spaxel
            isource2 = isource * telarea                                # erg/s/Hz per spaxel
            isource3 = iqlambda * isource2 * delta_hz_per_specpixel     # erg/s per spaxel
            isource4 = isource3 * specsampling                          # erg/s per spec-element per spaxel
            isource5 = isource4 / hv                                    # phot/s per spec-element per spaxel
            isource6[i] = isource5 * QE                                    # e/s per spec-element per spaxel

            # need to consider additional fraction if extracting area cannot include total source flux
            # (PSF size larger than npixw)
            # (??) the result will be same for extended source? flux in other spaxels will be counted in.


            isource = flux2electron(wavearr, galflux, lambdaq, tot_efficiency, fluxunit='erg/s/cm^2/Hz')
            pdb.set_trace()


            darkn = (darkc * repn * obst * npixw * specsampling)        # e/s/pix * sampling * t * extraction area
            rnn2 = rn**2 * (repn * npixw * specsampling)                # e/pix * sampling * readout times * extraction area
            sourcenn = (isource6[i] * repn * obst)                         # e/s/sampling * t per spaxel
            skynn = (nsky * repn * obst)                                # e/s/sampling * t per spaxel


            nn1 = np.sqrt(rnn2 + darkn + skynn + sourcenn)  # total noise
            sn1 = sourcenn / nn1  # S/N
            snarray[i] = sn1
            nn = np.sqrt(rnn2 + darkn + skynn)  # system noise
            
            
            # mockgal[i] = galflux[i] + galflux[i] / snarray[i] * np.random.randn(1,1)[0][0]  # in 10^{-12} erg/s/A/cm^2
            mockflux[i] = np.random.normal(galflux[i], scale=galflux[i]/snarray[i])
            mockerror[i] = galflux[i] / snarray[i]

            lista[i,:] = [ilambda, sn1, galflux[i], nn1,\
                        np.sqrt(sourcenn), nn, np.sqrt(rnn2), np.sqrt(darkn), \
                        np.sqrt(skynn), mockflux[i]]



            snr = get_snr(darkc=darkc, repn=repn, obst=obst, npixw=npixw, specsampling=specsampling,
                     rn=rn, nsky=nsky, isource=isource6[i])
            t = get_expt(darkc=darkc, repn=repn, snr=snarray[i], npixw=npixw, specsampling=specsampling,
                     rn=rn, nsky=nsky, isource=isource6[i])
            s = get_isource(darkc=darkc, repn=repn, snr=snarray[i], npixw=npixw, specsampling=specsampling,
                     rn=rn, nsky=nsky, obst=obst)   # identical to the f1 in the old version.



            # pdb.set_trace()


            # set the detection limit
            # detlimit = snlimit
            detlimit = snarray[i]

            nntmp = detlimit**2 + np.sqrt(detlimit**4 + 4.0 * detlimit**2 * nn**2)
            nntmp = nntmp / 2.0
            # calculate detection limit in uJy and mag
            fnn = nntmp
            f1 = fnn / obst / repn    #in e/s
            f2 = f1 * hv       #in 10^{-9} erg/s
            f3 = f2 / delta_lambda_per_pixel #in 10^{-9} erg/s/A
            f1 = f3 / telarea   #in 10^{-9} erg/s/A/cm^2
            f2 = f1 / iqlambda    #in 10^{-9} erg/s/A/cm^2
            expf2[i] = f2 / spaxel_area * 100000.   # in 10^{-14} erg/s/A/cm^2/arcsec^2


        pdb.set_trace()

        ############################################################################################
        self.output_spectra = lista
        # 'lambda', 'S/N', 'tar_flux', 'tot_noise', 'sc_noise', \
        # 'sys_noise', 'readnoise', 'dark_noise', 'sky_noise', 'mockgal'


        #####################################################################
        filter = read_filter(filterfile=os.getenv('SNPP_PATH')+'obs/filters/sdss_g0.par')
        # wavefilter = resulte[0]
        # fluxfilter = resulte[1]
        # vmin = resulte[2]
        # vmax = resulte[3]
        # filtereff = resulte[4]
        # FWHMmin = resulte[5]
        # FWHMmax = resulte[6]

        ii = np.logical_and(wavearr >= filter.FWHMmin , wavearr <= filter.FWHMmax)
        wavetmp = wavearr[ii]
        snm = np.median(snarray[ii])
        # the median SN of FWHM range to achieve the sn limit
        im = np.where(snarray[ii] == snm)[0]
        fact = expf2[ii][im] * 0.01 / galflux[ii][im]
        limitmag = -2.5 * np.log10(fact) + targetmaglimit
        self.aa = limitmag
        print('limitmag:', limitmag)

        # pdb.set_trace()


        if calculate_type == 1:
            # signal_at_targetband = filter_mag(wavearr, mockflux, filter.wave, filter.throughput, output='flux')
            # noise_at_targetband = filter_mag(wavearr, mockerror, filter.wave, filter.throughput, output='flux')
            ii = np.logical_and(wavearr >= filter.FWHMmin, wavearr <= filter.FWHMmax)
            median_snr = np.median(snarray[ii])
            self.result = median_snr

        elif calculate_type == 2:
            self.result = exptime_need

        elif calculate_type == 3:
            self.result = surface_brightness

        else:
            self.result = np.nan



    ############################################################################

    # def printf(self):
    #     return self.aa

    #############################################################################

    # def fits(self):
    #     return self.bb

    ###############################################################################

    def save_output_spectra(self, outfilename=''):

        list = self.output_spectra
        namedat = np.array(['lambda', 'S/N', 'tar_flux', 'tot_noise', 'sc_noise', \
                          'sys_noise', 'readnoise', 'dark_noise', 'sky_noise', 'mockgal'])
        unit = np.array(['A', ' ','1e-12 erg/s/cm2/A',\
                       '#e','#e','#e','#e','#e','#e', '1e-12 erg/s/cm2/A'])

        hdr = fits.Header()
        for i in range(len(namedat)):
            hdr[str(i)] = unit[i]

        hdu0 = fits.PrimaryHDU(header=hdr)
        hdu1 = fits.BinTableHDU.from_columns(
            [fits.Column(name=namedat[i], array=np.array(list[:,i]), format='1E') for i in range(len(namedat))]
        )
        hdulist = fits.HDUList([hdu0, hdu1])

        print('output filt:',outfilename)
        hdulist.writeto(outfilename, overwrite=True)



    # print('The END!')
        
#######################################################################################################

