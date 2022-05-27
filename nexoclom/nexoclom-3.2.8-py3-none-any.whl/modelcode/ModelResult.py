import os.path
import sys
import numpy as np
import copy
import shutil
import astropy.units as u
import pandas as pd
import pickle
from sklearn.neighbors import BallTree
import time
import tempfile
from nexoclom import math as mathMB
from nexoclom.atomicdata import gValue
from nexoclom.modelcode.input_classes import InputError
from nexoclom.modelcode.Output import Output
from nexoclom.modelcode.SourceMap import SourceMap
import nexoclom.__file__ as basefile
try:
    import condorMB
except:
    pass


class ModelResult:
    """Base class for nexoclom model comparisons with data.

    The ModelResult object is the base class for ModelImage (radiance and column
    density images), LOSResult (radiance or column along lines of sight), and
    ModelDensity (density along a trajectory or plane - not written yet).
    
    **Parameters**
    
    inputs
        An Input object
        
    params
        A dictionary containing parameters needed to create the model result.
        See LOSResult.py or ModelImage.py for details.
    
    **Methods**
    
    packet_weighting
        Determine the weighting factor each packet. When determining density
        or column, no weighting is needed. For radiance, takes into account
        determines g-value and takes into account shadowing.
        
    transform_reference_frame
        Will be used to transform packets from the central object reference frame
        to another location
        
    **Attributes**
    
    inputs
        Input object with the parameters associated with the model result
        
    params
        A dictionary containing parameters of the result. See LOSResult.py
        or ModelImage.py for details.
        
    outputfiles
        locations of saved Outputs associated with the inputs
    
    npackets
        total number of packets simulated
    
    totalsource
        total source in packets (if the initial fraction are all 1, then
        totalsource = npackets * nsteps
        
    quantity
        column, density, or radiance determined from params
        
    mechanism
        Emission mechanism if quantity = radiance else None
        
    wavelength
        Emssion wavelengths if quantity = radiance else None
      
    """
    def __init__(self, inputs, params):
        """
        :param inputs: Input object
        :param params: Dictionary with ModelResult parameters
        """
        self.inputs = copy.deepcopy(inputs)
        self.outid, self.outputfiles, _, _ = self.inputs.search()
        self.npackets = 0
        self.totalsource = 0.
        self.atoms_per_packet = 0.
        self.sourcerate = 0. * u.def_unit('10**23 atoms/s', 1e23 / u.s)
        if isinstance(params, str):
            if os.path.exists(params):
                self.params = {}
                with open(params, 'r') as f:
                    for line in f:
                        if ';' in line:
                            line = line[:line.find(';')]
                        elif '#' in line:
                            line = line[:line.find('#')]
                        else:
                            pass
                        
                        if '=' in line:
                            p, v = line.split('=')
                            self.params[p.strip().lower()] = v.strip()
                        else:
                            pass
            else:
                raise FileNotFoundError('ModelResult.__init__',
                                        'params file not found.')
        elif isinstance(params, dict):
            self.params = params
        else:
            raise TypeError('ModelResult.__init__',
                            'params must be a dict or filename.')
            
        # Do some validation
        quantities = ['column', 'radiance', 'density']
        self.quantity = self.params.get('quantity', None)
        if (self.quantity is None) or (self.quantity not in quantities):
            raise InputError('ModelImage.__init__',
                             "quantity must be 'column' or 'radiance'")
        else:
            pass

        if self.quantity == 'radiance':
            # Note - only resonant scattering currently possible
            self.mechanism = ['resonant scattering']
    
            if 'wavelength' in self.params:
                self.wavelength = tuple(sorted(int(m.strip())*u.AA for m
                    in self.params['wavelength'].split(',')))
            elif self.inputs.options.species is None:
                raise InputError('ModelImage.__init__',
                                 'Must provide either species or params.wavelength')
            elif self.inputs.options.species == 'Na':
                self.wavelength = (5891*u.AA, 5897*u.AA)
            elif self.inputs.options.species == 'Ca':
                self.wavelength = (4227*u.AA,)
            elif self.inputs.options.species == 'Mg':
                self.wavelength = (2852*u.AA,)
            else:
                raise InputError('ModelResult.__init__', ('Default wavelengths '
                                 f'not available for {self.inputs.options.species}'))
        else:
            self.mechanism = None
            self.wavelength = None
            
        self.unit = u.def_unit('R_' + self.inputs.geometry.planet.object,
                               self.inputs.geometry.planet.radius)
        
    def packet_weighting(self, packets, out_of_shadow, aplanet):
        """
        Determine weighting factor for each packet
        :param packets: DataFrame with packet parameters
        :param out_of_shadow: Boolean array, True if in sunlight; False if in shadow
        :param aplanet: Distance of planet from Sun (used for g-value calculation)
        :return: Adds a 'weight' column to the packets DataFrame
        """
        if self.quantity == 'column':
            packets['weight'] = packets['frac']
        elif self.quantity == 'density':
            packets['weight'] = packets['frac']
        elif self.quantity == 'radiance':
            if 'resonant scattering' in self.mechanism:
                gg = np.zeros(len(packets))/u.s
                for w in self.wavelength:
                    gval = gValue(self.inputs.options.species, w, aplanet)
                    gg += mathMB.interpu(packets['radvel_sun'].values *
                                         self.unit/u.s, gval.velocity, gval.g)

                weight_resscat = packets['frac']*out_of_shadow*gg.value/1e6
            else:
                weight_resscat = np.zeros(len(packets))
                
            packets['weight'] = weight_resscat  # + other stuff
        else:
            raise InputError('ModelResults.packet_weighting',
                             f'{self.quantity} is invalid.')

        assert np.all(np.isfinite(packets['weight'])), 'Non-finite weights'

    def make_source_map(self, smear_radius=10*np.pi/180, nlonbins=180,
                        nlatbins=90, nvelbins=100, nazbins=90, naltbins=23,
                        use_condor=False, normalize=True):
        """
        At each point in lon/lat grid want:
            * Source flux (atoms/cm2/s
            * Speed distribution (f_v vs v)
            * Azimuthal distribution (f_az vs az) -> measured CCW from north
            * Altitude distribution (f_alt vs alt) -> tangent = 0, normal = 90
        """
        params = {'smear_radius': smear_radius,
                  'nlonbins': nlonbins,
                  'nlatbins': nlatbins,
                  'nvelbins': nvelbins,
                  'nazbins': nazbins,
                  'naltbins': naltbins,
                  'use_condor': use_condor,
                  'normalize': normalize}

        X0 = None
        for outputfile in self.outputfiles:
            output = Output.restore(outputfile)
            if X0 is None:
                X0 = output.X0[['x', 'y', 'z', 'vx', 'vy', 'vz', 'frac']]
            else:
                X0 = pd.concat([X0, output.X0[['x', 'y', 'z', 'vx', 'vy', 'vz',
                                               'frac']]], ignore_index=True)
            del output
            
        velocity = (X0[['vx', 'vy', 'vz']].values *
                    self.inputs.geometry.planet.radius.value)
        speed = np.linalg.norm(velocity, axis=1)

        # Radial, east, north unit vectors
        rad = X0[['x', 'y', 'z']].values
        rad_ = np.linalg.norm(rad, axis=1)
        rad = rad/rad_[:, np.newaxis]

        east = X0[['y', 'x', 'z']].values
        east[:,1] = -1*east[:,1]
        east[:,2] = 0
        east_ = np.linalg.norm(east, axis=1)
        east = east/east_[:, np.newaxis]

        # north = np.array([-X0.z.values * X0.x.values,
        #                   -X0.z.values * X0.y.values,
        #                   X0.x.values**2 + X0.y.values**2])
        north = np.cross(rad, east, axis=1)
        north_ = np.linalg.norm(north, axis=1)
        north = north/north_[:, np.newaxis]

        v_rad = np.sum(velocity * rad, axis=1)
        v_east = np.sum(velocity * east, axis=1)
        v_north = np.sum(velocity * north, axis=1)

        v_rad_over_speed = v_rad/speed
        v_rad_over_speed[v_rad_over_speed > 1] = 1
        v_rad_over_speed[v_rad_over_speed < -1] = -1

        assert np.all(np.isclose(v_rad**2 + v_east**2 + v_north**2, speed**2))
        X0['altitude'] = np.arcsin(v_rad_over_speed)
        X0['azimuth'] = (np.arctan2(v_north, v_east) + 2*np.pi) % (2*np.pi)
        X0['v_rad'] = v_rad
        X0['v_east'] = v_east
        X0['v_north'] = v_north
        X0['speed'] = speed
        X0['longitude'] = (np.arctan2(X0.x.values, -X0.y.values) + 2*np.pi) % (2*np.pi)
        X0['latitude'] = np.arcsin(X0.z.values)

        source = self._calculate_histograms(X0, params, weight=True)

        if  self.__dict__.get('fitted', False):
            available = self._calculate_histograms(X0, params, weight=False)
        
            # Compute the abundance scaling factors based on phase space filling factor
            source.fraction_observed = self._phase_space_filling_factor(
                X0, source, params, weight=True)
            available.fraction_observed = self._phase_space_filling_factor(
                X0, available, params, weight=False)
        else:
            available, scalefactor_fit, scalefactor_avail = None, None, None

        return source, available, X0

    def _phase_space_filling_factor(self, X0, source, params, weight):
        if weight:
            X0['weight'] = X0.frac
        else:
            X0['weight'] = np.ones_like(X0.frac.values)
    
        # Figure out the v, alt, and az axis
        # Speed isn't used right now, but probably want to account for filling factor
        speed, azimuth, altitude = source.speed, source.azimuth, source.altitude
    
        gridazimuth, gridaltitude = np.meshgrid(azimuth, altitude)
        gridazimuth, gridaltitude = gridazimuth.T, gridaltitude.T
        lowalt = altitude < 85*u.deg
    
        # Area of each bin
        dalt, daz = altitude[1]-altitude[0], azimuth[1]-azimuth[0]
        dOmega = dalt * daz * np.cos(gridaltitude)
    
        tree = BallTree(X0[['latitude', 'longitude']], metric='haversine')
        gridlatitude, gridlongitude = np.meshgrid(source.latitude,
                                                  source.longitude)
    
        points = np.array([gridlatitude.flatten(), gridlongitude.flatten()]).T
        ind = tree.query_radius(points, params['smear_radius'])
        fraction_observed = np.ndarray((points.shape[0], ))
    
        if params['use_condor']:
            # cmd = '/bin/bash'
            # script = ('/Users/mburger/Work/Research/Mercury/model_fitting/'
            #           'calculation_step.sh')
            #
            # tempdir = '/Users/mburger/Work/Research/Mercury/model_fitting/temp/'
            
            env = [piece for piece in sys.executable.split('/') if 'nexoclom' in piece][0]
            python = f'/user/mburger/anaconda3/envs/{env}/bin/python'
            pyfile = os.path.join(os.path.dirname(basefile), 'modelcode',
                                  'calculation_step.py')
            tempdir = tempfile.mkdtemp()
        
            # Save the data
            # Break it down into pieces
            ct, nper = 0, points.shape[0]//condorMB.nCPUs() + 1
            datafiles = []
            while ct < points.shape[0]:
                inds = ind[ct:min(ct+nper, points.shape[0])]
                inds_ = []
                for idx in inds:
                    inds_.extend(idx)
                inds_ = list(set(inds_))
                sub = X0.loc[inds_]
            
                datafile = os.path.join(tempdir, f'data_{ct}.pkl')
                with open(datafile, 'wb') as file:
                    pickle.dump((sub, inds, params, lowalt, dOmega), file)
                datafiles.append(datafile)
                print(datafile)
            
                # submit to condor
                logfile = os.path.join(tempdir, f'{ct}.log')
                outfile = os.path.join(tempdir, f'{ct}.out')
                errfile = os.path.join(tempdir, f'{ct}.err')
            
                condorMB.submit_to_condor(python,
                                 delay=1,
                                 arguments=f'{pyfile} {datafile}',
                                 logfile=logfile,
                                 outlogfile=outfile,
                                 errlogfile=errfile,
                                 njobs=30)
                ct += nper
        else:
            for index in range(points.shape[0]):
                sub = X0.iloc[ind[index]]
            
                # Speed, az/alt phase space distribution in cell
                speed = mathMB.Histogram(sub.speed, bins=params['nvelbins'],
                                         weights=sub.weight,
                                         range=[0, sub.speed.max()])
            
                angdist = mathMB.Histogram2d(sub.azimuth, sub.altitude,
                                             weights=sub.weight,
                                             bins=(params['nazbins'],
                                                   params['naltbins']),
                                             range=[[0, 2*np.pi], [0, np.pi/2]])
            
                # Convolve with gaussian to smooth things out
                ang = mathMB.smooth2d(angdist.histogram, 3, wrap=True)
            
                az_max = np.zeros((2, params['nazbins']))
                alt_max = np.zeros((2, params['naltbins']))
                for i in range(params['nazbins']):
                    row = mathMB.smooth(ang[i,:], 7, wrap=True)
                    az_max[:,i] = [np.where(row == row.max())[0].mean(), row.max()]
                for i in range(params['naltbins']):
                    row = mathMB.smooth(ang[:,i], 7, wrap=True)
                    alt_max[:,i] = [np.where(row == row.max())[0][0], row.max()]
            
                # Ignore high altitudes (bad statistics)
                top = np.mean([az_max[1,:].max(), alt_max[1, lowalt].max()])
                ang /= top
                integral = np.sum(ang * dOmega)
                fraction_observed[index] = integral.value/(2*np.pi)
            
                if index % 500 == 0:
                    print(f'weight = {weight}: {index+1}/{points.shape[0]} completed')
    
        if params['use_condor']:
            while condorMB.n_condor_jobs() > 0:
                print(f'{condorMB.n_condor_jobs()} to go.')
                time.sleep(10)
        
            for datafile in datafiles:
                fracfile = datafile.replace('data', 'fraction')
                with open(fracfile, 'rb') as file:
                    fraction = pickle.load(file)
                ct = int(datafile[5:7])
                fraction_observed[ct:ct+len(fraction)] = fraction
                
            shutil.rmtree(tempdir)
    
        fraction_observed = fraction_observed.reshape(gridlongitude.shape)
    
        return fraction_observed
    
    def _calculate_histograms(self, X0, params, weight=True):
        if weight:
            w = X0.frac.values
        else:
            w = np.ones_like(X0.frac.values)
    
        # Determine source distribution
        if (params['nlonbins'] > 0) and (params['nlatbins'] > 0):
            source = mathMB.Histogram2d(X0.longitude, X0.latitude, weights=w,
                                        range=[[0, 2*np.pi], [-np.pi/2, np.pi/2]],
                                        bins=(params['nlonbins'], params['nlatbins']))
            source.x, source.dx = source.x * u.rad, source.dx * u.rad
            source.y, source.dy = source.y * u.rad, source.dy * u.rad
        
            if params['normalize']:
                # Convert histogram to flux
                # (a) divide by area of a grid cell
                #   Surface area of a grid cell =
                #       R**2 (lambda_2 - lambda_1) (sin(phi2)-sin(phi1))
                #   https://onlinelibrary.wiley.com/doi/epdf/10.1111/tgis.12636, eqn 1
                # (b) Multiply by source rate
                _, gridlatitude = np.meshgrid(source.x, source.y)
                area = (self.inputs.geometry.planet.radius**2 * source.dx.value *
                        (np.sin(gridlatitude + source.dy / 2) -
                         np.sin(gridlatitude - source.dy / 2)))
            
                source.histogram = (source.histogram / X0.frac.sum() /
                                    area.T.to(u.cm**2) * self.sourcerate.to(1 / u.s))
            else:
                pass
        else:
            source = None
        
        # Velocity flux atoms/s/(km/s)
        if params['nvelbins'] > 0:
            velocity = mathMB.Histogram(X0.speed, bins=params['nvelbins'],
                                        range=[0, X0.speed.max()], weights=w)
            velocity.x = velocity.x * u.km / u.s
            velocity.dx = velocity.dx * u.km / u.s
            if params['normalize']:
                velocity.histogram = (self.sourcerate * velocity.histogram /
                                      velocity.histogram.sum() / velocity.dx)
                velocity.histogram = velocity.histogram.to(self.sourcerate.unit *
                    u.def_unit('(km/s)^-1', u.s/u.km))
            else:
                pass
        else:
            velocity = None
    
        # Altitude distribution
        if params['naltbins'] > 0:
            altitude = mathMB.Histogram(X0.altitude, bins=params['naltbins'],
                                        range=[0, np.pi / 2], weights=w)
            altitude.x = altitude.x * u.rad
            altitude.dx = altitude.dx * u.rad
            if params['normalize']:
                altitude.histogram = (self.sourcerate * altitude.histogram /
                                      altitude.histogram.sum() / altitude.dx)
            else:
                pass
        else:
            altitude = None
    
        # Azimuth distribution
        if params['nazbins'] > 0:
            azimuth = mathMB.Histogram(X0.azimuth, bins=params['nazbins'],
                                       range=[0, 2 * np.pi], weights=w)
            azimuth.x = azimuth.x * u.rad
            azimuth.dx = azimuth.dx * u.rad
            if params['normalize']:
                azimuth.histogram = (self.sourcerate * azimuth.histogram /
                                     azimuth.histogram.sum() / azimuth.dx)
            else:
                pass
        else:
            azimuth = None
    
        source = SourceMap({'abundance': source.histogram,
                            'longitude': source.x,
                            'latitude': source.y,
                            'speed': velocity.x,
                            'speed_dist': velocity.histogram,
                            'altitude': altitude.x,
                            'altitude_dist': altitude.histogram,
                            'azimuth': azimuth.x,
                            'azimuth_dist': azimuth.histogram,
                            'coordinate_system': 'solar-fixed'})
    
        return source
    
    def show_source_map(self, filename, which='source', smooth=False, show=True,
                        source=None, available=None, X0=None):
        if X0 is None:
            source, available, X0 = self.make_source_map()
        elif (which == 'source') and (source is None):
            touse, _, X0 = self.make_source_map()
        elif which == 'source':
            touse = source
        elif (which == 'available') and (available is None):
            _, touse, X0 = self.make_source_map()
        elif which == 'available':
            touse = available
        else:
            raise InputError
    
    # def transform_reference_frame(self, output):
    #     """If the image center is not the planet, transform to a
    #        moon-centric reference frame."""
    #     assert 0, 'Not ready yet.'
    #
    #     # Load output
    #
    #     # # Transform to moon-centric frame if necessary
    #     # if result.origin != result.inputs.geometry.planet:
    #     #     assert 0, 'Need to do transparamsion for a moon.'
    #     # else:
    #     #     origin = np.array([0., 0., 0.])*output.x.unit
    #     #     sc = 1.
    #
    #     # Choose which packets to use
    #     # touse = output.frac >= 0 if keepall else output.frac > 0
    #
    #     # packet positions relative to origin -- not rotated
    #     # pts_sun = np.array((output.x[touse]-origin[0],
    #     #                     output.y[touse]-origin[1],
    #     #                     output.z[touse]-origin[2]))*output.x.unit
    #     #
    #     # # Velocities relative to sun
    #     # vels_sun = np.array((output.vx[touse],
    #     #                      output.vy[touse],
    #     #                      output.vz[touse]))*output.vx.unit
    #
    #     # Fractional content
    #     # frac = output.frac[touse]
    #
    #     return output #, pts_sun, vels_sun, frac
