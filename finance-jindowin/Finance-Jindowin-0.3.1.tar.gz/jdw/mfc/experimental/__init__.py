import os
MQ_URL = 'amqp://' + os.environ['MQ_URL'] + '/realtime?heartbeat=3600'
NTN_URL = 'mongodb://' + os.environ['NTN_URL']
NTN_COLL = NTN_URL.split('/')[-1]

ATL_URL = 'mongodb://' + os.environ['ATL_URL']
ATL_COLL = ATL_URL.split('/')[-1]