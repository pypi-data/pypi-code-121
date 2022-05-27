"""Create an object for each Solar System body containing basic information.
Information stored:
* object: Object name
* orbits: Body that the object orbits
* radius: in km
* mass: in kg
* a: orbital semi major axis. In AU if orbits the Sun; km
    if orbits a planet
* e: orbital eccentricity
* tilt: tilt of planetary axis in degrees
* rotperiod: rotation period in hours
* orbperiod: orbital period in days
* GM: mass * G in m**3/s**2
* moons: returned as a list of SSObjects

Values are astropy units quantities when appropriate.

"""
import os
import pandas as pd
from astropy import constants as const
from astropy import units as u
from nexoclom import __file__ as basefile


class SSObject:
    """Creates Solar System object."""
    def __init__(self, obj):
        basepath = os.path.dirname(basefile)
        pklfile = os.path.join(basepath, 'data', 'PlanetaryConstants.pkl')
        if not os.path.exists(pklfile):
            set_up_planetary_constants(pklfile)
        else:
            pass

        constants = pd.read_pickle(pklfile)
        
        row = constants.loc[constants.Object.apply(lambda x: x.casefold()) ==
                            obj.casefold()]
        if len(row) == 1:
            row = row.iloc[0]

            self.object = row.Object
            self.orbits = row.orbits
            self.radius = row.radius * u.km
            self.mass = row.mass * u.kg
            self.a = row.a
            self.e = row.e
            self.tilt = row.tilt * u.deg
            self.rotperiod = row.rot_period * u.h
            self.orbperiod = row.orb_period * u.d
            self.GM = -self.mass * const.G

            self.moons = [SSObject(moon) for moon in
                constants.loc[constants.orbits == self.object, 'Object'].to_list()]
            if len(self.moons) == 0:
                self.moons = None
            else:
                pass

            if self.orbits == 'Milky Way':
                self.type = 'Star'
                self.a *= u.km
            elif self.orbits == 'Sun':
                self.type = 'Planet'
                self.a *= u.au
            else:
                self.type = 'Moon'
                self.a *= u.km
        else:
            print(f'Object {obj} does not exist in table.')
            self.object = None

    def __len__(self):
        # Returns number of objects (e.g. Planet + moons) in the SSObeject
        return 1 if self.moons is None else len(self.moons)+1

    def __eq__(self, other):
        return self.object == other.object

    def __hash__(self):
        return hash((self.object, ))
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        out = (f'Object: {self.object}\n'
               f'Type = {self.type}\n'
               f'Orbits {self.orbits}\n'
               f'Radius = {self.radius:0.2f}\n'
               f'Mass = {self.mass:0.2e}\n'
               f'a = {self.a:0.2f}\n'
               f'Eccentricity = {self.e:0.2f}\n'
               f'Tilt = {self.tilt:0.2f}\n'
               f'Rotation Period = {self.rotperiod:0.2f}\n'
               f'Orbital Period = {self.orbperiod:0.2f}\n'
               f'GM = {self.GM:0.2e}')
        return out
    
def set_up_planetary_constants(pklfile):
    basepath = os.path.dirname(basefile)
    objfile = os.path.join(basepath, 'data', 'SolarSystemContents.csv')
    objects = pd.read_csv(objfile)
    
    # Columns to add: radius, mass, a, e, tilt, rot_period, orb_period
    
    
    table = pd.read_csv(pklfile.replace('.pkl', '.dat'), skipinitialspace=True,
                        skip_blank_lines=True, comment='#', sep=':')
    table.columns = [col.strip() for col in table.columns]
    table.Object = table.Object.apply(lambda x: x.strip())
    table.orbits = table.orbits.apply(lambda x: x.strip())
    table.to_pickle(pklfile)
