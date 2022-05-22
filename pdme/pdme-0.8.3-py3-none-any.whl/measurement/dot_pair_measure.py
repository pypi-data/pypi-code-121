from dataclasses import dataclass
import numpy
import numpy.typing


@dataclass
class DotPairMeasurement:
	"""
	Representation of a dot measuring oscillating dipoles.

	Parameters
	----------
	v : float
	The voltage measured at the dot.

	r1 : numpy.ndarray
	The position of the first dot.

	r2 : numpy.ndarray
	The position of the second dot.

	f : float
	The measurement frequency.
	"""

	v: float
	r1: numpy.ndarray
	r2: numpy.ndarray
	f: float

	def __post_init__(self) -> None:
		self.r1 = numpy.array(self.r1)
		self.r2 = numpy.array(self.r2)


@dataclass
class DotPairRangeMeasurement:
	"""
	Representation of a dot measuring oscillating dipoles.

	Parameters
	----------
	v_low : float
	The lower range of voltage measured at the dot.

	v_high : float
	The upper range of voltage measured at the dot.

	r1 : numpy.ndarray
	The position of the first dot.

	r2 : numpy.ndarray
	The position of the second dot.

	f : float
	The measurement frequency.
	"""

	v_low: float
	v_high: float
	r1: numpy.ndarray
	r2: numpy.ndarray
	f: float

	def __post_init__(self) -> None:
		self.r1 = numpy.array(self.r1)
		self.r2 = numpy.array(self.r2)
		if self.v_low > self.v_high:
			self.v_low, self.v_high = self.v_high, self.v_low
