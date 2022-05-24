#===============================================================================
# PSCAD Instrument Components
#===============================================================================

"""
================
Instruments
================
"""

#===============================================================================
# Imports
#===============================================================================

import logging #, math

from mhi.common.colour import Colour

from .remote import rmi_property
from .component import ZComponent
from .graph import FrameMixin


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Codecs
#===============================================================================

_colour_codec = Colour()


#===============================================================================
# PSCAD Control
#===============================================================================

class Instrument(ZComponent, FrameMixin):
    """
    Output controls allowing the user to observe quantities changing during
    a simulation.

    Includes Oscilloscopes, Phasor Meters and Poly Meters.
    """

    @rmi_property
    def link_id(self):
        """
        Related / linked component id
        """

    @property
    def linked(self):
        """
        Component which this control component is linked to.
        """
        return self.project().component(self.link_id)

    def parameters(self, *, parameters=None, **kwargs):
        return self.linked.parameters(None, parameters=parameters, **kwargs)

    def __getitem__(self, key):
        return self.linked[key]

    def range(self, parameter):
        return self.linked.range(parameter)

    @property
    def title(self):
        """The title displayed on the frame"""
        return self['Name']

    @title.setter
    def title(self, title):
        self['Name'] = title



#===============================================================================
# PSCAD Polymeter
#===============================================================================

class PolyMeter(Instrument):
    """
    A polymeter is a special runtime object used specifically for monitoring
    a single, multiple-trace curve.
    The polymeter dynamically displays the magnitude of each trace in
    bar type format (called gauges),
    which results in an overall appearance similar to a spectrum analyzer.
    The power of this device lies in its ability to compress a large amount
    of data into a small viewing area, which is particularly helpful when
    viewing harmonic spectrums such as data output from the Fast Fourier
    Transform (FFT) component.
    """

    labels = rmi_property(True, True, name="labels",
                          doc="Meter labels visible?")

    scrollable = rmi_property(True, True, name="scrollable",
                              doc="Scroll view enabled?")

    _colour = rmi_property(True, True, name="_colour", doc="Bar colour")

    @property
    def colour(self):
        """
        Colour of bars in Poly Meter
        """

        return _colour_codec.decode(str(self._colour))

    @colour.setter
    def colour(self, colour):

        abgr = _colour_codec.encode(colour)
        self._colour = int(abgr[7:9] + abgr[5:7] + abgr[3:5], 16) # rgb

    color = colour



#===============================================================================
# PSCAD PhasorMeter
#===============================================================================

class PhasorMeter(Instrument):
    """
    A PhasorMeter is a special runtime object that can be used to display
    up to six, separate phasor quantities.
    The phasormeter displays phasors in a polar graph, where the magnitude and
    phase of each phasor responds dynamically during a simulation run.
    This device is perfect for visually representing phasor quantities,
    such as output from the Fast Fourier Transform (FFT) component.
    """

    degrees = rmi_property(True, True, name='degrees',
                           doc='True if Phasor Meter angle input is in degrees')

    @rmi_property
    def index(self):
        """
        Active phasor index (read-only)

        :type: int
        """

    @property
    def radians(self):
        """True if Phasor Meter angle input is in radians"""
        return not self.degrees

    @radians.setter
    def radians(self, radians):
        self.degrees = not radians



#===============================================================================
# PSCAD Oscilloscope
#===============================================================================

class Oscilloscope(Instrument):

    """
    An Oscilloscope is a special runtime object that is used to mimic the
    triggering effects of a real-world oscilloscope on a time varying,
    cyclical signal like an AC voltage or current.
    Given a base frequency, the oscilloscope will follow the signal during
    a simulation (like a moving window), refreshing its display at the rate
    given by the base frequency.
    This gives the illusion that the oscilloscope is transfixed on the signals
    being displayed, resulting in a triggering effect.
    """

    frequency = rmi_property(True, True, name='frequency',
                             doc="Base frequency")

    cycles = rmi_property(True, True, name='cycles',
                          doc="Number of cycles to display")
