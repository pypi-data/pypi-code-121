from alira.instance import Instance
from alira.modules import module

PIPELINE_MODULE_NAME = "flagging"


class Flagging(module.Module):
    """This module optimizes the decision of routing instances to a human
    using a threshold.

    Any instance with a confidence below the threshold will be sent for
    human review.

    Args:
        threshold(float): The minimum confidence threshold that will be
            considered to not flag this instance.
    """

    def __init__(
        self,
        threshold: float = 0.6,
        **kwargs,
    ):
        super().__init__(
            module_id=PIPELINE_MODULE_NAME,
            **kwargs,
        )
        self.threshold = threshold

    def run(self, instance: dict, **kwargs):
        confidence = instance.confidence
        return {"flagged": int(confidence < self.threshold)}


class CostSensitiveFlagging(module.Module):
    """This module optimizes the decision of routing instances to a human
    using cost sensitivity criteria to reduce the cost of mistakes.

    Instances can overwrite the false positive, false negative, and human
    review costs used by this module by specifying a value for the `fp_cost`,
    `fn_cost`, and `human_review_cost` attributes::

        instance.metadata['flagging']['fp_cost'] = 100
        instance.metadata['flagging']['fn_cost'] = 300
        instance.metadata['flagging']['human_review_cost'] = 10

    The costs specified as part of the instance will always be used over
    the costs specified for this module.

    Args:
        fp_cost(float): The cost of a false positive prediction. This argument
            is optional and when not specified the module will assume the cost
            is `0`.
        fn_cost(float): The cost of a false negative prediction. This argument
            is optional and when not specified the module will assume the cost
            is `0`.
        human_review_cost(float): The cost of a human review. This argument is
            optional and when not specified the module will assume the cost
            is `0`.
    """

    def __init__(
        self,
        fp_cost: float = None,
        fn_cost: float = None,
        human_review_cost: float = None,
        **kwargs,
    ):
        super().__init__(
            module_id=PIPELINE_MODULE_NAME,
            **kwargs,
        )

        self.fp_cost = fp_cost or 0
        self.fn_cost = fn_cost or 0
        self.human_review_cost = human_review_cost or 0

    def run(self, instance: Instance, **kwargs):
        """Processes the supplied instance and returns a field indicating
        whether the instance should be sent for human review together with
        the computed costs.

        Args:
            instance(dict): The instance that should be processed.
        """

        # If the instance comes with specific costs, we want to use those
        # instead of the costs specified on this module.
        fp_cost = instance.get_attribute(
            f"metadata.{PIPELINE_MODULE_NAME}.fp_cost", default=self.fp_cost
        )
        fn_cost = instance.get_attribute(
            f"metadata.{PIPELINE_MODULE_NAME}.fn_cost", default=self.fn_cost
        )
        human_review_cost = instance.get_attribute(
            f"metadata.{PIPELINE_MODULE_NAME}.human_review_cost",
            default=self.human_review_cost,
        )

        prediction = instance.prediction
        confidence = instance.confidence

        cost_prediction_positive = (1 - confidence) * fp_cost
        cost_prediction_negative = confidence * fn_cost

        # Let's compute the likelihood of being wrong times the cost of
        # making a mistake. If that cost is higher than the cost of asking
        # for help, let's ask for a human review.
        if (prediction == 1 and cost_prediction_positive > human_review_cost) or (
            prediction == 0 and cost_prediction_negative > human_review_cost
        ):
            return {
                "flagged": 1,
                "cost_prediction_positive": cost_prediction_positive,
                "cost_prediction_negative": cost_prediction_negative,
            }

        # At this point there's no upside to ask for a human review,
        # so let's continue without asking for help.
        return {
            "flagged": 0,
            "cost_prediction_positive": cost_prediction_positive,
            "cost_prediction_negative": cost_prediction_negative,
        }
