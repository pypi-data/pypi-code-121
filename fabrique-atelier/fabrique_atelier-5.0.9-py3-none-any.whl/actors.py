from multiprocessing import Pool
import os

# import traceback

FABRIQUE_KAFKA_SERVERS = os.getenv('FABRIQUE_KAFKA_SERVERS', '')
FABRIQUE_METRIC_COLLECTOR_TOPIC = os.getenv('FABRIQUE_METRIC_COLLECTOR_TOPIC', 'monitor.in')

if FABRIQUE_KAFKA_SERVERS:
    import fabrique_actor.pipeline_actors as actor
else:
    import fabrique_atelier.dummy.pipeline_actors as actor

from fabrique_atelier.constants import VALID_ACTOR_TYPES

# imports for emulator
from fabrique_atelier.dummy.store import Store
from fabrique_atelier.dummy.router import Router
from fabrique_atelier.dummy.metric_collector import MetricCollector
from fabrique_atelier.validators.pipeline_validator import validate_pipeline
from fabrique_atelier.config_generator import ActorConfigs
# from fabrique_atelier.message import Message
from time import time

from collections import namedtuple


class BaseActor:
    """
    Base pipeline actor wrapper class
    """
    _actor_type = None
    _outputs = []
    destinations = namedtuple('destinations', [])(*[])

    def __init__(self):
        self._actor = None
        self.logger = None

    def __str__(self):
        actor_type = self._actor_type
        class_name = type(self).__name__

        outputs = list(self._outputs)

        return f'{class_name}, type = {actor_type}, outputs = {outputs}'

    @classmethod
    def to(cls, *destinations):
        """
        Class method for pipeline topology configuration

        For example (from easy_balloons example):

        ```
        pipeline = Pipeline(['balloon_dispatcher', 'balloon_repainter'])
        ids = pipeline.ids
        nodes = pipeline.nodes
        nodes.balloon_dispatcher = BalloonDispatcher.to(ids.end, ids.balloon_repainter)
        nodes.balloon_repainter = BalloonRepainter.to(ids.end)
        ```

        makes topology:
        ```
        -->[balloon_dispatcher]--(if mes['destination'] == 'balloon_repainter')-->[balloon_repainter]-->{end}
                      `---------(if mes['destination'] == 'end')-----------------------------------------^
        ```

        :param destinations : node_id string (for Processor/Mapper), or node strings (for Dispatcher)
        :return: this class
        """
        cls._outputs = destinations
        cls.destinations = namedtuple('destinations', destinations)(*destinations)
        return cls

    def mp_get_batch_result(self, batch):
        """
        Multiprocessing batch callback (experimental!!!)
        To use this feature you must define get_mp_result method (must be static!!!)
        And you can override this method

        :param batch: list of messages bodies
        :return: list of message bodies
        """
        if not batch:
            return []
        with Pool(4) as p:
            res_batch = p.map(self.get_mp_result, batch)

        return res_batch

    def get_result(self, body):
        """
        Single message processing callback (must be overridden if you want to use it)

        Or you can define self.get_batch_result(batch) where batch  is microbatch of message bodies [body0, body1,
        body2, ...]

        :param body: message body
        :return: message body
        """
        raise Exception("This method needs to be defined in a subclass")

    def _start_actor(self, actor_instance, autorun=True):
        self._actor = actor_instance
        self.logger = self._actor.logger

        try:
            self._actor.batch_callback = self.__getattribute__(
                'get_batch_result')
        except AttributeError:
            if hasattr(self, 'get_mp_result'):
                self._actor.batch_callback = self.mp_get_batch_result
            else:
                self._actor.body_callback = self.get_result
                self._actor.consumer_poll_num_messages = 1

        if autorun:
            self._actor.run()


class Mapper(BaseActor):
    """
    Actor with one output
    """
    _actor_type = VALID_ACTOR_TYPES.mapper

    def start(self, config):
        """
        Start actor with consumer loop

        :param config: dict with message_bus config
        :return: None
        """
        self._start_actor(actor.Mapper(config))


Processor = Mapper  # alias


class Dispatcher(BaseActor):
    """
    Actor with many outputs (use destinaton message body field to set output for message)
    """
    _actor_type = VALID_ACTOR_TYPES.dispatcher

    def start(self, config):
        """
        Start actor with consumer loop

        :param config:
        :return: None
        """
        self._start_actor(actor.Dispatcher(config))


class Nodes(dict):
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self


class Pipeline(object):
    """
    Create topology on init, and save this topology in start_emulation with testing on samples
    """
    def __init__(self, nodes_lst):
        """
        Create pipeline topology

        :param nodes_lst: list of strings with node ids
        """
        assert nodes_lst
        assert (not set(nodes_lst).intersection({'begin', 'end', 'monitor'}))
        self.nodes = Nodes()
        for node_id in nodes_lst:
            setattr(self.nodes, node_id, None)

        nodes_lst.extend(['begin', 'end'])
        self.ids = namedtuple('ids', nodes_lst)(*nodes_lst)

    def start_emulation(self, input_iterator=None, session_timeout=60.0,
                        output_dir=None, pipeline_dir='..'):
        """
        Start test on message samples and create pipeline.json
        :param input_iterator: list, tuple, generator, or another iterator with test message samples
        :param session_timeout: timeout in seconds
        :param output_dir: directory with results of emulation (output messages, metrics, logs, ...)
        :param pipeline_dir: dir of pipeline.py
        :return: None
        """

        proj_path = os.path.abspath(pipeline_dir)
        if not output_dir:
            output_dir = os.path.join(proj_path, 'dev')

        OUTPUT_EMULATION_DIR = os.path.join(output_dir, 'out')
        FILE_OUT_DIR = os.path.join(OUTPUT_EMULATION_DIR, 'data')
        os.environ["OUTPUT_EMULATION_DIR"] = OUTPUT_EMULATION_DIR

        starter_dir = os.path.abspath(os.getcwd())

        os.chdir(proj_path)

        assert input_iterator, 'Must be iterator with messages'

        nodes = validate_pipeline(self)

        cfg = ActorConfigs(nodes)
        cfg.make_message_bus_configs()
        cfg.save_nodes_for_prod(proj_path)
        cfg.generate_dockerfile(proj_path)
        cfg.generate_templates(proj_path)

        store = Store()
        pipeline_in_topic = cfg.pipeline_in_topic
        kafka_out_topic = 'results.out'
        errors_topic = 'errors.out'

        nodename2configs = cfg.nodename2configs(store)

        topic_in2act = {nodename2configs[name]['message_bus']['in_topic']:
                        dict(node=node(), cfg=nodename2configs[name])
                        for name, node in self.nodes.items()}

        mc = MetricCollector(store, out_pth=f'{OUTPUT_EMULATION_DIR}/metrics.ndjson')

        router = Router(store, pipeline_in_topic, kafka_out_topic, errors_topic, input_iterator)
        router.send_messages2pipeline()

        # emulate message_bus
        t = time()
        while True:
            if time() - t > session_timeout:
                raise Exception('Timeout')

            fullen, topic2len = store.get_topic_lens()
            if topic2len.get(router.kafka_out, 0) == fullen:
                break

            for topic in topic2len.keys():
                if topic == FABRIQUE_METRIC_COLLECTOR_TOPIC:
                    mc.run()
                    continue

                actor_node = topic_in2act.get(topic, {'node': None})['node']
                if actor_node:
                    actor_node.start(topic_in2act[topic]['cfg'])

        residual = {key for key, val in topic2len.items() if val and key != router.kafka_out}
        assert topic2len[router.kafka_out] == fullen, f"There are unprocessed messages in {residual}"

        os.makedirs(FILE_OUT_DIR, exist_ok=True)
        i = 0
        for messages in store.reader_generator(router.kafka_out):
            for mes in messages:
                filepath = os.path.join(f'{FILE_OUT_DIR}/data{i}.bin')
                ser_value = mes.value()
                with open(filepath, 'wb') as f:
                    try:
                        f.write(ser_value)
                    except TypeError:
                        raise TypeError(f"body['data'] of final node must be bytearray not {type(ser_value)}")
                i += 1

        os.chdir(starter_dir)
