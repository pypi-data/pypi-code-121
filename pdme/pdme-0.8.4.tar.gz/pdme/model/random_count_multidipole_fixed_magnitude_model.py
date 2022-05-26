import numpy
import numpy.random
from pdme.model.model import DipoleModel
from pdme.measurement import (
	OscillatingDipole,
	OscillatingDipoleArrangement,
)


class RandomCountMultipleDipoleFixedMagnitudeModel(DipoleModel):
	"""
	Model of multiple oscillating dipoles with a fixed magnitude, but free rotation.

	Parameters
	----------
	pfixed : float
	The fixed dipole magnitude.

	n_max : int
	The maximum number of dipoles.

	prob_occupancy : float
	The probability of dipole occupancy
	"""

	def __init__(
		self,
		xmin: float,
		xmax: float,
		ymin: float,
		ymax: float,
		zmin: float,
		zmax: float,
		pfixed: float,
		n_max: int,
		prob_occupancy: float,
	) -> None:
		self.xmin = xmin
		self.xmax = xmax
		self.ymin = ymin
		self.ymax = ymax
		self.zmin = zmin
		self.zmax = zmax
		self.pfixed = pfixed
		self.rng = numpy.random.default_rng()
		self.n_max = n_max
		if prob_occupancy >= 1 or prob_occupancy <= 0:
			raise ValueError(
				f"The probability of a dipole site occupancy must be between 0 and 1, got {prob_occupancy}"
			)
		self.prob_occupancy = prob_occupancy

	def __repr__(self) -> str:
		return f"RandomCountMultipleDipoleFixedMagnitudeModel({self.xmin}, {self.xmax}, {self.ymin}, {self.ymax}, {self.zmin}, {self.zmax}, {self.pfixed}, {self.n_max}, {self.prob_occupancy})"

	def get_dipoles(
		self, max_frequency: float, rng_to_use: numpy.random.Generator = None
	) -> OscillatingDipoleArrangement:
		rng: numpy.random.Generator
		if rng_to_use is None:
			rng = self.rng
		else:
			rng = rng_to_use

		dipoles = []

		n = rng.binomial(self.n_max, self.prob_occupancy)

		for i in range(n):
			theta = numpy.arccos(rng.uniform(-1, 1))
			phi = rng.uniform(0, 2 * numpy.pi)
			px = self.pfixed * numpy.sin(theta) * numpy.cos(phi)
			py = self.pfixed * numpy.sin(theta) * numpy.sin(phi)
			pz = self.pfixed * numpy.cos(theta)
			s_pts = numpy.array(
				(
					rng.uniform(self.xmin, self.xmax),
					rng.uniform(self.ymin, self.ymax),
					rng.uniform(self.zmin, self.zmax),
				)
			)
			frequency = rng.uniform(0, max_frequency)

			dipoles.append(
				OscillatingDipole(numpy.array([px, py, pz]), s_pts, frequency)
			)
		return OscillatingDipoleArrangement(dipoles)

	def get_monte_carlo_dipole_inputs(
		self,
		monte_carlo_n: int,
		max_frequency: float,
		rng_to_use: numpy.random.Generator = None,
	) -> numpy.ndarray:

		rng: numpy.random.Generator
		if rng_to_use is None:
			rng = self.rng
		else:
			rng = rng_to_use

		shape = (monte_carlo_n, self.n_max)
		theta = 2 * numpy.pi * rng.random(shape)
		phi = numpy.arccos(2 * rng.random(shape) - 1)

		p_mask = rng.binomial(1, self.prob_occupancy, shape)
		p_magnitude = self.pfixed * p_mask

		px = p_magnitude * numpy.cos(theta) * numpy.sin(phi)
		py = p_magnitude * numpy.sin(theta) * numpy.sin(phi)
		pz = p_magnitude * numpy.cos(phi)

		sx = rng.uniform(self.xmin, self.xmax, shape)
		sy = rng.uniform(self.ymin, self.ymax, shape)
		sz = rng.uniform(self.zmin, self.zmax, shape)

		w = rng.uniform(1, max_frequency, shape)

		return numpy.stack([px, py, pz, sx, sy, sz, w], axis=-1)
