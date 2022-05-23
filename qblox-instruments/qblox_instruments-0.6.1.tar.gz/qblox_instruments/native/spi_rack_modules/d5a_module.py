# ----------------------------------------------------------------------------
# Description    : D5a SPI module native interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------

import numpy as np
import threading
from time import sleep

from typing import List, Optional, Tuple

from spirack.D5a_module import D5a_module as D5aApi
from qblox_instruments.native.spi_rack_modules import SpiModuleBase


class DummyD5aApi:
    """
    Mock implementation of
    `spirack API <https://github.com/mtiggelman/SPI-rack/blob/master/spirack/D5a_module.py>`_,
    for use with the dummy drivers.
    """

    # DAC software span constants
    range_4V_uni = 0
    range_4V_bi = 2
    range_8V_uni = 1
    range_8V_bi = 3
    range_2V_bi = 4
    SPAN_MAPPING = {
        "range_4V_uni": range_4V_uni,
        "range_8V_uni": range_8V_uni,
        "range_4V_bi": range_4V_bi,
        "range_8V_bi": range_8V_bi,
        "range_2V_bi": range_2V_bi,
    }
    DAC_RESOLUTION = 2 ** 18

    def __init__(
        self,
        spi_rack,
        module: int,
        reset_voltages: bool = True,
        num_dacs: int = 16
    ):
        """
        Instantiates the mock communication layer with identical parameters to
        the `spirack.D5a_module.D5a_module` constructor.

        Parameters
        ----------
        spi_rack : DummySpiApi
            Mock SPI_rack class object via which the communication runs
        module : int
            module number set on the hardware
        reset_voltages : bool
            if True, then reset all voltages to zero and change the span
            to `range_4V_bi`. If a voltage jump would occur, then ramp
            to zero in steps of 10 mV
        num_dacs: int
            number of DAC channels available

        Returns
        ----------
        """
        self.parent = spi_rack
        self._voltages = [0.0] * num_dacs
        init_span = self.SPAN_MAPPING["range_4V_bi"] if reset_voltages else 0
        self._num_dacs = num_dacs
        self._spans = [init_span] * num_dacs
        self.address = module

    def change_span_update(self, DAC: int, span: int) -> None:
        """
        Mocks the `change_span_update` function of the API.

        Parameters
        ----------
        DAC : int
            Current output of which to change the span
        span : int
            Values for the span as mentioned in the datasheet, use from
            SPAN_MAPPING

        Returns
        ----------
        """
        self._spans[DAC] = span

    def change_span(self, DAC: int, span: int) -> None:
        """
        Mocks the `change_span` function of the API.

        Parameters
        ----------
        DAC : int
            Current output of which to change the span
        span : int
            Values for the span as mentioned in the datasheet, use from
            SPAN_MAPPING

        Returns
        ----------
        """
        self.change_span_update(DAC, span)

    def set_voltage(self, DAC: int, voltage: float) -> None:
        """
        Mocks the `set_voltage` function of the API

        Parameters
        ----------
        DAC: int
            DAC inside the module of which to update the voltage
        voltage: float
            new DAC voltage

        Returns
        ----------
        """
        self._voltages[DAC] = voltage

    def get_settings(self, DAC: int) -> Tuple[float, int]:
        """
        Mocks the `get_settings` function of the API

        Parameters
        ----------
        DAC : int
            Current output of which the settings will be read

        Returns
        ----------
        float
            voltage
        int
            span
        """
        return self._voltages[DAC], self._spans[DAC]

    def get_stepsize(self, DAC: int) -> float:
        """
        Mocks the `get_stepsize` function of the API.

        Parameters
        ----------
        DAC : int
            DAC inside the module of which the stepsize is calculated

        Returns
        ----------
        float
            Smallest voltage step possible with DAC
        """
        if DAC not in range(self._num_dacs):
            raise ValueError(
                "D5a module {} [get_stepsize]: DAC {} does not exist.".format(self.address, DAC)
            )

        voltage_ranges = {
            "range_4V_uni": 4.0,
            "range_8V_uni": 8.0,
            "range_4V_bi": 8.0,
            "range_8V_bi": 16.0,
            "range_2V_bi": 4,
        }

        # Reverse dict lookup
        span_as_str = next(
            key for key, value in self.SPAN_MAPPING.items() if value == self._spans[DAC]
        )
        return voltage_ranges[span_as_str] / self.DAC_RESOLUTION


class D5aModule(SpiModuleBase):
    """
    Native driver for the D5a SPI module.
    """

    NUMBER_OF_DACS = 16  # Set by hardware constraints

    def __init__(
        self,
        parent,
        name: str,
        address: int,
        reset_voltages: bool = False,
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
        reset_voltages : bool
            If True, then reset all voltages to zero and change the span to
            `range_max_bi`.
        dac_names : Optional[List[str]]
            List of all the names to use for the dac channels. If no list is
            given or is None, the default name "dac{i}" is used for the i-th
            dac channel.
        is_dummy : bool
            If true, do not connect to physical hardware, but use dummy module.

        Returns
        ----------

        Raises
        ----------
        ValueError
            Length of the dac names list does not match the number of dacs.
        """
        super().__init__(parent, name, address)

        api = DummyD5aApi if is_dummy else D5aApi

        self.api = api(
            parent.spi_rack,
            module=address,
            reset_voltages=reset_voltages,
            num_dacs=self.NUMBER_OF_DACS,
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
            channel = D5aDacChannel(self, ch_name)
            self._channels.append(channel)

    def set_dacs_zero(self) -> None:
        """
        Sets all voltages of all outputs to 0.

        Returns
        ----------
        """
        for ch in self._channels:
            ch.voltage(0)


class D5aDacChannel:
    """
    Native driver for the dac channels of the D5a module. This class is used
    by the :class:`~qblox_instruments.native.spi_rack_modules.D5aModule` to
    define the individual dac channels and should not be used directly.
    """

    def __init__(self, parent: D5aModule, name: str):
        """
        Constructor for the dac channel instrument channel.

        Parameters
        ----------
        parent : D5aModule
            Reference to the parent
            :class:`~qblox_instruments.native.spi_rack_modules.D5aModule`
        name : str
            Name for the instrument channel
        dac : int
            Number of the dac that this channel corresponds to

        Returns
        ----------

        Raises
        ----------
        """
        self._api = parent.api
        self._chan_name = name
        self._ramping_enabled = False
        self._ramp_rate = 100e-3
        self._ramp_max_step = 100e-3
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

        val: int
            The integer representation of the new spen

        Raises
        ----------
        ValueError
            When the present current on the output does not fit into the new span
        """
        v, _ = self._api.get_settings(dac)
        # check if v fits into the new span
        if val == self._api.range_4V_uni:
            maxV = 4.0
            minV = 0.0
        elif val == self._api.range_4V_bi:
            maxV = 4.0
            minV = -4.0
        if val == self._api.range_8V_uni:
            maxV = 8.0
            minV = 0.0
        elif val == self._api.range_8V_bi:
            maxV = 8.0
            minV = -8.0
        elif val == self._api.range_2V_bi:
            maxV = 2.0
            minV = -2.0
        if v < minV or v > maxV:
            raise ValueError(f'Present voltage is {v} V, which is out of the range [{minV} V, {maxV } V], the newly selected span')

        self._api.change_span(dac, val)
        self.set_voltage_instant(dac, v)


    def _get_voltage(self, dac: int) -> float:
        """ "
        Gets the voltage set by the module.

        Parameters
        ----------
        dac : int
            the dac of which to get the voltage

        Returns
        ----------
        float
            The output voltage reported by the hardware
        """
        voltage, _ = self._api.get_settings(dac)
        return voltage

    def _set_voltage(self, dac: int, val: float) -> None:
        """
        Sets the voltage either through ramping or instantly.

        Parameters
        ----------
        dac : int
            the dac of which to set the voltage
        val : float
            The new value of the voltage

        Returns
        ----------
        """
        if self._ramping_enabled:
            self._set_voltage_ramp(dac, val)
        else:
            self.set_voltage_instant(dac, val)

    def set_voltage_instant(self, dac: int, val: float) -> None:
        """ "
        Wrapper function around the set_voltage API call. Instantaneously sets
        the voltage.

        Parameters
        ----------
        dac : int
            the dac of which to set the voltage
        val : float
            The new value of the voltage

        Returns
        ----------
        """
        self._api.get_settings(dac)
        self._api.set_voltage(dac, val)

    def _set_voltage_ramp(self, dac: int, val: float) -> None:
        """
        Ramps the voltage in steps set by `ramp_max_step` with a rate set by
        `ramp_rate`. Ramping is non-blocking so the user should check
        `is_ramping() == False` to see if the final value is reached.

        Parameters
        ----------
        dac : int
            the dac of which to set the voltage
        val : float
            The new value of the voltage after ramping

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
                    ch.set_voltage_instant(dac, val)
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

        val_begin = self._get_voltage(dac)
        num_steps = int(np.ceil(np.abs(val_begin - val) / self._ramp_max_step))
        vals = np.linspace(val_begin, val, num_steps)
        dt = np.abs(val_begin - val) / self._ramp_rate / num_steps
        th = RampThread(args=(self, dac, vals, dt))
        self._ramp_thread = th
        th.start()
