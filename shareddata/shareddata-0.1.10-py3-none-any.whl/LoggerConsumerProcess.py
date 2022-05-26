import sys

from SharedData.Logger import Logger
from SharedData.SharedDataAWSKinesis import KinesisLogStreamConsumer

if len(sys.argv)>=2:
    USER = str(sys.argv[1])
else:
    raise Exception ('Missing user parameter!')

logger = Logger(__file__,user=USER)
Logger.log.info('Starting SharedDataLogsConsumer process')
consumer = KinesisLogStreamConsumer(user=USER)
dflogs = consumer.readLogs()
stream = consumer.connect()
Logger.log.info('Starting SharedDataLogsConsumer process STARTED!')
consumer.loop()