"""LabVIEW's waveform data type in Python"""
from numbers import Number
import numpy as np
from unyt import matplotlib_support, unyt_array

matplotlib_support()
matplotlib_support.label_style = "/"


class WaveformDT(np.lib.mixins.NDArrayOperatorsMixin):
    """Python implementation of LabVIEW's waveform data type

    LabVIEW's waveform data type has three required attributes: t0, dt, and Y.
    Additional attributes can be set and are included in the returned WaveformDT.
    WaveformDT has the function to_xy() that will generate the x-axis array from the
    t0, dt and number of samples in the Y array.

    Attributes:
        Y (array-like): data
        dt (float): wf_increment
        t0 (float or datetime): wf_start_time

    Example:

        >>> data = WaveformDT([1,2,3], 1, 0)
        >>> x, y = data.to_xy()
        >>> x
        array([0., 1., 2.])
        >>> y
        array([1, 2, 3])

    WaveformDT supports a variety of workflows with and without units where unit
    support is provided by the Unyt library.

        >>> data.xunit = "s"
        >>> data.yunit = "V"
        >>> x, y = data.to_xy()
        >>> x
        unyt_array([0., 1., 2.], 's')
        >>> y
        unyt_array([0, 1, 2], 'V')

    WaveformDT supports Matplotlib and its labeled data interface:

        >>> import matplotlib.pyplot as plt
        >>> waveform = WaveformDT([1,2,3], 1, 0)
        >>> plt.plot('x', 'y', 'r-', data=waveform)
        [<matplotlib.lines.Line2D object ... >]
        >>> plt.show()

    Note:
        The x-axis array will be relative time by default. For absolute time, set the
        relative parameter to False.
    """

    def __init__(self, Y, dt, t0):
        self.Y = np.asanyarray(Y)
        self.dt = dt
        self.t0 = t0
        self._yunit = None
        self._xunit = None

    def __array__(self):
        return self.Y

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        args = []
        for input_ in inputs:
            if isinstance(input_, WaveformDT):
                args.append(input_.Y)
            else:
                args.append(input_)
        output = kwargs.pop("out", (None,))[0]
        if output is not None:
            if isinstance(output, WaveformDT):
                kwargs["out"] = output.Y
            else:
                kwargs["out"] = output
        arr_result = self.Y.__array_ufunc__(ufunc, method, *args, **kwargs)
        if arr_result is NotImplemented:
            return NotImplemented
        if method == "at":
            return None
        result = WaveformDT(arr_result, self.dt, self.t0) if output is None else output
        return result

    def set_attributes(self, **kwargs):
        """Set waveform attributes"""
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def size(self):
        """Return the number of elements in Y"""
        return self.Y.size

    @property
    def yunit(self):
        """units (str, Unit): Y-axis unit"""
        unit = self.Y.units if isinstance(self.Y, unyt_array) else self._yunit
        self._yunit = unit
        return unit

    @yunit.setter
    def yunit(self, units):
        try:
            self.Y.convert_to_units(units)
        except AttributeError:
            pass
        self._yunit = units

    @property
    def xunit(self):
        """units (str, Unit): X-axis unit, based on dt"""
        unit = self.dt.units if isinstance(self.dt, unyt_array) else self._xunit
        self._xunit = unit
        return unit

    @xunit.setter
    def xunit(self, units):
        try:
            self.dt.convert_to_units(units)
        except AttributeError:
            pass
        self._xunit = units

    @property
    def min(self):
        """(float): minimum value"""
        return np.min(self.Y)

    @property
    def max(self):
        """(float): maximum value"""
        return np.max(self.Y)

    @property
    def std(self):
        """(float): standard deviation"""
        return np.std(self.Y)

    def to_xy(self, relative=True, inunits=True):
        """Generate the (x, y) tuple

        Parameters:
            relative (bool): y is relative time if True, absolute if False
            inunits (bool): convert arrays to unyt_array if yunit and xunit are defined

        Returns:
            tuple: x, y arrays
        """
        y = self.Y
        y = y.flatten()
        dt = self.dt
        t0 = self.t0
        t0_offset = getattr(self, "wf_start_offset", 0.0)
        samples = y.size
        if relative:
            t0 = t0 if isinstance(t0, Number) else 0.0
            t0 = t0 + t0_offset
            x = np.linspace(t0, t0 + samples * dt, samples, False)
        else:
            t0 = np.datetime64(t0.astimezone().replace(tzinfo=None))
            t0_array = np.asarray([t0] * samples)
            dt = np.timedelta64(np.uint32(dt * 1e9), "ns")
            dt_array = np.asarray(
                [np.timedelta64(0, "ns")] + [dt] * (samples - 1)
            ).cumsum()
            x = t0_array + dt_array
        if inunits:
            if not isinstance(x, unyt_array) and self._xunit is not None:
                x = unyt_array(x, self._xunit)
            if not isinstance(y, unyt_array) and self._yunit is not None:
                y = unyt_array(y, self._yunit)
        else:
            x = x.v if isinstance(x, unyt_array) else x
            y = y.v if isinstance(y, unyt_array) else y
        return (x, y)

    def head(self, n=5):
        """Return first n samples of the waveform

        Args:
            n (int): number of samples to return

        Returns:
            WaveformDT: first n samples
        """
        return self[:n]

    def tail(self, n=5):
        """Return the last n samples of the waveform

        Args:
            n (int): number of samples to return

        Returns:
            WaveformDT: last n samples
        """
        start_offset = self.t0 if isinstance(self.t0, Number) else 0.0
        start_offset += getattr(self, "wf_start_offset", 0.0)
        start_offset += (self.size - n) * self.dt
        wf = self[-n:]
        setattr(wf, "wf_start_offset", start_offset)
        return wf

    def __dir__(self):
        inst_attr = list(filter(lambda k: not k.startswith("_"), self.__dict__.keys()))
        cls_attr = list(filter(lambda k: not k.startswith("_"), dir(self.__class__)))
        return inst_attr + cls_attr

    def __getitem__(self, key):
        if key in ["y", "Y"]:
            return self.Y
        if key in ["x", "X"]:
            return self.to_xy()[0]
        return self.__class__(self.Y[key], self.dt, self.t0)

    def __repr__(self):
        t0 = self.t0 if isinstance(self.t0, Number) else 0.0
        t0 += getattr(self, "wf_start_offset", 0.0)
        dt = self.dt
        rows = []
        if self.size < 50:
            for i, sample in enumerate(self.Y):
                rows.append(f"{t0 + i*dt:11.4e}\t{sample:11.4e}")
        else:
            for i, sample in enumerate(self[:5].Y):
                rows.append(f"{t0 + i*dt:11.4e}\t{sample:11.4e}")
            rows.append(" ...")
            t0 = t0 + (self.size - 5) * dt
            for i, sample in enumerate(self[-5:].Y):
                rows.append(f"{t0 + i*dt:11.4e}\t{sample:11.4e}")
        rows.append(f"Length: {self.size}")
        rows.append(f"t0: {self.t0}")
        rows.append(f"dt: {self.dt:11.4e}")
        return "\n".join(rows)
