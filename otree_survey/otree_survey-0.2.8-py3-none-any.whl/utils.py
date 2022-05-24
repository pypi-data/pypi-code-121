import random
from typing import List

from .views import ProgressItem


def update_progress(progress: List[ProgressItem], section: str, width: int = 100):
    """Update a progress bar, by setting the width of all sections before `section` to 100,
    the width of `section` to `width` and the width of all the following sections to 0."""
    past_current = False
    for i, p in enumerate(progress):
        if p.title == section:
            progress[i].width = width
            past_current = True
        elif not past_current:
            progress[i].width = 100
        else:
            progress[i].width = 0
    return progress


def randomize_order(player, field):
    order = getattr(player, field)
    assert order, f"field {field} has to be non-empty for randomization"
    order = order.split()
    assert (
        len(order) > 1
    ), f"field {field} has to have format `value1 value2 [value3 […]]` for randomization"
    random.shuffle(order)
    setattr(player, field, " ".join(order))
