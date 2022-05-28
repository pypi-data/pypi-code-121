from __future__ import absolute_import
from __future__ import print_function
import os
import requests
import logging
import uuid
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway
import time
import mlflow
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.DEBUG)


def get_url(pushgateway_url, pushgateway_namespace, port):
    if pushgateway_url.endswith("svc.cluster.local"):
        return pushgateway_url
    else:
        return "http://{}.{}.svc.cluster.local:{}".format(pushgateway_url, pushgateway_namespace, port)


class MetricClient(object):

    def __init__(self, port=9091):
        self.MAX_RETRIES = 10
        self.port = port
        self.namespace = os.environ["NAMESPACE"]
        self.myelin_installation_namespace = os.environ["MYELIN_NAMESPACE"]
        self.pushgateway_namespace = os.environ["PUSHGATEWAY_NAMESPACE"]
        self.task_id = os.environ["TASK_ID"]
        self.task_name = os.environ["TASK_NAME"]
        self.axon_name = os.environ["AXON_NAME"]
        self.pushgateway_url = os.environ["PUSHGATEWAY_URL"]
        self.mlflow_tracking_url = os.environ.get("MLFLOW_TRACKING_URI")
        self.url = get_url(self.pushgateway_url, self.pushgateway_namespace, self.port)
        self.counter_registries = {}
        self.process_id = str(uuid.uuid4())

    def get_metric(self, name):
        metric = "{}_{}".format(name, self.axon_name)
        return metric.replace("-", "__")

    def post_update(self, metric, value, job_name=None, grouping_key=None):
        job = job_name if job_name else self.task_id
        internal_metric = self.get_metric(metric)
        registry = CollectorRegistry()
        g = Gauge(internal_metric, '', registry=registry)
        g.set(value)

        # Remove pod and service since they are attached by the push gateway
        if grouping_key is None:
            grouping_key = {}
        grouping_key["pod"] = ""
        grouping_key["service"] = ""

        push_to_gateway(self.url, job=job, registry=registry, grouping_key=grouping_key)

    def post_increment(self, metric, amount=1):
        """
        Note that counters are stateful and need to be kept to increment
        """
        internal_metric = self.get_metric(metric)

        if internal_metric in self.counter_registries:
            r = self.counter_registries[internal_metric]
            # get the counter (only one counter per registry)
            c = r._names_to_collectors["{}_total".format(internal_metric)]
        else:
            r = CollectorRegistry()
            c = Counter(internal_metric, "", ["uuid"], registry=r)
            self.counter_registries[internal_metric] = r
        c.labels(uuid=self.process_id).inc(amount=amount)
        push_to_gateway(self.url, job=self.task_id, registry=r, grouping_key={"pod": "", "service": ""})

    def post_hpo_result(self, config_id, config, budget, loss_metric, loss, params, tags, info_map, additional_metrics):
        # publish to train controller
        self.train_controller_export(budget, config, config_id, info_map, loss, self.MAX_RETRIES)

        # publish to mlflow
        if self.mlflow_tracking_url is not None:
            self.mlflow_export(config, loss, loss_metric, params, tags, self.MAX_RETRIES,
                               additional_metrics=additional_metrics)

    def train_controller_export(self, budget, config, config_id, info_map, loss, num_tries):
        try:
            train_controller_url = os.environ['TRAIN_CONTROLLER_URL']
            logging.info("train_controller_url: %s" % train_controller_url)
            result_dict = ({
                'loss': loss,
                'info': info_map
            })
            result = {'result': result_dict, 'exception': None}
            res_post = {'result': result, 'budget': budget, 'config_id': self.build_config_id(config_id),
                        'config': config}
            print(f"{self.task_id} - hpo export result to controller, requset: {res_post}")
            response = requests.post("%s/submit_result" % train_controller_url, json=res_post)
            print('response: %s' % response.status_code)
            if response.status_code != 200:
                raise Exception("reporting HP failed, error: %s" % response.text)
        except Exception as e:
            logging.error(f"{self.task_id} - hpo export result to controller failed, error: {str(e)}")
            time.sleep(2)
            if num_tries == 0:
                raise e
            else:
                return self.train_controller_export(budget, config, config_id, info_map, loss, num_tries - 1)

    def mlflow_export(self, config: Dict[str, Any], loss: Optional[float], loss_metric: Optional[str],
                      params: Dict[str, Any], tags: Dict[str, str], num_tries: int, experiment_name: str = None,
                      additional_metrics: Dict[str, float] = {}):
        try:
            if experiment_name:
                mlflow.set_experiment(experiment_name)
            else:
                mlflow.set_experiment(self.axon_name)
            default_tags = {'AxonName': self.axon_name, 'TaskName': self.task_name}
            default_tags = self._add_env_var('MYELIN_NODE_NAME', 'NodeName', default_tags)
            default_tags = self._add_env_var('MYELIN_POD_NAME', 'PodName', default_tags)
            tags = {**default_tags, **tags}
            nested = False
            run_name = self.task_id
            with mlflow.start_run(run_name=run_name, nested=nested, tags=tags) as run:
                # Log parameters and metrics using the MLflow APIs
                mlflow.log_params({**config, **params})
                if loss:
                    metrics = {loss_metric: loss}
                    mlflow.log_metrics({**metrics, **additional_metrics})
        except Exception as e:
            logging.error(f"{self.task_id} - hpo export result to mlflow failed, error: {str(e)}")
            time.sleep(2)
            if num_tries == 0:
                raise e
            else:
                return self.mlflow_export(config=config, loss=loss, loss_metric=loss_metric, params=params,
                                          tags=tags, num_tries=num_tries - 1)

    @staticmethod
    def build_config_id(config_id):
        return [int(x) for x in config_id.split("_")]

    @staticmethod
    def _add_env_var(env_var, dict_key, tags):
        value = os.environ.get(env_var)
        if value is not None:
            tags[dict_key] = value
        return tags
