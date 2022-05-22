import numpy
import logging


_logger = logging.getLogger(__name__)


def fast_s_nonlocal(
	dot_pair_inputs: numpy.ndarray, dipoles: numpy.ndarray
) -> numpy.ndarray:
	"""
	No error correction here baby.
	"""
	ps = dipoles[:, 0:3]
	ss = dipoles[:, 3:6]
	ws = dipoles[:, 6]

	_logger.debug(f"ps: {ps}")
	_logger.debug(f"ss: {ss}")
	_logger.debug(f"ws: {ws}")

	r1s = dot_pair_inputs[:, 0, 0:3]
	r2s = dot_pair_inputs[:, 1, 0:3]
	f1s = dot_pair_inputs[:, 0, 3]
	f2s = dot_pair_inputs[:, 1, 3]

	if (f1s != f2s).all():
		raise ValueError(f"Dot pair frequencies are inconsistent: {dot_pair_inputs}")

	diffses1 = r1s - ss[:, None]
	diffses2 = r2s - ss[:, None]
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"diffses1: {diffses1}")
		_logger.debug(f"diffses2: {diffses2}")

	norms1 = numpy.linalg.norm(diffses1, axis=2) ** 3
	norms2 = numpy.linalg.norm(diffses2, axis=2) ** 3
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"norms1: {norms1}")
		_logger.debug(f"norms2: {norms2}")

	alphses1 = numpy.einsum("...ji, ...i", diffses1, ps) / norms1
	alphses2 = numpy.einsum("...ji, ...i", diffses2, ps) / norms2
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"alphses1: {alphses1}")
		_logger.debug(f"alphses2: {alphses2}")

	bses = (1 / numpy.pi) * (ws[:, None] / (f1s**2 + ws[:, None] ** 2))
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"bses: {bses}")

	return alphses1 * alphses2 * bses


def fast_s_nonlocal_dipoleses(
	dot_pair_inputs: numpy.ndarray, dipoleses: numpy.ndarray
) -> numpy.ndarray:
	"""
	No error correction here baby.
	"""
	ps = dipoleses[:, :, 0:3]
	ss = dipoleses[:, :, 3:6]
	ws = dipoleses[:, :, 6]

	_logger.debug(f"ps: {ps}")
	_logger.debug(f"ss: {ss}")
	_logger.debug(f"ws: {ws}")

	r1s = dot_pair_inputs[:, 0, 0:3]
	r2s = dot_pair_inputs[:, 1, 0:3]
	f1s = dot_pair_inputs[:, 0, 3]
	f2s = dot_pair_inputs[:, 1, 3]

	if (f1s != f2s).all():
		raise ValueError(f"Dot pair frequencies are inconsistent: {dot_pair_inputs}")

	diffses1 = r1s[:, None] - ss[:, None, :]
	diffses2 = r2s[:, None] - ss[:, None, :]
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"diffses1: {diffses1}")
		_logger.debug(f"diffses2: {diffses2}")

	norms1 = numpy.linalg.norm(diffses1, axis=3) ** 3
	norms2 = numpy.linalg.norm(diffses2, axis=3) ** 3
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"norms1: {norms1}")
		_logger.debug(f"norms2: {norms2}")

	alphses1 = numpy.einsum("abcd,acd->abc", diffses1, ps) / norms1
	alphses2 = numpy.einsum("abcd,acd->abc", diffses2, ps) / norms2
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"alphses1: {alphses1}")
		_logger.debug(f"alphses2: {alphses2}")

	bses = (1 / numpy.pi) * (ws[:, None, :] / (f1s[:, None] ** 2 + ws[:, None, :] ** 2))
	if _logger.isEnabledFor(logging.DEBUG):
		_logger.debug(f"bses: {bses}")

	_logger.debug(f"Raw pair calc: [{alphses1 * alphses2 * bses}]")
	return numpy.einsum("...j->...", alphses1 * alphses2 * bses)
