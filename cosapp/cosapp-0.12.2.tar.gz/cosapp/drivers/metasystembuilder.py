from collections import OrderedDict
from typing import Any, Dict, List, Set, Type, Union, Optional

from cosapp.recorders import DataFrameRecorder
from cosapp.systems import MetaSystem
from cosapp.utils.surrogate_models import ResponseSurface
from cosapp.drivers.driver import Driver
from cosapp.drivers.lineardoe import LinearDoE
from cosapp.drivers.nonlinearsolver import NonLinearSolver


# TODO
# [ ] Quid for vector variables
# [ ] Simplify the builder by using inputs and outputs of the targeted system.
class MetaSystemBuilder(Driver):

    __slots__ = ('responses', 'model_type', '_metasystem')

    def __init__(
        self,
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

        self.responses = set()  # type: Set[str]
        self.model_type = ResponseSurface  # type: Type
        self._metasystem = None  # type: cosapp.systems.MetaSystem

        self.add_child(LinearDoE("doe"))
        self.doe.add_child(NonLinearSolver("solve"))

    def compute(self):
        includes = list(self.doe.input_vars)
        includes.extend(self.responses)
        self.doe.add_recorder(DataFrameRecorder(raw_output=True, includes=includes))
        self.doe.run_once()

        class MyMeta(MetaSystem):
            def setup(self, model_type=ResponseSurface, ref_model=None):
                self._default_model = model_type

                if ref_model:
                    self.inputs = OrderedDict(ref_model.inputs)
                    self.outputs = OrderedDict(ref_model.outputs)

        self._metasystem = MyMeta(
            "meta",
            self.doe.recorder.export_data(),
            model_type=self.model_type,
            ref_model=self.owner,
        )

    def add_input_var(
        self,
        definition: Union[str, Dict[str, Any]],
        lower: float = None,
        upper: float = None,
        count: int = 2,
    ):
        self.doe.add_input_var(definition, lower, upper, count)

    def add_response(self, name: Union[str, List[str]]):

        if not isinstance(name, (str, list)):
            raise TypeError(
                f"'name' should be a string or a list of strings; got {type(name).__name__}."
            )

        def add_unique_response_var(name: str):
            self.check_owner_attr(name)
            self.responses.add(name)

        if isinstance(name, str):
            add_unique_response_var(name)
        else:
            for n in name:
                if isinstance(n, str):
                    add_unique_response_var(n)
                else:
                    raise TypeError(
                        f"name list should only contain strings; got {type(n).__name__}."
                    )
