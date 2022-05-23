"""
Class extending functionality of StateSpace from python control

Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>,
Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>
"""
import control
import numpy as np
from spicypy.signal.time_series import TimeSeries


class System(control.StateSpace):
    """
    Class to model control systems and their response

    """

    def __init__(self, sys):
        if isinstance(sys, control.StateSpace):
            print("Info: supplied control.StateSpace")
            super().__init__(sys)
        elif isinstance(sys, control.TransferFunction):
            super().__init__(control.tf2ss(sys))
            print(
                "Info: supplied transfer function was converted to control.StateSpace using control.tf2ss()"
            )
        else:
            raise ValueError(
                "Unsupported type of control system! Expected either control.StateSpace or "
                "control.TransferFunction"
            )

    def feedback(self, *args, **kwargs):
        return System(control.StateSpace.feedback(self, *args, **kwargs))

    def response(self, time_series):
        t = np.array(time_series.times)
        v = np.array(time_series.value)
        resp = control.input_output_response(control.ss2io(self), t, v)
        return TimeSeries(resp.outputs, times=resp.time, unit=time_series.unit)
