from dataclasses import dataclass

EMPTY = 'EMPTY'
SUCCESS = 'SCS'
FAILURE = 'FAIL'


@dataclass
class Result:
    EMPTY: str = EMPTY
    SUCCESS: str = SUCCESS
    FAILURE: str = FAILURE


RESULT_CHOICES = (
    (EMPTY, EMPTY),
    (FAILURE, FAILURE),
    (SUCCESS, SUCCESS),
)
