import random

from alira.modules import module
from alira.instance import Instance

PIPELINE_MODULE_NAME = "selection"


class Selection(module.Module):
    """
    Selects a percentage of instances as they go through the pipeline and
    flags them for human review.

    Having a group of instances reviewed by humans gives the model
    a baseline understanding of its performance, and allows it to compute
    metrics that can later be extrapolated to all processed instances.

    To make sure the group of instances selected by this module is
    statistically valid, this implementation doesn't rely on any
    of the data attached to the instance to make a decision of whether it
    should be selected for review.

    Args:
        percentage(float): The percentage of instances that should be selected
            for human review. This attribute is optional, and if not specified,
            20% of the instances will be selected.

    Raises:
        ValueError: If `percentage` is either less than 0.0
        or greater than 1.0.
    """

    def __init__(self, percentage: float = 0.2, **kwargs):
        super().__init__(module_id=PIPELINE_MODULE_NAME)

        if percentage < 0.0 or percentage > 1.0:
            raise ValueError("The specified percentage should be between 0.0 and 1.0")

        self.percentage = percentage

    def run(self, instance: Instance, **kwargs):
        """
        Processes the supplied instances and set a boolean value indicating
        whether it should be selected for human review.

        Args:
            instance: The instance that should be processed.
        Returns:
            A dictionary containing a `selected` attribute that indicates
            whether the instance should be selected for review.
        """
        value = random.random()
        return {"selected": int(value < self.percentage)}
