from __future__ import annotations

__all__ = [
    "AbstractIntegrator",
]

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ...typing import Array, ArrayLike


class AbstractIntegrator(ABC):
    """Interface for integrators"""

    def __init__(self, rhs: Callable, y0: Union[Array, ArrayLike]) -> None:
        self.kwargs: Dict[str, Any] = {}
        self.rhs = rhs
        self.y0 = y0

    @abstractmethod
    def reset(self) -> None:
        """Reset the integrator and simulator state"""
        ...

    @abstractmethod
    def _simulate(
        self,
        *,
        t_end: Optional[float] = None,
        steps: Optional[int] = None,
        time_points: Optional[ArrayLike] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[ArrayLike], Optional[ArrayLike]]:
        ...

    @abstractmethod
    def _simulate_to_steady_state(
        self,
        *,
        tolerance: float,
        integrator_kwargs: Dict[str, Any],
        simulation_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[ArrayLike], Optional[ArrayLike]]:
        ...

    @abstractmethod
    def get_integrator_kwargs(self) -> Dict[str, Any]:
        """Get possible integration settings"""
        ...
