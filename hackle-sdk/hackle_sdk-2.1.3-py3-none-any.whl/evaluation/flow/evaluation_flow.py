from hackle.decision import DecisionReason
from hackle.evaluation.evaluator import Evaluation


class EvaluationFlow(object):

    def __init__(self, flow_evaluator=None, next_flow=None):
        self.flow_evaluator = flow_evaluator
        self.next_flow = next_flow

    def evaluate(self, workspace, experiment, user, default_variation_key):
        if self.is_end():
            return Evaluation.of(experiment, default_variation_key, DecisionReason.TRAFFIC_NOT_ALLOCATED)
        else:
            return self.flow_evaluator.evaluate(workspace, experiment, user, default_variation_key, self.next_flow)

    def is_end(self):
        return self.flow_evaluator is None or self.next_flow is None

    @staticmethod
    def of(*flow_evaluators):
        flow = EvaluationFlow()
        for flow_evaluator in reversed(flow_evaluators):
            flow = EvaluationFlow(flow_evaluator, flow)
        return flow
