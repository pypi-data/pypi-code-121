"""
.. todo:: Decide where to put all owa related functions
"""

from math import log
from typing import List, cast

from ..core.aliases import (
    NumericPerformanceTable,
    NumericValue,
    PerformanceTable,
    Value,
)
from ..core.functions import FuzzyNumber
from ..core.performance_table import (
    apply_criteria_weights,
    normalize,
    sum_table,
)
from ..core.scales import FuzzyScale, Scale
from ..core.sets import difference, index_to_set
from ..core.sorting import sort_elements_by_values


def normalized_weighted_sum(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
) -> List[NumericValue]:
    """Compute alternatives values as weighted sum of normalized alternatives'
    performances.

    :param performance_table:
    :param criteria_weights:
    :return: alternatives values
    """
    weighted_table = cast(
        PerformanceTable,
        apply_criteria_weights(performance_table, criteria_weights),
    )
    res = sum_table(weighted_table, axis=1)
    res = cast(List[NumericValue], res)
    return res


def weighted_sum(
    performance_table: PerformanceTable,
    criteria_scales: List[Scale],
    criteria_weights: List[NumericValue],
) -> List[NumericValue]:
    """Compute alternatives values as weighted sum of alternatives'
    performances.

    :param performance_table:
    :param criteria_scales:
    :param criteria_weights:
    :return: alternatives values
    """
    normalized_table = normalize(performance_table, criteria_scales)
    weighted_table = cast(
        PerformanceTable,
        apply_criteria_weights(normalized_table, criteria_weights),
    )
    res = sum_table(weighted_table, axis=1)
    res = cast(List[NumericValue], res)
    return res


def choquet_integral_capacity(
    values: List[NumericValue], capacity: List[NumericValue]
) -> NumericValue:
    """Return Choquet integral using a capacity.

    :param values:
    :param capacity:
    :return:

    .. note:: Implementation is based on :cite:p:`grabisch2008review`.
    """
    permutation = [*range(len(values))]
    sort_elements_by_values(values, permutation, reverse=True)
    index = len(capacity) - 1
    res = 0
    for i in permutation:
        next_index = difference(index, 2 ** i)
        res += values[i] * (capacity[index] - capacity[next_index])
        index = next_index
    return res


def choquet_integral_mobius(
    values: List[NumericValue], mobius: List[NumericValue]
) -> NumericValue:
    """Return Choquet integral using a möbius.

    :param values:
    :param mobius:
    :return:

    .. note:: Implementation is based on :cite:p:`grabisch2008review`.
    """
    return sum(
        mobius[t] * min(index_to_set(t, values)) for t in range(1, len(mobius))
    )


def owa(
    values: List[NumericValue], weights: List[NumericValue]
) -> NumericValue:
    """Return Ordered Weighted Aggregation of values.

    :param values:
    :param weights:
    :return:

    .. note:: Implementation is based on :cite:p:`yager1988owa`
    """
    return sum(a * w for a, w in zip(sorted(values, reverse=True), weights))


def owa_and_weights(size: int) -> List[NumericValue]:
    """Return *and* OWA weights of given size.

    :param size:
    :return:

    .. note:: :math:`W_*` as defined in :cite:p:`yager1988owa`
    """
    return cast(List[NumericValue], [0] * (size - 1) + [1])


def owa_or_weights(size: int) -> List[NumericValue]:
    """Return *or* OWA weights of given size.

    :param size:
    :return:

    .. note:: :math:`W^*` as defined in :cite:p:`yager1988owa`
    """
    return cast(List[NumericValue], [1] + [0] * (size - 1))


def owa_weights_orness(weights: List[NumericValue]) -> NumericValue:
    """Return *orness* measure of OWA weights.

    :param weights:
    :retuen:

    .. note:: *orness* as defined in :cite:p:`yager1988owa`
    """
    return sum((len(weights) - i - 1) * w for i, w in enumerate(weights)) / (
        len(weights) - 1
    )


def owa_weights_andness(weights: List[NumericValue]) -> NumericValue:
    """Return *andness* measure of OWA weights.

    :param weights:
    :return:

    .. note:: *andness* as defined in :cite:p:`yager1988owa`
    """
    return 1 - owa_weights_orness(weights)


def owa_weights_dispersion(weights: List[NumericValue]) -> NumericValue:
    """Return OWA weights dispersion (also called entropy).

    :param weights:
    :return:

    .. note:: dispersion as defined in :cite:p:`yager1988owa`
    """
    return -sum(w * log(w) if w > 0 else 0 for w in weights)


def owa_weights_divergence(weights: List[NumericValue]) -> NumericValue:
    """Return OWA weights divergence.

    :param weights:
    :return:

    .. note:: divergence as defined in :cite:p:`yager2002heavy`
    """
    addition = 0.0
    j = 1
    n = len(weights)
    orness = owa_weights_orness(weights)
    for w in weights:
        operation = (((n - j) / (n - 1)) - orness) ** 2
        j = j + 1
        addition = addition + w * operation
    return addition


def owa_weights_balance(weights: List[NumericValue]) -> NumericValue:
    """Return OWA weights balance.

    :param weights:
    :return:

    .. note:: divergence as defined in :cite:p:`yager1996constrainedowa`
    """
    addition = 0.0
    j = 1
    n = len(weights)
    for w in weights:
        operation = (n + 1 - 2 * j) / (n - 1)
        j = j + 1
        addition = addition + w * operation
    return addition


def owa_weights_quantifier(weights: List[NumericValue]) -> List[NumericValue]:
    """Return quantifier corresponding to OWA weights.

    :param weights:
    :return:

    .. note:: quantifier as defined in :cite:p:`yager1988owa`
    """
    return [sum(w for w in weights[:i]) for i in range(len(weights) + 1)]


def quantifier_to_owa_weights(
    quantifier: List[NumericValue],
) -> List[NumericValue]:
    """Return OWA weights corresponding to given quantifier.

    :param quantifier:
    :return:

    .. note:: quantifier as defined in :cite:p:`yager1988owa`
    """
    return [q - q_1 for q, q_1 in zip(quantifier[1:], quantifier[:-1])]


def ulowa_delta(
    a: Value, b: Value, weight: NumericValue, scale: FuzzyScale
) -> NumericValue:
    """Returns ULOWA delta value.

    :param a: worst value
    :param b: best value
    :param weight: ULOWA weight
    :param scale: fuzzy scale
    :return:
    """
    xa = cast(NumericValue, scale.transform_to(a))
    xb = cast(NumericValue, scale.transform_to(b))
    return xa + weight * (xb - xa)


def ulowa_most_similar(
    a: Value, b: Value, ref_fuzzy: FuzzyNumber, scale: FuzzyScale
) -> Value:
    """Returns label which fuzzy number is the most similar to the reference
    (between `a` and `b` labels).

    :param a:
    :param b:
    :param ref_fuzzy: fuzzy number that is being compared to
    :param scale: fuzzy scale
    :return:
    """
    if scale.ordinal_distance(a, b) == 1:
        _labels = [a, b]
    else:
        _labels = sorted(
            scale.labels, key=lambda v: scale.transform_to(v), reverse=True
        )
        lmin = min(_labels.index(a), _labels.index(b))
        lmax = max(_labels.index(a), _labels.index(b))
        _labels = _labels[lmin : lmax + 1]
    sims = [
        scale.similarity(scale.fuzzy[scale.labels.index(v)], ref_fuzzy)
        for v in _labels
    ]
    return _labels[max(range(len(_labels)), key=lambda i: sims[i])]


def ulowa(
    values: List[Value], weights: List[NumericValue], scale: FuzzyScale
) -> Value:
    """Returns Unbalanced Linguistic Weighted Average of values.

    :param values:
    :param weights:
    :param scale: fuzzy scale
    :return:
    :raise ValueError: if `values` contains less than 2 items

    .. note:: implementation based on :cite:p:`isern2010ulowa`

    .. warning::
        this function is intended for use with a fuzzy scale defining a fuzzy
        partition
    """
    values = sorted(values, key=lambda v: scale.transform_to(v), reverse=True)
    weights = weights.copy()
    if len(values) == 0:
        raise ValueError("ULOWA needs at least one value")
    if len(values) == 1:
        return values[0]
    denominator = weights[-2] + weights[-1]
    weight = 0 if denominator == 0 else weights[-2] / denominator
    delta = ulowa_delta(values[-1], values[-2], weight, scale)
    values[-2] = ulowa_most_similar(
        values[-1], values[-2], FuzzyNumber([delta] * 4), scale
    )
    weights[-2] += weights[-1]
    return ulowa(values[:-1], weights[:-1], scale)
