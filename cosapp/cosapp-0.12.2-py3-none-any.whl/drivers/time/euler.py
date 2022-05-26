from numbers import Number
from typing import Optional

from cosapp.drivers.time.interfaces import ExplicitTimeDriver


class EulerExplicit(ExplicitTimeDriver):
    def __init__(
        self,
        name="Euler",
        owner: Optional["cosapp.systems.System"] = None,
        **options
    ):
        """Initialize driver

        Parameters
        ----------
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
        name: str, optional
            Name of the `Driver`.
        **options : Dict[str, Any]
            Optional keywords arguments; may contain time step and interval, with keys `dt` and `time_interval`
        """
        super().__init__(name, owner, **options)

    def _update_transients(self, dt: Number) -> None:
        """
        Time integration of transient variables over time step `dt` by explicit Euler scheme.
        """
        for x in self._transients.values():
            x.value += x.d_dt * dt
