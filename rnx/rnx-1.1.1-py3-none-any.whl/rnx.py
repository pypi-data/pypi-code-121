"""
Copyright 2022 David Woodburn

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

--------------------------------------------------------------------------------

This library is designed to read version 2.11 RINEX navigation ('N') and
observation ('O') files, specifically for GPS ('G') and mixed ('M') system data.

Reading Data
------------
First import the library::

    import rnx

To read a RINEX file, call the `read` function passing the name of the
navigation or observation file::

    nav = rnx.read("ohdt0710.22n")
    obs = rnx.read("ohdt0710.22o")

The type of file (navigation or observation) is determined automatically by the
first line of the file contents, not by the extension.  You can also read both a
navigation file and its corresponding observation file in one command::

    nav, obs = rnx.read("ohdt0710.22n", "ohdt0710.22o")

This has the added benefit of mapping the ephemeris data from the navigation
object to the corresponding moments in time and space vehicles of the
observation object.  It creates a new attribute in the observation object called
`ephs`.

Navigation Objects
------------------
The navigation object (`nav` in the above examples) has three main attributes:
the array of times of clock `t_oc` in GPS week seconds, the array of PRN numbers
for all GPS space vehicles found in the navigation file, and the matrix of
ephemerides `ephs` corresponding to each pairing of time and PRN.  The
relationship of these three attributes can be visualized as follows::

            .-------------------.
            |    |    |    |    | prns
            '-------------------'
    .----.  .-------------------.
    |    |  |    |    |    |    |
    |----|  |----|----|----|----|
    |    |  |    |    |    |    |
    |----|  |----|----|----|----|
    |    |  |    |    |    |    |
    '----'  '-------------------'
    t_oc                          ephs

Not all elements of the `ephs` matrix are populated.  In such cases, the value
of that element of the matrix is `None`.

Suppose we wish to get the time of clock, the PRN number, and the ephemeris for
the third space vehicle at the first moment in time.  Then we would write ::

    t = nav.t_oc[0]
    prn = nav.prns[2]
    eph = nav.ephs[0, 2]

Then, each ephemeris parameter is an attribute of `eph`.  As an example, if we
wanted the square root of the orbit semi-major axis radius, we would do ::

    eph.sqrtA

The complete set of attributes of `eph` are listed in the `EphG` class.  The
navigation object has an additional property which stores the date and time
stamp of the beginning of the GPS week corresponding to the first record in the
file: `ts_bow`.  So, if we wanted to get the timestamp of the kth moment in
time, we would do ::

    ts = nav.ts_bow + datetime.timedelta(seconds=nav.t_oc[k])

Observation Objects
-------------------
The observation object (`obs` in the opening examples) is organized in a manner
similar to navigation object.  The arrays of receiver times `t` in GPS week
seconds and receiver clock offsets `T_os` have as many elements as there are
rows in the observation matrices and the arrays of space vehicle names `svs`,
system letters `sys`, and space vehicle numbers `prns` have as many elements as
there are columns in the observation matrices::

                  .-------------------.
                  |    |    |    |    | sys
                  :===================:
                  |    |    |    |    | prns
                  :===================:
                  |    |    |    |    | svs
                  '-------------------'
    .----..----.  .-------------------.
    |    ||    |  |    |    |    |    |
    |----||----|  |----|----|----|----|
    |    ||    |  |    |    |    |    |
    |----||----|  |----|----|----|----|
    |    ||    |  |    |    |    |    |
    '----''----'  '-------------------'
    t      T_os                         C1, L2, D5, wf1, ephs, etc.

The `sys` array stores the space vehicle's GNSS system letter (like 'G' for GPS
or 'R' for GLONASS).  The `prns` array stores the space vehicle's PRN number
(like 1 through 32 for GPS).  The `svs` array is the concatenation of the system
letter and the PRN number (like "G05").  You can find the column index of a
space vehicle by name with the `sv_ind` dictionary::

    j = obs.sv_ind["G05"]

Suppose we wish to get the receiver time, the event flag, the PRN number, the
GNSS system letter, and the L1 C/A pseudorange for the fifth space vehicle at
the third moment in time.  Then we would write ::

    t = obs.t[2]
    prn = obs.prns[4]
    sys = obs.sys[4]
    C1 = obs.C1[2, 4]

A RINEX observation file does not necessarily hold every possible type of
observation.  The types are labeled with a letter and a frequency band number.
The possible band numbers are 1, 2, 5, 6, 7, and 8.  The possible letters are ::

    Letter | Meaning           | Units
    ------ | ----------------- | ------
    'C'    | C/A pseudorange   | m
    'P'    | P(Y) pseudorange  | m
    'L'    | Carrier phase     | cycles
    'D'    | Doppler frequency | Hz
    'S'    | Signal strength   | dB-Hz

(The units of signal strength are, in fact, receiver-dependent and might not be
dB-Hz.)  So, to access the C/A pseudorange from the L1 frequency of the jth
space vehicle at the kth moment in time, we would write ::

    rho = obs.C1[k, j]

Observation types which are nowhere defined within the RINEX file will still
exist as attributes of the observation object but will have a value of `None`.

To see if a space vehicle has any observation data at a given moment in time,
we can use the `is_vis` matrix::

    obs.is_vis[k, j]

This is a matrix of Boolean values (`True` or `False`).  Very similar to this,
the `vis_prn` matrix is `NaN` wherever `is_vis` is `False` and is equal to the
PRN of the space vehicle wherever `is_vis` is `True`.  So, we could plot the
visibility of space vehicles by PRN with ::

    import matplotlib.pyplot as plt
    plt.plot(obs.t, obs.vis_prn)

Like with the navigation object, we can get the timestamp of the kth moment in
time by ::

    ts = obs.ts_bow + datetime.timedelta(seconds=obs.t[k])

When a navigation file is read in the same command as an observation file, the
observation object will get an additional attribute called `ephs`.  So, to get
the `C1` pseudorange and corresponding ephemeris for space vehicle `j` at time
`k`, we would write ::

    C1 = obs.C1[k, j]
    eph = obs.ephs[k, j]

Additional attributes are described in the `Obs` class.

Finding Data
------------
Some sites from which RINEX files can be downloaded for free are ::

    https://geodesy.noaa.gov/UFCORS/
    https://gssc.esa.int/portal/
"""

__author__ = "David Woodburn, Ph.D."
__credits__ = []
__license__ = "MIT"
__date__ = "2022-05-26"
__maintainer__ = "David Woodburn"
__email__ = "david.woodburn@icloud.com"
__status__ = "Development"

import datetime
import copy
import os
import numpy as np

# constants (from IS-GPS-200M)
c = 299792458.0             # speed of light [m/s] (p. 98)
F1 = 1575.42e6              # L1 carrier frequency for GPS [Hz] (p. 14)
F2 = 1227.6e6               # L2 carrier frequency for GPS [Hz] (p. 14)
PI = 3.1415926535898        # pi as defined for GPS calculations (p. 109)
W_IE = 7.2921151467e-5      # sidereal Earth rate [rad/s] (p. 106)


class EphG:
    """
    A class for storing the ephemeris data of a GPS space vehicle for a
    particular moment in time.

    Attributes
    ----------
    prn : int
        The pseudorandom noise value.
    t_oc : float
        Time of clock since start of the GPS week [s].
    t_oe : float
        Time of ephemeris since start of the GPS week [s].
    t_sv : float
        Time of transmission since start of the GPS week [s].
    a_f0 : float
        Clock bias correction coefficient [s].
    a_f1 : float
        Clock drift [s/s].
    a_f2 : float
        Clock drift rate [s/s^2].  It is often just zero.
    T_GD : float
        Group delay differential [s].
    T_fit : float, default 14400.0
        Fit interval [s].
    sqrtA : float
        Square root of orbit semi-major axis radius [sqrt(m)].
    M_0 : float
        Mean anomaly at time of ephemeris, `t_oe`, [rad].
    Delta_n : float
        Mean motion correction [rad/s].
    e : float
        Orbit eccentricity [ND].
    omega : float
        Argument of perigee [rad].
    i_0 : float
        Inclination angle at time of ephemeris, `t_oe`, [rad].
    Di : float
        Rate of inclination [rad/s].
    Omega_0 : float
        Longitude of ascending node at the beginning of the GPS week [rad].
    DOmega : float
        Rate of right ascension [rad/s].
    C_uc : float
        Argument of latitude cosine factor [rad].
    C_us : float
        Argument of latitude sine factor [rad].
    C_rc : float
        Orbit radius cosine factor[m].
    C_rs : float
        Orbit radius sine factor[m].
    C_ic : float
        Inclination angle cosine factor [rad].
    C_is : float
        Inclination angle sine factor [rad].
    WN : int
        Week number [wk].
    health : int
        Health flag.
    acc : float
        Accuracy of space vehicle [m].
    IODE : int
        Issue of data, ephemeris [counter].
    IODC : int
        Issue of data, clock [counter].
    cL2 : float
        Codes on L2 channel.
    pL2 : float
        P data flag on L2 channel.
    """

    def __init__(self):
        self.prn = 0                # pseudorandom noise value

        self.t_oc = 0.0             # time of clock since week start [s]
        self.t_oe = 0.0             # time of ephemeris since week start [s]
        self.t_sv = 0.0             # time of transmission since week start [s]
        self.a_f0 = 0.0             # clock bias correction coefficient [s]
        self.a_f1 = 0.0             # clock drift [s/s]
        self.a_f2 = 0.0             # clock drift rate [s/s^2]
        self.T_GD = 0.0             # group delay differential [s]
        self.T_fit = 0.0            # fit interval [s]

        self.sqrtA = 0.0            # sqrt of orbit semi-major axis [sqrt(m)]
        self.M_0 = 0.0              # mean anomaly at t_oe [rad]
        self.Delta_n = 0.0          # mean motion correction [rad/s]
        self.e = 0.0                # orbit eccentricity [ND]
        self.omega = 0.0            # argument of perigee [rad]
        self.i_0 = 0.0              # inclination angle at t_oe [rad]
        self.Di = 0.0               # rate of inclination [rad/s]
        self.Omega_0 = 0.0          # lon. of ascending node at ts_bow [rad]
        self.DOmega = 0.0           # rate of right ascension [rad/s]

        self.C_uc = 0.0             # argument of latitude cosine factor [rad]
        self.C_us = 0.0             # argument of latitude sine factor [rad]
        self.C_rc = 0.0             # orbit radius cosine factor[m]
        self.C_rs = 0.0             # orbit radius sine factor[m]
        self.C_ic = 0.0             # inclination angle cosine factor [rad]
        self.C_is = 0.0             # inclination angle sine factor [rad]

        self.WN = 0                 # week number [wk]
        self.health = 0             # health flag
        self.acc = 0.0              # accuracy of space vehicle [m]

        self.IODE = 0               # issue of data, ephemeris [counter]
        self.IODC = 0               # issue of data, clock [counter]
        self.cL2 = 0.0              # codes on L2 channel
        self.pL2 = 0.0              # P data flag on L2 channel


class NavG:
    """
    Class for creating RINEX (Receiver Independent Exchange Format) GPS
    navigation objects.

    Attributes, metadata
    --------------------
    program : str
        Program that created the file.
    author : str
        Agency that created the file.
    created : str
        Date the file was created.  This is only a string.
    ion_alpha : (4,) float np.ndarray
        Ionosphere parameters A0-A3
    ion_beta : (4,) float np.ndarray
        Ionosphere parameters B0-B3
    UTC_A0 : float
        Constant factor of UTC polynomial [s].
    UTC_A1 : float
        Rate factor of UTC polynomial [s/s].
    UTC_t_ot : int
        Reference time for UTC [s].
    UTC_WN_t : int
        UTC continuous reference week number [week].
    UTC_Dt_LS : int
        UTC delta time due to leap seconds [s].
    ts_bow : datetime.datetime
        Date and timestamp of the beginning of the week relative to the earliest
        observation in the file.
    len : int
        Number of points in time.

    Attributes, arrays
    ------------------
    t_oc : (K,) float np.ndarray
        Array of K time of clock values since beginning of week in seconds.
    prns : (J,) int np.ndarray
        Array of J space vehicle pseudorandom noise values.
    ephs : (K, J) EphG np.ndarray
        A matrix of EphG objects, each storing an ephemeris data set for a
        particular moment in time and space vehicle.  If there is no data for
        the given space vehicle at the given time, the value will be `None`.
    """

    def __init__(self, file_name):
        """
        Read a navigation RINEX file into a NavG object.

        Parameters
        ----------
        file_name : str
            Name of navigation file, including extension.

        Returns
        -------
        self : NavG
            GPS navigation object.
        """

        # function to parse datetime stamp
        def parse_datetime(line):
            """
            Parse the date and time of a GPS navigation epoch.
            """
            year = int(line[3:5])
            year += 2000 if year < 80 else 1900
            t_stamp = datetime.datetime(year,               # year
                    int(line[6:8]),   int(line[9:11]),      # M, d
                    int(line[12:14]), int(line[15:17]),     # h, m
                    int(line[18:20]), int(line[21])*100000) # s, us
            return t_stamp

        def parse_3(line):
            """
            Parse one line into three values.
            """
            if not line[22:41].isspace():
                b = float(f"{line[22:37]}e{line[38:41]}")
            else:
                b = 0.0
            if not line[41:60].isspace():
                c = float(f"{line[41:56]}e{line[57:60]}")
            else:
                c = 0.0
            if not line[60:79].isspace():
                d = float(f"{line[60:75]}e{line[76:79]}")
            else:
                d = 0.0
            return b, c, d

        def parse_4(line):
            """
            Parse one line into four values.
            """
            if not line[3:22].isspace():
                a = float(f"{line[3:18]}e{line[19:22]}")
            else:
                a = 0.0
            b, c, d = parse_3(line)
            return a, b, c, d

        def parse_2(line):
            """
            Parse one line into two values.
            """
            if not line[3:22].isspace():
                a = float(f"{line[3:18]}e{line[19:22]}")
            else:
                a = 0.0
            if not line[22:41].isspace():
                b = float(f"{line[22:37]}e{line[38:41]}")
            else:
                b = 0.0
            return a, b

        # constants
        SPACE_SIZE = 1024

        # states
        STATE_INIT = 0              # initial state
        STATE_HEADER = 1            # looking for header values
        STATE_EPOCH = 2             # after header, expecting new epoch
        STATE_ORBITS = 3            # after header, reading orbital data
        state = STATE_INIT

        # basic metadata
        program = ""                # program that created the file
        author = ""                 # agency that created the file
        created = ""                # date the file was created
        ion_alpha = np.zeros(4)     # ionosphere parameters A0-A3
        ion_beta = np.zeros(4)      # ionosphere parameters B0-B3
        UTC_A0 = 0.0                # constant factor of UTC polynomial [s]
        UTC_A1 = 0.0                # rate factor of UTC polynomial [s/s]
        UTC_t_ot = 0                # reference time for UTC [s]
        UTC_WN_t = 0                # UTC continuous reference week number
        UTC_Dt_LS = 0               # UTC delta time due to leap seconds
        ts_bow = None               # timestamp of beginning of week

        # file-level variables
        n_line = 0                  # RINEX file line number (base 1)
        t_oc = None                 # array of times of ephemeris [s]
        prns = None                 # space vehicle PRN for each epoch
        ephs = None                 # list of EphG objects
        ephs_space = 0              # rows allocated to `ephs` list
        ephs_rows = 0               # rows used in `ephs` list

        # epoch-level variables
        ts_ep = None                # timestamp of an epoch
        orbit_set = 0               # orbital set counter

        # Check the input.
        if not isinstance(file_name, str):
            raise Exception("rnx: file_name must be a string!")
        if not os.path.exists(file_name):
            raise Exception("rnx: could not find file %s!" % (file_name))

        # Open the file.
        file = open(file_name, "r")

        # Read each line of the file.
        for line in file:
            # Increment the RINEX file line number (initialized as 0).
            n_line += 1

            # Remove the newline character and pad with spaces to 80 chars.
            line = line.rstrip().ljust(80)

            # Get the label.
            label = line[60:80]

            # State machine
            if state == STATE_INIT:
                # The first line should be the version and file type.
                if label != "RINEX VERSION / TYPE":
                    raise Exception("rnx: expected version in first line!")

                # RINEX version number
                if float(line[0:9]) != 2.11:
                    raise Exception("rnx: NavG can only process version 2.11!")

                # file-type letter: 'O', 'N', 'M', 'G', 'L', 'H', 'B', 'C', 'S'
                if line[20] != 'N':
                    raise Exception("rnx: NavG can only read navigation files!")

                # Look for header data.
                state = STATE_HEADER
            elif state == STATE_HEADER:
                if label == "PGM / RUN BY / DATE ":
                    # Parse out the program, author, and date created.
                    program = line[0:20].strip()
                    author = line[20:40].strip()
                    created = line[40:60].strip()

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "ION ALPHA           ":
                    # Parse out the ionosphere parameters A0-A3.
                    ion_alpha[0] = float(f"{line[2:10]}e{line[11:14]}")
                    ion_alpha[1] = float(f"{line[14:22]}e{line[23:26]}")
                    ion_alpha[2] = float(f"{line[26:34]}e{line[35:38]}")
                    ion_alpha[3] = float(f"{line[38:46]}e{line[47:50]}")

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "ION BETA            ":
                    # Parse out the ionosphere parameters B0-B3.
                    ion_beta[0] = float(f"{line[2:10]}e{line[11:14]}")
                    ion_beta[1] = float(f"{line[14:22]}e{line[23:26]}")
                    ion_beta[2] = float(f"{line[26:34]}e{line[35:38]}")
                    ion_beta[3] = float(f"{line[38:46]}e{line[47:50]}")

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "DELTA-UTC: A0,A1,T,W":
                    # Parse out UTC calculation parameters.
                    UTC_A0 = float(f"{line[3:18]}e{line[19:22]}")
                    UTC_A1 = float(f"{line[22:37]}e{line[38:41]}")
                    UTC_t_ot = int(line[41:50])
                    UTC_WN_t = int(line[50:59])

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "LEAP SECONDS        ":
                    # Get the UTC delta time due to leap seconds.
                    UTC_Dt_LS = int(line[0:6])

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "END OF HEADER       ":
                    # Initialize file-level storage.
                    t_oc = np.zeros(SPACE_SIZE, dtype=float)
                    prns = np.zeros(SPACE_SIZE, dtype=int)
                    ephs = [None]*SPACE_SIZE
                    ephs_space = SPACE_SIZE

                    # Start looking for the first epoch.
                    state = STATE_EPOCH
                else:
                    # Continue in the header.
                    state = STATE_HEADER
            elif state == STATE_EPOCH:
                # Create new ephemeris object.
                eph = EphG()

                # pseudorandom noise value and timestamp of epoch (clock)
                eph.prn = int(line[0:3])
                ts_ep = parse_datetime(line)

                # Get the timestamp of the beginning of the week.
                if ts_bow is None:
                    day_of_week = ts_ep.isoweekday() % 7
                    ts_bow = ts_ep - datetime.timedelta(days=day_of_week)
                    ts_bow = ts_bow.replace(hour=0, minute=0, second=0,
                            microsecond=0)

                # Get the time of clock relative to start of week.
                eph.t_oc = (ts_ep - ts_bow).total_seconds()

                # Read clock bias, drift, and drift rate.
                eph.a_f0, eph.a_f1, eph.a_f2 = parse_3(line)

                # Continue reading orbit data.
                state = STATE_ORBITS
            elif state == STATE_ORBITS:
                # Parse the numbers depending on the orbital set counter.
                orbit_set += 1
                if orbit_set == 1:
                    IODE, eph.C_rs, eph.Delta_n, eph.M_0 = parse_4(line)
                    eph.IODE = int(IODE)
                elif orbit_set == 2:
                    eph.C_uc, eph.e, eph.C_us, eph.sqrtA = parse_4(line)
                elif orbit_set == 3:
                    eph.t_oe, eph.C_ic, eph.Omega_0, eph.C_is = parse_4(line)
                elif orbit_set == 4:
                    eph.i_0, eph.C_rc, eph.omega, eph.DOmega = parse_4(line)
                elif orbit_set == 5:
                    eph.Di, eph.cL2, WN, eph.pL2 = parse_4(line)
                    eph.WN = int(WN)
                elif orbit_set == 6:
                    eph.acc, health, eph.T_GD, IODC = parse_4(line)
                    eph.health = int(health)
                    eph.IODC = int(IODC)
                elif orbit_set == 7:
                    eph.t_sv, T_fit = parse_2(line)
                    # Scale hours to seconds and default to four hours.
                    eph.T_fit = 3600.0*T_fit if T_fit > 0.0 else 4*3600.0

                    # Add rows to the list space if needed.
                    if ephs_rows + 1 >= ephs_space:
                        t_oc = np.concatenate((t_oc,
                                np.zeros(SPACE_SIZE, dtype=float)))
                        prns = np.concatenate((prns,
                                np.zeros(SPACE_SIZE, dtype=int)))
                        ephs.extend([None]*SPACE_SIZE)
                        ephs_space += SPACE_SIZE

                    # Store data from this epoch and PRN.
                    t_oc[ephs_rows] = eph.t_oc
                    prns[ephs_rows] = eph.prn
                    ephs[ephs_rows] = copy.copy(eph)
                    ephs_rows += 1

                    # Reset the orbital set counter.
                    orbit_set = 0
                    state = STATE_EPOCH

        # Close the file.
        file.close()

        # Drop the extra space.
        t_oc = t_oc[:ephs_rows]
        prns = prns[:ephs_rows]
        ephs = ephs[:ephs_rows]

        # Find the unique moments in time and the unique PRNs.  `kk` and `jj`
        # are the arrays of "indices to reconstruct the original array from the
        # unique array".
        t_oc, kk = np.unique(t_oc, return_inverse=True)
        prns, jj = np.unique(prns, return_inverse=True)
        K = len(t_oc)
        J = len(prns)

        # Convert list of ephemerides to matrix.
        ephs_mat = np.empty((K, J), dtype=EphG)
        ephs_mat[kk, jj] = ephs

        # Save metadata attributes.
        self.program = program
        self.author = author
        self.created = created
        self.ion_alpha = ion_alpha.copy()
        self.ion_beta = ion_beta.copy()
        self.UTC_A0 = UTC_A0
        self.UTC_A1 = UTC_A1
        self.UTC_t_ot = UTC_t_ot
        self.UTC_WN_t = UTC_WN_t
        self.UTC_Dt_LS = UTC_Dt_LS
        self.ts_bow = ts_bow
        self.len = len(t_oc)

        # Save array attributes.
        self.t_oc = t_oc.copy()
        self.prns = prns.copy()
        self.ephs = ephs_mat.copy()


class Obs:
    """
    Class for creating RINEX (Receiver Independent Exchange Format) observation
    objects.

    Attributes, metadata
    --------------------
    system : str
        The GNSS system letter: ' ', 'G', 'R', 'S', 'E', or 'M'.
    program : str
        Program that created the file.
    author : str
        Agency that created the file.
    created : str
        Date the file was created.  This is only a string.
    marker : str
        The name of the antenna marker.
    observer : str
        Name of observing person.
    agency : str
        Name of observing agency.
    rec_number : str
        Receiver serial number.
    rec_type : str
        Receiver type.
    rec_version : str
        Receiver version.
    ant_number : str
        Antenna number.
    ant_type : str
        Antenna type.
    pos : (3,) float np.ndarray
        ECEF receiver position coordinates from the RINEX file.
    tz_approx : int
        Approximate time zone offset based only on the longitude [hr].
    ant_height : float
        Height of antenna bottom above marker in meters.
    ant_east_ecc : float
        East eccentricitiy of antenna from marker in meters.
    ant_north_ecc : float
        North eccentricitiy of antenna from marker in meters.
    ts_bow : datetime.datetime
        Date and timestamp of the beginning of the week based on the earliest
        observation in the file.
    len : int
        Number of points in time (i.e., epochs).

    Attributes, arrays
    ------------------
    types : (I,) str np.ndarray
        Observation type names (e.g., "L1", "C5", "S2", etc.) with actual data.
        This is not always everything specified in the header.
    t : (K,) float np.ndarray
        Receiver time values since beginning of GPS week in seconds, with tenth
        of a microsecond precision.
    T_os : (K,) float np.ndarray
        Receiver clock offsets in seconds, with nanosecond precision.
    sys : (J,) str np.ndarray
        Space vehicle system letters: 'G' for GPS, 'R' for GLONASS, and 'E' for
        Galileo.
    prns : (J,) int np.ndarray
        Space vehicle pseudorandom noise values starting from 1.
    svs : (J,) str np.ndarray
        Space vehicle names: the system letters (`sys`) with their pseudorandom
        noise values (`prns`).
    sv_ind : (J,) int dict
        Dictionary of space vehicles.  The keys are the space vehicle names
        (`svs`) and the values are the column indices to the observation
        matrices (L1, C5, S2, etc.).
    n_E : (N,) int np.ndarray
        Array of column indices to the observation matrices, which columns
        correspond to the Galileo system space vehicles.  If none of the space
        vehicles are part of this system, then the array will be empty.
    n_G : (N,) int np.ndarray
        Array of column indices to the observation matrices, which columns
        correspond to the GPS system space vehicles.  If none of the space
        vehicles are part of this system, then the array will be empty.
    n_R : (N,) int np.ndarray
        Array of column indices to the observation matrices, which columns
        correspond to the GLONASS system space vehicles.  If none of the space
        vehicles are part of this system, then the array will be empty.
    n_S : (N,) int np.ndarray
        Array of column indices to the observation matrices, which columns
        correspond to the geostationary system space vehicles.  If none of the
        space vehicles are part of this system, then the array will be empty.
    is_vis : (K, J) bool np.ndarray FIXME test
        Matrix of Boolean values indicating the visibility of the space vehicles
        with a row for each of the `K` moments in time and a column for each of
        the `J` space vehicles found in the file.
    vis_prn : (K, J) float np.ndarray
        Matrix of floats.  Where the given space vehicle (column) at the given
        moment in time (row) has any observation data, the PRN of the space
        vehicle as a float is provided.  Where the space vehicle has no data,
        NAN is provided.
    wf1 : (K, J) int np.ndarray
        Waveform factor for L1 carrier-phase measurements with a row for each of
        the `K` moments in time and a column for each of the `J` space vehicles
        found in the file.
    wf2 : (K, J) int np.ndarray
        Waveform factor for L2 carrier-phase measurements with a row for each of
        the `K` moments in time and a column for each of the `J` space vehicles
        found in the file.
    Ax : (K, J) float np.ndarray
        Possible matrix of obervation values, with a row for each of the `K`
        moments in time and a column for each of the `J` space vehicles found in
        the file.  The `A` is the observation type and can be 'C' for C/A
        pseudoranges in meters, 'P' for P(Y) pseudoranges in meters, 'L' for
        carrier phase in cycles, 'D' for Doppler frequency in hertz, or 'S' for
        signal strength (likely in dB-Hz, but ultimately receiver-dependent).
        The `x` is the frequency band (one of 1, 2, 5, 6, 7, or 8).  So,
        altogether, `Ax` could be something like 'C1', 'L1', or 'P2'.
    Ax_LLI : (K, J) int np.ndarray
        Possible matrix of loss of lock indicators (0 to 7), with a row for each
        of the `K` moments in time and a column for each of the `J` space
        vehicles found in the file.  The `A` and `x` have the same meaning as in
        the `Ax` attributes.
    Ax_SSI : (K, J) int np.ndarray
        Possible matrix of signal strength integers (0 to 9), with a row for
        each of the `K` moments in time and a column for each of the `J` space
        vehicles found in the file.  The `A` and `x` have the same meaning as in
        the `Ax` attributes.

    Attributes, event flags
    -----------------------
    t_events : (M,) float np.ndarray
        Receiver time values since beginning of GPS week in seconds at event
        flags, with tenth of a microsecond precision.  This is not necessarily
        the same length as the `t` array.
    events : (M,) int np.ndarray
        Event flags (integers from 0 to 6).  This is not necessarily the same
        length as the `t` array.

    Notes
    -----
    Sometimes observation types claimed in a header have no actual data anywhere
    in the RINEX file.  The attributes for such observation types are defined as
    `None` and no entry is made for them in the `types` array.

    The `t_events` and `events` arrays are not the same lengths as the other
    time array because events do not necessarily happen when observations do.
    Forcing these arrays to all be the same length would require that the
    observation matrices would sometimes have whole rows of NANs.  Also, events
    do not happen all the time.  Note, not all events come with the time of the
    event recorded.  In such cases, this library uses the most recently declared
    time.

    Todo
    ----
    -   Add loss of lock indicator data.
    -   Add signal strength integer data.
    """

    def __init__(self, file_name):
        """
        Read an observation RINEX file into an Obs object.

        Parameters
        ----------
        file_name : str
            Name of observation file, including extension.

        Returns
        -------
        self : Obs
            Observation object.
        """

        # constants
        SPACE_SIZE = 1024
        FILLER = np.nan

        # states
        STATE_INIT = 0              # initial state
        STATE_HEADER = 1            # looking for header values
        STATE_TYPES = 2             # expecting more observation types
        STATE_EPOCH = 3             # after header, expecting new epoch
        STATE_PRNS = 4              # expecting more PRNs
        STATE_OBS = 5               # expecting observations in epoch
        STATE_SPECIAL = 6           # expecting non-observation data
        state = STATE_INIT          # state variable

        # basic metadata
        system = ''                 # ' ', 'G', 'R', 'S', 'E', or 'M'
        program = ""                # program that created the file
        author = ""                 # agency that created the file
        created = ""                # date the file was created
        marker = ""                 # marker name
        observer = ""               # name of observing person
        agency = ""                 # name of observing agency
        rec_number = ""             # receiver serial number
        rec_type = ""               # receiver type
        rec_version = ""            # receiver version
        ant_number = ""             # antenna number
        ant_type = ""               # antenna type
        pos = np.zeros(3)           # calculated ECEF position of receiver
        tz_approx = 0.0             # approximate time zone offset [hr]
        ant_height = 0.0            # height of antenna bottom above marker
        ant_east_ecc = 0.0          # east eccentricitiy of antenna from marker
        ant_north_ecc = 0.0         # north eccentricitiy of antenna from marker
        ts_bow = None               # timestamp of beginning of week

        # file-level variables
        types_list = None           # array of observation types: "L1", etc.
        types_cnt = 0               # number of observation types in file
        types_left = 0              # observation types left for an epoch
        t_rx = None                 # receiver times of week [s] for each epoch
        T_os = None                 # receiver clock offsets [s] for each epoch
        t_events = []               # receiver times of week [s] at event > 0
        events = []                 # list of event flags
        svs = None                  # space vehicle labels for each epoch
        wf1 = None                  # wavelength factors for any L1 signal
        wf2 = None                  # wavelength factors for any L2 signal
        obs = None                  # matrix of observations
        LLI = None                  # matrix of loss of lock indicators
        SSI = None                  # matrix of signal strength integers
        obs_space = 0               # rows allocated to `obs` matrix
        obs_rows = 0                # rows used in `obs` matrix
        records_left = 0            # special records left in epoch
        n_line = 0                  # RINEX file line number (base 1)

        # epoch-level variables
        t_rx_epoch = 0.0            # receiver time of week [s]
        T_os_ep = 0.0               # receiver clock offset [s]
        event_ep = 0                # the epoch flag (integer from 0 to 6)
        svs_ep_list = [0]*99        # list of space vehicles in epoch
        svs_ep_cnt = 0              # number of space vehicles in epoch
        svs_ep_left = 0             # space vehicles left to read in epoch
        obs_ep_list = [0]*26*98     # list of observations in epoch
        LLI_ep_list = [0]*26*98     # list of loss of lock indicators
        SSI_ep_list = [0]*26*98     # list of signal strength integers
        obs_ep_cnt = 0              # number of observations in epoch
        obs_ep_left = 0             # observations left in epoch
        wf1_ep = np.ones(98)        # template wavelength factors for GPS L1
        wf2_ep = np.ones(98)        # template wavelength factors for GPS L2

        # ---------------------------
        # Read in and parse the data.
        # ---------------------------

        # Check the input.
        if not isinstance(file_name, str):
            raise Exception("rnx: file_name must be a string!")
        if not os.path.exists(file_name):
            raise Exception("rnx: could not find file %s!" % (file_name))

        # Open the file.
        file = open(file_name, "r")

        # For each line of the file,
        for line in file:
            # Increment the RINEX file line number (initialized as 0).
            n_line += 1

            # Remove the newline character and pad with spaces to 80 chars.
            line = line.rstrip().ljust(80)

            # Get the label.
            label = line[60:80]

            # State machine
            if state == STATE_INIT:
                # The first line should be the version and file type.
                if label != "RINEX VERSION / TYPE":
                    raise Exception("rnx: expected version in first line!")

                # RINEX version number
                if float(line[0:9]) != 2.11:
                    raise Exception("rnx: Obs can only process version 2.11!")

                # file-type letter: 'O', 'N', 'M', 'G', 'L', 'H', 'B', 'C', 'S'
                if line[20] != 'O':
                    raise Exception("rnx: Obs can only read observation files!")

                # system letter: ' ', 'G', 'R', 'S', 'E', or 'M'
                system = line[40]
                if (system != ' ') and (system != 'G') and (system != 'M'):
                    raise Exception("rnx: system must be 'G' or 'M'!")

                # Look for header data.
                state = STATE_HEADER
            elif state == STATE_HEADER:
                if label == "PGM / RUN BY / DATE ":
                    # Parse out the program, author, and date created.
                    program = line[0:20].strip()
                    author = line[20:40].strip()
                    created = line[40:60].strip()

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "MARKER NAME         ":
                    # Get the marker name.
                    marker = line[0:60].strip()

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "OBSERVER / AGENCY   ":
                    # Parse out the observer and agency.
                    observer = line[0:20].strip()
                    agency = line[20:60].strip()

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "REC # / TYPE / VERS ":
                    # Parse out the receiver serial number, type, and version.
                    rec_number = line[0:20].strip()
                    rec_type = line[20:40].strip()
                    rec_version = line[40:60].strip()

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "ANT # / TYPE        ":
                    # Parse out the receiver serial number, type, and version.
                    ant_number = line[0:20].strip()
                    ant_type = line[20:40].strip()

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "APPROX POSITION XYZ ":
                    # Save the approximate receiver position.
                    pos[0] = float(line[0:14])
                    pos[1] = float(line[14:28])
                    pos[2] = float(line[28:42])

                    # Get the approximate time zone offset from longitude.
                    tz_approx = round(np.arctan2(pos[1], pos[0])*12/np.pi)

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "ANTENNA: DELTA H/E/N":
                    # Parse out the antenna height and eccentricities.
                    ant_height = float(line[0:14])
                    ant_east_ecc = float(line[14:28])
                    ant_north_ecc = float(line[28:42])

                    # Continue in the header.
                    state = STATE_HEADER
                elif label == "WAVELENGTH FACT L1/2":
                    # Get the integers.
                    k1 = 0 if line[0:6].isspace() else int(line[0:6])
                    k2 = 0 if line[6:12].isspace() else int(line[6:12])
                    k3 = 0 if line[12:18].isspace() else int(line[12:18])

                    # General GPS wavelength factor setting.
                    if k3 == 0:
                        wf1_ep[:] = k1
                        wf2_ep[:] = k2

                    # For each GPS prn listed,
                    for j in range(k3):
                        # Get the starting index of this prn.
                        m = 21 + 6*j

                        # This should only be a GPS space vehicle.
                        if line[m] != 'G':
                            raise Exception("rnx: attempted wavelength " +
                                    "factor for non-GPS space vehicle!  " +
                                    "line %d" % (n_line))

                        # Store these wavelength factors.
                        prn = int(line[(m + 1):(m + 3)])
                        wf1_ep[prn - 1] = k1
                        wf2_ep[prn - 1] = k2

                    # Continue looking for header data.
                    state = STATE_HEADER
                elif label == "# / TYPES OF OBSERV ":
                    # Check if this was already defined.
                    if types_cnt != 0:
                        raise Exception("rnx: observations over-defined!" +
                                "  line %d" % (n_line))

                    # Read the observation types.
                    types_cnt = int(line[0:6])
                    types_left = types_cnt
                    types_list = np.empty(types_cnt, dtype="U2")
                    J = types_cnt if types_cnt < 9 else 9
                    for j in range(J):
                        m = 10 + 6*j
                        types_list[j] = line[m:(m + 2)]
                        types_left -= 1

                    # Initialize file-level storage.
                    t_rx = np.zeros(SPACE_SIZE, dtype=float)
                    T_os = np.zeros(SPACE_SIZE, dtype=float)
                    svs = np.empty(SPACE_SIZE, dtype="U3")
                    wf1 = np.ones(SPACE_SIZE, dtype=int)
                    wf2 = np.ones(SPACE_SIZE, dtype=int)
                    obs = np.full((SPACE_SIZE, types_cnt), FILLER)
                    LLI = np.zeros((SPACE_SIZE, types_cnt), dtype=int)
                    SSI = np.zeros((SPACE_SIZE, types_cnt), dtype=int)
                    obs_space = SPACE_SIZE

                    # Decide if more observation type labels need to be read.
                    state = STATE_HEADER if types_left == 0 else STATE_TYPES
                elif label == "TIME OF FIRST OBS   ":
                    # Get the timestamp of the beginning of the week.
                    t_start = datetime.datetime(
                            int(line[2:6]), int(line[10:12]),   # year, month
                            int(line[16:18]), int(line[22:24]), # day, hour
                            int(line[28:30]), int(line[30:35]), # minute, sec.
                            int(line[36:42]))                   # microsecond
                    day_of_week = t_start.isoweekday() % 7
                    ts_bow = t_start - datetime.timedelta(days=day_of_week)
                    ts_bow = ts_bow.replace(hour=0, minute=0, second=0,
                            microsecond=0)

                    # Continue looking for header data.
                    state = STATE_HEADER
                elif label == "END OF HEADER       ":
                    # Start looking for the first epoch.
                    state = STATE_EPOCH
                else:
                    # Continue looking for header data.
                    state = STATE_HEADER
            elif state == STATE_TYPES:
                # Read more observation type labels.
                J = types_left if types_left < 9 else 9
                for j in range(J):
                    m = 10 + 6*j
                    n_type = types_cnt - types_left
                    types_list[n_type] = line[m:(m + 2)]
                    types_left -= 1

                # Decide if more observation type labels need to be read.
                state = STATE_HEADER if types_left == 0 else STATE_TYPES
            elif state == STATE_EPOCH:
                # Read the date and time and convert to time of week.
                if not line[1:3].isspace():
                    year = int(line[1:3])
                    year += 2000 if year < 80 else 1900
                    ts_ep = datetime.datetime(year,             # year
                            int(line[4:6]),   int(line[7:9]),   # M, d
                            int(line[10:12]), int(line[13:15]), # h, m
                            int(line[15:18]), int(line[19:25])) # s, us
                    # The total_seconds method returns a floating-point value
                    # including microsecond precision.
                    t_rx_epoch = (ts_ep - ts_bow).total_seconds()
                    # Add on fraction of a microsecond.
                    t_rx_epoch += float(line[25])*1e-10

                # Get the event flag (integer from 0 to 6).
                event_ep = 0 if line[28] == ' ' else int(line[28])

                # Get the number of space vehicles (or special records).
                svs_ep_cnt = 0 if line[29:32].isspace() else int(line[29:32])
                svs_ep_left = svs_ep_cnt

                # Log events other than 0.
                if event_ep > 0:
                    t_events.append(t_rx_epoch)
                    events.append(event_ep)

                # Stop processing line if event flag is over 1.
                if event_ep > 1:
                    records_left = svs_ep_cnt
                    if records_left > 0:
                        state = STATE_SPECIAL
                    continue

                # Read the space vehicle PRNs.
                J = svs_ep_cnt if svs_ep_cnt < 12 else 12
                for j in range(J):
                    m = 32 + 3*j
                    sys_letter = 'G' if line[m] == ' ' else line[m]
                    svs_ep_list[j] = f"{sys_letter}{line[(m + 1):(m + 3)]}"
                    svs_ep_left -= 1

                # Receiver clock offset [s]
                T_os_ep = 0.0 if line[68:80].isspace() else float(line[68:80])

                # Prepare for reading observations.
                obs_ep_cnt = svs_ep_cnt*types_cnt
                obs_ep_left = obs_ep_cnt

                # Decide if more space vehicle PRNs need to be read.
                state = STATE_OBS if svs_ep_left == 0 else STATE_PRNS
            elif state == STATE_PRNS:
                # Read more space vehicle PRNs.
                J = svs_ep_left if svs_ep_left < 12 else 12
                for j in range(J):
                    m = 32 + 3*j
                    n_sv = svs_ep_cnt - svs_ep_left
                    sys_letter = 'G' if line[m] == ' ' else line[m]
                    svs_ep_list[n_sv] = f"{sys_letter}{line[(m + 1):(m + 3)]}"
                    svs_ep_left -= 1

                # Decide if more space vehicle PRNs need to be read.
                state = STATE_OBS if svs_ep_left == 0 else STATE_PRNS
            elif state == STATE_OBS:
                # Read the observations.
                J = obs_ep_left if obs_ep_left < 5 else 5
                for j in range(J):
                    m = 16*j
                    n_obs = obs_ep_cnt - obs_ep_left
                    obs_str = line[m:(m + 14)]
                    obs_ep_list[n_obs] = FILLER if obs_str.isspace() or \
                        float(obs_str) == 0.0 else float(obs_str)
                    LLI_ep_list[n_obs] = 0 if line[m + 14] == ' ' \
                        else int(line[m + 14])
                    SSI_ep_list[n_obs] = 0 if line[m + 15] == ' ' \
                        else int(line[m + 15])
                    obs_ep_left -= 1

                    # Break early.  Observations for a space vehicle start on a
                    # new line.
                    if (obs_ep_cnt - obs_ep_left) % types_cnt == 0:
                        break

                # If more observations need to be read, go to next line.
                if obs_ep_left > 0:
                    state = STATE_OBS
                    continue

                # Add space to the file-level storage if needed.
                if obs_rows + svs_ep_cnt >= obs_space:
                    t_rx = np.concatenate((t_rx,
                            np.zeros(SPACE_SIZE, dtype=float)))
                    T_os = np.concatenate((T_os,
                            np.zeros(SPACE_SIZE, dtype=float)))
                    svs = np.concatenate((svs,
                            np.empty(SPACE_SIZE, dtype="U3")))
                    wf1 = np.concatenate((wf1,
                            np.ones(SPACE_SIZE, dtype=int)))
                    wf2 = np.concatenate((wf2,
                            np.ones(SPACE_SIZE, dtype=int)))
                    obs = np.vstack((obs,
                            np.full((SPACE_SIZE, types_cnt), FILLER)))
                    LLI = np.vstack((LLI,
                            np.zeros((SPACE_SIZE, types_cnt), dtype=int)))
                    SSI = np.vstack((SSI,
                            np.zeros((SPACE_SIZE, types_cnt), dtype=int)))
                    obs_space += SPACE_SIZE

                # Store the time, space vehicle label, and observations.
                ma = 0         # starting observation index for SV
                mb = types_cnt # ending observation index for SV
                for n_sv in range(svs_ep_cnt):
                    t_rx[obs_rows] = t_rx_epoch
                    T_os[obs_rows] = T_os_ep
                    svs[obs_rows] = svs_ep_list[n_sv]
                    if svs_ep_list[n_sv][0] == 'G':
                        prn = int(svs_ep_list[n_sv][1:3])
                        wf1[obs_rows] = wf1_ep[prn - 1]
                        wf2[obs_rows] = wf2_ep[prn - 1]
                    obs[obs_rows, :] = obs_ep_list[ma:mb]
                    LLI[obs_rows, :] = LLI_ep_list[ma:mb]
                    SSI[obs_rows, :] = SSI_ep_list[ma:mb]
                    obs_rows += 1
                    ma = mb
                    mb += types_cnt

                # Resume looking for a new epoch.
                state = STATE_EPOCH
            elif state == STATE_SPECIAL:
                if label == "WAVELENGTH FACT L1/2":
                    # Get the integers.
                    k1 = 0 if line[0:6].isspace() else int(line[0:6])
                    k2 = 0 if line[6:12].isspace() else int(line[6:12])
                    k3 = 0 if line[12:18].isspace() else int(line[12:18])

                    # General GPS wavelength factor setting.
                    if k3 == 0:
                        wf1_ep[:] = k1
                        wf2_ep[:] = k2

                    # For each GPS prn listed,
                    for j in range(k3):
                        # Get the starting index of this prn.
                        m = 21 + 6*j

                        # This should only be a GPS space vehicle.
                        if line[m] != 'G':
                            raise Exception("rnx: attempted wavelength " +
                                    "factor for non-GPS space vehicle!  " +
                                    "line %d" % (n_line))

                        # Store these wavelength factors.
                        prn = int(line[(m + 1):(m + 3)])
                        wf1_ep[prn - 1] = k1
                        wf2_ep[prn - 1] = k2

                # Count down the number of special records left.
                records_left -= 1

                # Decide if more special records need to be read.
                state = STATE_EPOCH if records_left == 0 else STATE_SPECIAL

        # Close the file.
        file.close()

        # ----------------------
        # Post-process the data.
        # ----------------------

        # Drop the extra space.
        t_rx = t_rx[:obs_rows]
        T_os = T_os[:obs_rows]
        svs = svs[:obs_rows]
        wf1 = wf1[:obs_rows]
        wf2 = wf2[:obs_rows]
        obs = obs[:obs_rows, :]
        LLI = LLI[:obs_rows, :]
        SSI = SSI[:obs_rows, :]

        # Remove unused observation types (i.e., columns of `obs`).
        n_col_keep = ~np.all(np.isnan(obs), axis=0)
        obs = obs[:, n_col_keep]
        LLI = LLI[:, n_col_keep]
        SSI = SSI[:, n_col_keep]
        types_list = types_list[n_col_keep]
        types_cnt = len(types_list)

        # Find the unique moments in time and the unique space vehicles.  `ii`
        # is the array of "indices of the first occurrences of the unique values
        # in the original array".  `kk` and `jj` are the arrays of "indices to
        # reconstruct the original array from the unique array".
        t_rx, ii, kk = np.unique(t_rx, return_index=True, return_inverse=True)
        svs, jj = np.unique(svs, return_inverse=True)
        K = len(t_rx)   # number of unique moments in time
        J = len(svs) # number of unique space vehicles

        # Keep only one clock offset per moment in time.
        T_os = T_os[ii]

        # Build the space vehicle dictionary.
        sv_ind = dict((svs[j], j) for j in range(J))

        # Parse the `svs` array into the system letter and pseudorandom noise.
        sys = np.array([sv[0] for sv in svs], dtype="U1")
        prns = np.array([int(sv[1:]) for sv in svs], dtype=int)

        # Reshape the wavelength factors.
        wf1_mat = np.ones((K, J))
        wf1_mat[kk, jj] = wf1[:]
        wf2_mat = np.ones((K, J))
        wf2_mat[kk, jj] = wf2[:]

        # Define observation, signal strength integer, and loss of lock
        # indicator attributes.  Build the visibility matrix.
        is_vis = np.full((K, J), False)
        for n_type in range(types_cnt):
            obs_mat = np.full((K, J), FILLER)
            obs_mat[kk, jj] = obs[:, n_type]
            is_vis += ~np.isnan(obs_mat)
            setattr(self, types_list[n_type], obs_mat.copy())
            LLI_mat = np.zeros((K, J), dtype=int)
            LLI_mat[kk, jj] = LLI[:, n_type]
            setattr(self, f"{types_list[n_type]}_LLI", LLI_mat.copy())
            SSI_mat = np.zeros((K, J), dtype=int)
            SSI_mat[kk, jj] = SSI[:, n_type]
            setattr(self, f"{types_list[n_type]}_SSI", SSI_mat.copy())

        # Define unused observation attributes as `None`.
        all_types = ["C1", "D1", "L1", "S1", "C2", "D2", "L2", "S2",
                "C5", "D5", "L5", "S5", "C6", "D6", "L6", "S6",
                "C7", "D7", "L7", "S7", "C8", "D8", "L8", "S8", "P1", "P2"]
        for type_str in all_types:
            if not hasattr(self, type_str):
                setattr(self, type_str, None)
                setattr(self, f"{type_str}_LLI", None)
                setattr(self, f"{type_str}_SSI", None)

        # Build the prn visibility matrix.  It is the same as the visibility
        # matrix, except that instead of `False` it has FILLER, and instead of
        # `True` it has the space vehicle's number.
        vis_prn = np.full((K, J), FILLER)
        for j in range(J):
            vis_prn[is_vis[:, j], j] = float(prns[j])

        # Save metadata attributes.
        self.system = system
        self.program = program
        self.author = author
        self.created = created
        self.marker = marker
        self.observer = observer
        self.agency = agency
        self.rec_number = rec_number
        self.rec_type = rec_type
        self.rec_version = rec_version
        self.ant_number = ant_number
        self.ant_type = ant_type
        self.pos = pos.copy()
        self.tz_approx = tz_approx
        self.ant_height = ant_height
        self.ant_east_ecc = ant_east_ecc
        self.ant_north_ecc = ant_north_ecc
        self.ts_bow = ts_bow
        self.len = len(t_rx)

        # Save array attributes.
        self.types = types_list.copy()
        self.t = t_rx.copy()
        self.T_os = T_os.copy()
        self.sys = sys.copy()
        self.prns = prns.copy()
        self.svs = svs.copy()
        self.sv_ind = sv_ind.copy()
        self.n_E = np.nonzero(sys == 'E')[0].copy()
        self.n_G = np.nonzero(sys == 'G')[0].copy()
        self.n_R = np.nonzero(sys == 'R')[0].copy()
        self.n_S = np.nonzero(sys == 'S')[0].copy()
        self.is_vis = is_vis.copy()
        self.vis_prn = vis_prn.copy()
        self.wf1 = wf1_mat.copy()
        self.wf2 = wf2_mat.copy()
        self.t_events = np.array(t_events, dtype=float).copy()
        self.events = np.array(events, dtype=int).copy()


def read(file_one, file_two=None, file_ref=None):
    """
    Read in RINEX data.

    Parameters
    ----------
    file_one : str
        Name of first RINEX file.  Can be a navigation or an observation file.
    file_two : str, default None
        Name of second RINEX file.  Can be a navigation or an observation file.
    file_ref : str, default None
        Name of reference RINEX observation file.

    Returns
    -------
    NavG or Obs objects corresponding to the order of the file names.
    """

    def get_file_type(file_name):
        """
        Open the RINEX file by name `file_name` and check the file type from the
        first line.  Options include ::

            O: Observation file
            N: GPS Navigation file
            M: Meteorological data file
            G: GLONASS Navigation file
            L: Future Galileo Navigation file
            H: Geostationary GPS payload nav mess file
            B: Geo SBAS broadcast data file
            C: Clock file
            S: Summary file (used e.g., by IGS, not a standard!)

        Returns
        -------
        file_type : str
            Letter of the file type.
        """

        file = open(file_name, "r")
        line = file.readline()
        line = line.rstrip().ljust(80)
        file.close()

        if line[60:80] != "RINEX VERSION / TYPE":
            raise Exception("rnx: expected version in first line!")
        file_type = line[20]

        return file_type

    def map_nav_to_obs(nav, obs):
        """
        Map the EphG navigation objects to the correct observations.  This
        function adds the attribute `ephs` to the Obs object.  An ephemeris fits
        the time period defined by the time of ephemeris, `t_oe`, +/- half of
        the fit interval, `T_fit`.  The closer ephemeris will be applied to the
        given space vehicle for the given observation time.  If no matching
        ephemeris data exists, the corresponding element of the `ephs` property
        matrix will be `None`.  The `ephs` matrix will have the same dimensions
        as any of the observation type matrices (e.g., C1, L1, P2, etc.).

        Parameters
        ----------
        nav : NavG
            GPS navigation object.
        obs : Obs
            Observation object.
        """

        # Get the times from the NavG and Obs objects.
        t_oc = nav.t_oc.copy()
        t_rx = obs.t

        # Shift the copy of nav times if nav and obs do not share the same
        # beginning of week timestamp.
        if nav.ts_bow != obs.ts_bow:
            t_oc += (nav.ts_bow - obs.ts_bow).total_seconds()

        # Find the intersection of the two PRN arrays.
        obs_gps_prns = np.zeros(len(obs.prns), dtype=int)
        obs_gps_prns[obs.n_G] = obs.prns[obs.n_G]
        prns, j_nav, j_obs = np.intersect1d(nav.prns, obs_gps_prns,
                return_indices=True)

        # Initialize the ephemeris mapping (a matrix of `None`s).
        setattr(obs, "ephs", np.empty((len(t_rx), len(obs.prns)), dtype=EphG))

        # Check if there is no overlap.
        if len(prns) == 0:
            Warning("rnx: PRNs of NavG and Obs data sets do not overlap.")

        # For each PRN that matches,
        for j in range(len(prns)):
            # Initialize an array of time differences to a large number.
            del_t = np.full(len(t_rx), 604800.0) # a week of seconds

            # Initialize found-overlap flag.
            found_overlap = False

            # For each moment in the nav time array,
            for k in range(len(t_oc)):
                # Get the ephemeris data for this space vehicle at this moment
                # in time.  Skip if there is no data.
                eph = nav.ephs[k, j_nav[j]]
                if eph is None:
                    continue

                # Get the beginning and ending of the fit interval.
                t_a = t_oc[k] - 0.5*eph.T_fit
                t_b = t_oc[k] + 0.5*eph.T_fit

                # Find the indices of the receiver's time array which fall
                # within the fit interval.  Skip is there is no match.
                n_ab = np.nonzero((t_rx >= t_a) * (t_rx <= t_b))[0]
                if len(n_ab) == 0:
                    continue
                found_overlap = True

                # Save this ephemeris data for those moments where the time fit
                # is the best.
                del_t_ab = np.abs(t_oc[k] - t_rx[n_ab])
                is_better = (del_t_ab <= del_t[n_ab])
                obs.ephs[n_ab[is_better], j_obs[j]] = eph
                del_t[n_ab[is_better]] = del_t_ab[is_better]

            # Check and report if there was no overlap.
            if not found_overlap:
                Warning("rnx: GPS %d had no overlapping NavG and Obs data." %
                        (prns[j]))

    def map_ref_to_obs(ref, obs):
        """
        Find the intersection of the `ref` and `obs` observation times and svs.
        Four new attributes are added to the Obs object::

            j_ref   array of indices to the intersected ref SV columns
            j_obs   array of indices to the intersected obs SV columns
            k_ref   array of indices to the intersected ref time rows
            k_obs   array of indices to the intersected obs time rows
        """

        svs, j_ref, j_obs = np.intersect1d(ref.svs, obs.svs,
                return_indices=True)
        _, k_ref, k_obs = np.intersect1d(ref.t, obs.t,
                return_indices=True)
        setattr(obs, "j_ref", j_ref)
        setattr(obs, "k_ref", k_ref)
        setattr(obs, "j_obs", j_obs)
        setattr(obs, "k_obs", k_obs)

    # Initialize the objects.
    nav = None
    obs = None
    ref = None

    # Read in file one.
    if not isinstance(file_one, str):
        raise Exception("rnx: file_one must be a string!")
    file_one_type = get_file_type(file_one)
    if file_one_type == 'N':
        nav = NavG(file_one)
    elif file_one_type == 'O':
        obs = Obs(file_one)

    # Read in file two.
    if file_two is not None:
        if not isinstance(file_two, str):
            raise Exception("rnx: file_two must be a string!")
        file_two_type = get_file_type(file_two)
        if file_two_type == 'N':
            if file_one_type == 'N':
                raise Exception("rnx: cannot read two navigation files!")
            nav = NavG(file_two)
        elif file_two_type == 'O':
            if file_one_type == 'O':
                raise Exception("rnx: cannot read two observation files!")
            obs = Obs(file_two)
        map_nav_to_obs(nav, obs)

    # Read in reference file.
    if file_ref is not None:
        if not isinstance(file_ref, str):
            raise Exception("rnx: file_ref must be a string!")
        file_ref_type = get_file_type(file_ref)
        if file_ref_type != 'O':
            raise Exception("rnx: reference file must be an observation type!")
        ref = Obs(file_ref)
        map_ref_to_obs(ref, obs)

    # Return the objects in the order the files were specified.
    if file_two is None:
        if file_ref is None:
            if nav is not None:
                return nav
            elif obs is not None:
                return obs
        else:
            if nav is not None:
                return nav, ref
            elif obs is not None:
                return obs, ref
    else:
        if file_ref is None:
            if file_one_type == 'N':
                return nav, obs
            else:
                return obs, nav
        else:
            if file_one_type == 'N':
                return nav, obs, ref
            else:
                return obs, nav, ref
