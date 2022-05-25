from typing import Optional, Union

from text_selection_core.validation import ValidationErr

TQDM_LINE_UNIT = " line(s)"

ChangedAnything = bool
#ExecutionResult = Tuple[Optional[ValidationError], ChangedAnything]
ExecutionResult = Union[ValidationErr, Optional[ChangedAnything]]
