import abc
import logging
from typing import Optional

from cosapp.drivers.runonce import RunOnce

logger = logging.getLogger(__name__)


class IterativeCase(RunOnce):
    """Abstract interface to children cases for a :py:class:`~cosapp.drivers.abstractsolver.AbstractSolver`.

    Parameters
    ----------
    name: str, optional
        Name of the `Module`
    owner : System, optional
        :py:class:`~cosapp.systems.system.System` to which driver belongs; defaults to `None`
    **kwargs : Dict[str, Any]
        Optional keywords arguments
    """

    __slots__ = ()

    def __init__(self,
        name: str,
        owner: Optional["cosapp.systems.System"] = None,
        **kwargs
    ) -> None:
        """Initialize a driver

        Parameters
        ----------
        name: str, optional
            Name of the `Driver`.
        owner: System, optional
            :py:class:`~cosapp.systems.system.System` to which this driver belong; defaults to `None`.
        **kwargs:
            Additional keywords arguments forwarded to base class.
        """
        super().__init__(name, owner, **kwargs)
        self.reset_problem()

    def _set_owner(self, system: Optional["cosapp.systems.System"]) -> bool:
        defined = self.owner is not None
        changed = super()._set_owner(system)
        if changed:
            self.reset_problem()
            if defined:
                logger.warning(
                    f"System owner of Driver {self.name!r} has changed. Mathematical problem has been cleared."
                )

    @abc.abstractmethod
    def reset_problem(self) -> None:
        """Reset mathematical problem(s) defined on case."""
        pass

    def _postcompute(self) -> None:
        """Actions to carry out after the :py:meth:`~cosapp.drivers.runonce.RunOnce.compute` method call.

        This gathers the residues for this point and undo the variable status changes
        """
        # Request the residues of the current case to be updated
        for residue in self.get_problem().residues.values():
            residue.update()

        super()._postcompute()

    # TODO No longer needed after the suppression of RunOptim -> integrate with RunSingleCase
