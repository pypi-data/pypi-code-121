from nutpy.core.satellite import Satellite
import nutpy.algorithms.visibility as vs
import nutpy.postprocessing.pgraph as pg

import pandas as pd


class Nut:
    """
    Interface with the user

    Attributes
    ----------
    name : str
        Name of the mission
    mission_time : float
        Period of time considered for the numerical analysis
    dT : float
        Step time used for the numerical analysis
    sensor_id : int
        Sensor id number
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

    # default options
    options = {'name': "Default_mission",
               'mission_time': 3600,
               'dT': 2,
               'N': 100,
               'Nth': 360,
               'nside': 16,
               'bar': True,
               'detailed': False,
               'dense': False
               }

    def __init__(self, **kwargs):
        """
        Constructor

        Parameters
        ----------
        name : str
            Name of the mission
        """

        # update default_options
        self.options.update(kwargs)

        self.name = self.options['name']
        self._mission_time = self.options['mission_time']
        self._dT = self.options['dT']
        self._N = self.options['N']
        self._Nth = self.options['Nth']
        self._nside = self.options['nside']
        self.bar = self.options['bar']
        self.detailed = self.options['detailed']
        self.dense = self.options['dense']

        self.sat = Satellite(**kwargs)

        self._SSP = None
        self._delta_detector = None

        self.numerical_results_df = pd.DataFrame()
        self.sensors_results_global_df = pd.DataFrame()

        self.numerical_analysis_status = False
        self.check_sensor_flag(None)

    @property
    def SSP(self):
        return self._SSP

    @property
    def delta_detector(self):
        return self._delta_detector

    @property
    def mt(self):
        return self._mission_time

    @property
    def dT(self):
        return self._dT

    @property
    def N(self):
        return self._N

    @property
    def Nth(self):
        return self._Nth

    @property
    def nside(self):
        return self._nside

    @property
    def border_angle(self):
        return self.SSP[0] + self.SSP[1] + self.SSP[4]

    def check_sensor_flag(self, sensor_id):
        """
        Checks if sensor_id is provided and therefore whether the
        calculations should be made for detectors
        """

        if sensor_id is None:
            self._SSP = self.sat.SSP
            self._delta_detector = None
        else:
            self._SSP = self.sat.inst.sensor_SSP(sensor_id)
            self._delta_detector = self.sat.inst.delta_detector

        return 0

    def check_attitude(self):
        """
        Checks if the generated attitude corresponds to the mission
        parameters
        """

        pass

    def check_numerical_analysis(self):
        """
        Checks if the numerical analysis has been performed
        """

        pass

    def update(self, **kwargs):
        """
        Updates Nut class

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

        # update default_options
        self.options.update(kwargs)

        self.sat.update(**kwargs)

        self.check_sensor_flag(None)

        return 0

    def analytical_profile(self,
                           Nr=100,
                           tf=1,
                           quantity="TAT",
                           fig_flag=True,
                           precession='trace',
                           sensor_id=None
                           ):
        """
        Calculates analytically the demanded quantity from the temporal
        analysis for the instrument as a function of the angle regarding the
        precession axis

        Parameters
        ----------
        Nr : int
            Resolution of results
        tf : float
            Total time considered
        quantity : str
            Quantity to be computed
        fig_flag : bool
            If True, figure is returned
        precession : str
            Method to be used to account for precession

        Returns
        -------
        fig : matplotlib figure
            Figure of profile
        T : ndarray (N)
            Results of calculations (profile)
        """
        self.check_sensor_flag(sensor_id=None)

        fig, T = vs.analytical_profile(self.SSP,
                                       Nr,
                                       tf,
                                       quantity,
                                       fig_flag,
                                       precession,
                                       self.delta_detector
                                       )

        return fig, T

    def analytical_map(self,
                       quantity="TAT",
                       fig_flag=True,
                       precession='trace',
                       **kwargs
                       ):
        """
        Calculates analytically the demanded quantity for all the celestial
        sphere and plots it.

        Parameters
        ----------
        SSP : list (5)
            Scan Law Parameters (alpha, beta, spin, precesion, delta)/
            (deg, deg, min, min, deg)
        N : int
            Resolution of results
        tf : float
            Total time considered
        quantity : str
            Quantity to be computed
        fig_flag : bool
            If True, figure is returned
        precession : str
            Method to be used to account for precession
        units : str
            Time units for the output
        cbar_size : float
            Size of the colorbar

        Returns
        -------
        fig : matplotlib figure
            Figure of profile
        data : ndarray (N)
            Results of calculations (value per pixel for Healpix scheme)
        """

        fig, data = vs.analytical_map(self.SSP,
                                      quantity,
                                      self.N,
                                      self.dT,
                                      fig_flag,
                                      precession,
                                      self.delta_detector,
                                      **kwargs
                                      )

        return fig, data

    def generate_attitude(self):
        """
        Emulates satellite attitude motion
        """

        self.sat.generate_attitude(self.mt,
                                   self.dT,
                                   self.sat.q0,
                                   self.SSP
                                   )

        return 0

    def numerical_analysis(self):
        """
        Performs numerical analysis.

        Computes which sensors are viewed and for how long

        This analysis produces two sets of data: sensors_results_global_df and sensors_results_detailed_dict.
        The former stores the Figures of Merit (FOM) of computed for each point in the sky. The second
        stores the FOM of each detectors for each case point in the sky (requires dense=True)
        """

        self.generate_attitude()

        (self.numerical_results_df,
         self.numerical_results_detailed_df) = vs.numerical_analysis(self.sat.inst,
                                                                     self.nside,
                                                                     self.bar,
                                                                     self.detailed,
                                                                     self.dense,
                                                                     self.border_angle
                                                                     )

        self.numerical_analysis_status = True

        return 0

    def numerical_profile(self,
                          quantity="TAT",
                          unit='s',
                          fig_flag=True,
                          sensor_id=None
                          ):
        """
        Calculates analytically the demanded quantity from the temporal
        analysis for the instrument as a function of the angle regarding the
        precession axis

        Parameters
        ----------
        Nr : int
            Resolution of results
        tf : float
            Total time considered
        quantity : str
            Quantity to be computed
        fig_flag : bool
            If True, figure is returned
        precession : str
            Method to be used to account for precession

        Returns
        -------
        fig : matplotlib figure
            Figure of profile
        T : ndarray (N)
            Results of calculations (profile)
        """

        self.check_numerical_analysis()

        fig, T = vs.numerical_profile(self,
                                      quantity,
                                      unit,
                                      self.N,
                                      self.Nth,
                                      fig_flag,
                                      sensor_id
                                      )

        return fig, T

    def numerical_map(self,
                      quantity="TAT",
                      units='s',
                      sensor_id=None,
                      **kwargs
                      ):
        """
        Plot temporal analysis results

        Parameters
        ----------
        map_type : str
            Result to be plotted
        N : int
            Mesh for plotting

        Returns
        -------
        fig :  matplotlib figure
            Plotted figure

        """

        fig, data = vs.numerical_map(self,
                                     quantity,
                                     self.N,
                                     units,
                                     sensor_id,
                                     **kwargs
                                     )

        return fig, data

    def plot_focal_plane(self,
                         cases_dict=None,
                         case_id=None,
                         quantity='Viewed',
                         numbered=False
                         ):
        """
        Plots focal plane results for a given case (pixel in sky)

        Parameters
        ----------
        xd : float
            X coordinates of detectors in focal plane
        yd : float
            Y coordinates of detectors in focal plane
        nd : int
            Number of detectors
        r : float
            Half-angle of the detector fov (degrees)
        cases_dict : dict
            Temporal results for point in the sky
        case_id : str
            Id of case to be plotted
        quantity : str
            Quantity to be shown
        numbered : bool
            If True, sensors Id is plotted

        Returns
        -------
        fig : matplotlib figure
            Figure of profile
        ax : axes
            Matplotlib figure axes of sensor array and FOV
        """

        fig, ax = pg.plot_focal_plane(self.sat.inst.xd,
                                      self.sat.inst.yd,
                                      self.sat.inst.r,
                                      cases_dict,
                                      case_id,
                                      quantity,
                                      numbered
                                      )

        return fig, ax

    def visibility_results(self, quantity, sensor_id):
        """
        Retrieves visibility results and completes them

        Returns
        -------
        visibility_global_results_df : pandas DataFrame
            Results of visibility analysis
        """

        if sensor_id is None:
            if quantity in ['SGA', 'PVS'] and (self.detailed is False):
                raise Exception("Detailed results not present")
            else:
                data = self.numerical_results_df[quantity].values

        else:
            if (self.detailed and self.dense) is False:
                raise Exception("Detailed results not present")

            df = self.numerical_results_detailed_df
            data = df[df['sensor_id'] == sensor_id][quantity].values

        return data
