from hackle import logger as _logging


class ActionResolver(object):
    def __init__(self, bucketer, logger=None):
        self.bucketer = bucketer
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())

    def resolve_or_none(self, action, workspace, experiment, user):
        if action.type == 'VARIATION':
            return self._resolve_variation(action, experiment)
        elif action.type == 'BUCKET':
            return self._resolve_bucket(action, workspace, experiment, user)
        else:
            self.logger.debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(action.type))
            return None

    def _resolve_variation(self, action, experiment):
        variation = experiment.get_variation_by_id_or_none(action.variation_id)
        if not variation:
            raise Exception('variation[{}]'.format(action.variation_id))
        return variation

    def _resolve_bucket(self, action, workspace, experiment, user):
        bucket = workspace.get_bucket_or_none(action.bucket_id)
        if not bucket:
            raise Exception('bucket[{}]'.format(action.bucket_id))

        allocated_slot = self.bucketer.bucketing(bucket, user)
        if not allocated_slot:
            return None

        return experiment.get_variation_by_id_or_none(allocated_slot.variation_id)
