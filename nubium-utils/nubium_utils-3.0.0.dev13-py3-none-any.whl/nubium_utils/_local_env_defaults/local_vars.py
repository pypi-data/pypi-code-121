local_dotenv_dict = dict(

# faust - default override
FAUST_DATADIR_BASE='/tmp',
USE_ROCKSDB='False',
TOPIC_REPLICATION_FACTOR='1',
STREAM_RECOVERY_DELAY='3',
KIWF_LOG_FILEPATH='',

# global - default override
DO_METRICS_PUSHING='False',
LOGLEVEL='DEBUG',

# global - required
HOSTNAME='local-app-0',
APP_NAME='local_app',
MP_PROJECT='none',
)
