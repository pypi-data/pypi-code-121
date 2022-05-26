import atexit
import json
import asyncio
from aiohttp import ClientSession, TCPConnector

# default send interval is in seconds
DEFAULT_SEND_INTERVAL = 5

# default max size before sending
DEFAULT_MAX_QUEUE_SIZE = 100

# default value for max retries on failure
DEFAULT_MAX_RETRIES = 5


class RasaEventBroker():
    def __init__(self, api_key, api_url, max_queue_size = DEFAULT_MAX_QUEUE_SIZE, send_interval = DEFAULT_SEND_INTERVAL, max_retries = DEFAULT_MAX_RETRIES, enable_debug = False):
        if max_retries < 0:
            raise Exception("max_retries must be >= 0")
        if max_queue_size <= 0:
            raise Exception("max_queue_size must be > 0")
        if send_interval <= 0:
            raise Exception("send_interval must be > 0")

        self.api_key = api_key
        self.api_url = api_url
        self.max_queue_size = max_queue_size
        self.send_interval = send_interval
        self.enable_debug = enable_debug
        self.max_retries = max_retries

        self.events_count = 0
        self.send_events_count = 0
        self.requests_count = 0

        self.queue = list()
        self.loop = asyncio.get_event_loop()
        self.task = self.loop.create_task(self.start_loop())
        connection_pool = TCPConnector(limit=15, limit_per_host=15)
        self._http_client = ClientSession(connector=connection_pool, trust_env=True)

        atexit.register(self._shutdown)

    def debug(self, str):
        if self.enable_debug:
            print(str)

    def insert_entities_text(self, text, entities):
        for entity in entities:
            entity["text"] = text[entity["start"]:entity["end"]]
        return entities

    def check_duplicate_entities(self, entities):
        entities_start = list()
        new_entities = list()
        entities = sorted(entities, key=lambda entity: entity['start'])
        for entity in entities:
            if entity["start"] not in entities_start:
                entities_start.append(entity["start"])
                new_entities.append(entity)
        return new_entities

    ## called by Rasa on events
    def publish(self, event):
        try:
            if event['event'] == 'user':
                text = event['text']
                new_text = text
                event['parse_data']['entities'] = self.insert_entities_text(text, event["parse_data"]["entities"])
                entities = self.check_duplicate_entities(event['parse_data']['entities'])
                event['handled'] = event['parse_data']['intent']['name'] != 'nlu_fallback'
                for entity in entities:
                    dict_entity = {'entity': entity['entity'], 'value': entity['value']}
                    new_text = new_text.replace(entity["text"], f"[{entity['text']}]{json.dumps(dict_entity)}", 1)
                event['text'] = new_text
            if event['event'] in ['session_started', 'user', 'bot']:
                self.add_to_queue(event)
        except:
            print('Failed to add event to queue')

    def add_to_queue(self, event):
        self.events_count += 1
        self.queue.append(event)
        if len(self.queue) >= self.max_queue_size:
            self.create_flush_task()

    async def flush(self, events):
        self.requests_count +=1
        count = self.requests_count
        for retry in range(self.max_retries + 1):
            try:
                url = f"{self.api_url}/track"
                params = {
                    "apiKey": self.api_key,
                    "platform": "rasa"
                }
                async with self._http_client.post(url, params=params, json=events) as request:
                    await request.read()
                    if request.status == 201:
                        self.send_events_count += len(events)
                        self.debug(f"{count} Sent {len(events)} events to Hecho after {retry} retries!")
                        return
                    elif retry == self.max_retries:
                        print(f"Failed sending {len(events)} events to Hecho after {retry} retries with status code:{request.status}")
                        return
                    self.debug(f"Failed sending {len(events)} events to Hecho after {retry} retries with status code:{request.status}, retrying...")
            except RuntimeError as e:
                if retry == self.max_retries:
                    print(f"RuntimeError: Failed to send events to Hecho after {retry} retries", e)
            except Exception as e:
                if retry == self.max_retries:
                    print(f"Exception: Failed to send events to Hecho after {retry} retries: {e.message}")

    def create_flush_task(self):
        if len(self.queue) <= 0:
            return
        events = self.queue
        self.queue = list()
        self.loop.create_task(self.flush(events))

    async def start_loop(self):
        try:
            while True:
                await asyncio.sleep(self.send_interval)
                self.create_flush_task()
        except:
            self.debug('Exiting Hecho Events Broker...')

    ## called by Rasa on close bot
    async def close(self):
        self.task.cancel()
        self.create_flush_task()

    def _shutdown(self):
        asyncio.run(self._http_client.close())

    @classmethod
    async def from_endpoint_config(cls, broker_config):
        if broker_config is None:
            return None
        return cls(**broker_config.kwargs)
