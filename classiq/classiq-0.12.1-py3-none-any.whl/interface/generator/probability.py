import secrets
from typing import Tuple


def random_probability(options_count: int) -> Tuple[float, ...]:
    random_generator = secrets.SystemRandom()
    random_numbers = tuple(
        random_generator.uniform(0, 10) for _ in range(options_count)
    )

    total = sum(random_numbers)
    assert total != 0, "Error creating random probability."

    return tuple(i / total for i in random_numbers)
