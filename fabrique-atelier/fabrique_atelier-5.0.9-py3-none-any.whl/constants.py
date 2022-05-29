from collections import namedtuple

conv2ntuple = lambda fields: namedtuple('namedtuple', fields)(*fields)

MessageFieldsConstants = conv2ntuple(['data',  # main field with data
                                      'error',
                                      'metrics',
                                      'alerts',
                                      'kafka_key',  # will be written to key field
                                      'timestamp',  # event timestamp in ms (153718528187)
                                      'destination'])

outgoing_fields = ['data', 'timestamp']  # fields in messages which must be sent to output

special_topics = namedtuple('namedtuple', ['end', 'metrics', 'error', 'begin']
                            )('%end%', '%metrics%', '%error%', '%begin%')

VALID_ACTOR_TYPES = conv2ntuple(['mapper', 'dispatcher'])

PIPELINE_INPUT_TPL = '{prefix}.{pipeline_name}.{pipeline_version}.in'
TOPIC_TPL = '{prefix}.{pipeline_name}.{pipeline_version}_{from_node}.out'
TOPIC_TPL_IN = '{prefix}.{pipeline_name}.{pipeline_version}_{to_node}.in'
