from dataclasses import dataclass
from math import exp, log
from types import SimpleNamespace

from respice.math.linalg import TaylorPolynomial
from .TwoTerminalCurrentComponent import TwoTerminalCurrentComponent


@dataclass(eq=False)
class LinearizedShockleyDiode(TwoTerminalCurrentComponent):
    """
    Describes an ideal Shockley Diode, linearized after a certain voltage `V_L`.

    Additionally to https://en.wikipedia.org/wiki/Diode_modelling#Shockley_diode_model, for better convergence this
    linearized diode model exists. Exponential terms grow too big too fast and often prevent convergence of the
    solution. A very accurate approximation can be made by linearizing or Taylor-expanding the equations after a certain
    linearization threshold voltage where the curve only grows linearly. So if you encounter convergence problems
    because you have used diodes that are caused by overflow errors or bad convergence properties, this linearized model
    might want you want to use.

    For the pure ideal model, see `respice.components.ShockleyDiode`.

    i_s:
        Reverse bias saturation current (also known as leakage current).
        Depending on the material used, common values are
        * silicon diodes: usually between 10^-12 A and 10^-10 A (1uA to 100uA).
        * germanium diodes: about 10^-4 A (0.1mA)
    v_t:
        Thermal voltage V_T. For approximate room temperate 300K this value
        is 25.85mV (0.02585V). This is default.
    n:
        Ideality factor (also known as quality factor). By default 1.
    dv_th:
        The threshold gradient at which the voltage is linearized / Taylor-expanded (a.k.a. differential resistance).
    order:
        Order :math:`k` of Taylor-expansion to be used behind the threshold voltage.
    """
    i_s: float = 1e-12
    v_t: float = 0.02585
    n: float = 1.0
    dv_th: float = 10000.0
    order: int = 2

    def __post_init__(self):
        super().__post_init__()

        self._cache = SimpleNamespace()
        self._cache.taylor_expansion = SimpleNamespace()
        self._cache.taylor_expansion.key = None
        self._cache.taylor_expansion.value = None

    @property
    def v_th(self):
        return log(self.dv_th * self.v_t / self.i_s) * self.v_t

    def get_ideal_current(self, v: float):
        return self.i_s * (exp(v / (self.n * self.v_t)) - 1)

    def get_ideal_current_derivative(self, v: float, d: int = 1):
        return self.i_s / (self.n * self.v_t)**d * exp(v / (self.n * self.v_t))

    def _get_taylor_expansion(self):
        cachekey = (self.i_s, self.v_t, self.n, self.dv_th, self.order)
        if cachekey is self._cache.taylor_expansion.key:
            return self._cache.taylor_expansion.value

        v_th = self.v_th
        taylor = TaylorPolynomial(
            (
                [self.get_ideal_current(v_th)] +
                [self.get_ideal_current_derivative(v_th, d=i + 1) for i in range(self.order)]
            ),
            v_th,
        )

        self._cache.taylor_expansion.value = taylor
        self._cache.taylor_expansion.key = cachekey

        return taylor

    def get_current(self, v: float, t1: float, t2: float) -> float:
        return (self.get_ideal_current(v)
                if v <= self.v_th else
                self._get_taylor_expansion()(v))

    def get_jacobian(self, v: float, t1: float, t2: float) -> float:
        return (self.get_ideal_current_derivative(v)
                if v <= self.v_th else
                self._get_taylor_expansion().derivate()(v))
