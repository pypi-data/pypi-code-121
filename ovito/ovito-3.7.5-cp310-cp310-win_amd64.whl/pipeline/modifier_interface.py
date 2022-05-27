import ovito
import ovito.pipeline
from ..data import DataCollection
from ..modifiers import PythonScriptModifier
#from ..nonpublic import OvitoObjectWeakRef
import abc
import traits.api
from typing import List, Mapping

class ModifierInterface(traits.api.ABCHasStrictTraits):
    # Internal reference to the PythonScriptModifier object that owns this ModifierInterface instance:
    # _owner = traits.api.Instance(OvitoObjectWeakRef, allow_none=False, transient=True, required=True)
    
    # The number of additional input pipeline slots used by the modifier.
    extra_input_slots = traits.api.Range(low=0, transient=True, visible=False)

    # Import the InputSlot helper class into the namespace.
    InputSlot = PythonScriptModifier.InputSlot

    # Abstract methods that can be implemented by sub-classes:
    #
    # def output_frame_count(self, input_slots: List[InputSlot]) -> int: ...
    # def input_frame_cache(self, output_frame: int, input_slots: List[InputSlot]) -> Mapping[InputSlot, Union[int, Sequence[int]]]: ...
 
    # Method that must be implemented by sub-classes:
    @abc.abstractmethod
    def modify(self, data: DataCollection, *, frame: int, input_slots: List[InputSlot], data_cache: DataCollection, **kwargs) -> None:
        raise NotImplementedError
 
ovito.pipeline.ModifierInterface = ModifierInterface