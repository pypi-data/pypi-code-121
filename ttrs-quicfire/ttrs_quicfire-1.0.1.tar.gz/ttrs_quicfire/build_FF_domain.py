# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 11:37:57 2022

@author: zcope
"""
import os
import numpy as np
import inspect
import ttrs_quicfire.quic_fire as qf

class AlbersEqualAreaConic: # Used exclusively to convert Albers  to Lat/Long (Forward) and the Inverse
    

    """
    Implements forward and inverse projection on Albers Equal Area Conic
    Attributes:
        lambda_0 (float): origin of longitude
        a (float): semi-major axis of earth (GRS80)
        e2 (float): eccentricity squared
        e (float): eccentricity
        n (float): stored map constant
        C (float): stored map constant
        rho_0 (float): stored map constant
    """

    def __init__(self, phi_1=29.5, phi_2=45.5, phi_0=23.0, lambda_0=-96.0):
        """
        Creates an instance of AlbersEqualAreaConic, initializes attributes and
        computes map constants
        Note:
            Geographic constants are based on the GRS 1980 ellipsoid
        Args:
            phi_1 (float): first standard parallel
            phi_2 (float): second standard parallel
            phi_0 (float): origin of latitude
            lambda_0 (float): origin of longitude
        """

        # convert map params to radians
        phi_0 = np.radians(phi_0)
        phi_1 = np.radians(phi_1)
        phi_2 = np.radians(phi_2)
        self.lambda_0 = np.radians(lambda_0)

        # GRS 1980 REFERENCE ELLIPSIOD CONSTANTS
        # geographic constants
        self.a = 6378137.0
        # derived geometrical constants
        f = 1.0/298.2572221010042 # flattening
        self.e2 = 2*f - f**2 # eccentricity squared
        self.e = np.sqrt(self.e2) # eccentricity

        # preliminaries
        m_1 = self._m(phi_1)
        m_2 = self._m(phi_2)
        q_0 = self._q(phi_0)
        q_1 = self._q(phi_1)
        q_2 = self._q(phi_2)

        # map constants
        self.n = (m_1**2 - m_2**2)/(q_2 - q_1)
        self.C = m_1**2 + self.n*q_1
        self.rho_0 = self.a*(self.C - self.n*q_0)**0.5/self.n

    def _m(self, phi):
        """Private member
        Convenience method for computing map constants
        """

        return np.cos(phi)/np.sqrt(1 - self.e2*(np.sin(phi))**2)

    def _q(self, phi):
        """Private member
        Another convenience method for computing map constants
        """

        return (1 - self.e2)*(np.sin(phi)/(1 - self.e2*(
            np.sin(phi))**2) - (1.0/(2*self.e))*np.log((1-self.e*np.sin(
            phi))/(1 + self.e*np.sin(phi))))

    def forward(self, lat, lon):
        """
        Performs forward projection from geodetic coordinates to projected
        coordinates
        Args:
            lat (float): latitude
            lon (float): longitude
        Returns:
            (x,y) coordinate projected in Albers Equal Area Conic
        """

        # convert to radians for numpy trig functions
        lat = np.radians(lat)
        lon = np.radians(lon)

        # preliminaries
        q = self._q(lat)
        rho = self.a*(self.C - self.n*q)**0.5/self.n
        theta = self.n*(lon - self.lambda_0)

        # retrieve the projected coordinates
        x = rho*np.sin(theta)
        y = self.rho_0 - rho*np.cos(theta)

        return x,y

    def inverse(self, x, y):
        """
        Performs inverse projection from Albers to geodetic coordinates
        Args:
            x (float): x projected in Albers
            y (float): y projected in Albers
        Returns:
            lat and lon in geodetic coordinates
        """

        # preliminaries
        p = np.sqrt(x*x + (self.rho_0 - y)**2)
        theta = np.arctan2(x, self.rho_0 - y)
        q = (self.C - ((p*p)*(self.n**2))/(self.a**2))/self.n

        # convergence criteria
        epsilon = 1e-6

        # iterate latitude calculation until convergence
        phi = np.sin(q/2)
        next_phi = self._inverse_iteration(phi, q)
        while (np.abs(np.degrees(phi) - np.degrees(next_phi)) > epsilon):
            phi = next_phi
            next_phi = self._inverse_iteration(phi, q)

        return np.degrees(phi), np.degrees(self.lambda_0 + theta/self.n)

    def _inverse_iteration(self, phi, q):
        """Private member
        Formula to iterator until convergence for inverse projection of latitude
        """

        return np.radians(np.degrees(phi) + np.degrees((1 -
            self.e2*(np.sin(phi)**2)**2)/(2*np.cos(phi))*(
            (q/(1-self.e2)) - (np.sin(phi)/(1-self.e2*(np.sin(phi)**2))) +
            (1/(2*self.e))*np.log((1 - self.e*np.sin(phi))/(1 +
            self.e*np.sin(phi))))))

def fastfuels_access(domain_params,out_dir): # NEEDS CLEANING UP # DRG, THIS CAN BE ADDED TO THE DOM CLASS ZACH PRODUCED
    import fastfuels as ff
    x_center,y_center,x_ext,y_ext =  domain_params
    albers = AlbersEqualAreaConic()
    fio = ff.open('https://wifire-data.sdsc.edu:9000/fastfuels/index.fio', ftype='s3')
    fio.cache_limit = 1e16
    
    lat, long = albers.inverse(x_center,y_center)
    roi = fio.query(long, lat,xlen=x_ext,ylen=y_ext)
    roi.write(out_dir+'/',res_xyz=[2,2,1])     
    del roi
    
def build_ff_domain(dom, out_dir, FF_request):
    domain_params = [dom.x_center, dom.y_center, dom.X_length, dom.Y_length]  
    # if out_dir=='default':
    #     #main_loc should contain file path of main.py script calling this one
    #     main_loc = os.path.split(inspect.stack()[1][1])[0] #https://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing
    #     out_dir = os.path.join(main_loc, 'FF_Fuel')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    if FF_request:
        fastfuels_access(domain_params, out_dir)
    
    return qf.QF_Fuel_Arrays(dom, out_dir)
    