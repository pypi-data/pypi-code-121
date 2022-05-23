# ----------------------------------------------------------------------------
# Description    : S4g SPI module native interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------

import numpy as np
import threading
from time import sleep

from typing import List, Optional, Tuple

from spirack.S4g_module import S4g_module as S4gApi
from qblox_instruments.native.spi_rack_modules import SpiModuleBase


class DummyS4gApi:
    """
    Mock implementation of
    `spirack API <https://github.com/mtiggelman/SPI-rack/blob/master/spirack/S4g_module.py>`_,
    for use with the dummy drivers.
    """

    # DAC software span constants
    range_max_uni = 0
    range_max_bi = 2
    range_min_bi = 4

    DAC_RESOLUTION = 2 ** 18
    NUMBER_OF_DACS = 4

    def __init__(
        self,
        spi_rack,
        module: int,
        max_current: float = 50e-3,
        reset_currents: bool = True,
    ):
        """
        Instantiates the mock communication layer with identical parameters to
        the `spirack.S4g_module.S4g_module` constructor.

        Parameters
        ----------
        spi_rack : DummySpiApi
            Mock SPI_rack class object via which the communication runs
        module : int
            module number set on the hardware
        max_current : float
            maximum range of the S4g, configured in hardware
        reset_currents : bool
            if True, then reset all currents to zero and change the span to
            `range_max_bi`

        Returns
        ----------
        """
        self.parent = spi_rack
        self._currents = [0.0] * self.NUMBER_OF_DACS
        init_span = self.range_max_bi if reset_currents else 0
        self._num_dacs = self.NUMBER_OF_DACS
        self._spans = [init_span] * self.NUMBER_OF_DACS
        self.max_current = max_current
        self.address = module

    def change_span_update(self, dac: int, span: int) -> None:
        """
        Mocks the `change_span_update` function of the API.

        Parameters
        ----------
        dac : int
            Current output of which to change the span
        span : int
            values for the span as mentioned in the datasheet, use from
            SPAN_MAPPING

        Returns
        ----------
        """
        self._spans[dac] = span

    def change_span(self, dac, span) -> None:
        """
        Mocks the `change_span` function of the API

        Parameters
        ----------
        dac : int
            Current output of which to change the span
        span : int
            values for the span as mentioned in the datasheet, use from
            SPAN_MAPPING

        Returns
        ----------
        """
        self.change_span_update(dac, span)

    def set_current(self, dac: int, current: float) -> None:
        """
        Mocks the `set_voltage` function of the API

        Parameters
        ----------
        dac: int
            Current output of which to update the current
        voltage: float
            new DAC current
        """
        self._currents[dac] = current

    def get_settings(self, dac: int) -> Tuple[float, int]:
        """
        Mocks the `get_settings` function of the API

        Parameters
        ----------
        dac : int
            Current output of which the settings will be read

        Returns
        ----------
        float
            current
        int
            span
        """
        return self._currents[dac], self._spans[dac]

    def get_stepsize(self, dac) -> float:
        """
        Mocks the `get_stepsize` function of the API

        Parameters
        ----------
        dac : int
            Current output of which the stepsize is calculated

        Returns
        ----------
        float
            Smallest current step possible with DAC
        """
        if self._spans[dac] == self.range_max_bi:
            return 2 * self.max_current / self.DAC_RESOLUTION

        return self.max_current / self.DAC_RESOLUTION


class S4gModule(SpiModuleBase):
    """
    Native driver for the S4g SPI module.
    """

    NUMBER_OF_DACS = 4  # Set by hardware constraints

    def __init__(
        self,
        parent,
        name: str,
        address: int,
        reset_currents: bool = False,
        dac_names: Optional[List[str]] = None,
        is_dummy: bool = False,
    ):
        """
        Instantiates the driver object. This is the object that should be
        instantiated by the
        :func:`~qblox_instruments.native.SpiRack.add_spi_module` function.

        Parameters
        ----------
        parent
            Reference to the :class:`~qblox_instruments.native.SpiRack` parent
            object. This is handled by the
            :func:`~qblox_instruments.native.SpiRack.add_spi_module` function.
        name : str
            Name given to the InstrumentChannel.
        address : int
            Module number set on the hardware.
        reset_currents : bool
            If True, then reset all currents to zero and change the span to
            `range_max_bi`.
        dac_names : Optional[List[str]]
            List of all the names to use for the dac channels. If no list is
            given or is None, the default name "dac{i}" is used for the i-th
            dac channel.
        is_dummy : bool
            If true, do not connect to physical hardware, but use dummy
            module.

        Returns
        ----------

        Raises
        ----------
        ValueError
            Length of the dac names list does not match the number of dacs.
        """
        super().__init__(parent, name, address)

        api = DummyS4gApi if is_dummy else S4gApi

        self.api = api(
            parent.spi_rack,
            module=address,
            reset_currents=reset_currents,
        )
        self._channels = []

        for dac in range(self.NUMBER_OF_DACS):
            if dac_names is None:
                ch_name = "dac{}".format(dac)
            elif len(dac_names) == self.NUMBER_OF_DACS:
                ch_name = dac_names[dac]
            else:
                raise ValueError(
                    f"Length of dac_names must be {self.NUMBER_OF_DACS}"
                )
            channel = S4gDacChannel(self, ch_name)
            self._channels.append(channel)

    def set_dacs_zero(self) -> None:
        """
        Sets all currents of all outputs to 0.

        Returns
        ----------
        """
        for ch in self._channels:
            ch.current(0)


class S4gDacChannel:
    """
    Native driver for the dac channels of the S4g module. This class is used
    by the :class:`~qblox_instruments.native.spi_rack_modules.S4gModule` to
    define the individual dac channels and should not be used directly.
    """

    def __init__(self, parent: S4gModule, name: str):
        """
        Constructor for the dac channel instrument channel.

        Parameters
        ----------
        parent : S4gModule
            Reference to the parent
            :class:`~qblox_instruments.native.spi_rack_modules.S4gModule`
        name : str
            Name for the instrument channel

        Returns
        ----------

        Raises
        ----------
        """
        self._api = parent.api
        self._chan_name = name
        self._ramping_enabled = False
        self._ramp_rate = 1e-3
        self._ramp_max_step = 0.5e-3
        self._is_ramping = False
        self._ramp_thread = None

    def _get_span(self, dac: int) -> int:
        """
        Gets the span set by the module.

        Parameters
        ----------
        dac : int
            the dac of which to get the span

        Returns
        ----------
        int
            The current span
        """
        _, span = self._api.get_settings(dac)
        return span

    def _set_span(self, dac: int, val: int) -> None:
        """
        Sets the span set by the module.

        Parameters
        ----------
        dac : int
            the dac of which to set the span

        val : int
            the integer representation of the new span

        Raises
        ----------
        ValueError
            When the present current on the output does not fit into the new span
        """
        cur, _ = self._api.get_settings(dac)
        # check if cur fits into the new span
        if val == self._api.range_max_uni:
            maxI = self._api.max_current
            minI = 0.0
        elif val == self._api.range_max_bi:
            maxI = self._api.max_current
            minI = -self._api.max_current
        elif val == self._api.range_min_bi:
            maxI = self._api.max_current / 2.0
            minI = -(self._api.max_current / 2.0)
        if cur < minI or cur > maxI:
            raise ValueError(f'Present current is {cur*1e3} mA, which is out of the range [{minI*1e3} mA, {maxI*1e3} mA], the newly selected span')
        self._api.change_span(dac, val)
        self.set_current_instant(dac, cur)

    def _get_current(self, dac: int) -> float:
        """
        Gets the current set by the module.

        Parameters
        ----------
        dac : int
            the dac of which to get the current

        Returns
        ----------
        float
            The output current reported by the hardware
        """
        current, _ = self._api.get_settings(dac)
        return current

    def _set_current(self, dac: int, val: float) -> None:
        """
        Sets the current either through ramping or instantly.

        Parameters
        ----------
        dac : int
            the dac of which to set the current
        val : float
            The new value of the current

        Returns
        ----------
        """
        if self._ramping_enabled:
            self._set_current_ramp(dac, val)
        else:
            self.set_current_instant(dac, val)

    def _set_current_ramp(self, dac, val) -> None:
        """
        Ramps the current in steps set by `ramp_max_step` with a rate set by
        `ramp_rate`. Ramping is non-blocking so the user should check
        `is_ramping() == False` to see if the final value is reached.

        Parameters
        ----------
        dac : int
            the dac of which to set the current
        val : float
            The new value of the current after ramping

        Returns
        ----------
        """

        class RampThread(threading.Thread):
            """
            Inner class that defines a thread that can be safely killed.
            """

            def __init__(self, *args, **kwargs):
                super().__init__(target=self.worker_function, *args, **kwargs)
                self._stopped = False

            def worker_function(self, ch, dac, vals, dt):
                """
                Conducts the actual ramping
                """
                for val in vals:
                    if self._stopped:
                        return
                    sleep(dt)
                    ch.set_current_instant(dac, val)
                ch._is_ramping = False

            def exit(self):
                """
                Stops the thread.
                """
                self._stopped = True

        # Start of function code
        # Stop ramping to the value set previously, and ramp to new value.
        if self._is_ramping:
            self._ramp_thread.exit()

        self._is_ramping = True

        val_begin = self._get_current(dac)
        num_steps = int(np.ceil(np.abs(val_begin - val) / self._ramp_max_step))
        vals = np.linspace(val_begin, val, num_steps)
        dt = np.abs(val_begin - val) / self._ramp_rate / num_steps
        th = RampThread(args=(self, dac, vals, dt))
        self._ramp_thread = th
        th.start()

    def set_current_instant(self, dac, val) -> None:
        """
        Wrapper function around the set_current API call. Instantaneously
        sets the current.

        Parameters
        ----------
        dac : int
            the dac of which to set the current
        val : float
            The new value of the current

        Returns
        ----------
        """
        self._api.get_settings(dac)
        self._api.set_current(dac, val)
