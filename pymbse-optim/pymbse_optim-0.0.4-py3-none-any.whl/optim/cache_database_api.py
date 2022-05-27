import pandas as pd
import requests

MODEL_SNAPSHOTS_API_ENDPOINT = "api/model_snapshots"
DESCENDING = -1
ASCENDING = 1


def get_max_optimization_ix(ip_with_port: str) -> int:
    url = get_url(ip_with_port)
    pipeline = [{"$match": {"input_parameters.optimization_ix": {"$exists": True}}},
                {"$project": {"input_parameters.optimization_ix": 1, "_id": 0}},
                {"$sort": {"input_parameters.optimization_ix": DESCENDING}},
                {"$limit": 1}]
    response = requests.get(url, json=pipeline)
    if response.status_code == 200:
        if not response.json():
            return -1
        else:
            return response.json()[0]['input_parameters']['optimization_ix']
    else:
        raise ConnectionError(response.json())


def get_url(ip_with_port: str) -> str:
    return "%s/%s/generic_query/" % (ip_with_port, MODEL_SNAPSHOTS_API_ENDPOINT)


def get_list_of_best_generation_ix_individual_ix_score(ip_with_port: str, optimization_ix: int) -> pd.DataFrame:
    url = get_url(ip_with_port)
    pipeline = [
        {"$match": {"input_parameters.optimization_ix": optimization_ix}},
        {"$sort": {"input_parameters.generation_ix": ASCENDING,
                   "figures_of_merit.value": ASCENDING}},
        {"$group": {"_id": "$input_parameters.generation_ix",
                    "doc_with_min_value": {"$first": "$$ROOT"},
                    }},
        {"$replaceWith": "$doc_with_min_value"},
        {"$project": {"input_parameters.generation_ix": 1,
                      "input_parameters.individual_ix": 1,
                      "figures_of_merit": 1, "_id": 0}},
        {"$sort": {"input_parameters.generation_ix": ASCENDING}}
    ]
    response = requests.get(url, json=pipeline)
    if response.status_code == 200:
        output = []
        for dct in response.json():
            value = dct['figures_of_merit']['value']
            del dct['figures_of_merit']['value']
            output.append({**dct['input_parameters'], 'value': value, 'figures_of_merit': dct['figures_of_merit']})
        return pd.DataFrame(output)
    else:
        raise ConnectionError(response.json())


def get_best_optimization_snapshot(ip_with_port: str, optimization_ix: int) -> dict:
    url = get_url(ip_with_port)

    pipeline = [{"$match": {"input_parameters.optimization_ix": optimization_ix}},
                {"$project": {"_id": 0}},
                {"$sort": {"figures_of_merit.value": ASCENDING}},
                {"$limit": 1}]

    response = requests.get(url, json=pipeline)
    if response.status_code == 200:
        return response.json()[0]
    else:
        raise ConnectionError(response.json())


def get_selected_optimization_snapshot(ip_with_port: str,
                                       optimization_ix: int,
                                       generation_ix: int,
                                       individual_ix: int) -> dict:
    url = get_url(ip_with_port)

    pipeline = [{"$match": {'input_parameters.optimization_ix': optimization_ix,
                            'input_parameters.generation_ix': generation_ix,
                            'input_parameters.individual_ix': individual_ix}},
                {'$project': {'input_parameters': 1,
                              'figures_of_merit': 1,
                              'artefacts': 1,
                              '_id': 0}}]

    response = requests.get(url, json=pipeline)
    if response.status_code == 200:
        return response.json()[0]
    else:
        raise ConnectionError(response.json())
