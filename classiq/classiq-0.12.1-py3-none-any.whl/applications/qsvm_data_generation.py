import logging
from collections import defaultdict
from typing import Dict, Optional, Tuple

import numpy as np

_logger = logging.getLogger(__name__)


def generate_data(
    dimension: int = 2,
    amount: int = 20,
    amount_of_sources: int = 2,
    range_min: float = 0,
    range_max: float = 2 * np.pi,
    std: float = 0.5,
    sources: Optional[np.ndarray] = None,
) -> Dict[int, np.ndarray]:
    if sources is None:
        sources = np.random.uniform(
            range_min, range_max, (amount_of_sources, dimension)
        )
    _logger.debug("Generating data around: %s", sources)

    results = {}
    for index, s in enumerate(sources):
        temp = []
        # for each dimension
        for point in s:
            # draw from a gaussian distribution
            temp.append(np.random.normal(point, std, amount))
        # combine the list of np.arrays
        results[index] = np.array(list(zip(*temp)))

    for r in results.values():
        r[r > range_max] = range_max
        r[r < range_min] = range_min

    return results


def data_dict_to_data_and_labels(data_dict: dict) -> Tuple[np.ndarray, np.ndarray]:
    data = []
    labels = []
    for k, v in data_dict.items():
        for i in v:
            labels.append(k)
            data.append(i)
    return np.array(data), np.array(labels)


def data_and_labels_to_data_dict(data: np.ndarray, labels: np.ndarray) -> dict:
    data_dict = defaultdict(list)
    for i, k in zip(data, labels):
        data_dict[k].append(i)
    # Convert the lists to np.array
    for k in data_dict:
        data_dict[k] = np.array(data_dict[k])  # type: ignore[assignment]
    return dict(data_dict)
