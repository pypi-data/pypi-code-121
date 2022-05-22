import numpy as np
from nutpy.core.kinematics import rotations as kr
import nutpy.utilities as utl
import pkg_resources
import pandas as pd


class Satellite:
    """
    Satellite model class, includes instances of Instrument class

    Attributes
    ----------
    name : str
        Name of the satellite
    q0 : ndarray (4,1)
        Initial satellite attitude expressed as quaternion
    attitude : pandas DataFrame
        Attitude over time of the satellite
    instrument_pointing : pandas DataFrame
        Pointing of the instrument over time
    inst : Instrument class
        Instance of instrument class with default configuration
    """

    options = {'name': 'Default_sat',
               'q0': np.array([0, 0, 0, 1]).reshape(-1, 1),
               'attitude': pd.DataFrame(columns=['q1', 'q2', 'q3', 'q4']),
               'instrument_pointing': pd.DataFrame(columns=['ux', 'uy', 'uz'])
               }

    def __init__(self, **kwargs):
        """
        Constructor

        Parameters
        ----------
        name : str
            Name of the satellite
        q0 : ndarray (4,1)
            Initial satellite attitude expressed as quaternion
        attitude : pandas DataFrame (empty)
            Attitude over time of the satellite
        instrument_pointing : pandas DataFrame (empty)
            Pointing of the instrument over time
        **kwargs : dict
            Arguments to define the instrument
        """

        self.options.update(kwargs)

        self.name = self.options['name']
        self.q0 = self.options['q0']
        self.attitude_df = self.options['attitude']
        self.inst = Instrument(**kwargs)

    @property
    def SSP(self):
        return self.inst.SSP

    @property
    def instrument_attitude_df(self):
        return self.inst.attitude_df

    def update(self, **kwargs):
        """
        Updates instrument configuration

        Parameters
        ----------
        SSP : list (5) of floats
            Scan strategy parameters [alpha (deg), beta (deg), spin period
            (min), precesion period (min), delta (deg)]
        delta_detector : float
            Half-angle of the detector fov (degrees)
        Nx : int
            Number of horizontal detectors (rectangular array)
        Ny : int
            Number of vertical detectors (rectangular array)
        layout : str
            Type of array layout (circular/rectangular/custome)
        Nd : int
            Number of detectors of the circular array
        file_name : str
            File with detectors positions
        """

        self.inst.update(**kwargs)

        return 0

    def generate_attitude(self, mt, dT, q0, SSP):
        """
        Generates satellite and instrument attitude

        Parameters
        ----------
        mt : float
            Period of time considered for the numerical analysis
        dT : float
            Step time
        q0 : ndarray (4,1)
            Initial satellite attitude expressed as quaternion
        SSP : list (5) of floats
            Scan strategy parameters [alpha (deg), beta (deg), spin period
            (min), precesion period (min), delta (deg)]
        """

        time, satellite_quaternions = kr.emulate_attitude(mt,
                                                          dT,
                                                          q0,
                                                          SSP
                                                          )

        self.attitude_df = pd.DataFrame(columns=self.attitude_df.columns,
                                        data=satellite_quaternions.T,
                                        index=time
                                        )

        mounting_quaternion = kr.C2q(self.inst.mounting_matrix)

        instrument_quaternions = kr.quat_product(mounting_quaternion,
                                                 satellite_quaternions
                                                 )

        self.inst.attitude_df = pd.DataFrame(columns=self.attitude_df.columns,
                                             data=instrument_quaternions.T,
                                             index=time
                                             )

        return 0


class Instrument:
    """
    Instrument model

    Attributes
    ----------
    SSP : list (5) of floats
        Scan strategy parameters [alpha (deg), beta (deg), spin period (min),
        precesion period (min), delta (deg)]
    delta_detector : float
        Half-angle of the detector fov (degrees)
    Nx : int
        Number of horizontal detectors (rectangular array)
    Ny : int
        Number of vertical detectors (rectangular array)
    layout : str
        Type of array layout (circular/rectangular/custome)
    Nd : int
        Number of detectors of the circular array
    file_name : str
        File with detectors positions
    xd : float
        X coordinates of detectors in focal plane
    yd : float
        Y coordinates of detectors in focal plane
    nd : int
        Number of detectors
    r : float
        Half-angle of the detector fov (degrees)
    ids : 1D-array
        List of detectors id
    """

    options = {'SSP': [45., 50., 10., 93., 7.5],
               'delta_detector': 0.25,
               'Nx': 20,
               'Ny': 20,
               'layout': 'rectangular',
               'Nd': 400,
               'file_name': 'example_custome_layout.txt',
               'u0': np.array([1, 0, 0]).reshape(-1, 1)
               }

    def __init__(self, **kwargs):
        """
        Constructor

        Parameters
        ----------
        SSP : list (5) of floats
            Scan strategy parameters [alpha (deg), beta (deg), spin period
            (min), precesion period (min), delta (deg)]
        delta_detector : float
            Half-angle of the detector fov (degrees)
        Nx : int
            Number of horizontal detectors (rectangular array)
        Ny : int
            Number of vertical detectors (rectangular array)
        layout : str
            Type of array layout (circular/rectangular/custome)
        Nd : int
            Number of detectors of the circular array
        file_name : str
            File with detectors positions
        u0 : ndarray (3,1)
            Direction of observation (in instrument frame)
        xd : float
            X coordinates of detectors in focal plane
        yd : float
            Y coordinates of detectors in focal plane
        nd : int
            Number of detectors
        r : float
            Half-angle of the detector fov (degrees)
        ids : 1D-array
            List of detectors id
        """

        # makes sure that SSP elements are floats
        try:
            kwargs['SSP'] = list(map(float, kwargs['SSP']))
            if len(kwargs['SSP']) != 5:
                raise ValueError("The Scan Strategy Parameters (SSP) are 5")
        except KeyError:
            pass

        self.options.update(kwargs)

        self.SSP = self.options['SSP']
        self.delta_detector = self.options['delta_detector']
        self.Nx = self.options['Nx']
        self.Ny = self.options['Ny']
        self.layout = self.options['layout']
        self.Nd = self.options['Nd']
        self.file_name = self.options['file_name']
        self.u0 = self.options['u0']

        self.xd = None
        self.yd = None
        self.nd = None
        self.r = None
        self.ids = None
        self.mounting_matrix = None

        self.grid_functions_dict = {'rectangular': self.generate_rectangular_grid,
                                    'circular': self.generate_circular_grid,
                                    'custome': self.generate_custome_grid
                                    }

        self.setup_instrument()

    @property
    def fov(self):
        return 2 * self.SSP[4]

    def setup_instrument(self):
        """
        Configures the instrument generating the grid and the mounting matrix

        The mounting matrix is defined as a rotation around satellite's Z-axis.
        """

        beta = self.SSP[1] * np.pi/180

        self.mounting_matrix = kr.Cz(beta)

        # generate desired layout
        self.grid_functions_dict[self.layout]()

        return 0

    def update(self, **kwargs):
        """
        Updates the instrument configuration

        Parameters
        ----------
        SSP : list (5) of floats
            Scan strategy parameters [alpha (deg), beta (deg), spin period
            (min), precesion period (min), delta (deg)]
        delta_detector : float
            Half-angle of the detector fov (degrees)
        Nx : int
            Number of horizontal detectors (rectangular array)
        Ny : int
            Number of vertical detectors (rectangular array)
        layout : str
            Type of array layout (circular/rectangular/custome)
        Nd : int
            Number of detectors of the circular array
        file_name : str
            File with detectors positions
        """

        # makes sure that SSP elements are floats
        try:
            kwargs['SSP'] = list(map(float, kwargs['SSP']))
            if len(kwargs['SSP']) != 5:
                raise ValueError("The Scan Strategy Parameters (SSP) are 5")
        except Exception:
            ValueError("SSP values not valid")

        self.options.update(kwargs)

        for k, v in self.options.items():
            setattr(self, k, v)

        # layout is generated again just in case
        self.grid_functions_dict[self.layout]()

        return 0

    def generate_rectangular_grid(self):
        """"
        Generates rectangular array of detectors

        The fov of the instrument is considered to have unitary radius, then the
        size of a rectangle circumscribed to it calculated. Such rectangle have
        the same side lenghts ratio (Lx/Ly) as the ratio of detectors (Nx/Ny)
        """

        # ratio of detectors
        s = self.Nx/self.Ny

        # scale detectors half-angle fov (its size) with instrument half-angle
        # fov (fov size)
        self.r = self.delta_detector/(self.SSP[4])

        # size of rectangle (with its sides having  ratio s) circumscribed to
        # unitary circle (fov)
        Lx = 2 * np.sqrt(1/(1 + 1/(s**2)))
        Ly = Lx/s

        # length between corner detectors centers
        lx = Lx/2 - self.r
        ly = Ly/2 - self.r

        # position of Nx/Ny detectors, equally spaced
        x = np.linspace(-lx, lx, self.Nx)
        y = np.linspace(-ly, ly, self.Ny)

        X, Y = np.meshgrid(x, y)

        self.xd = X.flatten()
        self.yd = Y.flatten()

        # number of detectors
        self.nd = self.Nx * self.Ny

        # id of detectors
        self.ids = np.arange(self.nd)

        return 0

    def generate_circular_grid(self):
        """
        Generates circular array of detectors

        This distribution is the same as the seeds of a sunflower

        References
        ----------
        .. [1] https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere/26127012#26127012 # noqa
        """

        # scale detectors half-angle fov (its size) with instrument half-angle fov (fov size)
        self.r = self.delta_detector/(self.SSP[4])

        indices = np.arange(0, self.Nd, dtype=float) + 0.5

        # golden number
        phi = (1 + 5**0.5)/2

        # sequence of raius and angle
        r = np.sqrt(indices/self.Nd) - self.r
        theta = 2 * np.pi * phi * indices

        self.xd = r * np.cos(theta)
        self.yd = r * np.sin(theta)

        # number of detectors
        self.nd = self.Nd

        # id of detectors
        self.ids = np.arange(self.nd)

        return 0

    def generate_custome_grid(self):
        """
        Generates custome array of detectors

        The coordinates of the detectors center are retrieved from txt file
        """

        # scale detectors half-angle fov (its size) with instrument half-angle
        # fov (fov size)
        self.r = self.delta_detector/(self.SSP[4])

        self.folder_path = pkg_resources.resource_filename('nutpy', 'data/')

        self.xd, self.yd = utl.read_detectors_coordinates(self.folder_path + self.file_name)

        # number of detectors
        self.nd = len(self.xd)

        # id of detectors
        self.ids = np.arange(self.nd)

        return 0

    def sensor_SSP(self,
                   sensor_id
                   ):
        """
        Calculates the modified Scan Strategy parameters based on the location
        of the choosen sensor in the instrument layout.

        Parameters
        ----------
        SSP : list (5)
            Scan Strategy Parameters (alpha, beta, spin, precesion, delta)/
            (deg, deg, min, min, deg)
        sensor_id : int
            Sensor id number

        Returns
        -------
        SSP : list (5)
            Modified Scan Strategy Parameters (alpha, beta, spin, precesion,
            delta)/(deg, deg, min, min, deg)
        """

        # make a copy to modify it later
        SSP_mod = self.SSP.copy()

        beta = self.SSP[1]
        delta = self.SSP[4]

        # adjust beta to account for the sensor location in focal plane
        # xd and yd coordinates are normalized with delta
        xd = self.inst.xd[sensor_id] * delta
        yd = self.inst.yd[sensor_id] * delta

        # new beta
        db = np.sqrt((beta + xd)**2 + yd**2)
        SSP_mod[1] = db

        return SSP_mod
