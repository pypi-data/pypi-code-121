"""Classes used by the Inputs class"""
import os
import numpy as np
import pickle
import pandas as pd
from astropy.time import Time
import astropy.units as u
import sqlalchemy as sqla
import sqlalchemy.dialects.postgresql as pg
from nexoclom.solarsystem import SSObject
from nexoclom.utilities import InputError, NexoclomConfig
from nexoclom.modelcode.SourceMap import SourceMap


dtor = np.pi/180.
# Tolerances for floating point values
dtaa = 2.*dtor


config = NexoclomConfig()


class Geometry:
    def __init__(self, gparam):
        """Define a Geometry object.
        
        See :doc:`inputfiles#Geometry` for more information.
        """
        # Planet
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
            result += f'geometry.{key} = {value}\n'
        return result.strip()
    
    def insert(self):
        # check to see if it is already there
        ids = self.search()
        
        if ids is None:
            engine = config.create_engine()
            metadata_obj = sqla.MetaData()
            if self.type == 'geometry with starttime':
                if self.objects is None:
                    objs = None
                else:
                    objs = [o.object for o in self.objects]

                table = sqla.Table("geometry_without_time",
                                   metadata_obj,
                                   autoload_with=engine)
                insert_stmt = pg.insert(table).values(
                    planet=self.planet.object,
                    startpoint=self.startpoint,
                    objects=objs,
                    starttime = self.time)
            elif self.type == 'geometry without starttime':
                if self.objects is None:
                    objs = None
                else:
                    objs = [o.object for o in self.objects]
                    
                subspt = [s.value for s in self.subsolarpoint]
                
                if self.phi is None:
                    phi = None
                else:
                    phi = [p.value for p in self.phi]
                    
                table = sqla.Table("geometry_without_time",
                                   metadata_obj,
                                   autoload_with=engine)
                
                insert_stmt = pg.insert(table).values(
                    planet=self.planet.object,
                    startpoint=self.startpoint,
                    objects=objs,
                    phi=phi,
                    subsolarpt=subspt,
                    taa=self.taa.value)
            else:
                raise InputError('Geometry.insert()',
                                 f'geometry.type = {self.type} not allowed.')
            
            with engine.connect() as con:
                result = con.execute(insert_stmt)
                con.commit()
            
            ids = result.inserted_primary_key
            assert len(ids) == 1
            ids = ids[0]
        else:
            pass
        
        return int(ids)

    def search(self):
        engine = config.create_engine()
        metadata_obj = sqla.MetaData()

        if self.objects is None:
            objects = None
        else:
            objects = [o.object for o in self.objects]
            
        if self.type == 'geometry with starttime':
            table = sqla.Table("geometry_without_time",
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum,
                                table.columns.taa).where(
                table.columns.planet == self.planet.object,
                table.columns.startpoint == self.startpoint,
                table.columns.objects  ==  objects,
                table.columns.starttime  ==  self.time)
        elif self.type == 'geometry without starttime':
            if self.phi is None:
                phi = None
            else:
                phi = [p.value for p in self.phi]
            
            subspoint = [s.value for s in self.subsolarpoint]

            table = sqla.Table("geometry_without_time",
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum,
                                table.columns.taa).where(
                table.columns.planet == self.planet.object,
                table.columns.startpoint == self.startpoint,
                table.columns.objects == objects,
                table.columns.phi == phi,
                table.columns.subsolarpt == subspoint,
                table.columns.taa >= self.taa.value - dtaa/2.,
                table.columns.taa < self.taa.value + dtaa/2.)
        else:
            raise InputError('geometry.search()',
                             f'geometry.type = {self.type} not allowed.')
                    
        with engine.connect() as con:
            results = pd.DataFrame(con.execute(query))
            
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return int(results.loc[0, 'idnum'])
        else:
            diff = np.abs(results.taa - self.taa.value)
            q = np.where(diff == diff.min())[0]
            if len(q) == 1:
                return int(results.loc[q, 'idnum'][0])
            else:
                raise RuntimeError('geometry.search()',
                                   'Duplicates in geometry table')


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
                self.stick_map = SourceMap(self.stick_mapfile)
            else:
                print('Warning: stick_mapfile does not exist')
                self.stick_map = None
            self.subsolarlon = sparam.get('subsolarlon', None)
            if self.subsolarlon is not None:
                self.subsolarlon *= u.rad
            else:
                pass

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
            engine = config.create_engine()
            metadata_obj = sqla.MetaData()
            if self.sticktype == 'constant':
                table = sqla.Table('surface_int_constant',
                                   metadata_obj,
                                   autoload_with=engine)
                
                insert_stmt = pg.insert(table).values(
                    stickcoef=self.stickcoef,
                    accomfactor=self.accomfactor)
            elif self.sticktype == 'surface map':
                table = sqla.Table('surface_int_map',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    mapfile=self.stick_mapfile,
                    accomfactor = self.accomfactor)
            elif self.sticktype == 'temperature dependent':
                table = sqla.Table('surface_int_tempdependent',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    accomfactor = self.accomfactor,
                    a = self.A)
            else:
                raise InputError('SurfaceInteraction.search()',
                    f'surfaceinteraction.sticktype = {self.sticktype} not allowed.')

            with engine.connect() as con:
                result = con.execute(insert_stmt)
                con.commit()

            ids = result.inserted_primary_key
            assert len(ids) == 1
            ids = ids[0]
        else:
            pass

        return int(ids)

    def search(self):
        engine = config.create_engine()
        metadata_obj = sqla.MetaData()
        
        if self.sticktype == 'constant':
            table = sqla.Table('surface_int_constant',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.accomfactor == self.accomfactor,
                table.columns.stickcoef == self.stickcoef)
        elif self.sticktype == 'temperature dependent':
            table = sqla.Table('surface_int_tempdependent',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.accomfactor == self.accomfactor,
                table.columns.a == self.A)
        elif self.sticktype == 'surface map':
            table = sqla.Table('surface_int_map',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.accomfactor == self.accomfactor,
                table.columns.mapfile == self.stick_mapfile)
        else:
            raise InputError('SurfaceInteraction.search()',
             f'surfaceinteraction.sticktype = {self.sticktype} not allowed.')
        
        with engine.connect() as con:
            results = pd.DataFrame(con.execute(query))
            
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return int(results.loc[0, 'idnum'])
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
            engine = config.create_engine()
            metadata_obj = sqla.MetaData()
            table = sqla.Table('forces', metadata_obj, autoload_with=engine)
            insert_stmt = pg.insert(table).values(
                gravity=self.gravity,
                radpres=self.radpres)
            
            with engine.connect() as con:
                result = con.execute(insert_stmt)
                con.commit()
                
            ids  = result.inserted_primary_key
            assert len(ids) == 1
            ids = ids[0]
        else:
            pass

        return int(ids)

    def search(self):
        engine = config.create_engine()
        metadata_obj = sqla.MetaData()
        table = sqla.Table('forces', metadata_obj, autoload_with=engine)
        
        query = sqla.select(table.columns.idnum).where(
            table.columns.gravity == self.gravity,
            table.columns.radpres == self.radpres)
        
        with engine.connect() as con:
            results = pd.DataFrame(con.execute(query))
    
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return int(results.loc[0, 'idnum'])
        else:
            raise RuntimeError('Forces.search()', 'Duplicates in forces table')


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
                self.sourcemap = SourceMap(self.mapfile)
            else:
                print('Warning: mapfile does not exist')
                self.sourcemap = None
                
            self.subsolarlon = sparam.get('subsolarlon', None)
            if self.subsolarlon is not None:
                self.subsolarlon *= u.rad
            else:
                pass
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
            engine = config.create_engine()
            metadata_obj = sqla.MetaData()
            if self.type == 'uniform':
                long = [l.value for l in self.longitude]
                lat = [l.value for l in self.latitude]
                
                table = sqla.Table("spatdist_uniform",
                                   metadata_obj,
                                   autoload_with=engine)
                insert_stmt = pg.insert(table).values(
                    exobase = self.exobase,
                    longitude = long,
                    latitude = lat)
            elif self.type == 'surface map':
                sslon = (None
                         if self.subsolarlon is None
                         else self.subsolarlon.value)
                table = sqla.Table("spatdist_surfmap",
                                   metadata_obj,
                                   autoload_with=engine)
                insert_stmt = pg.insert(table).values(
                    exobase=self.exobase,
                    mapfile=self.mapfile,
                    subsolarlon=sslon,
                    coordinate_system=self.coordinate_system)
            elif self.type == 'surface spot':
                table = sqla.Table("spatdist_spot",
                                   metadata_obj,
                                   autoload_with=engine)
                insert_stmt = pg.insert(table).values(
                    exobase=self.exobase,
                    longitude=self.longitude.value,
                    latitude=self.latitude.value,
                    sigma=self.sigma.value)
            elif self.type == 'fitted output':
                table = sqla.Table("spatdist_fittedoutput",
                                   metadata_obj,
                                   autoload_with=engine)
                insert_stmt = pg.insert(table).values(
                    unfit_outid=self.unfit_outid,
                    query=self.query)
            else:
                raise InputError('SpatialDist.search()',
                                 f'SpatialDist.type = {self.type} not allowed.')
            with engine.connect() as con:
                result = con.execute(insert_stmt)
                con.commit()

            ids  = result.inserted_primary_key
            assert len(ids) == 1
            ids = ids[0]
        else:
            pass
        
        return int(ids)

    def search(self):
        engine = config.create_engine()
        metadata_obj = sqla.MetaData()
        
        if self.type == 'uniform':
            table = sqla.Table('spatdist_uniform',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.exobase == self.exobase,
                table.columns.longitude ==  [self.longitude[0].value,
                                             self.longitude[1].value],
                table.columns.latitude == [self.latitude[0].value,
                                           self.latitude[1].value])
        elif self.type == 'surface map':
            sslon = (None
                     if self.subsolarlon is None
                     else self.subsolarlon.value)
            table = sqla.Table('spatdist_surfmap',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.exobase == self.exobase,
                table.columns.mapfile == self.mapfile,
                table.columns.subsolarlon == sslon,
                table.columns.coordinate_system == self.coordinate_system)
        elif self.type == 'surface spot':
            table = sqla.Table('spatdist_spot',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.exobase == self.exobase,
                table.columns.longitude == self.longitude.value,
                table.columns.latitude == self.latitude.value,
                table.columns.sigma == self.sigma.value)
        elif self.type == 'fitted output':
            table = sqla.Table('spatdist_fittedoutput',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.unfit_outid == self.unfit_outid,
                table.columns.query == self.query)
        else:
            raise InputError('SpatialDist.__init__',
                             f'SpatialDist.type = {self.type} not defined.')

        with engine.connect() as con:
            results = pd.DataFrame(con.execute(query))
    
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return int(results.loc[0, 'idnum'])
        else:
            raise RuntimeError('SpatialDist.search()',
                               'Duplicates in forces table')


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
            if os.path.exists(self.vdistfile):
                self.vdist = SourceMap(self.vdistfile)
            else:
                print('Warning: vdistfile does not exist')
                self.vdist = None
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
            engine = config.create_engine()
            metadata_obj = sqla.MetaData()
            if self.type == 'gaussian':
                table = sqla.Table('speeddist_gaussian',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    vprob=self.vprob.value,
                    sigma=self.sigma.value)
            elif self.type == 'sputtering':
                table = sqla.Table('speeddist_sputtering',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    alpha=self.alpha,
                    beta=self.beta,
                    U=self.U.value)
            elif self.type == 'maxwellian':
                table = sqla.Table('speeddist_maxwellian',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    temperature=self.temperature.value)
            elif self.type == 'flat':
                table = sqla.Table('speeddist_flat',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    vprob=self.vprob.value,
                    delv=self.delv.value)
            elif self.type == 'user defined':
                table = sqla.Table('speeddist_user',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    vdistfile=self.vdistfile)
            elif self.type == 'fitted output':
                table = sqla.Table('speeddist_fittedoutput',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    unfit_outid=self.unfit_outid,
                    query=self.query)
            else:
                raise InputError('SpeedDist.search()',
                                 f'speeddist.type = {self.type} not allowed.')

            with engine.connect() as con:
                result = con.execute(insert_stmt)
                con.commit()

            ids = result.inserted_primary_key
            assert len(ids) == 1
            ids = ids[0]
        else:
            pass

        return int(ids)

    def search(self):
        engine = config.create_engine()
        metadata_obj = sqla.MetaData()
        
        if self.type == 'gaussian':
            table = sqla.Table('vprob_gaussian',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.vprob == self.vprob.value,
                table.columns.sigma == self.sigma.value)
        elif self.type == 'sputtering':
            table = sqla.Table('speeddist_sputtering',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.alpha == self.alpha,
                table.columns.beta == self.beta,
                table.columns.U == self.U.value)
            
        elif self.type == 'maxwellian':
            table = sqla.Table('speeddist_maxwellian',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.temperature == self.temperature.value)
        elif self.type == 'flat':
            table = sqla.Table('speeddist_flat',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.vprob == self.vprob.value,
                table.columns.delv == self.delv.value)
        elif self.type == 'user defined':
            table = sqla.Table('speeddist_user',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.vdistfile == self.vdistfile)
        elif self.type == 'fitted output':
            table = sqla.Table('speeddist_fittedoutput',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.unfit_outid == self.unfit_outid,
                table.columns.query == self.query)
        else:
            raise InputError('SpeedDist.__init__',
                             f'SpeedDist.type = {self.type} not defined.')

        with engine.connect() as con:
            results = pd.DataFrame(con.execute(query))
            
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return int(results.loc[0, 'idnum'])
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
            engine = config.create_engine()
            metadata_obj = sqla.MetaData()
            
            if self.type == 'radial':
                assert False, 'Should not be able to get here.'
            elif self.type == 'isotropic':
                alt = [a.value for a in self.altitude]
                az = [a.value for a in self.azimuth]
                table = sqla.Table('angdist_isotropic',
                                   metadata_obj,
                                   autoload_with=engine)
    
                insert_stmt = pg.insert(table).values(
                    altitude=alt,
                    azimuth=az)
            else:
                raise InputError('AngularDist.search()',
                                 f'angulardist.type = {self.type} not allowed.')

            with engine.connect() as con:
                result = con.execute(insert_stmt)
                con.commit()

            ids = result.inserted_primary_key
            assert len(ids) == 1
            ids = ids[0]
        else:
            pass

        return int(ids)

    def search(self):
        engine = config.create_engine()
        metadata_obj = sqla.MetaData()
        
        if self.type == 'radial':
            return 0
        elif self.type == 'isotropic':
            alt = [a.value for a in self.altitude]
            az = [a.value for a in self.azimuth]
            table = sqla.Table('angdist_isotropic',
                               metadata_obj,
                               autoload_with=engine)
            query = sqla.select(table.columns.idnum).where(
                table.columns.altitude == alt,
                table.columns.azimuth == az)
        else:
            raise InputError('AngularDist.__init__',
                             f'AngularDist.type = {self.type} not defined.')
    
        with engine.connect() as con:
            results = pd.DataFrame(con.execute(query))
            
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return int(results.loc[0, 'idnum'])
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
            engine = config.create_engine()
            metadata_obj = sqla.MetaData()
            table = sqla.Table('options',
                               metadata_obj,
                               autoload_with=engine)

            insert_stmt = pg.insert(table).values(
                endtime=self.endtime.value,
                species=self.species,
                lifetime=self.lifetime.value,
                outer_edge=self.outeredge,
                step_size=self.step_size,
                resolution=self.resolution,
                fitted=self.fitted)
                
            with engine.connect() as con:
                result = con.execute(insert_stmt)
                con.commit()

            ids = result.inserted_primary_key
            assert len(ids) == 1
            ids = ids[0]
        else:
            pass

        return int(ids)

    def search(self):
        engine = config.create_engine()
        metadata_obj = sqla.MetaData()
        
        table = sqla.Table('options',
                           metadata_obj,
                           autoload_with=engine)
        query = sqla.select(table.columns.idnum).where(
            table.columns.endtime == self.endtime.value,
            table.columns.species == self.species,
            table.columns.lifetime == self.lifetime.value,
            table.columns.outer_edge == self.outeredge,
            table.columns.step_size == self.step_size,
            table.columns.resolution == self.resolution,
            table.columns.fitted == self.fitted)
        
        with engine.connect() as con:
            results = pd.DataFrame(con.execute(query))

        if len(results) == 0:
            return None
        elif len(results) == 1:
            return int(results.loc[0, 'idnum'])
        else:
            raise RuntimeError('Options.search()', 'Duplicates in options table')
