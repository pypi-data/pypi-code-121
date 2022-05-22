from enum import Enum, IntEnum


# --- STATE ENUM --- #

class BaseModelConvFormat:
    """
    The original format of the model (ex. pytorch, keras), or the desired training format
    Used to convert model during training
    """
    pytorch_format = 0
    tensorflow_format = 1
    keras_format = 2

    formats = [pytorch_format, tensorflow_format, keras_format]

class ClientState(IntEnum):
    """
    Client states defined in the STADLE Agent specification
    """
    waiting_sgm = 0
    training = 1
    sending = 2
    sg_ready = 3


class ModelType(Enum):
    """
    Types of models
    """
    local = 0
    cluster = 1
    semi_global = 2


class IDPrefix:
    agent = 'agent'
    aggregator = 'aggregator'


# --- MESSAGE PROTOCOL --- #

# MESSAGE TYPES

class DBMsgType(Enum):
    """
    Message types defined in the STADLE AGG-DB protocol
    """
    push = 0
    aggr_poll = 1
    get_list = 2
    get_models = 3
    aggr_register = 4
    agent_register = 5
    base_model_register = 6
    base_model_request = 7
    agg_bm_update = 8
    ack = 9
    update = 10
    registration_failed = 11


class AgentMsgType(Enum):
    """
    Message types defined in the STADLE protocol sent from an agent to an aggregator
    """
    participate = 0
    update = 1
    initialize_model = 2
    waiting_sgm = 3
    # sending_local_model = 4
    # polling


class AggMsgType(Enum):
    """
    Message types defined in the STADLE protocol sent from an aggregator to an agent
    """
    welcome = 0
    update = 1
    registration_failed = 2
    ack = 3
    not_opt = 4
    max_agents_reached = 5


# MESSAGE HEADER LOCATION INFO

# AGGR <-> DB
class DBPushMsgLocation(IntEnum):
    """
    index indicator to read a push message
    """
    msg_type = 0
    push_rep = 1
    aggregator_info = 2
    state_manager_info = 3
    agent_info = 4


# AGGR <-> AGT
class SGMDistributionMsgLocation(IntEnum):
    """
    index indicator to read a sg_model distribution message
    """
    msg_type = 0
    aggregator_id = 1
    model_id = 2
    round = 3
    sg_models = 4
    base_model = 5