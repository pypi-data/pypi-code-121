"""Classes used by the Inputs class"""
import os
import numpy as np
import pickle
from astropy.time import Time
import astropy.units as u
from sqlalchemy import text
from nexoclom.solarsystem import SSObject
from nexoclom.utilities import InputError, NexoclomConfig


dtor = np.pi/180.
# Tolerances for floating point values
dtaa = 2.*dtor


class InputClass:
    def __init__(self):
        self.type = None
        self.config = NexoclomConfig()
    
    def __repr__(self):
        result = ''
        for key,value in self.__dict__.items():
            result += f'geometry.{key} = {value}\n'
        return result.strip()
    
    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            pass
    
        keys_self, keys_other = set(self.__dict__.keys()), set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            return all([self.__dict__[key] == other.__dict__[key] for key in keys_self])
        
    def make_query(self):
        fields = ', '.join(self.__dict__.keys())
        values = '%' + ', %'.join(self.__dict__.keys())
        return fields, values

    def insert(self):
        fields, values = self.make_query()
        query = text(f'''INSERT INTO {self.type} ({fields})
                         VALUES ({values});''')
        with self.config.create_engine().begin as con:
            con.execute(query, self.__dict__)
            
        ids = self.search()
        return ids
    
    def search(self):
        fields, values = self.make_query()
        query = text(f'''SELECT idnum FROM {self.type}
                         WHERE {fields}''')
        with self.config.create_engine().connect() as con:
            result = con.execute(query, self.__dict__)
            ids = [row.idnum for row in result]
        return ids
        

class Geometry(InputClass):
    def __init__(self, gparam):
        """Define a Geometry object.
        
        See :doc:`inputfiles#Geometry` for more information.
        """
        # Planet
        super().__init__()
        
        planet = gparam.get('planet', None)
        if planet is None:
            raise InputError('Geometry.__init__',
                             'Planet not defined in inputfile.')
        else:
            self.planet = SSObject(planet.title())

        # All possible objects
        objlist = [self.planet.object]
        if self.planet.moons is not None:
            objlist.extend([m.object for m in self.planet.moons])
        else:
            pass

        # Choose the starting point
        self.startpoint = gparam.get('startpoint', self.planet.object).title()
        if self.startpoint not in objlist:
            print(f'{self.startpoint} is not a valid starting point.')
            olist = '\n\t'.join(objlist)
            print(f'Valid choices are:\n\t{olist}')
            raise ValueError
        else:
            pass

        # Choose which objects to include
        # This is given as a list of names
        # Default = geometry.planet and geometry.startpoint
        if 'objects' in gparam:
            inc = set(i.strip().title()
                      for i in gparam['objects'].split(','))
        else:
            inc = {self.planet.object, self.startpoint}

        for i in inc:
            if i not in objlist:
                raise InputError('Geometry.__init__',
                                 f'Invalid object {i} in geometry.include')
            
        # Only remember objects that will be included
        self.objects = set(SSObject(o) for o in inc)
        if len(self.objects) == 0:
            # Probably not possible to get here
            self.objects = None
        else:
            pass

        # Different objects are created for geometry_with_starttime and
        # geometry_without_starttime
        if 'starttime' in gparam:
            self.type = 'geometry with starttime'
            try:
                self.time = Time(gparam['starttime'].upper())
            except:
                raise InputError('Geometry.__init__',
                         f'Invalid starttime format: {gparam["starttime"]}')
        else:
            self.type = 'geometry without starttime'
            if len(self.planet) == 1:
                self.phi = None
            elif 'phi' in gparam:
                phi_ = gparam['phi'].split(',')
                phi = tuple(float(p)*u.rad for p in phi_)
                nmoons = len(self.objects - {self.planet})
                if len(phi) == nmoons:
                    self.phi = phi
                else:
                    raise InputError('Geometry.__init__',
                          'The wrong number of orbital positions was given.')
            else:
                raise InputError('Geometry.__init__',
                                 'geometry.phi was not specified.')

            # Subsolar longitude and latitude
            if 'subsolarpoint' in gparam:
                subs = gparam['subsolarpoint'].split(',')
                try:
                    self.subsolarpoint = (float(subs[0])*u.rad,
                                          float(subs[1])*u.rad)
                except:
                    raise InputError('Geometry.__init__',
                         'The format for geometry.subsolarpoint is wrong.')
            else:
                self.subsolarpoint = (0*u.rad, 0*u.rad)

            # True Anomaly Angle
            self.taa = float(gparam.get('taa', 0.))*u.rad
            

class SurfaceInteraction:
    def __init__(self, sparam):
        """Define a SurfaceInteraction object.

        See :doc:`inputfiles#SurfaceInteraction` for more information.
        """
        sticktype = (sparam['sticktype'].lower()
                     if 'sticktype' in sparam
                     else None)
        if sticktype == 'temperature dependent':
            self.sticktype = sticktype
            
            if 'accomfactor' in sparam:
                self.accomfactor = float(sparam['accomfactor'])
            else:
                raise InputError('SurfaceInteraction.__init__',
                                 'surfaceinteraction.accomfactor not given.')
            
            if 'a' in sparam:
                A = tuple([float(a) for a in sparam['a'].split(',')])
                if len(A) == 3:
                    self.A = A
                else:
                    raise InputError('SurfaceInteraction.__init__',
                                     'surfaceinteraction.A must have 3 values')
            else:
                self.A = (1.57014, -0.006262, 0.1614157)
        elif sticktype == 'surface map':
            self.sticktype = sticktype
            self.stick_mapfile = sparam.get('stick_mapfile', 'default')

            if os.path.exists(self.stick_mapfile):
                if self.stick_mapfile.endswith('.pkl'):
                    with open(self.stick_mapfile, 'rb') as f:
                        sourcemap = pickle.load(f)
                    self.coordinate_system = sourcemap.get('coordinate_system',
                                                           'solar-fixed')
                else:
                    self.coordinate_system = 'solar-fixed'
                    # assert 0, 'Not set up yet'
            else:
                print('Warning: mapfile does not exist')
                self.coordinate_system = 'solar-fixed'

            if (self.coordinate_system == 'planet-fixed'):
                self.subsolarlon = sparam.get('subsolarlon', 0.) * u.rad
            else:
                self.subsolarlon = None

            if 'accomfactor' in sparam:
                self.accomfactor = float(sparam['accomfactor'])
            else:
                raise InputError('SurfaceInteraction.__init__',
                                 'surfaceinteraction.accomfactor not given.')
        elif 'stickcoef' in sparam:
            # Constant sticking
            self.sticktype = 'constant'
            self.stickcoef = float(sparam['stickcoef'])
            if self.stickcoef < 0:
                self.stickcoef = 0
            elif self.stickcoef > 1:
                self.stickcoef = 1
            else:
                pass
            
            if 'accomfactor' in sparam:
                self.accomfactor = float(sparam['accomfactor'])
            else:
                if self.stickcoef == 1:
                    self.accomfactor = None
                else:
                    raise InputError('SurfaceInteraction.__init__',
                                 'surfaceinteraction.accomfactor not given.')
        else:
            self.sticktype = 'constant'
            self.stickcoef = 1.
            self.accomfactor = None

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            pass
    
        keys_self, keys_other = set(self.__dict__.keys()), set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            return all([self.__dict__[key] == other.__dict__[key] for key in keys_self])

    def __str__(self):
        result = ''
        for key,value in self.__dict__.items():
            result += f'surfaceinteraction.{key} = {value}\n'
        return result.strip()
    
    def insert(self):
        ids = self.search()
        if ids is None:
            if self.sticktype == 'constant':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO surface_int_constant (
                                       stickcoef, accomfactor) VALUES (
                                       %s, %s)''',
                                (self.stickcoef, self.accomfactor))
            elif self.sticktype == 'surface map':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO surface_int_map (
                                       mapfile, accomfactor) VALUES (
                                       %s, %s)''',
                                (self.stick_mapfile, self.accomfactor))
            elif self.sticktype == 'temperature dependent':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO surface_int_tempdependent (
                                       accomfactor, a) VALUES
                                       (%s, %s::DOUBLE PRECISION[3])''',
                                (self.accomfactor, self.A))
            else:
                raise InputError('SurfaceInteraction.search()',
                    f'surfaceinteraction.sticktype = {self.sticktype} not allowed.')
            ids = self.search()
            assert ids is not None
        else:
            pass

        return ids

    def search(self):
        if self.sticktype == 'constant':
            params = [self.stickcoef]
            if self.accomfactor is None:
                afactor = 'accomfactor is NULL'
            else:
                afactor = 'accomfactor = %s'
                params.append(self.accomfactor)
            
            query = f"""SELECT idnum
                        FROM surface_int_constant
                        WHERE stickcoef = %s and
                              {afactor}"""
        elif self.sticktype == 'temperature dependent':
            params = [self.accomfactor, self.A]
            query = f"""SELECT idnum
                        FROM surface_int_tempdependent
                        WHERE accomfactor = %s and
                              a = %s::DOUBLE PRECISION[3]"""
        elif self.sticktype == 'surface map':
            params = [self.stick_mapfile, self.accomfactor]
            query = f"""SELECT idnum
                        FROM surface_int_map
                        WHERE mapfile = %s and
                              accomfactor = %s"""
        else:
            raise InputError('SurfaceInteraction.search()',
             f'surfaceinteraction.sticktype = {self.sticktype} not allowed.')
        
        with config.database_connect() as con:
            cur = con.cursor()
            cur.execute(query, tuple(params))
    
            if cur.rowcount == 0:
                return None
            elif cur.rowcount == 1:
                return cur.fetchone()[0]
            else:
                raise RuntimeError('SurfaceInteraction.search()',
                                   'Duplicates in surface interaction table')


class Forces:
    def __init__(self, fparam):
        """Define a Forces object.

        See :doc:`inputfiles#Forces` for more information.
        """
    
        self.gravity = (bool(eval(fparam['gravity'].title()))
                        if 'gravity' in fparam
                        else True)
        self.radpres = (bool(eval(fparam['radpres'].title()))
                        if 'radpres' in fparam
                        else True)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            pass
    
        keys_self, keys_other = set(self.__dict__.keys()), set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            return all([self.__dict__[key] == other.__dict__[key] for key in keys_self])

    def __str__(self):
        result = ''
        for key,value in self.__dict__.items():
            result += f'forces.{key} = {value}\n'
        return result.strip()
    
    def insert(self):
        ids = self.search()
        if ids is None:
            with config.database_connect() as con:
                cur = con.cursor()
                cur.execute('''INSERT INTO forces (
                                   gravity, radpres) VALUES (%s, %s)''',
                            (self.gravity, self.radpres))
            ids = self.search()
            assert ids is not None
        else:
                pass

        return ids

    def search(self):
        query = f'''SELECT idnum FROM forces
                    WHERE gravity = %s and
                          radpres = %s'''
        
        with config.database_connect() as con:
            cur = con.cursor()
            cur.execute(query, (self.gravity, self.radpres))
    
            if cur.rowcount == 0:
                return None
            elif cur.rowcount == 1:
                return cur.fetchone()[0]
            else:
                raise RuntimeError('Forces.search()',
                                   'Duplicates in forces table')


class SpatialDist:
    def __init__(self, sparam):
        """Define a SpatialDist object.

        See :doc:`inputfiles#SpatialDist` for more information.
        """
        if 'type' in sparam:
            self.type = sparam['type']
        else:
            raise InputError('SpatialDist.__init__',
                             'SpatialDist.type not given')
        
        if self.type == 'uniform':
            self.exobase = (float(sparam['exobase'])
                            if 'exobase' in sparam
                            else 1.)  # Unit gets set later
            if 'longitude' in sparam:
                lon0, lon1 = (float(l.strip())
                              for l in sparam['longitude'].split(','))
                lon0 = max(lon0, 0.)
                lon0 = min(lon0, 2*np.pi)
                lon1 = max(lon1, 0.)
                lon1 = min(lon1, 2*np.pi)
                self.longitude = (lon0*u.rad, lon1*u.rad)
            else:
                self.longitude = (0.*u.rad, 2*np.pi*u.rad)
                
            if 'latitude' in sparam:
                lat0, lat1 = (float(l.strip())
                              for l in sparam['latitude'].split(','))
                lat0 = max(lat0, -np.pi/2)
                lat0 = min(lat0, np.pi/2)
                lat1 = max(lat1, -np.pi/2)
                lat1 = min(lat1, np.pi/2)
                if lat0 > lat1:
                    raise InputError('SpatialDist.__init__',
                         'SpatialDist.latitude[0] > SpatialDist.latitude[1]')
                self.latitude = (lat0*u.rad, lat1*u.rad)
            else:
                self.latitude = (-np.pi/2*u.rad, np.pi/2*u.rad)
        elif self.type == 'surface map':
            self.exobase = (float(sparam['exobase'])
                            if 'exobase' in sparam
                            else 1.)  # Unit gets set later
            
            self.mapfile = sparam.get('mapfile', 'default')
            
            if os.path.exists(self.mapfile):
                if self.mapfile.endswith('.pkl'):
                    with open(self.mapfile, 'rb') as f:
                        sourcemap = pickle.load(f)
                    coord_systems = ['planet-fixed', 'solar-fixed']
                    assert sourcemap['coordinate_system'] in coord_systems, (
                        'source map must be in planet-fixed or solar-fixed coordinates.')
                    self.coordinate_system = sourcemap['coordinate_system']
                else:
                    self.coordinate_system = 'solar-fixed'
                    # assert 0, 'Not set up yet'
            else:
                print('Warning: mapfile does not exist')
                self.coordinate_system = 'planet-fixed'

            if (self.coordinate_system == 'planet-fixed'):
                self.subsolarlon = sparam.get('subsolarlon', 0.)*u.rad
            else:
                self.subsolarlon = None
        elif self.type == 'surface spot':
            self.exobase = (float(sparam['exobase'])
                            if 'exobase' in sparam
                            else 1.)  # Unit gets set later
            if 'longitude' in sparam:
                self.longitude = float(sparam['longitude'])*u.rad
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpatialDist.longitude not given.')
            
            if 'latitude' in sparam:
                self.latitude = float(sparam['latitude'])*u.rad
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpatialDist.latitude not given.')

            if 'sigma' in sparam:
                self.sigma = float(sparam['sigma'])*u.rad
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpatialDist.sigma not given.')
        elif self.type == 'fitted output':
            self.unfit_outid = -1
            self.query = None
        else:
            raise InputError('SpatialDist.__init__',
                             f'SpatialDist.type = {self.type} not defined.')

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            pass
    
        keys_self, keys_other = set(self.__dict__.keys()), set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            return all([self.__dict__[key] == other.__dict__[key] for key in keys_self])

    def __str__(self):
        result = ''
        for key,value in self.__dict__.items():
            result += f'SpatialDist.{key} = {value}\n'
        return result.strip()
    
    def insert(self):
        ids = self.search()
        if ids is None:
            if self.type == 'uniform':
                long = [l.value for l in self.longitude]
                lat = [l.value for l in self.latitude]
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO spatdist_uniform (
                                       exobase, longitude, latitude) VALUES (
                                       %s, %s::DOUBLE PRECISION[2],
                                       %s::DOUBLE PRECISION[2])''',
                                (self.exobase, long, lat))
            elif self.type == 'surface map':
                with config.database_connect() as con:
                    cur = con.cursor()
                    sslon = (None
                             if self.subsolarlon is None
                             else self.subsolarlon.value)
                    cur.execute('''INSERT INTO spatdist_surfmap (
                                       exobase, mapfile, subsolarlon,
                                       coordinate_system) VALUES (
                                       %s, %s, %s, %s)''',
                                (self.exobase, self.mapfile, sslon,
                                 self.coordinate_system))
            elif self.type == 'surface spot':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO spatdist_spot (
                                       exobase, longitude, latitude, sigma) VALUES (
                                       %s, %s, %s, %s)''',
                                (self.exobase, self.longitude.value,
                                 self.latitude.value, self.sigma.value))
            elif self.type == 'fitted output':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO spatdist_fittedoutput (
                                   unfit_outid, query)
                                       VALUES (%s, %s)''',
                                (self.unfit_outid, self.query))
            else:
                raise InputError('SpatialDist.search()',
                                 f'SpatialDist.type = {self.type} not allowed.')
            ids = self.search()
            assert ids is not None
        else:
            pass
        
        return ids

    def search(self):
        if self.type == 'uniform':
            params = [self.exobase,
                      [self.longitude[0].value, self.longitude[1].value],
                      [self.latitude[0].value, self.latitude[1].value]]
            query = '''SELECT idnum
                       FROM spatdist_uniform
                       WHERE exobase = %s and
                             longitude = %s::DOUBLE PRECISION[2] and
                             latitude = %s::DOUBLE PRECISION[2]'''
        elif self.type == 'surface map':
            params = [self.exobase, self.mapfile]
            if self.subsolarlon is None:
                sslon = 'subsolarlon is NULL'
            else:
                sslon = 'subsolarlon = %s'
                params.append(self.subsolarlon.value)
                
            params.append(self.coordinate_system)
            query = f'''SELECT idnum
                        FROM spatdist_surfmap
                        WHERE exobase = %s and
                              mapfile = %s and
                              {sslon} and
                              coordinate_system = %s'''
        elif self.type == 'surface spot':
            params = [self.exobase, self.longitude.value, self.latitude.value,
                      self.sigma.value]
            query = '''SELECT idnum
                       FROM spatdist_spot
                       WHERE exobase = %s and
                             longitude = %s and
                             latitude = %s and
                             sigma = %s'''
        elif self.type == 'fitted output':
            params = [self.unfit_outid, self.query]
            query = '''SELECT idnum
                       FROM spatdist_fittedoutput
                       WHERE unfit_outid = %s and
                             query = %s'''
        else:
            raise InputError('SpatialDist.__init__',
                             f'SpatialDist.type = {self.type} not defined.')

        with config.database_connect() as con:
            cur = con.cursor()
            # print(cur.mogrify(query, tuple(params)))
            cur.execute(query, tuple(params))
    
            if cur.rowcount == 0:
                return None
            elif cur.rowcount == 1:
                return cur.fetchone()[0]
            else:
                raise RuntimeError('SpatialDist.search()',
                                   'Duplicates in spatial distribution table')
        


class SpeedDist:
    """Define a SpeedDist object.

    See :doc:`inputfiles#SpeedDist` for more information.
    """
    def __init__(self, sparam):
        self.type = sparam['type']

        if self.type == 'gaussian':
            if 'vprob' in sparam:
                self.vprob = float(sparam['vprob'])*u.km/u.s
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.vprob not given.')
            if 'sigma' in sparam:
                self.sigma = float(sparam['sigma'])*u.km/u.s
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.sigma not given.')
        elif self.type == 'sputtering':
            if 'alpha' in sparam:
                self.alpha = float(sparam['alpha'])
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.alpha not given.')
            if 'beta' in sparam:
                self.beta = float(sparam['beta'])
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.beta not given.')
            if 'u' in sparam:
                self.U = float(sparam['u'])*u.eV
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.U not given.')
        elif self.type == 'maxwellian':
            if 'temperature' in sparam:
                self.temperature = float(sparam['temperature'])*u.K
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.temperature not given.')
        elif self.type == 'flat':
            if 'vprob' in sparam:
                self.vprob = float(sparam['vprob'])*u.km/u.s
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.vprob not given.')
            
            if 'delv' in sparam:
                self.delv = float(sparam['delv'])*u.km/u.s
            else:
                raise InputError('SpatialDist.__init__',
                                 'SpeedDist.delv not given.')
        elif self.type == 'user defined':
            self.vdistfile = sparam.get('vdistfile', 'default')
        elif self.type == 'fitted output':
            self.unfit_outid = -1
            self.query = None
        else:
            assert 0, f'SpeedDist.type = {self.type} not available'

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            pass
    
        keys_self, keys_other = set(self.__dict__.keys()), set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            return all([self.__dict__[key] == other.__dict__[key] for key in keys_self])

    def __str__(self):
        result = ''
        for key,value in self.__dict__.items():
            result += f'SpeedDist.{key} = {value}\n'
        return result.strip()
    
    def insert(self):
        ids = self.search()
        if ids is None:
            if self.type == 'gaussian':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO speeddist_gaussian (
                                       vprob, sigma) VALUES (%s, %s)''',
                                (self.vprob.value, self.sigma.value))
            elif self.type == 'sputtering':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO speeddist_sputtering (
                                       alpha, beta, U) VALUES (%s, %s, %s)''',
                                (self.alpha, self.beta, self.U.value))
            elif self.type == 'maxwellian':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO speeddist_maxwellian (
                                       temperature) VALUES (%s)''',
                                (self.temperature.value, ))
            elif self.type == 'flat':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO speeddist_flat (
                                       vprob, delv) VALUES (%s, %s)''',
                                (self.vprob.value, self.delv.value))
            elif self.type == 'user defined':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO speeddist_user (
                                       vdistfile) VALUES (%s)''',
                                (self.vdistfile,))
            elif self.type == 'fitted output':
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO speeddist_fittedoutput (
                                   unfit_outid, query)
                                   VALUES (%s, %s)''',
                                (self.unfit_outid, self.query))
            else:
                raise InputError('SpeedDist.search()',
                                 f'speeddist.type = {self.type} not allowed.')

            ids = self.search()
            assert ids is not None
        else:
            pass

        return ids

    def search(self):
        if self.type == 'gaussian':
            params = [self.vprob.value, self.sigma.value]
            query = '''SELECT idnum
                       FROM speeddist_gaussian
                       WHERE vprob = %s and
                             sigma = %s'''
        elif self.type == 'sputtering':
            params = [self.alpha, self.beta, self.U.value]
            query = '''SELECT idnum
                       FROM speeddist_sputtering
                       WHERE alpha = %s and
                             beta = %s and
                             U = %s'''
        elif self.type == 'maxwellian':
            params = [self.temperature.value]
            query = '''SELECT idnum
                       FROM speeddist_maxwellian
                       WHERE temperature = %s'''
        elif self.type == 'flat':
            params = [self.vprob.value, self.delv.value]
            query = '''SELECT idnum
                       FROM speeddist_flat
                       WHERE vprob = %s and
                             delv = %s'''
        elif self.type == 'user defined':
            params = [self.vdistfile]
            query = '''SELECT idnum
                       FROM speeddist_user
                       WHERE vdistfile = %s'''
        elif self.type == 'fitted output':
            params = [self.unfit_outid, self.query]
            query = '''SELECT idnum
                           FROM speeddist_fittedoutput
                           WHERE unfit_outid = %s and
                                 query = %s'''
        else:
            raise InputError('SpeedDist.__init__',
                             f'SpeedDist.type = {self.type} not defined.')

        with config.database_connect() as con:
            cur = con.cursor()
            cur.execute(query, tuple(params))
        
            if cur.rowcount == 0:
                return None
            elif cur.rowcount == 1:
                return cur.fetchone()[0]
            else:
                raise RuntimeError('SpeedDist.search()',
                                   'Duplicates in speed distribution table')
    

class AngularDist:
    def __init__(self, aparam):
        """Define a AngularDist object.

        See :doc:`inputfiles#AngularDist` for more information.
        """
        if 'type' in aparam:
            self.type = aparam['type']
            if self.type == 'radial':
                pass
            elif self.type == 'isotropic':
                if 'azimuth' in aparam:
                    az0, az1 = (float(l.strip())
                                for l in aparam['azimuth'].split(','))
                    az0 = max(az0, 0.)
                    az0 = min(az0, 2*np.pi)
                    az1 = max(az1, 0.)
                    az1 = min(az1, 2*np.pi)
                    self.aziumth = (az0*u.rad, az1*u.rad)
                else:
                    self.azimuth = (0*u.rad, 2*np.pi*u.rad)

                if 'altitude' in aparam:
                    alt0, alt1 = (float(l.strip())*u.rad
                                  for l in aparam['altitude'].split(','))
                    alt0 = max(alt0, 0)
                    alt0 = min(alt0, np.pi/2)
                    alt1 = max(alt1, 0)
                    alt1 = min(alt1, np.pi/2)
                    if alt0 > alt1:
                        raise InputError('AngularDist.__init__',
                         'AngularDist.altitude[0] > AngularDist.altitude[1]')
                    self.altitude = (alt0*u.rad, alt1*u.rad)
                else:
                    self.altitude = (0*u.rad, np.pi/2*u.rad)
            else:
                raise InputError('AngularDist.__init__',
                             f'AngularDist.type = {self.type} not defined.')
        else:
            self.type = 'isotropic'
            self.azimuth = (0*u.rad, 2*np.pi*u.rad)
            self.altitude = (0*u.rad, np.pi/2*u.rad)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            pass
    
        keys_self, keys_other = set(self.__dict__.keys()), set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            return all([self.__dict__[key] == other.__dict__[key] for key in keys_self])

    def __str__(self):
        result = ''
        for key,value in self.__dict__.items():
            result += f'AngularDist.{key} = {value}\n'
        return result.strip()
    
    def insert(self):
        ids = self.search()
        if ids is None:
            if self.type == 'radial':
                assert 0, 'Should not be able to get here.'
            elif self.type == 'isotropic':
                alt = [a.value for a in self.altitude]
                az = [a.value for a in self.azimuth]
                with config.database_connect() as con:
                    cur = con.cursor()
                    cur.execute('''INSERT INTO angdist_isotropic (
                                       altitude, azimuth) VALUES (
                                       %s::DOUBLE PRECISION[2],
                                       %s::DOUBLE PRECISION[2])''',
                                (alt, az))
            else:
                raise InputError('AngularDist.search()',
                                 f'angulardist.type = {self.type} not allowed.')

            ids = self.search()
            assert ids is not None
        else:
            pass

        return ids

    def search(self):
        if self.type == 'radial':
            return 0
        elif self.type == 'isotropic':
            params = [[a.value for a in self.altitude],
                      [a.value for a in self.azimuth]]
            query = '''SELECT idnum
                       FROM angdist_isotropic
                       WHERE altitude=%s::DOUBLE PRECISION[2] and
                             azimuth=%s::DOUBLE PRECISION[2]'''
        else:
            raise InputError('AngularDist.__init__',
                             f'AngularDist.type = {self.type} not defined.')
    
        with config.database_connect() as con:
            cur = con.cursor()
            cur.execute(query, tuple(params))
        
            if cur.rowcount == 0:
                return None
            elif cur.rowcount == 1:
                return cur.fetchone()[0]
            else:
                raise RuntimeError('AngularDist.search()',
                                   'Duplicates in angular distribution table')


class Options:
    def __init__(self, oparam):
        """Define a Options object.

        See :doc:`inputfiles#Options` for more information.
        """
        if 'endtime' in oparam:
            self.endtime = float(oparam['endtime'])*u.s
        else:
            raise InputError('Options.__init__',
                             'options.endtime not specified.')

        if 'species' in oparam:
            self.species = oparam['species'].capitalize()
        elif 'atom' in oparam:
            self.species = oparam['atom'].capitalize()
        else:
            raise InputError('Options.__init__',
                             'options.species not specified.')

        self.lifetime = float(oparam.get('lifetime', 0))*u.s
        
        if 'outeredge' in oparam:
            self.outeredge = float(oparam['outeredge'])
        elif 'outer_edge' in oparam:
            self.outeredge = float(oparam['outer_edge'])
        else:
            self.outeredge = 1e30
            
        if 'step_size' in oparam:
            self.step_size = float(oparam['step_size'])
        elif 'stepsize' in oparam:
            self.step_size = float(oparam['step_size'])
        else:
            self.step_size = 0.

        if self.step_size == 0:
            self.resolution = oparam.get('resolution', 1e-4)
        else:
            self.resolution = None
            
        if 'fitted' in oparam:
            self.fitted = (True if oparam['fitted'].casefold() == 'True'.casefold()
                           else False)
        else:
            self.fitted = False

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            pass
    
        keys_self, keys_other = set(self.__dict__.keys()), set(other.__dict__.keys())
        if keys_self != keys_other:
            return False
        else:
            return all([self.__dict__[key] == other.__dict__[key] for key in keys_self])

    def __str__(self):
        result = ''
        for key,value in self.__dict__.items():
            result += f'options.{key} = {value}\n'
        return result.strip()
    
    def insert(self):
        ids = self.search()
        if ids is None:
            with config.database_connect() as con:
                cur = con.cursor()
                cur.execute('''INSERT into options (endtime, species, lifetime,
                                   outer_edge, step_size, resolution, fitted) VALUES (
                                   %s, %s, %s, %s, %s, %s, %s)''',
                            (self.endtime.value, self.species,
                             self.lifetime.value, self.outeredge,
                             self.step_size, self.resolution, self.fitted))
            ids = self.search()
            assert ids is not None
        else:
            pass

        return ids

    def search(self):
        params = [self.endtime.value, self.species, self.lifetime.value,
                  self.outeredge, self.step_size, self.fitted]
        
        if self.resolution is None:
            resol = 'resolution is NULL'
        else:
            resol = 'resolution = %s'
            params.append(self.resolution)
            
        query = f'''SELECT idnum
                    FROM options
                    WHERE endtime = %s and
                          species = %s and
                          lifetime = %s and
                          outer_edge = %s and
                          step_size = %s and
                          {resol} and
                          fitted = %s'''
        
        with config.database_connect() as con:
            cur = con.cursor()
            cur.execute(query, tuple(params))
    
            if cur.rowcount == 0:
                return None
            elif cur.rowcount == 1:
                return cur.fetchone()[0]
            else:
                raise RuntimeError('Options.search()',
                                   'Duplicates in options table')
