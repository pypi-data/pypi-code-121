from typing import Optional

from sym.sdk.templates import ApprovalTemplateStep


def get_step_output(step: Optional[ApprovalTemplateStep] = None) -> dict:
    """
    Returns the output returned by the specified step (or the current step if no step is specified).

    For Lambda flows, this method can be used in `after_escalate` and `after_deescalate` hooks
    to retrieve responses from the lambda.

    For example::

        @hook
        def after_escalate(evt):
            escalate_output = get_step_output()
            print(escalate_output["body"])

    For :class:`custom Strategies <sym.sdk.strategies.access_strategy.AccessStrategy>`, this method
    can be used in :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.deescalate` to retrieve
    the output from the corresponding escalation by specifying the
    :class:`ApprovalTemplateStep.ESCALATE <sym.sdk.templates.approval.ApprovalTemplateStep>` step::

        def deescalate(self, target_id, event):
            escalate_output = get_step_output(ApprovalTemplateStep.ESCALATE)
            escalation_id = escalate_output["id"]
            ...

    Args:
        step: The step for which to retrieve output. If ``None`` or omitted, returns the output for
            the current step.
    """
