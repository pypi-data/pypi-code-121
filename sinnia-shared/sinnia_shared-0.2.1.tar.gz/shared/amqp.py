import pika, logging, time, threading, json
import urllib.request as urllib


## Configurable parameters

_default_log_level = logging.WARNING
_publish_sleeptime = 60
_default_helper_conf = "small"
_default_amqp_conf   = "db"

_helper_conf = { 
    "big": {
        'helper_sleeptime' : 300, # in seconds
        'ram_limit'        : 25,  # value in GB
        'host' : 'localhost',
        'user' : 'trb',
        'pass' : "clm28'Anglos",
        'virtual_host' :'twttr'        
    },
    "small": {
        'helper_sleeptime' : 300, # in seconds
        'ram_limit'        : 3,   # value in GB
        'host' : 'localhost',
        'user' : 'trb',
        'pass' : "clm28'Anglos",
        'virtual_host' :'twttr'        
    },
    "local": {
        'helper_sleeptime' : 300, # in seconds
        'ram_limit'        : 1,   # value in GB
        'host' : 'localhost',
        'user' : 'trb',
        'pass' : "clm28'Anglos",
        'virtual_host' :'twttr'
    }
}

_amqp_conf = {
    "db": {
        'host' : 'localhost',
        'user' : 'trb',
        'pass' : "clm28'Anglos",
        'virtual_host' :'twttr',
        'exchange'     :'capture',
        'routing_key'  :'rest.%s.no-log'
    },
    "twttr_consume": {
        'host' : 'localhost',
        'user' : 'trb',
        'pass' : "clm28'Anglos",
        'virtual_host' : 'twttr',
        'exchange'     : 'capture',
        'queue'        : 'send_to_bq',
        'routing_key'  : 'rest.%s.no-log'
    },
    "file": {
        'host' : 'localhost',
        'user' : 'trb',
        'pass' : "clm28'Anglos",
        'virtual_host' :'twttr',
        'exchange'     :'capture_to_file',
        'routing_key'  :'rest.%s.no-log'
    },
    "meaningcloud_process": {
        'host' : 'localhost',
        'user' : 'trb',
        'pass' : "clm28'Anglos",
        'virtual_host' : 'meaningcloud',
        'exchange'     : 'capture',
        'queue'        : 'capture',
        'routing_key'  : 'mc.%s'
    },
}

## Logger init
    
_instances = {}

## Class definition
class AMQPUtil():
    logging.basicConfig(level=_default_log_level)

    def __init__(self, config_name=None, with_helper=False):
        self.do_slow_down = False
        self.ram_current = None

        hconf = _helper_conf.get(_default_helper_conf, _helper_conf['local'])
        logging.debug('AMQPUtil.init helperconf %s'%str(hconf))
        self.helper = AMQPHelper(hconf['host'],hconf['user'],hconf['pass'],
                                 hconf['helper_sleeptime'],hconf['ram_limit'])
        if with_helper:
            self.helper.start()
        conf = _amqp_conf.get(config_name, 'db')
        logging.debug('AMQPUtil.init conf %s'%str(conf))        
        self._parameters = pika.ConnectionParameters(
            credentials=pika.PlainCredentials(conf['user'], conf['pass']),
            host=conf['host'], virtual_host=conf['virtual_host'])
        self._connection = None
        self._channel = None
        logging.info("Instance of AMQPUtil initialized")


    def _getChannel(self):
        global _publish_sleeptime
        if self._connection is None or self._channel is None \
                or self._connection.is_closed or self._channel.is_closed \
                or not self._connection.is_open:
            logging.info('Reconnecting ...')
            self._connection = pika.BlockingConnection(self._parameters)
            def _handleBackpressure():
                self.helper.tcp_handler()
            self._channel = self._connection.channel()
        if self.helper.do_slow_down():
            logging.warn('Sleeping ...')
            time.sleep(_publish_sleeptime)
            logging.warn('Awake ...')
        return self._channel

    @staticmethod
    def _getInstance(config_name = None):
        if not config_name: config_name = _default_amqp_conf
        instance = _instances.get(config_name)
        if instance is None:
            instance = AMQPUtil(config_name)
            logging.debug('getInstance started instance: %s'%str(instance))
            _instances[config_name] = instance
        return instance
        
    @staticmethod
    def publish(client, message, config = None, retry=0):
        try:
            if not client : client = "sinnia"
            client_key = (lambda c, m: m.get(c) if m.get(c) else c)\
                         (client, { "all": "all", 
                                    "sinnia": "sinnia"})
            conf = _amqp_conf.get(config, _amqp_conf[_default_amqp_conf])
            vhost = conf['virtual_host']
            routing_key = conf['routing_key'] % str(client_key)
            exchange = conf['exchange']
            inst = AMQPUtil._getInstance(config)
            chann = inst._getChannel()
            chann.basic_publish(exchange=exchange,
                                routing_key=routing_key,
                                body=message)
        except:
            if retry <= 10:
                retry += 1
                logging.info("Retry .... %s" % retry)
                AMQPUtil.publish(client, message, config, retry)
            else:
                logging.error("Retries exhausted: could not connect to host")

    @staticmethod
    def consume(config_name, callback):
        inst = AMQPUtil._getInstance(config_name)
        conf = _amqp_conf.get(config_name, 'db')
        inst._getChannel().basic_consume(conf['queue'], callback, auto_ack=False, exclusive=False, consumer_tag=None, arguments=None)
        try:
            inst._getChannel().start_consuming()
        except KeyboardInterrupt:
            inst._getChannel().stop_consuming()
        self._connection.close()



class AMQPHelper(threading.Thread):

    def __init__(self, host, user, passwd, sleeptime, ram_limit):
        self.api_url = 'http://%s:15672/api/nodes' % host 
        self.sleeptime = sleeptime
        self.ram_limit = ram_limit * 1000000000
        self.current_ram = 0
        self.tcp_trigered = False
        logging.debug('AMQPHelper.init: url=%s usr=%s pass=%s'%(self.api_url,user,passwd))

        # create a password manager
        # add the username and password
        # add the password manager to a handler
        password_mgr = urllib.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.api_url, user, passwd)
        handler = urllib.HTTPBasicAuthHandler(password_mgr)        
        # create "opener" (OpenerDirector instance)
        # install the opener. All calls to urllib.urlopen will use it.
        opener = urllib.build_opener(handler)
        urllib.install_opener(opener)
        
        threading.Thread.__init__(self)
        logging.debug('AMQPHelper.init started thread')

        
    def get_ram(self):
        return self.current_ram

    def is_ram_exceded(self):
        return self.ram_limit < self.get_ram()

    def is_tcp_trigered(self):
        if self.tcp_trigered:
            self.tcp_trigered = False
            return True
        return False

    def tcp_handler(self):
        self.tcp_trigered = True

    def do_slow_down(self):
        return self.is_ram_exceded() or self.is_tcp_trigered()
        
    def run(self):
        while 1:
            try:
                response = urllib.urlopen(self.api_url)
                data = json.loads(response.read())
                max_ram = 0
                for node in data:
                    ram = node.get('mem_used', 0)
                    if max_ram < ram: max_ram = ram
                self.current_ram = int(max_ram)
                logging.info("RAM: %sG" % (self.current_ram / 1000000000.0))
            except Exception as exc:
                logging.info("Could not obtain ram: %s" % self.api_url)
                logging.exception(exc)
            time.sleep(self.sleeptime)

