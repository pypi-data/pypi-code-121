import re
import copy


def is_constructpredictions(step):
    if step['primitive']['python_path'] == 'd3m.primitives.data_transformation.construct_predictions.Common':
        return True
    return False


def is_estimator(step):
    if step['primitive']['python_path'].startswith('d3m.primitives.classification.'):
        return True
    return False


def create_confidence_pipeline(pipeline):
    pipeline = copy.deepcopy(pipeline)
    steps = pipeline['steps']
    new_steps = []
    estimator = None

    for index, step in enumerate(steps):
        if is_estimator(step):
            estimator = step
            estimator['index'] = index
        elif is_constructpredictions(step):
            # Add 3 necessary primitives to calculate confidence
            input_id = int(re.match(r'steps.(\d+).produce', step['arguments']['inputs']['data']).groups()[0])

            step_horizontal_concat = {
                "type": "PRIMITIVE",
                "primitive": {
                    "id": "aff6a77a-faa0-41c5-9595-de2e7f7c4760",
                    "name": "Concatenate two dataframes",
                    "version": "0.2.0",
                    "python_path": "d3m.primitives.data_transformation.horizontal_concat.DataFrameCommon",
                    "digest": "f1e8fe6ba0456e562d9613bd5f4221e221e9cadd23c684564137b2aa14495ada"
                },
                "arguments": {
                    "left": {
                        "data": estimator['arguments']['inputs']['data'],
                        "type": "CONTAINER"
                    },
                    "right": {
                        "data": estimator['arguments']['outputs']['data'],
                        "type": "CONTAINER"
                    }
                },
                "outputs": [
                    {
                        "id": "produce"
                    }
                ]
            }
            new_steps.append(step_horizontal_concat)

            step_unique_values = {
                "type": "PRIMITIVE",
                "primitive": {
                    "id": "dd580c45-9fbe-493d-ac79-6e9f706a3619",
                    "version": "0.1.0",
                    "name": "Add all_distinct_values to the metadata of the input Dataframe",
                    "python_path": "d3m.primitives.operator.compute_unique_values.Common",
                    "digest": "04178b5c55f24e4f0a2acd5111affe8fc6fe752ab54a380028d439787ec170ef"
                },
                "arguments": {
                    "inputs": {
                        "type": "CONTAINER",
                        "data": 'steps.%d.produce' % (input_id + 1)
                    }
                },
                "outputs": [
                    {
                        "id": "produce"
                    }
                ]
            }
            new_steps.append(step_unique_values)

            step = {
                "type": "PRIMITIVE",
                "primitive": {
                    "id": "500c4f0c-a040-48a5-aa76-d6463ea7ea37",
                    "version": "0.1.0",
                    "name": "Construct confidence",
                    "python_path": "d3m.primitives.data_transformation.construct_confidence.Common",
                    "digest": "8685b43969b06ee2418e2852d8019b4c638813cca5cb2d94962ce782e0ae4651"
                },
                "arguments": {
                    "inputs": {
                        "type": "CONTAINER",
                        "data": 'steps.%d.produce' % (input_id + 2)
                    },
                    "reference": {
                        "type": "CONTAINER",
                        "data": step['arguments']['reference']['data']
                    }
                },
                "outputs": [
                    {
                        "id": "produce"
                    }
                ],
                "hyperparams": {
                    "primitive_learner": {
                        "type": "PRIMITIVE",
                        "data": estimator['index']
                    }
                }
            }

        new_steps.append(step)

    pipeline['steps'] = new_steps
    output_id = int(re.match('steps.(\d+).produce', pipeline['outputs'][0]['data']).groups()[0])
    pipeline['outputs'][0]['data'] = 'steps.%d.produce' % (output_id + 2)

    return pipeline
