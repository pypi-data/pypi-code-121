import grpc
import logging
import d3m_automl_rpc.core_pb2 as pb_core
import d3m_automl_rpc.core_pb2_grpc as pb_core_grpc
import d3m_automl_rpc.value_pb2 as pb_value
from d3m.utils import path_to_uri
from d3m.metadata import pipeline as pipeline_module
from d3m.metadata.problem import Problem, PerformanceMetric
from d3m_automl_rpc.utils import encode_problem_description, encode_performance_metric, encode_value, \
    decode_pipeline_description, decode_performance_metric, decode_value


logger = logging.getLogger(__name__)


class GrpcClient:
    def __init__(self, host='localhost', port=45042):
        self.channel = grpc.insecure_channel('%s:%d' % (host, port))
        self.core = pb_core_grpc.CoreStub(self.channel)

    def do_hello(self):
        self.core.Hello(pb_core.HelloRequest())

    def search_solutions(self, dataset_path, problem_path, time_bound, time_bound_run, automl_hyperparameters=None,
                         pipeline_template=None):
        problem = Problem.load(problem_uri=path_to_uri(problem_path))
        version = pb_core.DESCRIPTOR.GetOptions().Extensions[pb_core.protocol_version]
        automl_hyperparams_encoded = {k: encode_value({'type': 'object', 'value': v}, ['RAW'], '/tmp') for k, v in
                                      automl_hyperparameters.items()}

        search = self.core.SearchSolutions(pb_core.SearchSolutionsRequest(
            user_agent='ta3_stub',
            version=version,
            time_bound_search=time_bound,
            time_bound_run=time_bound_run,
            priority=10,
            rank_solutions_limit=0,
            allowed_value_types=['RAW', 'DATASET_URI', 'CSV_URI'],
            template=pipeline_template,
            problem=encode_problem_description(problem),
            automl_hyperparameters=automl_hyperparams_encoded,
            inputs=[pb_value.Value(
                dataset_uri='file://%s' % dataset_path,
            )],
        ))

        return str(search.search_id)

    def get_solutions(self, search_id):
        results = self.core.GetSearchSolutionsResults(
            pb_core.GetSearchSolutionsResultsRequest(
                search_id=search_id,
            )
        )

        for result in results:
            if result.solution_id:
                pipeline_id = result.solution_id
                yield {'id': pipeline_id}

    def score_solutions(self, solution_id, dataset_path, problem_path, method, stratified, shuffle, folds, train_ratio, random_seed):
        problem = Problem.load(problem_uri=path_to_uri(problem_path))
        methods_mapping = {'cross_validation': 'K_FOLD', 'holdout': 'HOLDOUT'}
        metrics = []
        score_data = None

        for metric in problem['problem']['performance_metrics']:
            metrics.append(encode_performance_metric(metric))
        # Showing only the first metric
        target_metric = problem['problem']['performance_metrics'][0]['metric']

        response = self.core.ScoreSolution(pb_core.ScoreSolutionRequest(
            solution_id=solution_id,
            inputs=[pb_value.Value(
                dataset_uri='file://%s' % dataset_path,
            )],
            performance_metrics=metrics,
            users=[],
            configuration=pb_core.ScoringConfiguration(
                method=methods_mapping[method],
                stratified=stratified,
                shuffle=shuffle,
                folds=folds,
                train_test_ratio=train_ratio,
                random_seed=random_seed
            ),
        ))

        results = self.core.GetScoreSolutionResults(
            pb_core.GetScoreSolutionResultsRequest(
                request_id=response.request_id,
            )
        )

        for result in results:
            if result.progress.state == pb_core.COMPLETED:
                scores = []
                for metric_score in result.scores:
                    metric = decode_performance_metric(metric_score.metric)['metric']
                    if metric == target_metric:
                        score = decode_value(metric_score.value)['value']
                        scores.append(score)

                if len(scores) > 0:
                    avg_score = round(sum(scores) / len(scores), 5)
                    normalized_score = PerformanceMetric[target_metric.name].normalize(avg_score)

                    score_data = {'score': avg_score, 'normalized_score': normalized_score,
                                  'metric': target_metric.name.lower()}
            elif result.progress.state == pb_core.ERRORED:
                raise RuntimeError(result.progress.status)

        return score_data

    def train_solution(self, solution_id, dataset_path, expose_outputs):
        fitted_solution_id = None
        pipeline_step_outputs = {}

        response = self.core.FitSolution(pb_core.FitSolutionRequest(
            solution_id=solution_id,
            inputs=[pb_value.Value(
                dataset_uri='file://%s' % dataset_path,
            )],
            expose_outputs=expose_outputs,
            expose_value_types=['CSV_URI'],
            users=[],
        ))
        results = self.core.GetFitSolutionResults(
            pb_core.GetFitSolutionResultsRequest(
                request_id=response.request_id,
            )
        )
        for result in results:
            if result.progress.state == pb_core.COMPLETED:
                fitted_solution_id = result.fitted_solution_id
                for exposed_output in result.exposed_outputs:
                    pipeline_step_outputs[exposed_output] = result.exposed_outputs[exposed_output].csv_uri
            elif result.progress.state == pb_core.ERRORED:
                raise RuntimeError(result.progress.status)

        return fitted_solution_id, pipeline_step_outputs

    def test_solution(self, fitted_solution_id, dataset_path, expose_outputs):
        pipeline_step_outputs = {}

        response = self.core.ProduceSolution(pb_core.ProduceSolutionRequest(
            fitted_solution_id=fitted_solution_id,
            inputs=[pb_value.Value(
                dataset_uri='file://%s' % dataset_path,
            )],
            expose_outputs=expose_outputs,
            expose_value_types=['CSV_URI'],
            users=[],
        ))
        results = self.core.GetProduceSolutionResults(
            pb_core.GetProduceSolutionResultsRequest(
                request_id=response.request_id,
            )
        )
        for result in results:
            if result.progress.state == pb_core.COMPLETED:
                for exposed_output in result.exposed_outputs:
                    pipeline_step_outputs[exposed_output] = result.exposed_outputs[exposed_output].csv_uri
            elif result.progress.state == pb_core.ERRORED:
                raise RuntimeError(result.progress.status)

        return pipeline_step_outputs

    def save_solution(self, solution_id):
        response = self.core.SaveSolution(pb_core.SaveSolutionRequest(solution_id=solution_id))

        return response.solution_uri

    def load_solution(self, solution_path):
        solution_uri = path_to_uri(solution_path)
        response = self.core.LoadSolution(pb_core.LoadSolutionRequest(solution_uri=solution_uri))

        return response.solution_id

    def save_fitted_solution(self, fitted_solution_id):
        response = self.core.SaveFittedSolution(pb_core.SaveFittedSolutionRequest(fitted_solution_id=fitted_solution_id))

        return response.fitted_solution_uri

    def load_fitted_solution(self, fitted_solution_path):
        fitted_solution_uri = path_to_uri(fitted_solution_path)
        response = self.core.LoadFittedSolution(pb_core.LoadFittedSolutionRequest(fitted_solution_uri=fitted_solution_uri))

        return response.fitted_solution_id

    def describe_solution(self, solution_id):
        pipeline_description = self.core.DescribeSolution(pb_core.DescribeSolutionRequest(solution_id=solution_id)).pipeline
        pipeline = decode_pipeline_description(pipeline_description, pipeline_module.NoResolver())

        if pipeline is None:
            raise TypeError('Pipeline got a None value during decoding')

        return pipeline.to_json_structure()

    def export_solution(self, fitted_solution_id, rank=1):
        self.core.SolutionExport(pb_core.SolutionExportRequest(solution_id=fitted_solution_id, rank=rank))

    def list_primitives(self):
        primitives = []
        response = self.core.ListPrimitives(pb_core.ListPrimitivesRequest())

        for primitive in response.primitives:
            primitives.append(primitive.python_path)

        return primitives

    def stop_search(self, search_id):
        self.core.StopSearchSolutions(pb_core.StopSearchSolutionsRequest(search_id=search_id))

    def end_search(self, search_id):
        self.core.EndSearchSolutions(pb_core.EndSearchSolutionsRequest(search_id=search_id))
