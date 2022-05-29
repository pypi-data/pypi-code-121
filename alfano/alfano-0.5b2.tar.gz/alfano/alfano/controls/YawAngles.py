#! python
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 11:11:52 2018

@version 0.5a1

@description:
    This module performs a lookup on a precomputed table of control law scale factors 
    by orbit ratio.  It is designed to be called from within a GMAT mission sequence.

    The result of the lookup is multiplied by the cosine of the Argument of Latitude and the 
    yaw angle is returned in degrees.
    
    Yaw is defined here as as an angle normal to the orbital plane in the 
    Velocity-Normal-Binormal satellite coordinate system.
    This can be confusing as aircraft define yaw as heading and pitch normal
     to the horizon.

    The computation of the yaw control angle is based on Edelbaum's control law, see
    Wiesel and Alfano, "Optimal Many-Revolution Orbit Transfer" and is implemented 
    in package alfano by AlfanoLib.py.

    The argment to the control law, the control variable, is read from a 901x1471 dictionary
    formatted as a JSON file:
    
    {
    Lambda_0:[cv1[0], cv1[1], ..., cv1[900]], 
    Lambda_1:[cv2[0], cv2[1], ..., cv2[900]], 
    ..., 
    Lambda_1470:[cv1470[0], cv1470[1], ..., cv1470[900]]
    }
    
    where the cv are in order of orbit ratio from 1.00 to 10.00.

    Internal Dependencies:
        get_control_onrev() ->
            get_control() ->
                get_yaw_angle() -> 
                    get_yaw_cv()  

@author: Colin Helms
@author_email: colinhelms@outlook.com

@license
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>

@change log:
    04/28/2018: Initial baseline.
    04/30/2018: AlfanoChebyshev.py used to generate u values.
    05/11/2018, Rewritten to use a pre-generated linear array of u values.
    05/18/2018, Added test cases and adjusted signatures for GMAT call.
    05/20/2018, Changed name of input files, integrated with GMAT.
    06/01/2018, Added logic for Kluever eclipse weighting, and test case.
    03/06/2019, Added costate parameter, enables variable inclinations under external control.
    04/08/2019, Controls.json elaborated for all costates. 
    04/10/2019, Added JSON codec to output dictionary of ndarray.
    04/28/2019, Deployed version 0.2a to C:/Users/chelm/Anaconda3/Lib/site-packages
    for integration of new Controls.json with GMAT.
    05/21/2019, get_yaw_sf() renamed get_yaw_cv(). Added interpolation of costate value.
    02/22/2022, Fixed Issue 02212022-001. Use shared file containing path for Controls.json.
    02/22/2022, Fixed Issue 02222022-001. Test case 3 costate limits are now max/min of alf.lambda.
"""
from asyncio.windows_events import NULL
from logging import NullHandler

import numpy as np
import json as js
from pathlib import Path
from pathlib import PurePath #Issue 03092022-001
from alfano import AlfanoLib as alf

_fp = None
""" file pointer in Global scope """

def get_control_onrev (costate, AOL, SMA, SMA_init = 6838.1366, more = -1):
    """ Function provides a wrapper to perform conversions from SMA in km
    to the orbit ratio; the given SMA is divided by SMA_init.  SMA_init is
    set to the canonical Earth radius to avoid divide by zero, but the 
    caller should pass in the SMA of the starting orbit to get correct results.
    
    Function checks for completed revolution and calls get_yaw_angle() with 
    given AOL and computed orbit_r, sets AOL_init equal to the current AOL, else
    returns original yaw angle.
    
    Future: eclipse effects will accounted for in function set_apsides().
    
    Returns:
        [Thrust vector components in Velocity-Normal-Bi-normal coordinates]
        
    Parameters:
        AOL: argument of longitude in degrees
        SMA: the current SMA in kilometers
        SMA_init: the SMA of the initial orbit in kilometers
        more: defines the direction of the yaw angle, -1 decreases inclination.
        costate: the lambda inclination solution.
    """
    if (costate >= -1.570) and (costate <= -0.100):
        """ costate is essentially a tangent, causes computation problems in the neighborhood of 0 """
        if SMA_init >= 6338.1366:
            orbit_r = np.round(SMA/SMA_init, 2)
        else:
            raise ValueError("SMA_init {0} is invalid.".format(SMA_init))
    else:
        raise BadCostate("Value {0} is out of range.".format(costate))
        
    if (orbit_r >= 1) and (orbit_r <= 10):
        B = 0.0
        """ For combined orbit-raising and inclination, the binormal thrust angle (pitch) is 0. """
        
        V, N = get_control(costate, AOL, orbit_r, more)
         
        return [V, N, B]
    
    else:
        raise ValueError ("Orbit ratio {0} is invalid value.".format(orbit_r))
        
def get_control (costate, AOL, orbit_r, nmore):
    """ Returns the Alfano control for each orbit increment.
    
            yaw_angle = arctan[cos(AOL)/sqrt(1/u - 1)].
        
        where u is indexed by orbit_r and costate in the controls.json file
        
        The algorithm is a reverse-lookup of precomputed values
        of the Edelbaum control variable, u (aka cv) which are computed in 
        another script using the Alfano method for solution of the 
        multi-revolution orbit transfer (see AlfanoLib.py)
        
        The precomputed values are first written into an Excel Workbook and
        a table of u is created by look-up from the optimization costate.
        This table is called the Trajectory table, because values of u for
        any given costate define trajectories in the inclination and 
        semi-major axis plane.  The Trajectory table is provided both in
        the generating Excel workbook, and in a JSON table.  
        
        The Excel workbook access may provide better performance since the
        Excel file remains open as an active object following the first call, 
        values are returned via the active object socket protocol.
        
        The JSON file method is more portable, however values for only one
        value of the optimization costate are available per file.
        
        Set useJSON = False in order to use the Excel active object.
        
        Returns:
            Components of thrust in VNB coordinates.
        
        Parameters:
            AOL: the angular position from the line of nodes, in degrees 
            orbit_r: the current orbit ratio
            nmore: +/1, defines the direction of the yaw angle, 
                defined negative for decreasing inclination.
    """
    theta = nmore * get_yaw_angle (AOL, orbit_r, costate)
    
    return [np.cos(theta), np.sin(theta)]

def get_yaw_angle (AOL, orbit_r, costate):
    """ Function implements the Edelbaum control law.  Returns the yaw angle
    in degrees.  This function is good for plots.
        
        Returns:
            Thrust angle in radians.
        
        Parameters:
            AOL: the angular position from the line of nodes, in degrees 
            orbit_r: the current orbit ratio  
    """
    
    AOL = AOL*(np.pi/180)
    """ GMAT provides degrees, np.cos expects radians """
    
    cv = get_cv(orbit_r, costate)
    
    if cv != 1:
        sf = np.sqrt(cv/(1-cv))
#        sf = np.sqrt(1/cv - 1)

        #Not sure how this makes sense, but it is consistent with Alfano and Edelbaum.
#        theta = np.arctan(np.cos(AOL)/sf)
        theta = np.arctan(np.cos(AOL) * sf)
        """ Make a pi/2 correction to align maximum yaw pi/2 from nodes. """
    else:
        theta = 1.570796326
        """ np.arctan(9999 9999 9999 9999) """
    
    return theta
         
def get_cv(orbit_r, costate) :
    """ Function looks up control variable in JSON Control file based on costate. 
    returns the denominator of the control function.
    Changed 08Apr2019: complete table of costates is searched.
    """
    global _fp
    
    if _fp == None:
        read_controlfile()
    
    row = int(round(1 + orbit_r/alf.PREC_ORBITR, 0)) - 100
    
    """ The given costate may not be an exact match for the key to UbyRbyL.  For
    example, a given value of -0.36 will fall between the values -0.3599 and
    -0.3604.  The array AlfanoLib.Lambda contains the exact keys.  Since the intervals
    between the values of Lambda are small in the costate dictionary (UbyRbyL),
    linear interpolation of the return value is feasible.
    """
    if costate > -0.1186 or costate < -1.5686:
        """ The costate should be a negative number and is the argument to a tangent. 
        A tangent has singularities at zero and pi/2 (1.57). 
        """
        raise KeyError('Costate value {0} is not a negative argument to a tangent.'.format(costate))
    
    isfound = np.where(alf.Lambda <= costate)
    """ This algorithm is similar to that used at line 290 in GenerateControlTable.py.
    
    Note: np.where returns an ndarray in element [0] with a sequence of indices to values
    which meet the condition.
    Costate values decrease (become more negative) from left to right.  Therefore the 
    first element which meets the condition is the index of the first number more negative than
    the given costate.  Remaining elements all point to more negative values than the given costate.
    The syntax for extracting the first element: "isfound[0][0]".
    """
    
    if np.size(isfound[0], 0) > 0:
        """ Possibly the given costate does not exist in Lambda. Obvious errors are 
        a number between zero and -0.1186, or a number less than -1.5686.
        """                
        found_index = isfound[0][0]
        l_found = alf.Lambda[found_index]
        l_before = alf.Lambda[found_index - 1]

        if costate == l_found:
            """ By chance or design the given costate exactly equals a canonical
            costate value.
            """
            return alf.UbyRbyL[l_found][row]
        else:
            """ Interpolate the value of cv """
            l_lo = l_found
            l_hi = alf.Lambda[found_index - 1]
            u_hi = alf.UbyRbyL[l_found][row]
            u_lo = alf.UbyRbyL[l_before][row]
            
            return alf.lin_interp(l_hi, l_lo, costate, u_lo, u_hi)
    else:
        """ Some other problem with the passed in costate value. """
        raise KeyError('The costate value {0} is not valid.'.format(costate))


def read_controlfile(ctlfile=None):
    """ 
    Reads the Controls.json file and initializes the AlfanoLib UbyRbyL global dictionary.
    The _fp global file pointer is used as a singleton to indicate whether the Control File
    has been read and UbyRbyL initialized.  This is only done once per YawAngles instance.

    Fix for AlfanoLib Issue 02212022-001, Bad Default Path in YawAngles. Remove the 
    default file path.
    """    
    global _fp

    # Begin Issue 02212022-001 Fix
    #sharedfname = Path.cwd() / Path('SavedJsonPath')
    """ SavedJsonPath filename constitutes an interface agreement with GenerateControlTable."""

    #Begin Issue 03092022-001 Fix
    thispath = PurePath(__file__)

    sharedfname = thispath.parent/'SavedJsonPath'
    """ SavedJsonPath filename constitutes an interface agreement with GenerateControlTable."""

    try:
        with open(sharedfname, 'r') as fd:
            ctlfile = fd.readline()
               
    except OSError as e:
        print('SaveJsonPath could not be opened for writing {0}.'.format(ctlfile))
   # End Issue 02212022-001 Fix

    try:
        if not ctlfile:
            raise FileNotFoundError("Control file path has not been set from SavedJsonPath.")
        else:
            with open(ctlfile, 'r') as _fp:
                dct = alf.load(_fp)
                            
    except OSError as e:
        raise OSError("Invalid Controls.json filepath: {0} {1}".format(ctlfile, sharedfname))
   
    except Exception as e:
        ("Exception reading JSON file: {0}".format(e.__doc__))

    for l in alf.UbyRbyL:
        """ Parameter dct is a dictionary of lists, key is a string.
        convert to ndarray with key as float64. Loop is elaborated for debug."""
                    
        try:
            U = np.array(dct[str(l)])
            #print ('np.array(dct[str(l)]) = {0}'.format(U))
            alf.UbyRbyL[l] = U
            
        except Exception as e:
            raise RuntimeError('Exception loading UbyRbyL dictionary: {0} for costate {1}.'.format(e.__doc__), l)        
   
def shadow_arc(beta, P, RMAG, MU = 1, RINIT = 6378.136):
    """ 
    This function implements the shadow arc computation from Vallado p.305.
    Vallado uses a cylindrical shadow model.
    
    Parameters: 
        beta, the beta angle from Earth to the sun for any season.
        P, the orbital period.
        RMAG, the magnitude of the orbit radius vector
    Returns:
        The shadow arc in radians
    """
    deg2rad = np.pi/180
    
    beta_rads = beta*deg2rad
    
    shadow_size = np.sqrt(1 - (6378.136/RMAG)**2)
    
    earth_angle = shadow_size/np.cos(beta_rads)
    
    if earth_angle <= 1:
        #sharc = np.arccos(earth_angle)*P/np.pi
        sharc = np.arccos(earth_angle)
    else:
        sharc = 0
    #return np.arccos(earth_angle/np.cos(beta_rads))*P/np.pi
    return sharc

def eclipse_weight(beta, P, RMAG):
    """ 
    This function is after the treatment by Kluever et al documented 
    in Journal of Guidance and Control, Vol 34, No 1, p.300.
    Function computes the time in shadow from sun Beta angle, RMAG, Period and the 
    radius of the Earth.
    Parameters:
        beta, P and RMAG passed to shadow_arc function
    Returns:
        Proportion of orbit that is in sunlight.
    """
    sharc = shadow_arc(beta, P, RMAG)
    return 1 - sharc/(2*np.pi)

class BadCostate(Exception):
    def __init__(self, message):
        self.message = message
        self.__doc__ = "Bad Costate"
  
""" *****Test cases***** """  
if __name__ == "__main__":
    import logging
    import platform
    import getpass
    import matplotlib as mpl
    import matplotlib.pyplot as plt
        
    logging.basicConfig(
            filename='./GenControls.log',
#            level=logging.INFO,
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s %(levelname)s:\n%(message)s', datefmt='%d%B%Y_%H:%M:%S')

    logging.info("!!!!!!!!!! Control Table Generation Started !!!!!!!!!!")
    
    host_attr = platform.uname()
    logging.info('User Id: %s\nNetwork Node: %s\nSystem: %s, %s, \nProcessor: %s', \
                 getpass.getuser(), \
                 host_attr.node, \
                 host_attr.system, \
                 host_attr.version, \
                 host_attr.processor)
    
    AOL = np.linspace(0, 360, 61) # Initialize Argument Of Latitude (AOL).
    mpl.rcParams['legend.fontsize'] = 10
    fig, axs = plt.subplots(2,1)

    """ Test Case 0: Initialize dictionary from Controls.json file."""
    read_controlfile() # Initializes alf.UbyRbyL dictionary.

    """ Test Case 1: Plot the values of yaw angles at least negative costate value."""
    maxlambda = max(alf.Lambda) # Don't get confused, Lambda values are negative numbers.
    angles21 = get_yaw_angle (AOL, 1.1, maxlambda)
    # Was: angles21 = get_yaw_angle (AOL, 1.1, -0.1186)
    # Fix for AlfanoLib Issue 02222022-001 Out of Bound Costate.

    axs[0].set_title('Test Case 1: Yaw Angle at R=1.1, costate {0}'.format(maxlambda))
    axs[0].set_xlabel('Arg of Latitude')
    axs[0].set_ylabel('Yaw(radians)')
    plot21 = axs[0].plot(AOL, angles21)
   
    angles61 = get_yaw_angle (AOL, 6.13, maxlambda)
    # Was: angles61 = get_yaw_angle (AOL, 6.13, -0.1186)
    # Fix for 02222022-001 Out of Bound Costate.

    axs[1].set_title('Test Case 1: Yaw Angle at R=6.13, costate {0}'.format(maxlambda))
    axs[1].set_xlabel('Arg of Latitude')
    axs[1].set_ylabel('Yaw(radians)')
    plot61 = axs[1].plot(AOL, angles61)
 
    plt.tight_layout()
    plt.show()
    plt.close()

    fig, axs = plt.subplots(2,1)

    angles21 = get_yaw_angle (AOL, 1.1, -0.4284)
    axs[0].set_title('Test Case 1: Yaw Angle at R=1.1, Costate -0.4284')
    axs[0].set_xlabel('Arg of Longitude')
    axs[0].set_ylabel('Yaw(radians)')
    plot21 = axs[0].plot(AOL, angles21)
   
    angles61 = get_yaw_angle (AOL, 6.13, -0.4284)
    axs[1].set_title('Test Case 1: Yaw Angle at R=6.13, Costate -0.4284')
    axs[1].set_xlabel('Arg of Longitude')
    axs[1].set_ylabel('Yaw(radians)')
    plot61 = axs[1].plot(AOL, angles61)
    
    plt.tight_layout()
    plt.show()
    plt.close()

    fig, axs = plt.subplots(2,1)

    angles21 = get_yaw_angle (AOL, 1.1, -0.6214)
    axs[0].set_title('Test Case 1: Yaw Angle at R=1.1, Costate -0.6214')
    axs[0].set_xlabel('Arg of Longitude')
    axs[0].set_ylabel('Yaw(radians)')
    plot21 = axs[0].plot(AOL, angles21)
   
    angles61 = get_yaw_angle (AOL, 6.13, -0.6214)
    axs[1].set_title('Test Case 1: Yaw Angle at R=6.13, Costate -0.6214')
    axs[1].set_xlabel('Arg of Longitude')
    axs[1].set_ylabel('Yaw(radians)')
    plot61 = axs[1].plot(AOL, angles61)
    
    plt.tight_layout()
    plt.show()
    plt.close()
    
    fig, axs = plt.subplots(2,1)

    angles21 = get_yaw_angle (AOL, 1.1, -0.9692)
    axs[0].set_title('Test Case 1: Yaw Angle at R=1.1, Costate -0.9692')
    axs[0].set_xlabel('Arg of Longitude')
    axs[0].set_ylabel('Yaw(radians)')
    plot21 = axs[0].plot(AOL, angles21)
   
    angles61 = get_yaw_angle (AOL, 6.13, -0.9692)
    axs[1].set_title('Test Case 1: Yaw Angle at R=6.13, Costate -0.9692')
    axs[1].set_xlabel('Arg of Longitude')
    axs[1].set_ylabel('Yaw(radians)')
    plot61 = axs[1].plot(AOL, angles61)
    
    plt.tight_layout()
    plt.show()
    plt.close()

    fig, axs = plt.subplots(2,1)

    minlambda = min(alf.Lambda)
    angles21 = get_yaw_angle (AOL, 1.1, minlambda)
    # Was: angles61 = get_yaw_angle (AOL, 1.1, -1.5686)
    # Fix for 02222022-001 Out of Bound Costate.
      
    axs[0].set_title('Test Case 1: Yaw Angle at R=1.1, costate {0}'.format(minlambda))
    axs[0].set_xlabel('Arg of Longitude')
    axs[0].set_ylabel('Yaw(radians)')
    plot21 = axs[0].plot(AOL, angles21)
   
    angles61 = get_yaw_angle (AOL, 6.13, minlambda)
    # Was: angles61 = get_yaw_angle (AOL, 6.13, -1.5686)
    # Fix for 02222022-001 Out of Bound Costate.
   
    axs[1].set_title('Test Case 1: Yaw Angle at R=6.13, costate {0}'.format(minlambda))
    axs[1].set_xlabel('Arg of Longitude')
    axs[1].set_ylabel('Yaw(radians)')
    plot61 = axs[1].plot(AOL, angles61)
    
    plt.tight_layout()
    plt.show()
    plt.close()

    """ Test Case 2: Interpolate the costate and plot the values of Yaw angles."""
    fig, axs = plt.subplots(2,1)

    angles21 = get_yaw_angle (AOL, 1.1, -0.36)
    axs[0].set_title('Test Case 2: Yaw Angle at R=1.1, Interpolate Costate -0.36')
    axs[0].set_xlabel('Arg of Longitude')
    axs[0].set_ylabel('Yaw(radians)')
    plot21 = axs[0].plot(AOL, angles21)
   
    angles61 = get_yaw_angle (AOL, 6.13, -0.36)
    axs[1].set_title('Test Case 2: Yaw Angle at R=6.13, Interpolate Costate -0.36')
    axs[1].set_xlabel('Arg of Longitude')
    axs[1].set_ylabel('Yaw(radians)')
    plot61 = axs[1].plot(AOL, angles61)
    
    plt.tight_layout()
    plt.show()
    plt.close()
    
    """ Test Case 3: Simulate GMAT call, Log thrust Components."""
    SMA_init = 6838.1366    
    SMA = np.linspace(6938, 41938, 10) # Semi-Major Axis
    MU = 1                  # canonical gravitational constant 
    DU = 6378.1366          # canonical dsistance unit - Earth radius
    TU = 806.81112382429    # canonical time unit - Solar second

    DUstar = SMA_init/DU    # non-dimensional DU 1.072121
    TUstar = TU * np.sqrt(np.power(DUstar,3)/MU) # canonical TU

    R_init = 1              # Orbit Ratio
    R_final = 10
    AOL_init = 0            # Argument of Latitude

    costates = -0.01*np.linspace(45, 59, 15)         # Alfano lambda

    thrustv = [0, 1.0, 0]   # thrust vector, initialized
        
    with open('thrustlog.log', 'w+') as log:
        log.write('Test Case 3, call simulates GMAT use.\n')
        log.write('Orbit Ratios from 1 to 10\n')
        log.write('With lambda = {0} to {1}.\n'.format(costates[0],costates[14]))
        log.write('By Argument of Longitude\n')
        log.write('Columns are velocity, normal, and binormal components of thrust angle.\n')
        
        for lamb in costates:
            for d in SMA: 
                for long in AOL:                
                    thrustv = get_control_onrev(lamb, long, d, 6838, -1)
                    log.write('\nCostate: {0:.2g}, '.format(lamb))
                    log.write('SMA: {0:.6g}, '.format(d))
                    log.write('AOL: {0:.6g}, '.format(long))
                    log.write('velocity: {0:.2g}, normal: {1:.2g}, binormal: {2:.2g}'\
                        .format(thrustv[0], thrustv[1], thrustv[2]))                 
        
    print('See file "thrustlog.log" for results of Test Case 3.')
    
    """ Test Case 4: shadow_arc() and eclipse_weight() """
    betas = np.linspace(-60, 60, 61)
    sharc = np.zeros(61)
    weights = np.ones(61)
    
    RMAG = 15000
    P = 18000 # 2*pi*sqrt(RMAG^3/mu)
    
    for n in range(0,60):
        beta = betas[n]
        sharc[n] =   shadow_arc(beta, P, RMAG,)
        weights[n] = eclipse_weight(beta, P, RMAG,)
        
    fig, axs = plt.subplots(2,1)

    axs[0].set_title('Shadow Angles at 15000km')
    axs[0].set_xlabel('Beta')
    axs[0].set_ylabel('Shadow Arc')
    plot21 = axs[0].plot(betas, sharc)
   
    axs[1].set_title('Kleuver Weights at 15000km')
    axs[1].set_xlabel('Beta')
    axs[1].set_ylabel('Weights')
    plot61 = axs[1].plot(betas, weights)
    
    plt.tight_layout()
    plt.show()
    plt.close()
    
        

 
