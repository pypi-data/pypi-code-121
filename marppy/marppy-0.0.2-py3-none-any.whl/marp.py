# marp.py

import numpy as np
from apexpy import Apex

RE = 6371.
hR = 0.

class Marp(Apex):
    """
    Performs coordinate conversions and base vector calculations.  Inherets
    :class:`apexpy.Apex` class.

    Parameters
    ----------
    date : float, :class:`dt.date`, or :class:`dt.datetime`, optional
        Determines which IGRF coefficients are used in conversions. Uses
        current date as default.  If float, use decimal year.
    refh : float, optional
        Reference height in km for apex coordinates (the field lines are mapped
        to this height)
    datafile : str, optional
        Path to custom coefficient file
    lam0 : float, optional
        Latitude of MARP origin in either Apex or geodetic coordinates
    phi0 : float, optional
        Longitude of MARP origin in either Apex or geodetic coordinates
    alt : float, optional
        Altitude of MARP origin location if it is specified in geodetic
        coordinates (does nothing if origin specified in Apex coordinates)
    coords : str, optional
        Coordinate system MARP origin is specified in

    Attributes
    ----------
    year : float
        Decimal year used for the IGRF model
    refh : float
        Reference height in km for apex coordinates
    datafile : str
        Path to coefficient file
    lam0 : float
        Apex latitude of the MARP origin
    phi0 : float
        Apex longitude of the MARP origin

    Notes
    -----
    The calculations use IGRF-13 with coefficients from 1900 to 2025 [1]_.
    The geodetic reference ellipsoid is WGS84.

    References
    ----------
    .. [1] Thebault, E. et al. (2015), International Geomagnetic Reference
           Field: the 12th generation, Earth, Planets and Space, 67(1), 79,
           :doi:`10.1186/s40623-015-0228-9`.
    """
    def __init__(self, date=None, refh=0, datafile=None, lam0=0., phi0=0., alt=300., coords='apex'):

        super(Marp, self).__init__(date=date, refh=refh, datafile=None)

        if coords == 'geo':
            lam0, phi0 = self.geo2apex(lam0, phi0, alt)

        self.lam0 = lam0
        self.phi0 = phi0


    def apex2marp(self, alat, alon):
        """
        Converts Apex to MARP coordinates.

        Parameters
        ----------
        alat : array_like
            Apex latitude
        alon : array_like
            Apex longitude

        Returns
        -------
        mlat : ndarray or float
            MARP latitude
        mlon : ndarray or float
            MARP longitude
        """

        lam = alat*np.pi/180.
        phi = alon*np.pi/180.
        lam0 = self.lam0*np.pi/180.
        phi0 = self.phi0*np.pi/180.

        xr = np.cos(lam0)*np.cos(lam)*np.cos(phi-phi0) + np.sin(lam0)*np.sin(lam)
        yr = np.cos(lam)*np.sin(phi-phi0)
        zr = -np.sin(lam0)*np.cos(lam)*np.cos(phi-phi0) + np.cos(lam0)*np.sin(lam)

        phir = np.arctan2(yr, xr)
        lamr = np.arcsin(zr)

        mlat = lamr*180./np.pi
        mlon = phir*180./np.pi

        return mlat, mlon

    def marp2apex(self, mlat, mlon):
        """
        Converts MARP to Apex coordinates.

        Parameters
        ----------
        mlat : ndarray or float
            MARP latitude
        mlon : ndarray or float
            MARP longitude

        Returns
        -------
        alat : array_like
            Apex latitude
        alon : array_like
            Apex longitude
        """

        lamr = mlat*np.pi/180.
        phir = mlon*np.pi/180.
        lam0 = self.lam0*np.pi/180.
        phi0 = self.phi0*np.pi/180.

        x = np.cos(phi0)*np.cos(lam0)*np.cos(lamr)*np.cos(phir) - np.cos(phi0)*np.sin(lam0)*np.sin(lamr) - np.sin(phi0)*np.cos(lamr)*np.sin(phir)
        y = np.sin(phi0)*np.cos(lam0)*np.cos(lamr)*np.cos(phir) - np.sin(phi0)*np.sin(lam0)*np.sin(lamr) + np.cos(phi0)*np.cos(lamr)*np.sin(phir)
        z = np.sin(lam0)*np.cos(lamr)*np.cos(phir) + np.cos(lam0)*np.sin(lamr)

        phi = np.arctan2(y, x)
        lam = np.arcsin(z)

        alat = lam*180./np.pi
        alon = phi*180./np.pi

        return alat, alon

    def geo2marp(self, glat, glon, height):
        """
        Converts Geodetic to MARP coordinates.

        Parameters
        ----------
        glat : ndarray or float
            Geodetic latitude
        glon : ndarray or float
            Geodetic longitude
        height : array_like
            Altitude in km

        Returns
        -------
        mlat : ndarray or float
            MARP latitude
        mlon : ndarray or float
            MARP longitude
        """
        alat, alon = self.geo2apex(glat, glon, height)
        mlat, mlon = self.apex2marp(alat, alon)
        return mlat, mlon

    def marp2geo(self, mlat, mlon, height):
        """
        Converts MARP to Geodetic coordinates.

        Parameters
        ----------
        mlat : ndarray or float
            MARP latitude
        mlon : ndarray or float
            MARP longitude
        height : array_like
            Altitude in km

        Returns
        -------
        glat : ndarray or float
            Geodetic latitude
        glon : ndarray or float
            Geodetic longitude
        err : ndarray or float
            Error returned by :class:`apexpy.Apex.apex2geo`
        """
        alat, alon = self.marp2apex(mlat, mlon)
        glat, glon, err = self.apex2geo(alat, alon, height)
        return glat, glon, err

    def basevectors_marp(self, lat, lon, height, coords='geo'):
        """
        Get MARP base vectors d1, d2, d3 and e1, e2, e3 at the specified
        coordinates.

        Parameters
        ----------
        lat : (N,) array_like or float
            Latitude
        lon : (N,) array_like or float
            Longitude
        height : (N,) array_like or float
            Altitude in km
        coords : {'geo', 'apex'}, optional
            Input coordinate system

        Returns
        -------
        d1 : (2, N) or (2,) ndarray
            MARP base vector normal to contours of constant PhiM
        d2 : (2, N) or (2,) ndarray
            MARP base vector that completes the right-handed system
        d3 : (2, N) or (2,) ndarray
            MARP base vector normal to contours of constant lambdaM
        e1 : (2, N) or (2,) ndarray
            MARP base vector tangent to contours of constant V0
        e2 : (2, N) or (2,) ndarray
            MARP base vector that completes the right-handed system
        e3 : (2, N) or (2,) ndarray
            MARP base vector tangent to contours of constant PhiM
        """
        # CHECK ABOVE DEFINITIONS for base vectors
        if coords == 'geo':
            glat = lat
            glon = lon
            alat, alon = self.geo2apex(glat, glon, height)
            mlat, mlon = self.apex2marp(alat, alon)

        if coords == 'apex':
            alat = lat
            alon = lon
            glat, glon, _ = self.apex2geo(alat, alon, height)
            mlat, mlon = self.apex2marp(alat, alon)


        lr = mlat*np.pi/180.
        pr = mlon*np.pi/180.
        l = alat*np.pi/180.
        p = alon*np.pi/180.
        l0 = self.lam0*np.pi/180.
        p0 = self.phi0*np.pi/180.


        f1, f2, f3, g1, g2, g3, d1, d2, d3, e1, e2, e3 = self.basevectors_apex(glat, glon, height)

        sinI = 2*np.sin(l)/np.sqrt(4-3*np.cos(l)**2)


        xr = np.cos(l0)*np.cos(l)*np.cos(p-p0) + np.sin(l0)*np.sin(l)
        yr = np.cos(l)*np.sin(p-p0)
        zr = -np.sin(l0)*np.cos(l)*np.cos(p-p0) + np.cos(l0)*np.sin(l)

        # contravariant derivatives
        dprdp = np.cos(l)*(np.cos(l0)*np.cos(l)+np.sin(l0)*np.sin(l)*np.cos(p-p0))/(xr**2+yr**2)
        dprdl = -np.sin(l0)*np.sin(p-p0)/(xr**2+yr**2)
        dlrdp = np.sin(l0)*np.cos(l)*np.sin(p-p0)/np.sqrt(1-zr**2)
        dlrdl = (np.sin(l0)*np.sin(l)*np.cos(p-p0)+np.cos(l0)*np.cos(l))/np.sqrt(1-zr**2)

        # from contravariant base vectors
        d1r = (d1/np.cos(l)*dprdp - d2/sinI*dprdl)*np.cos(l)/np.sqrt(dprdp*dlrdl-dprdl*dlrdp)
        d2r = -(d1/np.cos(l)*dlrdp - d2/sinI*dlrdl)*sinI/np.sqrt(dprdp*dlrdl-dprdl*dlrdp)
        d3r = d3


        x = np.cos(l)*np.cos(p)
        y = np.cos(l)*np.sin(p)
        z = np.sin(l)

        # covariant derivatives
        dpdpr = np.cos(lr)*(np.cos(l0)*np.cos(lr)-np.sin(l0)*np.sin(lr)*np.cos(pr))/(x**2+y**2)
        dpdlr = np.sin(l0)*np.sin(pr)/(x**2+y**2)
        dldpr = -np.sin(l0)*np.cos(lr)*np.sin(pr)/np.sqrt(1-z**2)
        dldlr = (-np.sin(l0)*np.sin(lr)*np.cos(pr)+np.cos(l0)*np.cos(lr))/np.sqrt(1-z**2)

        # form covariant base vectors
        e1r = (e1*np.cos(l)*dpdpr - e2*sinI*dldpr)/np.cos(l)/np.sqrt(dpdpr*dldlr-dldpr*dpdlr)
        e2r = -(e1*np.cos(l)*dpdlr - e2*sinI*dldlr)/sinI/np.sqrt(dpdpr*dldlr-dldpr*dpdlr)
        e3r = e3

        return d1r, d2r, d3r, e1r, e2r, e3r
