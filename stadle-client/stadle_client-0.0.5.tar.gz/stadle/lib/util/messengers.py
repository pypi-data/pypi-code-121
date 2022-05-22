import time
from typing import Dict, List, Any

import numpy as np

from stadle.lib.util.states import ModelType, DBMsgType, AgentMsgType, AggMsgType, DBPushMsgLocation

MESSAGE_MAX_SIZE = 100


def generate_lmodel_update_message(agent_id: str,
                                   model_id: str,
                                   local_models: Dict[str, np.array],
                                   performance_dict: Dict[str, float],
                                   num_samples: int) -> List[Any]:
    update_rep = {
        "agent_id": agent_id,
        "model_id": model_id,
        "models": local_models,
        "gene_time": time.time(),
        "performance_dict": performance_dict,
        "num_samples": num_samples
    }

    msg = [AgentMsgType.update, update_rep]

    return msg


def generate_participate_message(agent):
    # TODO jsonify

    agent_rep = {
        "agent_id": agent.id,
        "init_weights_flag": agent.init_weights_flag,
        "simulation_flag": agent.simulation_flag,
        "exch_port": agent.exch_port,
        "agent_name": agent.agent_name,
        "reg_time": time.time(),
        "agent_ip": agent.agent_ip,
        "token": agent.token,
        "exch_active": agent.exch_active
    }

    msg = [AgentMsgType.participate, agent_rep]

    return msg


def generate_initialize_model_message(agent, model_id, models, gene_time, performance_dict, base_model):

    agent_rep = {
        "agent_id": agent.id,
        "init_weights_flag": agent.init_weights_flag,
        "simulation_flag": agent.simulation_flag,
        "exch_port": agent.exch_port,
        "agent_name": agent.agent_name,
        "gene_time": gene_time,
        "agent_ip": agent.agent_ip,
        "token": agent.token,
        "exch_active": agent.exch_active,
        "model_id": model_id,
        "models": models,
        "performance_dict": performance_dict,
        "base_model": base_model
    }

    msg = [AgentMsgType.initialize_model, agent_rep]

    return msg
