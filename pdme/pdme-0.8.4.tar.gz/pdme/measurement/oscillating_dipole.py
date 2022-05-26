from dataclasses import dataclass
import numpy
import numpy.typing
from typing import Sequence, List
from pdme.measurement.dot_measure import DotMeasurement, DotRangeMeasurement
from pdme.measurement.dot_pair_measure import (
	DotPairMeasurement,
	DotPairRangeMeasurement,
)
from pdme.measurement.input_types import DotInput, DotPairInput


@dataclass
class OscillatingDipole:
	"""
	Representation of an oscillating dipole, either known or guessed.

	Parameters
	----------
	p : numpy.ndarray
	The oscillating dipole moment, with overall sign arbitrary.

	s : numpy.ndarray
	The position of the dipole.

	w : float
	The oscillation frequency.
	"""

	p: numpy.ndarray
	s: numpy.ndarray
	w: float

	def __post_init__(self) -> None:
		"""
		Coerce the inputs into numpy arrays.
		"""
		self.p = numpy.array(self.p)
		self.s = numpy.array(self.s)

	def s_at_position(self, r: numpy.ndarray, f: float) -> float:
		"""
		Returns the noise potential at a point r, at some frequency f.

		Parameters
		----------
		r : numpy.ndarray
		The position of the dot.

		f : float
		The dot frequency to sample.
		"""
		return (self._alpha(r)) ** 2 * self._b(f)

	def _alpha(self, r: numpy.ndarray) -> float:
		diff = r - self.s
		return self.p.dot(diff) / (numpy.linalg.norm(diff) ** 3)

	def _b(self, f: float) -> float:
		return (1 / numpy.pi) * (self.w / (f**2 + self.w**2))

	def s_for_dot_pair(self, r1: numpy.ndarray, r2: numpy.ndarray, f: float) -> float:
		return self._alpha(r1) * self._alpha(r2) * self._b(f)

	def to_flat_array(self) -> numpy.ndarray:
		return numpy.concatenate([self.p, self.s, numpy.array([self.w])])


class OscillatingDipoleArrangement:
	"""
	A collection of oscillating dipoles, which we are interested in being able to characterise.

	Parameters
	--------
	dipoles : Sequence[OscillatingDipole]
	"""

	def __init__(self, dipoles: Sequence[OscillatingDipole]):
		self.dipoles = dipoles

	def get_dot_measurement(self, dot_input: DotInput) -> DotMeasurement:
		r = numpy.array(dot_input[0])
		f = dot_input[1]
		return DotMeasurement(
			sum([dipole.s_at_position(r, f) for dipole in self.dipoles]), r, f
		)

	def get_dot_pair_measurement(
		self, dot_pair_input: DotPairInput
	) -> DotPairMeasurement:
		r1 = numpy.array(dot_pair_input[0])
		r2 = numpy.array(dot_pair_input[1])
		f = dot_pair_input[2]
		return DotPairMeasurement(
			sum([dipole.s_for_dot_pair(r1, r2, f) for dipole in self.dipoles]),
			r1,
			r2,
			f,
		)

	def get_dot_measurements(
		self, dot_inputs: Sequence[DotInput]
	) -> List[DotMeasurement]:
		"""
		For a series of points, each with three coordinates and a frequency, return a list of the corresponding DotMeasurements.
		"""
		return [self.get_dot_measurement(dot_input) for dot_input in dot_inputs]

	def get_dot_pair_measurements(
		self, dot_pair_inputs: Sequence[DotPairInput]
	) -> List[DotPairMeasurement]:
		"""
		For a series of pairs of points, each with three coordinates and a frequency, return a list of the corresponding DotPairMeasurements.
		"""
		return [
			self.get_dot_pair_measurement(dot_pair_input)
			for dot_pair_input in dot_pair_inputs
		]

	def get_percent_range_dot_measurement(
		self, dot_input: DotInput, low_percent: float, high_percent: float
	) -> DotRangeMeasurement:
		r = numpy.array(dot_input[0])
		f = dot_input[1]
		return DotRangeMeasurement(
			low_percent * sum([dipole.s_at_position(r, f) for dipole in self.dipoles]),
			high_percent * sum([dipole.s_at_position(r, f) for dipole in self.dipoles]),
			r,
			f,
		)

	def get_percent_range_dot_measurements(
		self, dot_inputs: Sequence[DotInput], low_percent: float, high_percent: float
	) -> List[DotRangeMeasurement]:
		"""
		For a series of pairs of points, each with three coordinates and a frequency, and also a lower error range and upper error range, return a list of the corresponding DotPairRangeMeasurements.
		"""
		return [
			self.get_percent_range_dot_measurement(dot_input, low_percent, high_percent)
			for dot_input in dot_inputs
		]

	def get_percent_range_dot_pair_measurement(
		self, pair_input: DotPairInput, low_percent: float, high_percent: float
	) -> DotPairRangeMeasurement:
		r1 = numpy.array(pair_input[0])
		r2 = numpy.array(pair_input[1])
		f = pair_input[2]
		return DotPairRangeMeasurement(
			low_percent
			* sum([dipole.s_for_dot_pair(r1, r2, f) for dipole in self.dipoles]),
			high_percent
			* sum([dipole.s_for_dot_pair(r1, r2, f) for dipole in self.dipoles]),
			r1,
			r2,
			f,
		)

	def get_percent_range_dot_pair_measurements(
		self,
		pair_inputs: Sequence[DotPairInput],
		low_percent: float,
		high_percent: float,
	) -> List[DotPairRangeMeasurement]:
		"""
		For a series of pairs of points, each with three coordinates and a frequency, and also a lower error range and upper error range, return a list of the corresponding DotPairRangeMeasurements.
		"""
		return [
			self.get_percent_range_dot_pair_measurement(
				pair_input, low_percent, high_percent
			)
			for pair_input in pair_inputs
		]

	def to_numpy_array(self) -> numpy.ndarray:
		"""
		Returns a numpy array with the canonical representation of each dipole in a nx7 numpy array.
		"""
		return numpy.array([dipole.to_flat_array() for dipole in self.dipoles])
