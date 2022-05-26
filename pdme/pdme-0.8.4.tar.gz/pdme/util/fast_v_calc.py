import numpy
import logging


_logger = logging.getLogger(__name__)


def fast_vs_for_dipoles(
	dot_inputs: numpy.ndarray, dipoles: numpy.ndarray
) -> numpy.ndarray:
	"""
	No error correction here baby.
	Expects dot_inputs to be numpy array of [rx, ry, rz, f] entries, so a n by 4 where n is number of measurement points.
	"""
	ps = dipoles[:, 0:3]
	ss = dipoles[:, 3:6]
	ws = dipoles[:, 6]

	_logger.debug(f"ps: {ps}")
	_logger.debug(f"ss: {ss}")
	_logger.debug(f"ws: {ws}")

	rs = dot_inputs[:, 0:3]
	fs = dot_inputs[:, 3]

	diffses = rs - ss[:, None]

	_logger.debug(f"diffses: {diffses}")
	norms = numpy.linalg.norm(diffses, axis=2) ** 3
	_logger.debug(f"norms: {norms}")
	ases = (numpy.einsum("...ji, ...i", diffses, ps) / norms) ** 2
	_logger.debug(f"ases: {ases}")

	bses = (1 / numpy.pi) * (ws[:, None] / (fs**2 + ws[:, None] ** 2))
	_logger.debug(f"bses: {bses}")
	return ases * bses


def fast_vs_for_dipoleses(
	dot_inputs: numpy.ndarray, dipoleses: numpy.ndarray
) -> numpy.ndarray:
	"""
	No error correction here baby.
	Expects dot_inputs to be numpy array of [rx, ry, rz, f] entries, so a n by 4 where n is number of measurement points.

	Dipoleses are expected to be array of arrays of arrays: list of sets of dipoles which are part of a single arrangement to be added together.
	"""
	ps = dipoleses[:, :, 0:3]
	ss = dipoleses[:, :, 3:6]
	ws = dipoleses[:, :, 6]

	_logger.debug(f"ps: {ps}")
	_logger.debug(f"ss: {ss}")
	_logger.debug(f"ws: {ws}")

	rs = dot_inputs[:, 0:3]
	fs = dot_inputs[:, 3]

	diffses = rs[:, None] - ss[:, None, :]

	_logger.debug(f"diffses: {diffses}")
	norms = numpy.linalg.norm(diffses, axis=3) ** 3
	_logger.debug(f"norms: {norms}")
	ases = (numpy.einsum("abcd,acd->abc", diffses, ps) / norms) ** 2
	_logger.debug(f"ases: {ases}")

	bses = (1 / numpy.pi) * (ws[:, None, :] / (fs[:, None] ** 2 + ws[:, None, :] ** 2))
	_logger.debug(f"bses: {bses}")
	return numpy.einsum("...j->...", ases * bses)


def between(a: numpy.ndarray, low: numpy.ndarray, high: numpy.ndarray) -> numpy.ndarray:
	"""
	Intended specifically for the case where a is a list of arrays, and each array must be between the single array low and high, but without error checking.
	"""
	return numpy.all(numpy.logical_and(low < a, high > a), axis=1)
