import os
import os.path
import pandas as pd
import numpy as np
import pickle
import astropy.units as u
import sqlalchemy as sqla
import sqlalchemy.dialects.postgresql as pg

import nexoclom.math as mathMB
from nexoclom.solarsystem import planet_dist
from nexoclom.atomicdata import RadPresConst
from nexoclom.modelcode.satellite_initial_positions import satellite_initial_positions
from nexoclom.modelcode.LossInfo import LossInfo
from nexoclom.modelcode.rk5 import rk5
from nexoclom.modelcode.bouncepackets import bouncepackets
from nexoclom.modelcode.source_distribution import (surface_distribution,
                                                    speed_distribution,
                                                    angular_distribution)
from nexoclom.modelcode.SurfaceInteraction import SurfaceInteraction


class Output:
    def __init__(self, inputs, npackets, compress=True, logger=None):
        """Determine and store packet trajectories.
        
        **Parameters**
        
        inputs
            An Input object with the run parameters.
            
        npackets
            Number of packets to run.
        
        compress
            Remove packets with frac=0 from the outputs to reduce file size.
            Default = True
            
        **Class Attributes**
        
        x0, y0, z0
        
        f0
        
        vx0, vy0, vz0
        
        phi0, lat0, lon0
        
        time, x, y, z, vx, vy, vz
        Index, npackets, totalsource
        
        inputs
            The inputs used for the simulation
            
        logfile
            Path to file with output log
            
        compress
            Whether output is compressed.
        
        unit
            Basic length unit used. Equal to radius of central planet.
        
        GM
            GM_planet in units of R_planet/s**2
            
        aplanet
            Distance of planet from the Sun in AU
         
        vrplanet
            Radial velocity of planet relative to the Sun in R_planet/s
        
        radpres
            Radiation pressure object containing acceleration as funtion
            of velocity in units of R_planet/s**2 and R_planet/s
        """
        # if logger is None:
        #     logger = logging.getLogger()
        #     logger.setLevel(logging.INFO)
        #     out_handler = logging.StreamHandler(sys.stdout)
        #     logger.addHandler(out_handler)
        #     fmt = logging.Formatter('%(levelname)s: %(msg)s')
        #     out_handler.setFormatter(fmt)
        # else:
        #     pass
        # self.logger = logger

        self.inputs = inputs
        self.planet = inputs.geometry.planet
        
        # initialize the random generator
        self.randgen = np.random.default_rng()
        
        # Not implemented yet.
        assert self.inputs.geometry.type != 'geometry with time', (
            'Initialization with time stamp not implemented yet.')

        # Keep track of whether output is compressed
        self.compress = compress

        # Determine spatial unit
        self.unit = u.def_unit('R_' + self.planet.object, self.planet.radius)

        # Change unit for GM
        self.GM = self.planet.GM.to(self.unit**3/u.s**2).value

        # Determine distance and radial velocity of planet relative to the Sun
        r, v_r = planet_dist(self.planet, self.inputs.geometry.taa)
        self.aplanet = r.value
        self.vrplanet = v_r.to(self.unit/u.s).value

        # Find the default reactions and datasets
        if inputs.options.lifetime.value <= 0:
            self.loss_info = LossInfo(inputs.options.species,
                                      inputs.options.lifetime,
                                      self.aplanet)
        else:
            self.loss_info = None

        # Set up the radiation pressure
        if inputs.forces.radpres:
            radpres = RadPresConst(inputs.options.species,
                                   self.aplanet)
            radpres.velocity = radpres.velocity.to(self.unit/u.s).value
            radpres.accel = radpres.accel.to(self.unit/u.s**2).value
            self.radpres = radpres
        else:
            self.radpres = None

        # set up surface accommodation + maybe other things if needed
        if (('stickcoef' not in inputs.surfaceinteraction.__dict__) or
            (inputs.surfaceinteraction.stickcoef != 1)):
            self.surfaceint = SurfaceInteraction(inputs, nt=201, nv=101, nprob=101)

        # Define the time that packets will run
        if inputs.options.step_size > 0:
            time = np.ones(npackets) * inputs.options.endtime
        else:
            time = self.randgen.random(npackets) * inputs.options.endtime

        self.X0 = pd.DataFrame()
        self.X0['time'] = time.value

        # Define the fractional content
        self.X0['frac'] = np.ones(npackets)

        self.npackets = npackets
        self.totalsource = self.X0['frac'].sum()

        # Determine initial satellite positions if necessary
        if self.planet.moons is not None:
            assert False, 'Not set up'
            sat_init_pos = satellite_initial_positions(inputs)
        else:
            pass

        # Determine starting location for each packet
        if self.inputs.spatialdist.type in ('uniform', 'surface map',
                                            'surface spot'):
            surface_distribution(self)
        else:
            assert 0, 'Not a valid spatial distribution type'
        
        # Determine inital speed for each packet
        speed_distribution(self)
        
        # Choose direction for each packet
        angular_distribution(self)

        # Rotate everything to proper position for running the model
        if (self.inputs.geometry.planet.object !=
            self.inputs.geometry.startpoint):
            assert 0, 'Not set up yet'
        else:
            pass
        
        # Reorder the dataframe columns
        cols = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac', 'v',
                'longitude', 'latitude', 'local_time']
        self.X0 = self.X0[cols]
        
        # Integrate the packets forward
        if self.inputs.options.step_size == 0:
            print('Running variable step size integrator.')
            self.X = self.X0.drop(['longitude', 'latitude', 'localtime'], axis=1)
            self.X['lossfrac'] = np.zeros(npackets)
            self.variable_step_size_driver()
        else:
            print('Running constant step size integrator.')
            self.constant_step_size_driver()
            
        self.save()

    def __str__(self):
        print('Contents of output:')
        print('\tPlanet = {}'.format(self.planet.object))
        print('\ta_planet = {}'.format(self.aplanet))
        print('\tvr_planet = {}'.format(self.vrplanet))
        print('\tNumber of Packets: {}'.format(self.npackets))
#        print('\tUnits of time: {}'.format(self.time.unit))
#        print('\tUnits of distance: {}'.format(self.X0.unit))
#        print('\tUnits of velocity: {}'.format(self.V0.unit))
        return ''

    def __len__(self):
        return self.npackets

    def __getitem__(self, keys):
        self.X = self.X.iloc[keys]

    def variable_step_size_driver(self):
        # Set up the step sizes
        count = 0  # Number of steps taken

        # These control how quickly the stepsize is increased or decreased
        # between iterations
        safety = 0.95
        shrink = -0.25
        grow = -0.2

        # yscale = scaling parameter for each variable
        #     x,y,z ~ R_plan
        #     vx, vy, vz ~ 1 km/s (1/R_plan R_plan/s)
        #     frac ~ exp(-t/lifetime) ~ mean(frac)
        rest = self.inputs.options.resolution
        resx = self.inputs.options.resolution
        resv = 0.1*self.inputs.options.resolution
        resf = self.inputs.options.resolution

        #########################################################
        # Keep taking RK steps until every packet has reached the
        # time of "image taken"
        #########################################################

        # initial step size
        step_size = np.zeros(self.npackets) + 1000.
        cols = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac']
        moretogo = (self.X['time'] > rest) & (self.X['frac'] > 0.)
        while moretogo.any():
            # Save old values
            # This is used for determining if anything hits the rings
            Xtodo = self.X[cols][moretogo].values
            step = step_size[moretogo]
            Xold = Xtodo.copy()
            
            if np.any(step < 0):
                # self.logger.error('Negative values of h '
                #                   'in variable_step_size_dirver')
                print('Negative values of h '
                      'in variable_step_size_dirver')
                assert 0, '\n\tNegative values of step_size'
            else:
                pass

            # Adjust stepsize to be no more than time remaining
            step = np.minimum(Xtodo[:,0], step)

            # Run the rk5 step
            Xnext, delta = rk5(self, Xtodo, step)

            # Do the error check
            # scale = a_tol + |y|*r_tol
            #   for x: a_tol = r_tol = resolution
            #   for v: a_tol = r_tol = resolution/10.-require v more precise
            #   for f: a_tol = 0.01, r_tol = 0 -> frac tol = 1%
            scalex = resx + np.abs(Xnext[:,1:4])*resx
            scalev = resv + np.abs(Xnext[:,4:7])*resv
            scalef = resf + np.abs(Xnext[:,7])*resf

            # Difference relative to acceptable difference
            delta[:,1:4] /= scalex
            delta[:,4:7] /= scalev
            delta[:,7] /= scalef

            # Maximum error for each packet
            errmax = delta.max(axis=1)

            # error check
            assert np.all(np.isfinite(errmax)), '\n\tInfinite values of emax'

            # Make sure no negative frac
            assert not np.any((Xnext[:,7] < 0) & (errmax < 1)),(
                'Found new values of frac that are negative')

            # Make sure frac doesn't increase
            errmax[(Xnext[:,7]-Xtodo[:,7] > scalef) & (errmax > 1)] = 1.1

            # Check where difference is very small. Adjust step size
            noerr = errmax < 1e-7
            errmax[noerr] = 1
            step[noerr] *= 10

            # Put the post-step values in
            g = errmax < 1.0
            b = errmax >= 1.0

            if np.any(g):
                Ximpcheck = Xnext[g,:]
                step_ = safety*step[g]*errmax[g]**grow

                # Impact Check
                tempR = np.linalg.norm(Ximpcheck[:,1:4], axis=1)
                hitplanet = (tempR - 1.) < 0
                if np.any(hitplanet):
                    if ((self.inputs.surfaceinteraction.sticktype == 'constant')
                        and (self.inputs.surfaceinteraction.stickcoef == 1.)):
                        Xnext[hitplanet, 7] = 0.
                    else:
                        bouncepackets(self, Xnext[hitplanet, :],
                                      tempR[hitplanet])
                else:
                    pass

                # Check for escape
                Ximpcheck[tempR > self.inputs.options.outeredge,7] = 0

                # Check for vanishing
                Ximpcheck[Ximpcheck[:,7] < 1e-10, 7] = 0.

                # set remaining time = 0 for packets that are done
                Ximpcheck[Ximpcheck[:,7] == 0, 0] = 0.

                # Put new values into arrays
                #Xnext[g,:] = Ximpcheck
                Xtodo[g] = Ximpcheck
                step[g] = step_
            else: pass

            if np.any(b):
                # Don't adjust the bad value, but do fix the stepsize
                step_ = safety*step[b]*errmax[b]**shrink
                assert np.all(np.isfinite(step_)), (
                    '\n\tInfinite values of step_size')

                # Don't let step size drop below 1/10th previous step size
                step[b] = np.maximum(step_, 0.1*step[b])

            assert np.all(step >= 0), '\n\tNegative values of step_size'

            # Insert back into the original arrays
            self.X.loc[moretogo,cols] = Xtodo
            self.X.loc[moretogo,'lossfrac'] += Xold[:,7] - Xtodo[:,7]
            step_size[moretogo] = step

            # Find which packets still need to run
            moretogo = (self.X['time'] > rest) & (self.X['frac'] > 0.)
            if count % 100 == 0:
                print(f'Step {count}. {np.sum(moretogo)} more to go\n'
                      f'\tstep_size: {mathMB.minmaxmean(step_size)}')
            count += 1

        # Add units back in
        self.aplanet *= u.au
        self.vrplanet *= self.unit/u.s
        self.vrplanet = self.vrplanet.to(u.km/u.s)
        self.GM *= self.unit**3/u.s**2

    def constant_step_size_driver(self):
        # Arrays to store the outputs
        cols = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'frac']

        #  step size and counters
        step_size = np.zeros(self.npackets) + self.inputs.options.step_size
        
        self.nsteps = int(np.ceil(self.inputs.options.endtime.value/step_size[0]
                             + 1))
        results = np.zeros((self.npackets,8,self.nsteps))
        results[:,:,0] = self.X0[cols]
        lossfrac = np.ndarray((self.npackets,self.nsteps))

        curtime = self.inputs.options.endtime.value
        ct = 1
        moretogo = results[:,7,0] > 0
        while (curtime > 0) and (moretogo.any()):
            Xtodo = results[moretogo,:,ct-1]
            step = step_size[moretogo]

            assert np.all(Xtodo[:,7] > 0)
            assert np.all(np.isfinite(Xtodo))

            # Run the rk5 step
            Xnext, _ = rk5(self, Xtodo, step)

            # Check for surface impacts
            tempR = np.linalg.norm(Xnext[:,1:4], axis=1)
            hitplanet = (tempR - 1.) < 0

            if np.any(hitplanet):
                if ((self.inputs.surfaceinteraction.sticktype == 'constant')
                    and (self.inputs.surfaceinteraction.stickcoef == 1.)):
                        Xnext[hitplanet,7] = 0.
                else:
                    bouncepackets(self, Xnext, tempR, hitplanet)
            else:
                pass

            # Check for escape
            Xnext[tempR > self.inputs.options.outeredge,7] = 0
            
            # Check for vanishing
            Xnext[Xnext[:, 7] < 1e-10, 7] = 0.

            # set remaining time = 0 for packets that are done
            Xnext[Xnext[:, 7] == 0, 0] = 0.

            # Put new values back into the original array
            results[moretogo,:,ct] = Xnext
            lossfrac[moretogo,ct] = (lossfrac[moretogo,ct-1] +
                results[moretogo,7,ct-1] - results[moretogo,7,ct])
            
            # Check to see what still needs to be done
            moretogo = results[:,7,ct] > 0

            if (ct % 100) == 0:
                print(ct, curtime, int(np.sum(moretogo)))

            # Update the times
            ct += 1
            curtime -= step_size[0]

        # Put everything back into output
        self.totalsource *= self.nsteps
        X = pd.DataFrame()
        index = np.mgrid[:self.npackets, :self.nsteps]
        npackets = self.npackets * self.nsteps
        X['Index'] = index[0,:,:].reshape(npackets)
        X['time'] = results[:,0,:].reshape(npackets)
        X['x'] = results[:,1,:].reshape(npackets)
        X['y'] = results[:,2,:].reshape(npackets)
        X['z'] = results[:,3,:].reshape(npackets)
        X['vx'] = results[:,4,:].reshape(npackets)
        X['vy'] = results[:,5,:].reshape(npackets)
        X['vz'] = results[:,6,:].reshape(npackets)
        X['frac'] = results[:,7,:].reshape(npackets)
        X['lossfrac'] = lossfrac.reshape(npackets)
        self.X = X

        # Add units back in
        self.aplanet *= u.au
        self.vrplanet *= self.unit/u.s
        self.vrplanet = self.vrplanet.to(u.km/u.s)
        self.GM *= self.unit**3/u.s**2

    def make_filename(self):
        """Determine filename for output."""
        # TAA for observation
        if self.planet.object == 'Mercury':
            taastr = '{:03.0f}'.format(
                      np.round(self.inputs.geometry.taa.to(u.deg).value))
        else:
            assert 0, 'Filename not set up for anything but Mercury'

        # Come up with a path name
        pathname = os.path.join(self.inputs.config.savepath,
                                self.planet.object,
                                self.inputs.options.species,
                                self.inputs.spatialdist.type,
                                self.inputs.speeddist.type,
                                taastr)

        # Make the path if necessary
        if os.path.exists(pathname) is False:
            os.makedirs(pathname)
        numstr = '{:010d}'.format(self.idnum)
        self.filename = os.path.join(pathname, f'{numstr}.pkl')

    def save(self):
        """Add output to database and save as a pickle."""
        geo_id = self.inputs.geometry.insert()
        sint_id = self.inputs.surfaceinteraction.insert()
        for_id = self.inputs.forces.insert()
        spat_id = self.inputs.spatialdist.insert()
        spd_id = self.inputs.speeddist.insert()
        ang_id = self.inputs.angulardist.insert()
        opt_id = self.inputs.options.insert()
        
        engine = self.inputs.config.create_engine()
        metadata_obj = sqla.MetaData()
        table = sqla.Table("outputfile", metadata_obj, autoload_with=engine)
        
        insert_stmt = pg.insert(table).values(
            filename = None,
            npackets = self.npackets,
            totalsource = self.totalsource,
            geo_type = self.inputs.geometry.type,
            geo_id = geo_id,
            sint_type = self.inputs.surfaceinteraction.sticktype,
            sint_id = sint_id,
            force_id = for_id,
            spatdist_type = self.inputs.spatialdist.type,
            spatdist_id = spat_id,
            spddist_type = self.inputs.speeddist.type,
            spddist_id = spd_id,
            angdist_type = self.inputs.angulardist.type,
            angdist_id = ang_id,
            opt_id = opt_id)
        
        with engine.connect() as con:
            result = con.execute(insert_stmt)
            con.commit()
            
        self.idnum = result.inserted_primary_key[0]
        self.make_filename()
        update = sqla.update(table).where(table.columns.idnum == self.idnum).values(
            filename=self.filename)
        with engine.connect() as con:
            con.execute(update)
            con.commit()
            
        # Remove frac = 0
        if self.compress:
            self.X = self.X[self.X.frac > 0]
        else:
            pass
        
        # Convert to 32 bit
        for column in self.X0:
            if self.X0[column].dtype == np.int64:
                self.X0[column] = self.X0[column].astype(np.int32)
            elif self.X0[column].dtype == np.float64:
                self.X0[column] = self.X0[column].astype(np.float32)
            else:
                pass

        for column in self.X:
            if self.X[column].dtype == np.int64:
                self.X[column] = self.X[column].astype(np.int32)
            elif self.X[column].dtype == np.float64:
                self.X[column] = self.X[column].astype(np.float32)
            else:
                pass

        # Save output as a pickle
        print(f'Saving file {self.filename}')
        if self.inputs.surfaceinteraction.sticktype == 'temperature dependent':
            self.surfaceint.stickcoef = 'FUNCTION'
            
        with open(self.filename, 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def restore(cls, filename):
        output = pickle.load(open(filename, 'rb'))
        return output
