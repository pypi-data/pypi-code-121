from typing import List, Optional

from ._Report import Report, NO_ID
from ._SpectrumPoint import SpectrumPoint


class Spectrum:
    """
    Class representing a spectrum in memory.
    """
    def __init__(self):
        self.report: Optional[Report] = Report()
        self.id: str = new_spectrum_id_initialiser()
        self.database_id: int = NO_ID
        self.points: List[SpectrumPoint] = []
        self.max_amplitude: Optional[SpectrumPoint] = None
        self.min_amplitude: Optional[SpectrumPoint] = None
        self.max_wavenumber: Optional[SpectrumPoint] = None
        self.min_wavenumber: Optional[SpectrumPoint] = None

    def invalidate_min_max(self):
        """
        Resets the min/max values so they can be recalculated.
        """
        self.max_amplitude = None
        self.min_amplitude = None
        self.max_wavenumber = None
        self.min_wavenumber = None

    def validate_min_max(self):
        """
        Recalculates the min/max values.
        """
        first = True

        for point in self:
            if first:
                self.min_amplitude = point
                self.max_amplitude = point
                self.min_wavenumber = point
                self.max_wavenumber = point
                first = False
            else:
                if point.wave_number > self.max_wavenumber.wave_number:
                    self.max_wavenumber = point
                if point.wave_number < self.min_wavenumber.wave_number:
                    self.min_wavenumber = point
                if point.amplitude > self.max_amplitude.amplitude:
                    self.max_amplitude = point
                if point.amplitude < self.min_amplitude.amplitude:
                    self.min_amplitude = point

    def has_report(self):
        """
        Whether this spectrum has a report for meta-data.

        :return:    True if it has a report, False if not.
        """
        return self.report is not None

    def __iter__(self):
        # Treat ourself as an iterator over our points
        return self.points.__iter__()

    def __getattribute__(self, item):
        # Make sure min/max are valid
        if item in {'min_wavenumber', 'max_wavenumber', 'min_amplitude', 'max_amplitude'}:
            if super().__getattribute__(item) is None:
                self.validate_min_max()

        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        # Don't handle specially until init is complete
        if key not in self.__dict__:
            super().__setattr__(key, value)
            return

        # Override report ids
        if key == 'report':
            if value is not None:
                value.database_id = self.database_id
                value.set_id(self.id.replace("'", ""))

        # Keep report id matching this id
        if key == 'id':
            if self.report is not None:
                self.report.id = value

        super().__setattr__(key, value)


def new_spectrum_id_initialiser() -> str:
    # TODO: Make return the curent date-time as per reference implementation. csterling
    return ''
