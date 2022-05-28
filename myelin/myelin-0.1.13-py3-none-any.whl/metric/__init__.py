from .metric_client import MetricClient
import os
import myelin.hpo
__all__ = ['MetricClient']

__MYELIN_CLIENT__ = MetricClient()


def get_loss_metric():
    return os.environ["LOSS_METRIC"]


def post_hpo_result(config_id, config, budget, loss_metric, loss, params, tags, info_map, additional_metrics):
    __MYELIN_CLIENT__.post_hpo_result(config_id, config, budget, loss_metric, loss, params, tags, info_map,
                                      additional_metrics)


def publish_result(loss_value, loss_metric, additional_metrics={}, params=None, tags=None):
    if tags is None:
        tags = {}
    if params is None:
        params = {}
    __MYELIN_CLIENT__.post_update(loss_metric, loss_value)
    if myelin.hpo.hpo_enabled():
        myelin.hpo.publish_result(loss_metric, loss_value, params, tags, additional_metrics)
