from typing import Tuple, Union

import numpy as np
from scipy.stats import rv_continuous

DistArg = Union[np.float64, np.ndarray, float, int]


def truncated(dist: rv_continuous) -> rv_continuous:
    class _Truncated(rv_continuous):
        def _pdf(self, x: DistArg, *args) -> DistArg:
            # The density function is the original density function restricted to the
            # allowed interval and rescaled such that the integral is 1 again.
            *args, trunc_min, trunc_max = args
            args = map(np.asarray, args)
            scale = 1 / (dist.cdf(trunc_max, *args) - dist.cdf(trunc_min, *args))
            in_intervall = (x >= trunc_min) & (x <= trunc_max)
            return dist.pdf(x, *args) * scale * in_intervall

        def _cdf(self, x: DistArg, *args) -> DistArg:
            *args, trunc_min, trunc_max = args
            scale = 1 / (dist.cdf(trunc_max, *args) - dist.cdf(trunc_min, *args))
            cdf_min = dist.cdf(trunc_min, *args)
            # For value in the intervall we simply have to rescale and reposition the known cdf
            res = scale * (dist.cdf(x, *args) - cdf_min)
            # For value below the min we set the value to 0
            res = res * (x >= trunc_min)
            # For values above the max we set the value to 1
            res = np.minimum(res, 1)
            return res

        def _sf(self, x: DistArg, *args) -> DistArg:
            # The survivial function works analogously to the cdf
            *args, trunc_min, trunc_max = args
            scale = 1 / (dist.cdf(trunc_max, *args) - dist.cdf(trunc_min, *args))
            sf_max = dist.sf(trunc_max, *args)
            res = scale * (dist.sf(x, *args) - sf_max)
            res = res * (x <= trunc_max)
            res = np.minimum(res, 1)
            return res

        def _ppf(self, q: DistArg, *args) -> DistArg:
            *args, trunc_min, trunc_max = args
            scale = 1 / (dist.cdf(trunc_max, *args) - dist.cdf(trunc_min, *args))
            cdf_min = dist.cdf(trunc_min, *args)
            return dist.ppf(q / scale + cdf_min, *args)

        def _get_support(self, *args) -> Tuple[DistArg, DistArg]:
            *args, trunc_min, trunc_max = args
            args = map(np.asarray, args)
            dist_min, dist_max = dist.support(*args)
            return (np.maximum(dist_min, trunc_min), np.minimum(dist_max, trunc_max))

        def _argcheck(self, *args) -> Union[bool, np.ndarray]:
            *args, trunc_min, trunc_max = args
            return dist._argcheck(*args) & (
                dist.cdf(trunc_max, *args) > dist.cdf(trunc_min, *args)
            )

        def __repr__(self) -> str:
            return f"Truncated {dist.name} distribution"

    if dist.shapes is not None:
        shapes = f"{dist.shapes}, trunc_min, trunc_max"
    else:
        shapes = "trunc_min, trunc_max"
    return _Truncated(
        name=f"truncated_{dist.name}",
        shapes=shapes,
        a=dist.a,
        b=dist.b,
        badvalue=dist.badvalue,
        xtol=dist.xtol,
        momtype=dist.moment_type,
    )
