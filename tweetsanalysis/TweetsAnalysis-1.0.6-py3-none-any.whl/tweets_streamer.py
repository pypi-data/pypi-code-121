import threading 
import os

from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream
from kafka import KafkaProducer

from TweetAnalysis.config.core import config
from TweetAnalysis.config import logging_config


_logger = logging_config.get_logger(__name__)

consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_secret = os.environ['TWITTER_ACCESS_SECRET']


class StdOutListener(StreamListener):
    """Listener class for the tweets stream"""

    def __init__(self, producer):
        self.producer = producer

    def on_data(self, data):
        try:
            self.producer.send(
                config.kafka.KAFKA_TOPIC_NAME, data.encode('utf-8'))
            # print(data)
        except BaseException as e:
            _logger.warning("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        _logger.warning(f'status: {status}')


def get_stream(topic):
    """getting the tweets stream with twitter api and handling it with kafka"""

    _logger.info('tweets streaming...')
    global stream
    producer = KafkaProducer(bootstrap_servers=config.kafka.KAFKA_HOST)
    l = StdOutListener(producer)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    stream = Stream(auth, l)
    stream.filter(track=[topic], languages=['en'])
    return None


def start_tweet_stream(topic):
    """starting the tweets stream in a process"""

    _logger.info('starting the tweets stream in a thread...')
    thread = threading.Thread(target=get_stream, args=(topic,))
    thread.start()
    return thread

def stop_tweet_stream(thread):
    """stopping the tweets stream in a thread"""

    _logger.info('stopping the tweets stream in a thread...')
    stream.disconnect()
    thread.join()
    return None

if __name__ == '__main__':
    # arg = sys.argv[1]
    # print(arg)
    get_stream('music')
    # _logger.info(f'Run From: {__name__}')
