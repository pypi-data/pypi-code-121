from python_helper import log
from globals import getGlobalsInstance
globalsInstance = getGlobalsInstance()


MESSAGE_API_KEY = globalsInstance.getSetting('queue.message.api-key')

LISTENER_TIMEOUT = globalsInstance.getSetting('queue.message.listener.timeout')

EMITTER_URL = globalsInstance.getSetting('queue.message.emitter.url')
EMITTER_TIMEOUT = globalsInstance.getSetting('queue.message.emitter.timeout')
SOME_UNIQUE_QUEUE_KEY = globalsInstance.getSetting('queue.message.emitter.queue-key.test-1')
