import atexit
import os
import random
import re
import sys
import time
import json
import signal
import platform
import logging
import datetime
import subprocess
import pandas as pd
import d3m_interface.visualization as vis
from d3m_interface.data_converter import is_d3m_format, is_d3m_collection, dataset_to_d3m, d3mtext_to_dataframe, to_d3m_json
from d3m_interface.confidence_calculator import create_confidence_pipeline
from d3m_interface.utils import copy_folder, fix_path_for_docker, is_port_in_use, is_openml_dataset
from d3m_interface.grpc_client import GrpcClient
from d3m_interface.pipeline import Pipeline
from threading import Thread
from os.path import join, split, exists, abspath
from posixpath import join as pjoin
from IPython.core.getipython import get_ipython
from d3m.metadata.problem import PerformanceMetric
from d3m.utils import compute_digest


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)


AUTOML_DOCKER_IMAGES = {'AlphaD3M': 'registry.gitlab.com/vida-nyu/d3m/alphad3m:latest',
                        'AutonML': 'registry.gitlab.com/sray/cmu-ta2:latest'}

IGNORE_SUMMARY_PRIMITIVES = {'d3m.primitives.data_transformation.construct_predictions.Common',
                             'd3m.primitives.data_transformation.extract_columns_by_semantic_types.Common',
                             'd3m.primitives.data_transformation.dataset_to_dataframe.Common',
                             'd3m.primitives.data_transformation.denormalize.Common',
                             'd3m.primitives.data_transformation.column_parser.Common'}


class DockerRuntime:
    dataset_in_container = '/input/dataset'
    output_in_container = '/output'
    static_in_container = '/static'

    @classmethod
    def default_port(cls):
        return random.randint(32769, 65535)

    def __init__(self, automl_id, dataset, output_folder, resource_folder, port=45042, verbose=False):
        image = AUTOML_DOCKER_IMAGES[automl_id]
        self.name = 'automl-container-%s' % port

        process_returncode = subprocess.call(['docker', 'inspect', '--type=image', image],
                                             stdout=subprocess.DEVNULL,
                                             stderr=subprocess.STDOUT)
        if process_returncode != 0:
            raise ValueError('Image "%s" does not exist, please download it.' % image)

        process_returncode = 0
        while process_returncode == 0:
            # Force to stop the docker container
            process_returncode = subprocess.call(['docker', 'stop', self.name],
                                                 stdout=subprocess.DEVNULL,
                                                 stderr=subprocess.STDOUT)
            time.sleep(2)

        logger.info("Creating Docker container %s...", self.name)

        stdout, stderr = subprocess.DEVNULL, subprocess.STDOUT
        if verbose:
            stdout, stderr = None, None

        self.proc = subprocess.Popen(
            [
                'docker', 'run', '--rm',
                '--name', self.name,
                '-p', '%d:45042' % port,
                '-e', 'D3MRUN=ta2ta3',
                '-e', 'D3MINPUTDIR=/input',
                '-e', 'D3MOUTPUTDIR=/output',
                '-e', 'D3MSTATICDIR=/static',
                '-v', '%s:/input/dataset/' % fix_path_for_docker(dataset),
                '-v', '%s:/output' % fix_path_for_docker(output_folder),
                '-v', '%s:/static' % fix_path_for_docker(resource_folder),
                image,
            ],
            stdout=stdout, stderr=stderr
        )

        atexit.register(self.close)

    def run_command(self, args):
        cmd = ['docker', 'exec', self.name]
        cmd.extend(args)
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
        )
        _, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(stderr.decode())

    def close(self):
        subprocess.call(['docker', 'stop', self.name], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    __del__ = close


class SingularityRuntime:
    dataset_in_container = '/input/dataset'
    output_in_container = '/output'
    static_in_container = '/static'

    @classmethod
    def default_port(cls):
        return 45042

    def __init__(self, automl_id, dataset, output_folder, resource_folder, port=45042, verbose=False):
        image = AUTOML_DOCKER_IMAGES[automl_id]

        if port != 45042:
            raise ValueError(
                "There is currently no way to change the port used by the "
                + "AutoML system when using Singularity"
            )

        process_returncode = 0
        while process_returncode == 0:
            # Force to stop the singularity container
            process_returncode = subprocess.call(['singularity', 'instance', 'stop', 'ta2_container'])
            time.sleep(2)

        os.makedirs(output_folder, exist_ok=True)
        logger.info("Creating Singularity instance...")

        stdout, stderr = subprocess.DEVNULL, subprocess.STDOUT
        if verbose:
            stdout, stderr = None, None

        process = subprocess.Popen(
            [
                'singularity', 'instance', 'start',
                '--writable-tmpfs',
                '--env', 'D3MRUN=ta2ta3',
                '--env', 'D3MINPUTDIR=/input',
                '--env', 'D3MOUTPUTDIR=/output',
                '--env', 'D3MSTATICDIR=/static',
                '--bind', '%s:/input/dataset/' % dataset,
                '--bind', '%s:/output' % output_folder,
                '--bind', '%s:/static' % resource_folder,
                'docker://' + image,
                'ta2_container',
            ],
            stderr=subprocess.PIPE,
        )
        _, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(stderr.decode())

        logger.info("Instance created, running command...")
        self.proc = subprocess.Popen(
            [
                'singularity', 'run',
                '--writable-tmpfs',
                '--env', 'D3MRUN=ta2ta3',
                '--env', 'D3MINPUTDIR=/input',
                '--env', 'D3MOUTPUTDIR=/output',
                '--env', 'D3MSTATICDIR=/static',
                '--bind', '%s:/input/dataset/' % dataset,
                '--bind', '%s:/output' % output_folder,
                '--bind', '%s:/static' % resource_folder,
                'instance://ta2_container',
            ],
            stdout=stdout, stderr=stderr
        )

        atexit.register(self.close)

    def run_command(self, args):
        cmd = ['singularity', 'exec', 'instance://ta2_container']
        cmd.extend(args)
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
        )
        _, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(stderr.decode())

    def close(self):
        subprocess.call(['singularity', 'instance', 'stop', 'ta2_container'])

    __del__ = close


class LocalRuntime:
    @classmethod
    def default_port(cls):
        return 45042

    def __init__(self, automl_id, dataset, output_folder, resource_folder, port=45042, verbose=False):
        if port != 45042:
            raise ValueError(
                "There is currently no way to change the port used by the "
                + "AutoML system when using local execution"
            )

        self.dataset_in_container = dataset
        self.output_in_container = output_folder
        self.static_in_container = resource_folder
        os.makedirs(output_folder, exist_ok=True)
        logger.info("Starting process...")

        stdout, stderr = subprocess.DEVNULL, subprocess.STDOUT
        if verbose:
            stdout, stderr = None, None

        self.proc = subprocess.Popen(
            ['eval.sh'],
            env=dict(
                os.environ,
                D3MRUN='ta2ta3',
                D3MINPUTDIR='/input',
                D3MOUTPUTDIR='/output',
                D3MSTATICDIR='/static',
            ),
            stdout=stdout, stderr=stderr
        )

        atexit.register(self.close)

    def run_command(self, args):
        process = subprocess.Popen(args, stderr=subprocess.PIPE)
        _, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(stderr.decode())

    def close(self):
        if self.proc is not None:
            self.proc.terminate()
            if self.proc.wait(10) is None:
                self.proc.kill()
            self.proc = None

    __del__ = close


class PypiRuntime:
    @classmethod
    def default_port(cls):
        return random.randint(32769, 65535)

    def __init__(self, automl_id, dataset, output_folder, resource_folder, port=45042, verbose=False):
        if is_port_in_use(port):
            logger.warning('Port %d is already used. Reusing that session. Use the "end_session()" method to end '
                           'sessions safely' % port)

        self.dataset_in_container = dataset
        self.output_in_container = output_folder
        self.static_in_container = resource_folder
        os.makedirs(output_folder, exist_ok=True)
        logger.info("Starting process...")

        stdout, stderr = subprocess.DEVNULL, subprocess.STDOUT
        if verbose:
            stdout, stderr = None, None

        os.environ['D3MOUTPUTDIR'] = output_folder
        os.environ['D3MSTATICDIR'] = resource_folder
        os.environ['D3MPORT'] = str(port)
        # TODO: Every AutoML should have an entry point like: '[id_automl]_serve' (We need to document it)
        entry_point = '%s_serve' % automl_id.lower()
        self.proc = subprocess.Popen([entry_point], stdout=stdout, stderr=stderr)
        atexit.register(self.close)

    def run_command(self, args):
        process = subprocess.Popen(args, stderr=subprocess.PIPE)
        _, stderr = process.communicate()

        if process.returncode != 0:
            raise RuntimeError(stderr.decode())

    def close(self):
        if self.proc is not None:
            self.proc.terminate()
            if self.proc.wait(10) is None:
                self.proc.kill()
            self.proc = None

    __del__ = close


class AutoML:
    def __init__(self, output_folder, automl_id='AlphaD3M', container_runtime='docker', resource_folder=None, grpc_port=None, verbose=False):
        """Create/instantiate an AutoML object

        :param output_folder: Path to the output directory
        :param automl_id: AutoML system name to be used. AutoML systems available are: 'AlphaD3M', 'AutonML'. Currently
            only AlphaD3M is available for the container_runtime='pypi' option
        :param resource_folder: Path to the directory where the resources are stored. This is needed only for some
            primitives that use pre-trained models, databases ,etc.
        :param container_runtime: The container runtime to use, can be 'docker', 'singularity', 'pypi', or 'local'
        :param grpc_port: Port to be used by GRPC
        :param verbose: Whether or not to show all the logs from AutoML systems
        """
        if automl_id not in AUTOML_DOCKER_IMAGES:
            raise ValueError('Unknown "%s" AutoML, you should choose among: [%s]' % (automl_id, ', '.join(AUTOML_DOCKER_IMAGES)))

        output_folder = abspath(output_folder)  # Make an absolute path
        self.output_folder = output_folder
        self.resource_folder = resource_folder if resource_folder is not None else output_folder

        if container_runtime == 'docker':
            self.container_runtime = DockerRuntime
        elif container_runtime == 'singularity':
            self.container_runtime = SingularityRuntime
        elif container_runtime == 'pypi':
            self.container_runtime = PypiRuntime
        elif container_runtime == 'local':
            self.container_runtime = LocalRuntime
        else:
            raise ValueError("Unknown container runtime %r" % container_runtime)
        if grpc_port is None:
            grpc_port = self.container_runtime.default_port()
        self.automl_id = automl_id
        self.pipelines = {}
        self.ta2 = None
        self.ta3 = None
        self.dataset = None
        self.problem_config = None
        self.port = grpc_port
        self.verbose = verbose

    def search_pipelines(self, dataset, time_bound, time_bound_run=5, target=None, metric=None, task_keywords=None,
                         method='holdout', stratified=False, shuffle=True, folds=10, train_ratio=0.70, random_seed=0,
                         exclude_primitives=None, include_primitives=None, **kwargs):
        """Perform the search of pipelines

        :param dataset: Path to dataset. It supports CSV file, D3M dataset, OpenML, and Sklearn datasets
        :param time_bound: Limit time in minutes to perform the search
        :param time_bound_run: Limit time in minutes to score a pipeline
        :param target: Column name of the potential target variable for a problem
        :param metric: The provided metrics are the following: `hammingLoss, accuracy, objectDetectionAP,
            rocAucMicro, f1Macro, meanSquaredError, f1, jaccardSimilarityScore, normalizedMutualInformation, rocAuc,
            f1Micro, hitsAtK, meanAbsoluteError, rocAucMacro, rSquared, recall, meanReciprocalRank, precision,
            precisionAtTopK, rootMeanSquaredError`
        :param task_keywords: A list of keywords that capture the nature of the machine learning task. The keywords
            that can be combined to describe the task are the following: `tabular, nested, multiLabel, video,
            linkPrediction, multivariate, graphMatching, forecasting, classification, graph, semiSupervised, text,
            timeSeries, clustering, collaborativeFiltering, univariate, missingMetadata, remoteSensing, multiClass,
            regression, multiGraph, lupi, relational, audio, grouped, objectDetection, vertexNomination,
            communityDetection, geospatial, image, overlapping, nonOverlapping, speech, vertexClassification, binary`
        :param method: Method to score the pipeline: `holdout, cross_validation`
        :param stratified: Whether or not to split the data using a stratified strategy
        :param shuffle: Whether or not to shuffle the data before splitting
        :param folds: the seed used by the random number generator
        :param train_ratio: Represent the proportion of the dataset to include in the train split
        :param random_seed: The number seed used by the random generator
        :param exclude_primitives: List of primitive's names to be excluded in the search space. If None, all the
            primitives will be used in the search
        :param include_primitives: List of primitive's names to be included in the  search space. If None, all the
            primitives will be used in the search
        :param kwargs: Different arguments for problem's settings (e.g. pos_label for binary problems using F1)
        """
        suffix = 'TRAIN'
        dataset = abspath(dataset) if not is_openml_dataset(dataset) else dataset

        if not is_d3m_format(dataset, suffix):
            self.problem_config = {'target_column': target, 'metric': metric, 'task_keywords': task_keywords,
                                   'extras': kwargs}
            dataset = dataset_to_d3m(dataset, self.output_folder, self.problem_config, suffix)

        self.dataset = split(dataset)[0]
        self.start_automl()

        search_id = None
        if platform.system() != 'Windows':
            signal.signal(signal.SIGALRM, lambda signum, frame: self.ta3.stop_search(search_id))
            signal.alarm(time_bound * 60)
        train_dataset_d3m = pjoin(self.ta2.dataset_in_container, 'TRAIN/dataset_TRAIN/datasetDoc.json')
        problem_path = join(dataset, 'problem_TRAIN/problemDoc.json')
        start_time = datetime.datetime.utcnow()

        automl_hyperparameters = {'exclude_primitives': exclude_primitives, 'include_primitives': include_primitives}
        try:
            search_id = self.ta3.search_solutions(train_dataset_d3m, problem_path, time_bound, time_bound_run,
                                                  automl_hyperparameters)
            pipelines = self.ta3.get_solutions(search_id)
        except KeyboardInterrupt:
            self.ta3.stop_search(search_id)
            raise

        jobs = []

        for pipeline in pipelines:
            end_time = datetime.datetime.utcnow()
            try:
                pipeline_json = self.ta3.describe_solution(pipeline['id'])
            except Exception as e:
                logger.warning('Pipeline id=%s could not be decoded' % pipeline['id'], exc_info=e)
                continue
            summary_pipeline = self.get_summary_pipeline(pipeline_json)
            pipeline['search_id'] = search_id
            pipeline['json_representation'] = pipeline_json
            pipeline['summary'] = summary_pipeline
            duration = str(end_time - start_time)
            logger.info('Found pipeline id=%s, time=%s, scoring...' % (pipeline['id'], duration))

            job = Thread(target=self.score_in_search, args=(pipeline, train_dataset_d3m, problem_path, self.pipelines,
                                                            method, stratified, shuffle, folds, train_ratio, random_seed))
            jobs.append(job)
            job.start()

        if len(jobs) > 0:
            logger.info('Search completed, still scoring some pending pipelines...')

            for job in jobs:
                job.join()

            logger.info('Scoring completed for all pipelines!')
        else:
            logger.info('Search completed, no pipelines found!')

        if platform.system() != 'Windows':
            signal.alarm(0)

    def train(self, pipeline_id, expose_outputs=None):
        """Train a model using an specific ML pipeline

        :param pipeline_id: Pipeline id
        :param expose_outputs: The output of the pipeline steps. If None, it doesn't expose any output of the steps.
            If str, should be 'all' to shows the output of each step in the pipeline, If list, it should contain the
            ids of the steps, e.g. 'steps.2.produce'
        :returns: An id of the fitted pipeline with/without the pipeline step outputs
        """
        # TODO: It should receive the path to the train dataset as an optional parameter

        if pipeline_id not in self.pipelines:
            raise ValueError('Pipeline id=%s does not exist' % pipeline_id)

        logger.info('Training model...')
        if expose_outputs is None:
            expose_outputs = []
        elif isinstance(expose_outputs, str) and expose_outputs == 'all':
            expose_outputs = ['outputs.0']
            for index, step in enumerate(self.pipelines[pipeline_id]['json_representation']['steps']):
                for id_output in step['outputs']:
                    expose_outputs.append('steps.%d.%s' % (index, id_output['id']))

        train_dataset_d3m = pjoin(self.ta2.dataset_in_container, 'TRAIN/dataset_TRAIN/datasetDoc.json')
        fitted_pipeline_id, pipeline_step_outputs = self.ta3.train_solution(pipeline_id, train_dataset_d3m, expose_outputs)

        for step_id, step_csv_uri in pipeline_step_outputs.items():
            if not step_csv_uri.startswith('file://'):
                logger.warning('Exposed step output "%s" cannot be read' % step_id)
                continue
            step_csv_path = step_csv_uri.replace('file://' + self.ta2.output_in_container, self.output_folder)
            step_dataframe = pd.read_csv(step_csv_path)
            pipeline_step_outputs[step_id] = step_dataframe

        self.pipelines[pipeline_id]['fitted_id'] = fitted_pipeline_id
        logger.info('Training finished!')

        if len(expose_outputs) == 0:
            return fitted_pipeline_id

        return fitted_pipeline_id, pipeline_step_outputs

    def test(self, pipeline_id, test_dataset, expose_outputs=None, calculate_confidence=False):
        """Test a model

        :param pipeline_id: The id of a fitted pipeline
        :param test_dataset: Path to dataset. It supports D3M dataset, and CSV file
        :param expose_outputs: The output of the pipeline steps. If None, it doesn't expose any output of the steps.
            If str, should be 'all' to shows the output of each step in the pipeline, If list, it should contain the
            ids of the steps, e.g. 'steps.2.produce'
        :param calculate_confidence: Whether or not to return the confidence instead of the predictions
        :returns: A dataframe that contains the predictions with/without the pipeline step outputs
        """
        suffix = 'TEST'
        test_dataset = abspath(test_dataset) if not is_openml_dataset(test_dataset) else test_dataset
        dataset_in_container = self.ta2.dataset_in_container
        train_dataset_d3m = pjoin(dataset_in_container, 'TRAIN/dataset_TRAIN/datasetDoc.json')
        problem_path = pjoin(dataset_in_container, 'TRAIN/problem_TRAIN/problemDoc.json')

        if not is_d3m_format(test_dataset, suffix):
            dataset_to_d3m(test_dataset, self.output_folder, self.problem_config, suffix)
        elif test_dataset != join(self.dataset, 'TEST'):  # Special case for D3M test dataset with different path
            destination_path = join(self.output_folder, 'temp', 'dataset_d3mformat', 'TEST')
            if test_dataset != destination_path:
                copy_folder(test_dataset, destination_path, True)
            dataset_in_container = pjoin(self.ta2.output_in_container,  'temp', 'dataset_d3mformat')

        logger.info('Testing model...')
        test_dataset_d3m = pjoin(dataset_in_container, 'TEST/dataset_TEST/datasetDoc.json')

        if calculate_confidence:
            # TODO: The only way to get the confidence is through the CLI utility, TA3TA2 API doesn't support it
            original_pipeline = self.pipelines[pipeline_id]['json_representation']
            confidence_pipeline = create_confidence_pipeline(original_pipeline)

            with open(join(self.output_folder, '%s.json' % pipeline_id), 'w') as fout:
                json.dump(confidence_pipeline, fout)  # Save temporally the json pipeline

            pipeline_path = pjoin(self.ta2.output_in_container, '%s.json' % pipeline_id)
            output_csv_path = pjoin(self.ta2.output_in_container, 'fit_produce_%s.csv' % pipeline_id)

            self.ta2.run_command([
                'python3', '-m', 'd3m',
                'runtime',
                '--context', 'TESTING',
                '--random-seed', '0',
                'fit-produce',
                '--pipeline', pipeline_path,
                '--problem', problem_path,
                '--input', train_dataset_d3m,
                '--test-input', test_dataset_d3m,
                '--output', output_csv_path,
            ])

            result_path = join(self.output_folder, 'fit_produce_%s.csv' % pipeline_id)
            predictions = pd.read_csv(result_path)
            logger.info('Testing finished!')

            return predictions

        fitted_pipeline_id = self.pipelines[pipeline_id]['fitted_id']

        if expose_outputs is None:
            expose_outputs = []
        elif isinstance(expose_outputs, str) and expose_outputs == 'all':
            expose_outputs = ['outputs.0']
            for index, step in enumerate(self.pipelines[pipeline_id]['json_representation']['steps']):
                for id_output in step['outputs']:
                    expose_outputs.append('steps.%d.%s' % (index, id_output['id']))

        # Force to generate the predictions
        if 'outputs.0' not in expose_outputs:
            expose_outputs.append('outputs.0')

        pipeline_step_outputs = self.ta3.test_solution(fitted_pipeline_id, test_dataset_d3m, expose_outputs)

        for step_id, step_csv_uri in pipeline_step_outputs.items():
            if not step_csv_uri.startswith('file://'):
                logger.warning('Exposed step output "%s" cannot be read' % step_id)
                continue
            step_csv_path = step_csv_uri.replace('file://' + self.ta2.output_in_container, self.output_folder)
            step_dataframe = pd.read_csv(step_csv_path)
            pipeline_step_outputs[step_id] = step_dataframe

        predictions = pipeline_step_outputs['outputs.0']
        logger.info('Testing finished!')

        if len(expose_outputs) == 1:
            return predictions

        return predictions, pipeline_step_outputs

    def score(self, pipeline_id, test_dataset):
        """Compute a proper score of the model

        :param pipeline_id: The id of a pipeline or a Pipeline object
        :param test_dataset: Path to dataset. It supports D3M dataset, and CSV file
        :returns: A tuple holding metric name and score value
        """
        suffix = 'SCORE'
        test_dataset = abspath(test_dataset) if not is_openml_dataset(test_dataset) else test_dataset

        if not is_d3m_format(test_dataset, suffix):
            # D3M format needs TEST and SCORE directories
            dataset_to_d3m(test_dataset, self.output_folder, self.problem_config, suffix)
            dataset_to_d3m(test_dataset, self.output_folder, self.problem_config, 'TEST')

        if isinstance(pipeline_id, Pipeline):
            pipeline_json = to_d3m_json(pipeline_id)
            pipeline_id = pipeline_json['id']
        elif isinstance(pipeline_id, str):
            if pipeline_id not in self.pipelines:
                raise ValueError('Pipeline id=%s does not exist' % pipeline_id)
            pipeline_json = self.pipelines[pipeline_id]['json_representation']
        else:
            raise TypeError("pipeline_id should be a Pipeline or str object")

        with open(join(self.output_folder, '%s.json' % pipeline_id), 'w') as fout:
            json.dump(pipeline_json, fout)  # Save temporally the json pipeline

        train_dataset_d3m = pjoin(self.ta2.dataset_in_container, 'TRAIN/dataset_TRAIN/datasetDoc.json')
        test_dataset_d3m = pjoin(self.ta2.dataset_in_container, 'TEST/dataset_TEST/datasetDoc.json')
        score_dataset_d3m = pjoin(self.ta2.dataset_in_container, 'SCORE/dataset_SCORE/datasetDoc.json')
        problem_path = pjoin(self.ta2.dataset_in_container, 'TRAIN/problem_TRAIN/problemDoc.json')
        pipeline_path = pjoin(self.ta2.output_in_container, '%s.json' % pipeline_id)
        output_csv_path = pjoin(self.ta2.output_in_container, 'fit_score_%s.csv' % pipeline_id)

        # TODO: Use TA2TA3 API to score
        self.ta2.run_command([
            'python3', '-m', 'd3m',
            'runtime',
            '--volumes', self.ta2.static_in_container,
            '--context', 'TESTING',
            '--random-seed', '0',
            'fit-score',
            '--pipeline', pipeline_path,
            '--problem', problem_path,
            '--input', train_dataset_d3m,
            '--test-input', test_dataset_d3m,
            '--score-input', score_dataset_d3m,
            '--scores', output_csv_path,
        ])

        result_path = join(self.output_folder, 'fit_score_%s.csv' % pipeline_id)
        df = pd.read_csv(result_path)
        score = round(df['value'][0], 5)
        metric = df['metric'][0].lower()

        return metric, score

    def save_pipeline(self, pipeline_id, output_folder):
        """Save a pipeline on disk

        :param pipeline_id: The id of the pipeline to be saved
        :param output_folder: Path to the folder where the pipeline will be saved
        """
        if pipeline_id not in self.pipelines:
            raise ValueError('Pipeline id=%s does not exist' % pipeline_id)

        solution_uri = self.ta3.save_solution(pipeline_id)
        folder_src_path = solution_uri.replace('file://' + self.ta2.output_in_container, self.output_folder)
        folder_dst_path = join(output_folder, pipeline_id)
        copy_folder(folder_src_path, folder_dst_path, True)
        pipeline_run = {
            'metric': self.pipelines[pipeline_id]['metric'],
            'score': self.pipelines[pipeline_id]['score'],
            'normalized_score': self.pipelines[pipeline_id]['normalized_score'],
            'start_time': self.pipelines[pipeline_id]['start_time'],
            'end_time': self.pipelines[pipeline_id]['end_time'],
            'search_id': self.pipelines[pipeline_id]['search_id'],
            'summary': self.pipelines[pipeline_id]['summary'],
            'json_representation': self.pipelines[pipeline_id]['json_representation'],
            'dataset_path': self.dataset
        }

        with open(join(folder_dst_path, 'run.json'), 'w') as fout:
            json.dump(pipeline_run, fout, indent=2)

        logger.info('Pipeline saved at "%s"' % folder_dst_path)

    def load_pipeline(self, pipeline_path):
        """Load a previous saved pipeline

        :param pipeline_path: Path to the folder where the pipeline is saved
        """
        pipeline_run_path = join(pipeline_path, 'run.json')
        if not exists(pipeline_run_path):
            raise ValueError('Can not load pipelines from "%s". File run.json does not exist' % pipeline_path)

        with open(pipeline_run_path) as fin:
            pipeline_run = json.load(fin)

        if self.ta2 is None:
            self.dataset = pipeline_run['dataset_path']
            self.start_automl()

        folder_dst_path = join(self.output_folder, 'temp', 'loaded_pipelines')
        copy_folder(pipeline_path, folder_dst_path, True)
        pipeline_path_container = pjoin(self.ta2.output_in_container, 'temp', 'loaded_pipelines')
        id_pipeline = self.ta3.load_solution(pipeline_path_container)
        pipeline_run['id'] = id_pipeline
        self.pipelines[id_pipeline] = pipeline_run
        logger.info('Pipeline id=%s loaded!' % id_pipeline)

    def get_best_pipeline_id(self):
        """Get the id of the best pipeline

        :returns: The id of the best pipeline
        """
        best_pipeline_id = max(self.pipelines.values(), key=lambda x: x['normalized_score'])['id']

        return best_pipeline_id

    def list_primitives(self):
        """Get a list of primitives used by the AutoML system
        
        :returns: List of primitives used by the AutoML system
        """
        primitives = self.ta3.list_primitives()

        return primitives

    def create_pipelineprofiler_inputs(self, test_dataset=None, source_name=None):
        """Create an proper input supported by PipelineProfiler based on the pipelines generated by an AutoML system

        :param test_dataset: Path to dataset. If None it will use the search scores, otherwise will score the
            pipelines over the passed dataset
        :param source_name: Name of the pipeline source. If None it will use the AutoML id
        :returns: List of pipelines in the PipelineProfiler input format
        """
        profiler_inputs = []
        pipeline_ids = set()

        if source_name is None:
            source_name = self.automl_id

        if test_dataset is not None:
            logger.info('Calculating scores in the test dataset...')

        for pipeline in self.pipelines.values():
            if pipeline['id'] not in pipeline_ids:
                pipeline_ids.add(pipeline['id'])
                if 'digest' not in pipeline['json_representation']:
                    pipeline['json_representation']['digest'] = compute_digest(pipeline['json_representation'])

                pipeline_score = [{'metric': {'metric': pipeline['metric']}, 'value': pipeline['score'],
                                   'normalized': pipeline['normalized_score']}]
                problem = self.dataset
                start_time = pipeline['start_time']
                end_time = pipeline['end_time']

                if test_dataset is not None:
                    problem = test_dataset
                    start_time = datetime.datetime.utcnow().isoformat() + 'Z'
                    try:
                        metric, score,  = self.score(pipeline['id'], test_dataset)
                    except Exception:
                        logger.warning('Pipeline id=%s could not be scored' % pipeline['id'], exc_info=True)
                        continue
                    end_time = datetime.datetime.utcnow().isoformat() + 'Z'
                    normalized_score = PerformanceMetric[metric.upper()].normalize(score)
                    pipeline_score = [{'metric': {'metric': metric}, 'value': score,
                                       'normalized': normalized_score}]

                profiler_data = {
                    'pipeline_id': pipeline['json_representation']['id'],
                    'inputs': pipeline['json_representation']['inputs'],
                    'steps': pipeline['json_representation']['steps'],
                    'outputs': pipeline['json_representation']['outputs'],
                    'pipeline_digest': pipeline['json_representation']['digest'],
                    'problem': problem,
                    'start': start_time,
                    'end': end_time,
                    'scores': pipeline_score,
                    'pipeline_source': {'name': source_name},
                }
                profiler_inputs.append(profiler_data)

            else:
                logger.warning('Ignoring repeated pipeline id=%s' % pipeline['id'])
        logger.info('Inputs for PipelineProfiler created!')

        return profiler_inputs

    def create_textanalizer_inputs(self, dataset, text_column, label_column, positive_label=1, negative_label=0):
        """Create an proper input supported by VisualTextAnalyzer

        :param dataset: Path to dataset.  It supports D3M dataset, and CSV file
        :param text_column: Name of the column that contains the texts
        :param label_column: Name of the column that contains the classes
        :param positive_label: Label for the positive class
        :param negative_label: Label for the negative class
        """
        suffix = split(dataset)[-1]

        if is_d3m_format(dataset, suffix):
            dataframe = d3mtext_to_dataframe(dataset, suffix, text_column)
        else:
            dataframe = pd.read_csv(dataset, index_col=False)

        return vis.get_words_entities(dataframe, text_column, label_column, positive_label, negative_label)

    def export_pipeline_code(self, pipeline_id, ipython_cell=True):
        """Converts a Pipeline Description to an executable Python script

        :param pipeline_id: Pipeline id
        :param ipython_cell: Whether or not to show the Python code in a Jupyter Notebook cell
        """
        pipeline_template = self.pipelines[pipeline_id]['json_representation']
        code = "from d3m_interface.pipeline import Pipeline\n\n"
        code += "pipeline = Pipeline()\n\n"
        code += "input_data = pipeline.make_pipeline_input()\n"

        prev_step = None
        prev_steps = {}
        count_template_steps = 0
        for pipeline_step in pipeline_template['steps']:
            if pipeline_step['type'] == 'PRIMITIVE':
                code += f"""\nstep_{count_template_steps} = pipeline.make_pipeline_step('{pipeline_step['primitive'][
                    'python_path']}')\n"""
                if 'outputs' in pipeline_step:
                    for output in pipeline_step['outputs']:
                        prev_steps['steps.%d.%s' % (count_template_steps, output['id'])] = "step_%d" % (
                            count_template_steps)

                if 'hyperparams' in pipeline_step:
                    code += f"""pipeline.set_hyperparams(step_{count_template_steps}"""
                    for hyper, desc in pipeline_step['hyperparams'].items():
                        if desc['type'] == 'VALUE':
                            code += f""", {hyper}={"'" + desc['data'] + "'" if type(desc['data']) == str else desc[
                                'data']}"""
                        else:
                            code += f""", {hyper}= {"{"}'type':'{desc['type']}' ,'data':{"'" + desc[
                                'data'] + "'" if type(desc['data']) == str else desc['data']}{"}"}"""
                    code += f""")\n"""

            else:
                # TODO: In the future we should be able to handle subpipelines
                break
            if prev_step:
                if 'arguments' in pipeline_step:
                    for argument, desc in pipeline_step['arguments'].items():
                        from_output = desc['data'].split('.')[-1]
                        to_input = argument
                        code += f"""pipeline.connect({prev_steps[desc['data']]}, step_{count_template_steps}"""

                        if from_output != 'produce':
                            code += f""", from_output='{from_output}'"""

                        if to_input != 'inputs':
                            code += f""", to_input='{argument}'"""
                        code += f""")\n"""
            else:
                code += f"""pipeline.connect(input_data, step_{count_template_steps}, from_output='dataset')\n"""
            prev_step = "step_%d" % count_template_steps
            count_template_steps += 1

        if ipython_cell:
            shell = get_ipython()

            payload = dict(
                source='set_next_input',
                text=code,
                replace=False,
            )
            shell.payload_manager.write_payload(payload, single=False)
        else:
            return code

    def end_session(self):
        """This safely ends session in D3M interface
        """
        logger.info('Ending session...')
        if self.ta2 is not None:
            self.ta2.close()
            self.ta2 = None

        logger.info('Session ended!')

    def start_automl(self):
        if self.ta2 is not None:
            self.end_session()

        logger.info('Initializing %s AutoML...', self.automl_id)

        self.ta2 = self.container_runtime(
            self.automl_id,
            self.dataset,
            self.output_folder,
            self.resource_folder,
            self.port,
            self.verbose
        )

        time.sleep(4)  # Wait for AutoML

        host = 'localhost'
        if os.environ.get('DOCKER_HOST'):
            m = re.match('tcp://([^:/]*):[0-9]+', os.environ['DOCKER_HOST'])
            if m is not None:
                host = m.group(1)
            else:
                logger.warning("Can't understand DOCKER_HOST")

        logger.info("Connecting via gRPC to %s:%d...", host, self.port)
        while True:
            try:
                self.ta3 = GrpcClient(host, self.port)
                self.ta3.do_hello()
                logger.info('%s AutoML initialized!', self.automl_id)
                break
            except Exception:
                if self.ta3.channel is not None:
                    self.ta3.channel.close()
                    self.ta3 = None

                time.sleep(4)

    def score_in_search(self, pipeline, train_dataset, problem_path, pipelines, method, stratified, shuffle, folds,
                        train_ratio, random_seed):
        try:
            pipeline['start_time'] = datetime.datetime.utcnow().isoformat() + 'Z'
            score_data = self.ta3.score_solutions(pipeline['id'], train_dataset, problem_path, method, stratified, shuffle,
                                                  folds, train_ratio, random_seed)
            logger.info('Scored pipeline id=%s, %s=%s' % (pipeline['id'], score_data['metric'], score_data['score']))
            pipeline['end_time'] = datetime.datetime.utcnow().isoformat() + 'Z'
            pipeline['score'] = score_data['score']
            pipeline['normalized_score'] = score_data['normalized_score']
            pipeline['metric'] = score_data['metric']
            pipelines[pipeline['id']] = pipeline
        except Exception as e:
            logger.warning('Pipeline id=%s could not be scored.' % pipeline['id'], exc_info=e)

    def get_summary_pipeline(self, pipeline_json):
        primitives_summary = []
        for primitive in pipeline_json['steps']:
            primitive_name = primitive['primitive']['python_path']
            if primitive_name not in IGNORE_SUMMARY_PRIMITIVES:
                primitive_name_short = '.'.join(primitive_name.split('.')[-2:]).lower()
                if primitive_name_short not in primitives_summary:
                    primitives_summary.append(primitive_name_short)

        return ', '.join(primitives_summary)

    def plot_leaderboard(self):
        """Plot pipelines' leaderboard
        """
        leaderboard_data = []
        metric = 'metric'

        if len(self.pipelines) > 0:
            sorted_pipelines = sorted(self.pipelines.values(), key=lambda x: x['normalized_score'], reverse=True)
            metric = sorted_pipelines[0]['metric']
            for position, pipeline in enumerate(sorted_pipelines, 1):
                leaderboard_data.append([position, pipeline['id'], pipeline['summary'],  pipeline['score']])

        leaderboard = pd.DataFrame(leaderboard_data, columns=['ranking', 'id', 'summary', metric])

        return leaderboard.style.hide_index()

    def plot_summary_dataset(self, dataset, text_column=None):
        """Plot histograms of the dataset

        :param dataset: Path to dataset.  It supports D3M dataset, and CSV file
        :param text_column: Name of the column that contains the texts. Only needed for D3M dataset that has collections
        """
        suffix = split(dataset)[-1]

        if is_d3m_format(dataset, suffix):
            if is_d3m_collection(dataset, suffix, 'text'):
                dataset = d3mtext_to_dataframe(dataset, suffix, text_column)
            else:
                dataset = join(dataset, 'dataset_%s' % suffix, 'tables', 'learningData.csv')

        vis.plot_metadata(dataset)

    def plot_comparison_pipelines(self, test_dataset=None, source_name=None, precomputed_pipelines=None):
        """Plot PipelineProfiler visualization

        :param test_dataset: Path to dataset. If None it will use the search scores, otherwise will score the
            pipelines over the passed dataset
        :param source_name: Name of the pipeline source. If None it will use the AutoML id
        :param precomputed_pipelines: If not None, it loads pipelines previously computed
        """
        if precomputed_pipelines is None:
            pipelineprofiler_inputs = self.create_pipelineprofiler_inputs(test_dataset, source_name)
            vis.plot_comparison_pipelines(pipelineprofiler_inputs)
        else:
            vis.plot_comparison_pipelines(precomputed_pipelines)

    def plot_text_analysis(self, dataset=None, text_column=None, label_column=None, positive_label=1, negative_label=0, precomputed_data=None):
        """Plot a visualization for text datasets

        :param dataset: Path to dataset.  It supports D3M dataset, and CSV file
        :param text_column: Name of the column that contains the texts
        :param label_column: Name of the column that contains the classes
        :param positive_label: Label for the positive class
        :param negative_label: Label for the negative class
        :param precomputed_data: If not None, it loads words/named entities previously computed
        """
        if precomputed_data is not None:
            vis.plot_text_summary(precomputed_data)
        else:
            precomputed_data = self.create_textanalizer_inputs(dataset, text_column, label_column, positive_label, negative_label)
            vis.plot_text_summary(precomputed_data)

    def plot_text_explanation(self, model_id, instance_text, text_column, label_column, num_features=5, top_labels=1):
        """Plot a LIME visualization for model explanation

        :param model_id: Model id
        :param instance_text: Text to be explained
        :param text_column: Name of the column that contains the texts
        :param label_column: Name of the column that contains the classes
        :param num_features: Maximum number of features present in the explanation
        :param top_labels: Number of labels with highest prediction probabilities to use in the explanations
        """
        train_path = join(self.dataset, 'TRAIN')
        artificial_test_path = join(self.output_folder, 'temp', 'dataset_d3mformat', 'TEST')
        vis.plot_text_explanation(self, train_path, artificial_test_path, model_id, instance_text, text_column,
                                  label_column, num_features, top_labels)

    @staticmethod
    def add_new_automl(automl_id, docker_image_url):
        """Add a new AutoML system that is not already defined in the D3M Interface. It can also be a different version
        of a pre-existing AutoML (however it must be added with a different name)

        :param automl_id: A id to identify the new AutoML
        :param docker_image_url: The docker image url of the new AutoML
        """
        AUTOML_DOCKER_IMAGES[automl_id] = docker_image_url
        logger.info('%s AutoML added!', automl_id)
