import json
import logging
import os
import pty
import select
import subprocess
from multiprocessing import Process
from os import environ
from pathlib import Path
from shutil import rmtree, copy2
from time import sleep
from typing import List
from unittest.mock import MagicMock, patch

from confluent_kafka import KafkaException, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource
from confluent_kafka.error import KafkaError
from dotenv import load_dotenv
from virtualenv import cli_run
from virtualenvapi.manage import VirtualEnvironment

from nubium_utils.confluent_utils import get_producers, produce_message
from nubium_utils.confluent_utils.confluent_configs import init_schema_registry_configs
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from nubium_utils.custom_exceptions import NoMessageError
from nubium_utils.yaml_parser import load_yaml_fp
from nubium_utils.confluent_utils.gtfo import GtfoBatchApp

LOGGER = logging.getLogger(__name__)


class DudeFinished(Exception):
    pass


class DudeConsumer(GtfoBatchApp):
    def __init__(self, app_function, consume_topics_list, *args, cluster_configs=None, topic_configs=None, **kwargs):
        if cluster_configs:
            environ['NU_KAFKA_CLUSTERS_CONFIGS_YAML'] = json.dumps(cluster_configs)
            env_vars._reload()
        if topic_configs:
            environ['NU_TOPIC_CONFIGS_YAML'] = json.dumps(topic_configs)
            env_vars._reload()
        self.all_messages = []  # allows you to do batches still, and return transformed versions of the messages
        super().__init__(app_function, consume_topics_list, metrics_manager=MagicMock(), *args, **kwargs)

    def seek_consumer_to_beginning(self):
        LOGGER.info('Setting up consumer to pull from the beginning of the topics...')
        self.consumer.poll(5)
        partitions = self.consumer.assignment()
        LOGGER.debug('Seeking all partitions to 0...')
        for partition in partitions:
            offset = self.consumer.get_watermark_offsets(partition)[0]
            topic = partition.topic
            p = partition.partition
            LOGGER.debug(f'Seeking {topic} p{p} to offset {offset}')
            self.consumer.seek(TopicPartition(topic=topic, partition=p, offset=offset))

    def _app_run_loop(self, *args, **kwargs):
        messages = []
        try:
            self.consume(*args, timeout=10, **kwargs)
            if self.app_function:
                messages = self.app_function(self.transaction, *self.app_function_arglist) # allows you to transform msgs to desired result if you'd like
            if not messages:  # if app_function does not return anything (maybe they passed a placeholder function or something)
                messages = self.transaction.messages()
            self.all_messages += messages
            if not self.transaction._committed:
                self.transaction.commit()
            if len(messages) < self.transaction._default_consume_max_count:
                self.producer.poll(0)
                raise DudeFinished
        except NoMessageError:
            self.producer.poll(0)
            LOGGER.debug(f'All messages pulled! Total count: {len(self.all_messages)}')
            raise DudeFinished
        except Exception as e:
            LOGGER.error(e)
            raise

    def run(self):
        self.seek_consumer_to_beginning()
        LOGGER.debug('Beginning consumption loop...')
        try:
            super().run()
        except DudeFinished:
            return self.all_messages


class KafkaToolbox:
    """
    Helpful functions for interacting with Kafka (mainly RHOSAK).
    Allows you to interface with multiple clusters at once by default assuming they are defined via your environment
    variables NUBIUM_CLUSTER_{N}. Actions include:

    Topics (multiple): create, delete, list

    Messages (multiple): produce, consume

    App: run, sync, build reqs, unit tests, integration tests
    """

    def __init__(self, cluster_configs=None, topic_configs=None, auto_configure=True):
        self.admin_clients = {}
        self.producers = {}
        self.consumer = {}
        self.schema_registry = None

        if cluster_configs:
            environ['NU_KAFKA_CLUSTERS_CONFIGS_YAML'] = json.dumps(cluster_configs)
            env_vars._reload()
        else:
            cluster_configs = load_yaml_fp(env_vars()['NU_KAFKA_CLUSTERS_CONFIGS_YAML'])
        self.cluster_configs = cluster_configs
        if topic_configs is not None:
            environ['NU_TOPIC_CONFIGS_YAML'] = json.dumps(topic_configs)
            env_vars._reload()
        else:
            topic_configs = load_yaml_fp(env_vars()['NU_TOPIC_CONFIGS_YAML'])
        self.topic_configs = topic_configs
        if self.cluster_configs and auto_configure:
            self.add_admin_cluster_clients(self.cluster_configs)

    def add_admin_cluster_clients(self, configs):
        """
        Add a new client connection for a given cluster.
        Added to 'self.admin_clients', where k:v is cluster_bootstrap_url: cluster_client_instance.

        By default, uses your environment to establish the client aside from the cluster URLS.

        You can provide configs in the following ways:
            {cluster1_confluent_config_dict}
            'cluster1_bootstrap_url'
        or lists of either.
        """
        if isinstance(configs, str):
            if self.cluster_configs: # "config" passed was just a cluster name
                configs = {configs: self.cluster_configs[configs]}
            else:
                raise Exception(f'Cant create admin client for {configs}; no cluster config metadata was provided for that name.')
        for cluster_name, cluster_config in configs.items():
            if cluster_name not in self.admin_clients:
                sleep(.2)
                apply_config = {
                    "bootstrap.servers": cluster_config['url']
                }
                if 'localhost' not in cluster_config['url']:
                    apply_config.update({
                        "sasl.username": cluster_config['username'],
                        "sasl.password": cluster_config['password'],
                        "security.protocol": "sasl_ssl",
                        "sasl.mechanisms": "PLAIN",
                    })
                client = AdminClient(apply_config)
                self.admin_clients[cluster_name] = client

    def create_topics(self, topic_cluster_dict, num_partitions=3, replication_factor=3, topic_config=None):
        """
        Accepts a "topic_cluster_dict" like: {'topic_a': 'cluster_x', 'topic_b': 'cluster_y', 'topic_c': ''},
        or list of topics.
        """
        defaults = {'partitions': num_partitions, 'replication_factor': replication_factor, 'config': {}}
        if isinstance(topic_cluster_dict, list):
            topic_cluster_dict = {k: self.topic_configs[k] for k in topic_cluster_dict}
        else:
            topic_cluster_dict = {topic: {'cluster': cfgs if isinstance(cfgs, str) else cfgs['cluster'], 'configs': self.topic_configs.get(topic, {'configs': {}})['configs']} for topic, cfgs in topic_cluster_dict.items()}
        topic_dict = {}
        for topic, configuration in topic_cluster_dict.items():
            configs = configuration['configs']
            configs.update({k: v for k, v in defaults.items() if k not in configs})
            topic_dict[configuration['cluster']] = topic_dict.get(configuration['cluster'], []) + [
                NewTopic(
                    topic=topic,
                    num_partitions=configs['partitions'],
                    replication_factor=configs['replication_factor'],
                    config=configs['config'])]
        for cluster, topic_creates in topic_dict.items():
            self.add_admin_cluster_clients(cluster)
            for topic in topic_creates:
                try:
                    _wait_on_futures_map(self.admin_clients[cluster].create_topics([topic]))
                    print(f"Topic created: {topic}")
                except KafkaException as e:
                    if e.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS:
                        print(f"Topic already exists: {topic}")
                        pass
                    else:
                        raise

    def create_all_topics(self):
        """Creates all the topics by passing the whole topic map to create_topics."""
        self.create_topics(self.topic_configs)

    def alter_topics(self, topic_cluster_dict):
        """
        Accepts a "topic_cluster_dict" like: {'topic_a': 'cluster_x', 'topic_b': 'cluster_y', 'topic_c': ''},
        or list of topics.
        """
        if isinstance(topic_cluster_dict, list):
            topic_cluster_dict = {k: {'cluster': self.topic_configs[k]['cluster'], 'config': self.topic_configs[k]['configs']['config']} for k in topic_cluster_dict}
        else:
            topic_cluster_dict = {topic: {'cluster': cfgs if isinstance(cfgs, str) else cfgs['cluster'], 'config': cfgs.get('configs', {}).get('config', {}) if isinstance(cfgs, dict) else {}} for topic, cfgs in topic_cluster_dict.items()}
        topic_dict = {}
        for topic, configuration in topic_cluster_dict.items():
            config_out = self.topic_configs.get(topic, {'configs': {'config': {}}})['configs']['config']
            config_out.update(configuration['config'])
            topic_dict[configuration['cluster']] = topic_dict.get(configuration['cluster'], []) + [
                dict(
                    topic=topic,
                    config=config_out)]
        for cluster, topic_alters in topic_dict.items():
            self.add_admin_cluster_clients(cluster)
            for topic_configs in topic_alters:
                try:
                    topic = topic_configs['topic']
                    current_config = self.admin_clients[cluster].describe_configs([ConfigResource(2, topic)])
                    _wait_on_futures_map(current_config)
                    new_config = list(current_config.values())[0]._result
                    new_config = {cfg.name: cfg.value for cfg in new_config.values()}
                    new_config.update(topic_configs['config'])
                    _wait_on_futures_map(self.admin_clients[cluster].alter_configs([ConfigResource(2, topic, set_config=new_config)]))
                    print(f"Topic config updated: {topic}")
                except KafkaException as e:
                    if e.args[0].code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        print(f"Topic altering failed because it doesn't exist: {topic}")
                        pass

    def delete_topics(self, topic_cluster_dict):
        if isinstance(topic_cluster_dict, list):
            topic_cluster_list = topic_cluster_dict[:]
            topic_cluster_dict = {}
            currently_exist = {}
            for cluster, client in self.admin_clients.items():
                # filter for topics in provided list that actually exist in the cluster
                currently_exist.update({topic: cluster for topic in self.list_topics()[cluster] if topic in topic_cluster_list})
            for topic in currently_exist:
                topic_cluster_dict[topic] = self.topic_configs[topic]["cluster"]
        for topic, cluster in topic_cluster_dict.items():
            self.add_admin_cluster_clients(cluster)
            try:
                _wait_on_futures_map(self.admin_clients[cluster].delete_topics([topic]))
                print(f"Topic deleted: {topic}")
            except KafkaException as e:
                if e.args[0].code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print(f"Topic deletion failed (likely because it didn't exist): {topic}")
                    pass

    def delete_all_topics(self):
        self.delete_topics({topic: config['cluster'] for topic, config in self.topic_configs.items()})

    def nuke_clusters_from_orbit(self):
        """It's the only way to be sure..."""
        cluster_set = set([configs["url"] for cluster, configs in self.cluster_configs.items()])
        pushed_big_red_button = input(f'You are about to wipe EVERYTHING from these clusters:\n{cluster_set}\nARE YOU SURE?\nYES/[else]')
        if pushed_big_red_button == 'YES':
            if len(cluster_set) == 1:
                cluster = list(self.cluster_configs.keys())[0]
                self.delete_topics({topic: cluster for topic in self.list_topics(mirrors=True, faust=True)[cluster]})
            else:
                self.delete_topics(self.list_topics(by_topic=True, mirrors=True, faust=True))
            print("BOOOOOOM!!!!!!!!! I THINK WE GOT EM, BOIS!")
        else:
            print('Nuclear launch aborted...that was a close one!')

    def sync_topics(self):
        cluster_set = set([configs["url"] for cluster, configs in self.cluster_configs.items()])
        single_cluster = True if len(cluster_set) == 1 else False

        def json_print(d):
            if single_cluster:
                return json.dumps(list(d.values())[0], indent=4)
            return json.dumps(d, indent=4)

        if single_cluster:
            current_topics_by_cluster = {list(self.list_topics().keys())[0]: set(self.list_topics(by_topic=True).keys())}
            topic_configs_by_cluster = {cluster: set(self.topic_configs.keys()) for cluster in current_topics_by_cluster.keys()}
        else:
            current_topics_by_cluster = {cluster: set(topics) for cluster, topics in self.list_topics().items()}
            topic_configs_by_cluster = {cluster: set([topic for topic, configs in self.topic_configs.items() if configs['cluster'] == cluster]) for cluster in current_topics_by_cluster.keys()}

        topics_to_create = {cluster: list(topic_configs_by_cluster[cluster] - current_topics_by_cluster[cluster]) for cluster in topic_configs_by_cluster.keys()}
        topics_to_delete = {cluster: list(current_topics_by_cluster[cluster] - topic_configs_by_cluster[cluster]) for cluster in topic_configs_by_cluster.keys()}

        if topics_to_create:
            print(f'\nTopics to create: {json_print(topics_to_create)}\n')
            create = input('Continue with CREATING the above topics?\nYES/[else]')
            if create == 'YES':
                self.create_topics({topic: cluster for cluster, topic_list in topics_to_create.items() for topic in topic_list})
            else:
                "\nSKIPPING CREATION"

        if topics_to_delete:
            print(f'\nTopics to delete: {json_print(topics_to_delete)}\n')
            delete = input('Continue with DELETING the above topics?\nYES/[else]')
            if delete == 'YES':
                self.create_topics({topic: cluster for cluster, topic_list in topics_to_create.items() for topic in topic_list})
            else:
                "\nSKIPPING DELETION"

        alter = input('Continue with ALTERING (aka UPDATING) all topic configs?\nYES/[else]')
        if alter == 'YES':
            self.alter_topics([topic for topic in self.topic_configs.keys()])
        else:
            "\nSKIPPING ALTERING"

    def list_topics(self, by_topic=False, mirrors=False, cluster_name=None, faust=False):
        """
        Allows you to list all topics across all cluster instances.

        If you want to return the output in a format that is used by the other toolbox functions, then
        you can change "by_topic"=True; the default format makes it easier to read.

        Will not include the mirrored topics by default, but can toggle with "mirrors".
        """
        def _faust_include(topic):
            if topic.endswith('__leader') or topic.endswith('-changelog') or 'GroupBy' in topic or '_Internal_' in topic:
                return faust
            return True

        def _mirror_include(topic):
            if topic.startswith('mm2-') or 'heartbeats' in topic:
                return mirrors
            return True

        def _valid(topic):
            return not topic.startswith('__') and 'schema' not in topic

        if cluster_name:
            self.add_admin_cluster_clients(cluster_name)
        else:
            self.add_admin_cluster_clients(self.cluster_configs)
        by_cluster = {clust: [topic for topic in list(client.list_topics().topics) if _valid(topic) and _mirror_include(topic) and _faust_include(topic)]
                      for clust, client in self.admin_clients.items()}
        if by_topic:
            topics = {topic: clust for clust, topics in by_cluster.items() for topic in topics}
            return {k: topics[k] for k in sorted(topics.keys())}
        return {k: sorted(by_cluster[k]) for k in sorted(by_cluster.keys())}

    def produce_messages(self, topic, message_list, schema=None, cluster_name=None):
        """
        Produce a list of messages (each of which is a dict with entries 'key', 'value', 'headers') to a topic.

        Must provide the schema if you haven't produced to that topic on this instance, or if using dude CLI.
        """
        # TODO extra producer error handling?
        if not self.producers.get(topic):
            if not schema:
                raise ValueError('Schema not provided and the topic producer instance was not previously configured. '
                                 'Please provide the schema!')
            if not cluster_name:
                cluster_name = self.topic_configs[topic]['cluster']
            self.add_admin_cluster_clients(cluster_name)
            if not self.schema_registry:
                self.schema_registry = init_schema_registry_configs(as_registry_object=True)
            self.producers.update(get_producers({topic: schema}, cluster_name, self.schema_registry, return_as_singular=False))
        producer = self.producers[topic]
        for message in message_list:
            produce_message(
                producer=producer,
                producer_kwargs=message,
                metrics_manager=MagicMock())  # TODO: change NU to allow a None here? dunno
        producer.flush(timeout=30)

    def consume_messages(self, topics, transform_function=None, consumer=None):
        """
        Consume a list of messages (each of which is a dict with entries 'key', 'value', 'headers') from a topic.
        """
        # TODO: add easy way of changing the consumer group on the fly
        if isinstance(topics, str):
            topics = topics.split(',')
        dude_app = DudeConsumer(
            app_function=transform_function,
            consume_topics_list=topics,
            consumer=consumer,
            produce_topic_schema_dict={topic: "string" for topic in topics} # throwaway until I convert it to accept empty dict for consuming only.
        )
        return dude_app.run()

    def run_app(self, skip_topic_creation=None, skip_sync=None, run_args="", runtime_env_overrides=None):
        if _is_nubium_app():
            if not skip_sync:
                _sync_virtual_environment()
            # TODO load DUDE_APP_VENV from dude's ConfigManager
            venv_path = Path(os.environ.get("DUDE_APP_VENV", "./venv"))
            load_dotenv(Path(f'{os.path.abspath(venv_path)}/.env'), override=True)
            if not skip_topic_creation:
                topics = {os.environ[var]: "" for var in os.environ if
                          var.endswith("_TOPIC") or var.endswith("_TOPICS")}
                try:
                    LOGGER.info("Attempting to create topics...")
                    cluster = next(iter(self.admin_clients))
                    self.create_topics({topic: cluster for topic in topics})
                    sleep(5)
                except Exception as e:
                    LOGGER.info(f"Topic creation failed (likely because they already exist): {e}")
                    pass
            if not [f for f in run_args if '.py' in f]:
                run_args = ['app.py'] + list(run_args)
            if _is_faust_app():
                run_args += ["worker", "-l", "info"]
            process = Process(target=run_command_in_virtual_environment, args=("python3.8", run_args))
            if not runtime_env_overrides:
                runtime_env_overrides = {}
            with patch.dict('os.environ', runtime_env_overrides):
                process.start()
            return process.pid

    @staticmethod
    def sync_venv(wipe_existing):
        if _is_nubium_app():
            _sync_virtual_environment(wipe_existing=wipe_existing)

    @staticmethod
    def build_reqs():
        if _is_nubium_app() and _has_requirements_in():
            _ensure_virtual_environment_exists()
            run_command_in_virtual_environment("pip-compile")

    @staticmethod
    def run_unit_tests():
        if _is_nubium_app():
            _sync_virtual_environment()
            run_command_in_virtual_environment("pytest", ["./tests/unit/", "-rA", "-v"])

    @staticmethod
    def run_integration_tests():
        if _is_nubium_app():
            _sync_virtual_environment()
            venv_path = Path(os.environ.get("DUDE_APP_VENV", "./venv"))
            load_dotenv(Path(f'{os.path.abspath(venv_path)}/.env'), override=True)
            run_command_in_virtual_environment("pytest", ["./tests/integration/", "-rA", "-svv", "--log-cli-level=INFO"])


def _wait_on_futures_map(futures):
    for future in futures.values():
        future.result()
        assert future.done()
        sleep(.1)


def _is_nubium_app():
    return Path("app.py").is_file()


def _is_faust_app():
    return Path("kiwf_openshift_health_check.py").is_file()


def _has_requirements_in():
    return Path("requirements.in").is_file()


def _sync_virtual_environment(wipe_existing=False):
    venv_path = _ensure_virtual_environment_exists(wipe_existing)
    run_command_in_virtual_environment("pip-sync")
    # TODO merge these .env files to support bringing in new variables without overwriting existing customizations (see dotenv's CLI list command)
    local_dotenv = Path("configs/local.env")
    venv_dotenv = Path(f"{venv_path}/.env")
    if local_dotenv.is_file() and not venv_dotenv.is_file():
        copy2(local_dotenv, venv_dotenv)


def _ensure_virtual_environment_exists(wipe_existing: bool = False) -> Path:
    venv_path = Path(os.environ.get("DUDE_APP_VENV", "./venv"))
    if wipe_existing:
        rmtree(venv_path)
    venv_path.mkdir(parents=True, exist_ok=True)
    # TODO load python version from configuration
    cli_run([str(venv_path), "-p", "python3.8"])
    venv = VirtualEnvironment(str(venv_path), readonly=True)
    if not venv.is_installed("pip-tools"):
        # TODO lock versions of pip-tools and dependencies
        run_command_in_virtual_environment("pip", args=["install", "pip-tools"])
    return venv_path


def run_command_in_virtual_environment(command: str = "", args: List[str] = None):
    if not args:
        args = []
    venv_path = Path(os.environ.get("DUDE_APP_VENV", "./venv"))
    run_command_in_pseudo_tty(command=str(venv_path / "bin" / command), args=args)


def run_command_in_pseudo_tty(
        command: str,
        args: List[str] = None,
        output_handler=lambda data: print(data.decode("utf-8"), end=""),
        buffer_limit=512,
        buffer_timeout_seconds=0.04,
):
    # In order to get colored output from a command, the process is unfortunately quite involved.
    # Constructing a pseudo terminal interface is necessary to fake most commands into thinking they are in an environment that supports colored output
    if not args:
        args = []

    # It's possible to handle stderr separately by adding p.stderr.fileno() to the rlist in select(), and setting stderr=subproccess.PIPE
    # which would enable directing stderr to click.echo(err=True)
    # probably not worth the additional headache
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen([command] + args, stdin=slave_fd, stdout=slave_fd, stderr=subprocess.STDOUT, close_fds=True)

    def is_proc_still_alive():
        return proc.poll() is not None

    while True:
        ready, _, _ = select.select([master_fd], [], [], buffer_timeout_seconds)
        if ready:
            data = os.read(master_fd, buffer_limit)
            output_handler(data)
        elif is_proc_still_alive():  # select timeout
            assert not select.select([master_fd], [], [], 0)[0]  # detect race condition
            break  # proc exited
    os.close(slave_fd)  # can't do it sooner: it leads to errno.EIO error
    os.close(master_fd)
    proc.wait()
