from hackle.entities import RunningExperiment


class ExperimentTargetDeterminer(object):
    def __init__(self, target_matcher):
        self.target_matcher = target_matcher

    def is_user_in_experiment_target(self, workspace, experiment, user):

        if not isinstance(experiment, RunningExperiment):
            raise Exception('experiment must be running [{}]'.format(experiment.id))

        if not experiment.target_audiences:
            return True

        for target in experiment.target_audiences:
            if self.target_matcher.matches(target, workspace, user):
                return True

        return False
