import numpy
import numpy.random
from pdme.measurement import (
	OscillatingDipoleArrangement,
)
import logging


_logger = logging.getLogger(__name__)


class DipoleModel:
	"""
	Interface for models based on dipoles.
	Some concepts are kept specific for dipole-based models, even though other types of models could be useful later on.
	"""

	def get_dipoles(
		self, max_frequency: float, rng: numpy.random.Generator = None
	) -> OscillatingDipoleArrangement:
		"""
		For a particular maximum frequency, gets a dipole arrangement based on the model that uniformly distributes its choices according to the model.
		If no rng is passed in, uses some default, but you might not want that.
		Frequencies should be chosen uniformly on range of (0, max_frequency).
		"""
		raise NotImplementedError

	def get_monte_carlo_dipole_inputs(
		self, n: int, max_frequency: float, rng: numpy.random.Generator = None
	) -> numpy.ndarray:
		"""
		For a given DipoleModel, gets a set of dipole collections as a monte_carlo_n x dipole_count x 7 numpy array.
		"""
		raise NotImplementedError
