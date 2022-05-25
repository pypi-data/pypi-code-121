class Evaluation(object):
    def __init__(self, variation_id, variation_key, reason):
        self.variation_id = variation_id
        self.variation_key = variation_key
        self.reason = reason

    def __eq__(self, o):
        if isinstance(o, self.__class__):
            return self.__dict__ == o.__dict__
        else:
            return False

    def __str__(self):
        return 'Evaluation(variation_id={}, variation_key={}, reason={})'.format(self.variation_id,
                                                                                 self.variation_key,
                                                                                 self.reason)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def with_key(variation_key, reason):
        return Evaluation(variation_id=None, variation_key=variation_key, reason=reason)

    @staticmethod
    def with_variation(variation, reason):
        return Evaluation(variation_id=variation.id, variation_key=variation.key, reason=reason)

    @staticmethod
    def of(experiment, variation_key, reason):
        variation = experiment.get_variation_by_key_or_none(variation_key)
        if variation:
            return Evaluation.with_variation(variation, reason)
        else:
            return Evaluation.with_key(variation_key, reason)


class Evaluator(object):

    def __init__(self, evaluation_flow_factory):
        self.evaluation_flow_factory = evaluation_flow_factory

    def evaluate(self, workspace, experiment, user, default_variation_key):
        evaluation_flow = self.evaluation_flow_factory.get_evaluation_flow(experiment.type)
        return evaluation_flow.evaluate(workspace, experiment, user, default_variation_key)
