import numpy
import numpy.typing
import itertools
from typing import Sequence, Tuple


def inputs_with_frequency_range(
	dots: Sequence[numpy.typing.ArrayLike], frequency_range: Sequence[float]
) -> Sequence[Tuple[numpy.typing.ArrayLike, float]]:
	return list(itertools.chain(*[[(dot, f) for f in frequency_range] for dot in dots]))


def input_pairs_with_frequency_range(
	dots: Sequence[numpy.typing.ArrayLike], frequency_range: Sequence[float]
) -> Sequence[Tuple[numpy.typing.ArrayLike, numpy.typing.ArrayLike, float]]:
	all_pairs = itertools.combinations(dots, 2)
	return list(
		itertools.chain(
			*[[(dot1, dot2, f) for f in frequency_range] for (dot1, dot2) in all_pairs]
		)
	)
