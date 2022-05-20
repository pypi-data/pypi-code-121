import os
import json
import shutil
import logging
import numpy as np
import pandas as pd
from os.path import join, exists, dirname, splitext
from d3m.container import Dataset
from d3m.utils import path_to_uri
from d3m.container.utils import save_container
from d3m.metadata.problem import PerformanceMetricBase, TaskKeywordBase
from d3m.container.dataset import FILE_EXTENSIONS

logger = logging.getLogger(__name__)
DATASET_ID = 'internal_dataset'


def is_d3m_format(dataset_path, suffix):
    """Checks whether the given dataset is in D3M format, or if it needs conversion.
    """
    if isinstance(dataset_path, str) and exists(join(dataset_path, 'dataset_%s' % suffix, 'datasetDoc.json')):
        return True

    return False


def is_d3m_collection(dataset_path, suffix, collection_type):
    """Checks whether the given D3M dataset is a "collection".
    """
    dataset_path = join(dataset_path, 'dataset_%s' % suffix, 'datasetDoc.json')
    with open(dataset_path) as fin:
        dataset_doc = json.load(fin)
        for data_resource in dataset_doc['dataResources']:
            if data_resource.get('isCollection', False):
                if data_resource['resType'] == collection_type:
                    return True
    return False


def dataset_to_d3m(dataset_path, output_folder, problem_config, suffix):
    """Converts a "raw" dataset to D3M format and returns the temporary dataset directory.
    """
    problem_config = check_problem_config(problem_config)
    d3m_root_folder = join(output_folder, 'temp', 'dataset_d3mformat', suffix)
    d3m_dataset_folder = join(d3m_root_folder, 'dataset_%s' % suffix)
    d3m_problem_folder = join(d3m_root_folder, 'problem_%s' % suffix)
    d3m_dataset = create_d3m_dataset(dataset_path, d3m_dataset_folder)
    create_d3m_problem(d3m_dataset['learningData'], d3m_problem_folder, problem_config)

    if 'collection' in problem_config['extras']:
        add_collection_resource(d3m_dataset['learningData'], d3m_dataset_folder, problem_config, dataset_path, suffix)

    if 'time_indicator' in problem_config['extras']:
        add_timeseries_info(d3m_dataset_folder, problem_config)

    if 'objectDetection' in problem_config['task_keywords']:
        modify_indexes(d3m_dataset_folder, problem_config)

    return d3m_root_folder


def check_problem_config(problem_config):
    if problem_config['target_column'] is None:
        raise ValueError('Parameter "target" not provided, but it is mandatory')

    valid_task_keywords = {keyword for keyword in TaskKeywordBase.get_map().keys() if keyword is not None}
    if problem_config['task_keywords'] is None:
        problem_config['task_keywords'] = ['classification', 'multiClass']
        logger.warning('Task keywords not defined, using: [%s]' % ', '.join(problem_config['task_keywords']))

    for task_keyword in problem_config['task_keywords']:
        if task_keyword not in valid_task_keywords:
            raise ValueError('Unknown "%s" task keyword, you should choose among [%s]' %
                             (task_keyword, ', '.join(valid_task_keywords)))

    valid_metrics = {metric for metric in PerformanceMetricBase.get_map()}
    if problem_config['metric'] is None:
        problem_config['metric'] = 'accuracy'
        if 'regression' in problem_config['task_keywords']:
            problem_config['metric'] = 'rootMeanSquaredError'
        logger.warning('Metric not defined, using: %s' % problem_config['metric'])
    elif problem_config['metric'] not in valid_metrics:
        raise ValueError('Unknown "%s" metric, you should choose among [%s]' %
                         (problem_config['metric'], ', '.join(valid_metrics)))

    #  Check special cases
    if 'f1' == problem_config['metric'] and 'binary' in problem_config['task_keywords'] and \
            'pos_label' not in problem_config['extras']:
        raise ValueError('pos_label parameter is mandatory for f1 and binary problems')

    if 'clustering' in problem_config['task_keywords'] and 'num_clusters' not in problem_config['extras']:
        raise ValueError('num_clusters parameter is mandatory for clustering problems')

    if 'timeSeries' in problem_config['task_keywords'] and 'forecasting' in problem_config['task_keywords'] and \
            'time_indicator' not in problem_config['extras']:
        raise ValueError('time_indicator parameter is mandatory for time-series forecasting problems')

    if 'timeSeries' in problem_config['task_keywords'] and 'grouped' in problem_config['task_keywords'] and \
            'grouping_category' not in problem_config['extras']:
        raise ValueError('grouping_category parameter is mandatory for grouped time-series forecasting problems')

    if 'timeSeries' in problem_config['task_keywords'] and 'classification' in problem_config['task_keywords'] and \
            'collection' not in problem_config['extras']:
        raise ValueError('collection parameter is mandatory for time-series classification problems')

    if any(x in problem_config['task_keywords'] for x in ['text', 'image', 'audio', 'video']) and \
            'collection' not in problem_config['extras']:
        raise ValueError('collection parameter is mandatory for text, image, audio, or video problems')

    return problem_config


def create_d3m_dataset(dataset_path, destination_path):
    if exists(destination_path):
        shutil.rmtree(destination_path)

    dataset = Dataset.load(path_to_uri(dataset_path), dataset_id=DATASET_ID)
    save_container(dataset, destination_path)

    return dataset


def create_d3m_problem(dataset, destination_path, problem_config):
    target_index = dataset.columns.get_loc(problem_config['target_column'])
    problem_config['target_index'] = target_index

    if exists(destination_path):
        shutil.rmtree(destination_path)
    os.makedirs(destination_path)

    metric = {"metric": problem_config['metric']}
    if 'pos_label' in problem_config['extras']:
        metric['posLabel'] = str(problem_config['extras']['pos_label'])

    target = {
        "targetIndex": 0,
        "resID": "learningData",
        "colIndex": problem_config['target_index'],
        "colName": problem_config['target_column']
    }
    if 'num_clusters' in problem_config['extras']:
        target["numClusters"] = problem_config['extras']['num_clusters']

    problem_json = {
        "about": {
            "problemID": "",
            "problemName": "",
            "problemDescription": "",
            "problemVersion": "4.0.0",
            "problemSchemaVersion": "4.0.0",
            "taskKeywords": problem_config['task_keywords']
        },
        "inputs": {
            "data": [
                {
                    "datasetID": DATASET_ID,
                    "targets": [target]
                }
            ],
            "performanceMetrics": [metric]
        },
        "expectedOutputs": {
            "predictionsFile": "predictions.csv"
        }
    }

    with open(join(destination_path, 'problemDoc.json'), 'w') as fout:
        json.dump(problem_json, fout, indent=4)


def add_collection_resource(dataset, d3m_dataset_folder, problem_config, dataset_path, suffix):
    with open(join(d3m_dataset_folder, 'datasetDoc.json')) as fin:
        dataset_json = json.load(fin)

    collection_column = problem_config['extras']['collection']['column']
    for column in dataset_json['dataResources'][0]['columns']:
        if column['colName'] == collection_column:
            column['role'].append('attribute')
            column['colType'] = 'string'
            column['refersTo'] = {'resID': '0', 'resObject': 'item'}

    extension = splitext(dataset[collection_column].iat[0])[1]  # Only use the first element to get the extension
    if extension not in FILE_EXTENSIONS:
        raise ValueError('Unknown "%s" extension, you should choose: [%s]' % (extension, ', '.join(FILE_EXTENSIONS)))

    collection_resource = {}
    collection_resource['resID'] = '0'
    collection_resource['resPath'] = 'collection'
    collection_resource['resType'] = FILE_EXTENSIONS[extension].split('/')[0]
    collection_resource['resFormat'] = {FILE_EXTENSIONS[extension]: [extension]}
    collection_resource['isCollection'] = True
    dataset_json['dataResources'].append(collection_resource)

    mapping_folders = {'TRAIN': 'train_folder', 'TEST': 'test_folder', 'SCORE': 'test_folder'}
    os.symlink(join(dirname(dataset_path), problem_config['extras']['collection'][mapping_folders[suffix]]),
               join(d3m_dataset_folder, 'collection'))

    with open(join(d3m_dataset_folder, 'datasetDoc.json'), 'w') as fout:
        json.dump(dataset_json, fout, indent=4)


def add_timeseries_info(d3m_dataset_folder, problem_config):
    with open(join(d3m_dataset_folder, 'datasetDoc.json')) as fin:
        dataset_json = json.load(fin)

    time_column = problem_config['extras']['time_indicator']
    grouping_column = problem_config['extras'].get('grouping_category', None)  # grouping_category can be optional

    for column in dataset_json['dataResources'][0]['columns']:
        if column['colName'] == time_column:
            column['role'] += ['attribute', 'timeIndicator']
            column['colType'] = 'dateTime'

        if column['colName'] == grouping_column:
            column['role'] += ['attribute', 'suggestedGroupingKey']
            column['colType'] = 'categorical'

    with open(join(d3m_dataset_folder, 'datasetDoc.json'), 'w') as fout:
        json.dump(dataset_json, fout, indent=4)


def modify_indexes(d3m_dataset_folder, problem_config):
    csv_path = join(d3m_dataset_folder, 'tables', 'learningData.csv')
    data = pd.read_csv(csv_path)
    collection_column = problem_config['extras']['collection']['column']
    data['d3mIndex'] = data.groupby(collection_column).ngroup()  # For the same values (e.g. images), the same indexes
    data.to_csv(csv_path, index=False)


def create_artificial_d3mtest(train_path, artificial_test_path, new_instances, target_column, text_column):
    # This is useful for cases where new instances are generated artificially
    if exists(artificial_test_path):
        shutil.rmtree(artificial_test_path)

    dataset_folder = join(artificial_test_path, 'dataset_TEST')
    problem_folder = join(artificial_test_path, 'problem_TEST')
    tables_folder = join(dataset_folder, 'tables')
    media_folder = join(dataset_folder, 'media')
    os.makedirs(dataset_folder)
    os.makedirs(problem_folder)
    os.makedirs(tables_folder)
    shutil.copy(join(train_path, 'dataset_TRAIN', 'datasetDoc.json'), join(dataset_folder, 'datasetDoc.json'))
    shutil.copy(join(train_path, 'problem_TRAIN', 'problemDoc.json'), join(problem_folder, 'problemDoc.json'))

    need_media_folder = False
    if exists(join(train_path, 'dataset_TRAIN', 'media')):
        need_media_folder = True
        os.makedirs(media_folder)

    data = {'d3mIndex': [], text_column: [], target_column: []}
    for i in range(len(new_instances)):
        text_value = new_instances[i]
        if need_media_folder:
            file_name = str(i) + '.txt'
            file_path = join(media_folder, file_name)
            with open(file_path, 'w') as fin:
                fin.write(text_value)
            text_value = file_name

        data['d3mIndex'].append(i)
        data[text_column].append(text_value)
        data[target_column].append(np.nan)

    train_columns = pd.read_csv(join(train_path, 'dataset_TRAIN', 'tables', 'learningData.csv')).columns
    data = pd.DataFrame(data, columns=train_columns)  # To have the same order of columns in train and test sets
    data.to_csv(join(tables_folder, 'learningData.csv'), index=False)


def d3mtext_to_dataframe(folder_path, suffix, text_column):
    """Reads a D3M text dataset into a single DataFrame, by loading the named text files.
    """
    dataframe = pd.read_csv(join(folder_path, 'dataset_%s' % suffix, 'tables', 'learningData.csv'))
    folder_files = join(folder_path, 'dataset_%s' % suffix, 'media')

    def read_text(file_name):
        file_path = join(folder_files, file_name)
        with open(file_path, 'r') as fin:
            text = fin.read().replace('\n', ' ')
            return text

    dataframe[text_column] = dataframe[text_column].apply(read_text)

    return dataframe


def _add_step(steps, modules, params, module_to_step, mod):
    if mod.id in module_to_step:
        return module_to_step[mod.id]

    # Special case: the "dataset" module
    if mod.package == 'data' and mod.name == 'dataset':
        module_to_step[mod.id] = 'inputs.0'
        return 'inputs.0'
    elif mod.package != 'd3m':
        raise ValueError("Got unknown module '%s:%s'", mod.package, mod.name)

    # Recursively walk upstream modules (to get `steps` in topological order)
    # Add inputs to a dictionary, in deterministic order
    inputs = {}

    for conn in sorted(mod.connections_to, key=lambda c: c.to_input_name):
        step = _add_step(steps, modules, params, module_to_step, modules[conn.from_module_id])

        if step.startswith('inputs.'):
            inputs[conn.to_input_name] = step
        else:
            if conn.to_input_name in inputs:
                previous_value = inputs[conn.to_input_name]
                if isinstance(previous_value, str):
                    inputs[conn.to_input_name] = [previous_value] + ['%s.%s' % (step, conn.from_output_name)]
                else:
                    inputs[conn.to_input_name].append('%s.%s' % (step, conn.from_output_name))
            else:
                inputs[conn.to_input_name] = '%s.%s' % (step, conn.from_output_name)
    # TODO load metadata from primitives
    primitive_desc = {
        'id': mod.id,
        'version': mod.version,
        'python_path': mod.name,
        'name': mod.name
    }
    with open(join(dirname(__file__), 'resource', 'primitives_metadata.json')) as f:
        primitives_metadata = json.load(f)
        for primitve in primitives_metadata:
            if primitive_desc['python_path'] == primitve['python_path']:
                primitive_desc['id'] = primitve['id']
                primitive_desc['version'] = primitve['version']
                primitive_desc['name'] = primitve['name']
                primitive_desc['digest'] = primitve['digest']
                break

    outputs = [{'id': 'produce'}]

    # Create step description
    if len(inputs) > 0:
        step = {
            'type': 'PRIMITIVE',
            'primitive': primitive_desc,
            'arguments': {
                name: {
                    'type': 'CONTAINER',
                    'data': data,
                }
                for name, data in inputs.items()
            },
            'outputs': outputs
        }
    else:
        step = {
            'type': 'PRIMITIVE',
            'primitive': primitive_desc,
        }

    # If hyperparameters are set, export them
    if mod.id in params:
        hyperparams = params[mod.id]
        # We check whether the hyperparameters have a value or the complete description
        hyperparams = {
            k: {'type': v['type'] if isinstance(v, dict) and 'type' in v else 'VALUE',
                'data': v['data'] if isinstance(v, dict) and 'data' in v else v}
            for k, v in hyperparams.items()
        }
        step['hyperparams'] = hyperparams

    step_nb = 'steps.%d' % len(steps)
    steps.append(step)
    module_to_step[mod.id] = step_nb

    return step_nb


def to_d3m_json(pipeline):
    """Converts a Pipeline to the JSON schema from metalearning working group.
    """
    steps = []
    modules = {mod.id: mod for mod in pipeline.modules}
    params = pipeline.parameters
    module_to_step = {}
    for _, mod in sorted(modules.items(), key=lambda x: x[0]):
        _add_step(steps, modules, params, module_to_step, mod)

    return {
        'id': str(pipeline.id),
        'name': str(pipeline.id),
        'description': pipeline.origin or '',
        'schema': 'https://metadata.datadrivendiscovery.org/schemas/'
                  'v0/pipeline.json',
        'created': pipeline.created_date.isoformat() + 'Z',
        'context': 'TESTING',
        'inputs': [
            {'name': "input dataset"},
        ],
        'outputs': [
            {
                'data': 'steps.%d.produce' % (len(steps) - 1),
                'name': "predictions",
            }
        ],
        'steps': steps,
    }
