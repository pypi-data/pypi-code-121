import numpy.typing
from typing import Tuple, Sequence, Union
from pdme.measurement.dot_measure import DotRangeMeasurement
from pdme.measurement.dot_pair_measure import DotPairRangeMeasurement


DotInput = Tuple[numpy.typing.ArrayLike, float]
DotPairInput = Tuple[numpy.typing.ArrayLike, numpy.typing.ArrayLike, float]


def dot_inputs_to_array(dot_inputs: Sequence[DotInput]) -> numpy.ndarray:
	return numpy.array(
		[numpy.append(numpy.array(input[0]), input[1]) for input in dot_inputs]
	)


def dot_pair_inputs_to_array(pair_inputs: Sequence[DotPairInput]) -> numpy.ndarray:
	return numpy.array(
		[
			[
				numpy.append(numpy.array(input[0]), input[2]),
				numpy.append(numpy.array(input[1]), input[2]),
			]
			for input in pair_inputs
		]
	)


def dot_range_measurements_low_high_arrays(
	dot_range_measurements: Union[
		Sequence[DotRangeMeasurement], Sequence[DotPairRangeMeasurement]
	]
) -> Tuple[numpy.ndarray, numpy.ndarray]:
	lows = [measurement.v_low for measurement in dot_range_measurements]
	highs = [measurement.v_high for measurement in dot_range_measurements]
	return (numpy.array(lows), numpy.array(highs))
