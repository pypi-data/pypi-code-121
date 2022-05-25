from typing import Optional, Union

from text_selection_core.validation import ValidationErrBase

Success = bool
ChangedAnything = bool

#ExecutionResult = Tuple[Success, Optional[ChangedAnything]]
ExecutionResult = Union[ValidationErrBase, Optional[ChangedAnything]]
