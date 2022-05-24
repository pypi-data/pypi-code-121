import asyncio
import time

import grpc
from github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 import Study as MDStudy
from github.com.metaprov.modelaapi.services.study.v1.study_pb2_grpc import StudyServiceStub
from github.com.metaprov.modelaapi.services.study.v1.study_pb2 import CreateStudyRequest, \
    UpdateStudyRequest, DeleteStudyRequest, GetStudyRequest, ListStudyRequest, \
    GetStudyProfileRequest, CreateStudyProfileRequest, AbortStudyRequest, PauseStudyRequest, ResumeStudyRequest
from tqdm import tqdm

import modela
from modela.common import *
from modela.training.models import ModelSearch, FeatureEngineeringSearch, BaselineSettings, Ensemble, Training, \
    Interpretability, StudySchedule, NotificationSettings, StudySpec, StudyStatus, DataLocation
from modela.Resource import Resource
from modela.ModelaException import ModelaException, ResourceNotFoundException
from typing import List, Union

from modela.data.Dataset import Dataset
from modela.infra.Lab import Lab
from modela.infra.VirtualBucket import VirtualBucket
from modela.training.Model import Model
from modela.training.common import *


class Study(Resource):
    def __init__(self, item: MDStudy = MDStudy(), client=None, namespace="", name="", version=Resource.DefaultVersion,
                 dataset: Union[str, Dataset] = "",
                 test_dataset: Union[str, Dataset] = "",
                 lab: Union[ObjectReference, Lab, str] = "default-lab",
                 bucket: Union[VirtualBucket, str] = None,
                 objective: Metric = None,
                 search: ModelSearch = None,
                 fe_search: FeatureEngineeringSearch = None,
                 baseline: BaselineSettings = None,
                 ensemble: Ensemble = None,
                 trainer_template: Training = None,
                 interpretability: Interpretability = None,
                 schedule: StudySchedule = None,
                 notification: NotificationSettings = None,
                 garbage_collect: bool = True,
                 keep_best_models: bool = True,
                 fast: bool = False,
                 timeout: int = 600,
                 template: bool = False):
        """

        :param client: The Study client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param dataset: If specified as a string, the SDK will attempt to find a Dataset resource with the given name.
            If specified as a Dataset object, or if one was found with the given name, it will be used in the Study.
        :param test_dataset: If specified, the Dataset will be used as the test dataset and the Dataset specified by
            the `dataset` field will be used solely as the training dataset
        :param lab: The object reference, Lab object, or lab name under the tenant of the resource for which all Study-related
            workloads will be performed under.
        :param bucket: The Bucket object or name of the bucket which will store the Study artifacts
        :param objective: The objective metric relevant to the task type.
        :param search: The search parameters define how many models to sample
        :param fe_search: The feature engineering search parameters of the Study
        :param baseline: The baseline settings for the Study, which if enabled will train an unoptimized model of each
            algorithm type for benchmarking.
        :param ensemble: The ensemble settings for the Study, which if enabled will combine the top estimators of
            the study after the initial model search.
        :param trainer_template: The training template for each model created by the Study.
        :param interpretability: The interpretability configuration for the Study, which specifies what type of
            model explainability plots will be generated from Shap values if they are computed
        :param schedule: The schedule for the study to run chronically
        :param notification: The notification settings, which if enabled will forward events about this resource to a notifier.
        :param garbage_collect: If enabled, models which did not move past the testing stage will be garbage collected by
            the system.
        :param keep_best_models: If enabled, the best models from each algorithm will not be garbage collected.
        :param fast: If enabled, the Study will skip profiling, explaining, and reporting.
        :param timeout: The timeout in seconds after which the Study will fail.
        :param template: If the Study is a template it will not start a search and can only be used as a template for
            other studies.
        """
        self.default_resource = False
        super().__init__(item, client, namespace=namespace, name=name, version=version)
        if not self.default_resource:  # Ignore the rest of the constructor; studies are immutable
            return

        spec = self.spec
        if type(dataset) == Dataset:
            dataset_name = dataset.name
        else:
            dataset_name = dataset
            dataset = client.modela.Dataset(namespace=namespace, name=dataset)
            if dataset.default_resource:
                raise ResourceNotFoundException("Dataset {0} does not exist".format(dataset_name))

        spec.DatasetName = dataset_name
        spec.Task = dataset.spec.Task

        if test_dataset:
            if type(test_dataset) == Dataset:
                test_dataset_name = dataset.name
            else:
                test_dataset_name = dataset
                test_dataset = client.modela.Dataset(namespace=namespace, name=dataset)
                if test_dataset.default_resource:
                    raise ResourceNotFoundException("Dataset {0} does not exist".format(dataset_name))

            spec.TrainingTemplate.Split.TrainDataset = dataset_name
            spec.TrainingTemplate.Split.TestDataset = test_dataset_name
            spec.TrainingTemplate.Split.Method = DataSplitMethod.TestDataset

        if type(lab) == Lab:
            lab = lab.reference
        elif type(lab) == str:
            lab = ObjectReference(Namespace=client.modela.tenant, Name=lab)

        if bucket is not None:
            if type(bucket) == VirtualBucket:
                bucket = bucket.name
            spec.Location = DataLocation(BucketName=bucket)

        if objective is not None:
            spec.Search.Objective = objective

        if search is not None:
            spec.Search = search

        if fe_search is not None:
            spec.FeSearch = fe_search

        if baseline is not None:
            spec.Baseline = baseline

        if ensemble is not None:
            spec.Ensembles = ensemble

        if trainer_template is not None:
            spec.TrainingTemplate = trainer_template

        spec.TrainingTemplate.LabRef = lab

        if interpretability is not None:
            spec.Interpretability = interpretability

        if schedule is not None:
            spec.Schedule = schedule

        if notification is not None:
            spec.Notification = notification

        if garbage_collect:
            spec.Gc.CollectAtStudyEnd = True

        if keep_best_models:
            spec.Gc.KeepOnlyBestModelPerAlgorithm = True

        spec.Fast = fast
        # spec.ActiveDeadlineSeconds = timeout
        spec.Template = template

    @property
    def spec(self) -> StudySpec:
        return StudySpec().copy_from(self._object.spec)

    @property
    def status(self) -> StudyStatus:
        self.sync()
        return StudyStatus().copy_from(self._object.status)

    def default(self):
        self.default_resource = True
        StudySpec().apply_config(self._object.spec)

    def abort(self):
        self.ensure_client_repository()
        self._client.abort(self.namespace, self.name)

    def pause(self):
        self.ensure_client_repository()
        self._client.pause(self.namespace, self.name)

    def resume(self):
        self.ensure_client_repository()
        self._client.resume(self.namespace, self.name)

    def submit_and_visualize(self, replace: bool = False, show_progress_bar=True):
        """
        Submit the resource and call visualize().

        :param replace: Replace the resource if it already exists on the cluster.
        :param show_progress_bar: If enabled, the visualization will render a progress bar indicating the study progress.
        """
        self.submit(replace)
        self.visualize(show_progress_bar)

    def visualize(self, show_progress_bar=True):
        """
        Display a real-time visualization of the Study's progress

        :param show_progress_bar: If enabled, the visualization will render a progress bar indicating the study progress.
        """
        desc = tqdm(total=0, position=0, bar_format='{desc}Time Elapsed: {elapsed}')
        bars = {}

        current_status, objective, cv_top, alg_top = None, self.spec.Search.Objective, 0, ""
        try:
            while True:
                status = self.status
                if current_status != status:
                    current_status = status
                    desc.set_description('Phase: %s | Active Models: %d | Best Algorithm: %s | Best Score: %s' %
                                         (StudyPhaseToProgress[self.phase], current_status.Models,
                                          alg_top if alg_top != "" else "[Waiting]",
                                          str(cv_top) if cv_top != 0 else "[Waiting]"))

                    desc.refresh()

                if current_status.Phase == StudyPhase.Failed:
                    desc.set_description("Phase: Failed | Error Message: {0}".format(current_status.FailureMessage))
                    desc.colour = "red"
                    desc.refresh()
                    time.sleep(5)
                    self.sync()
                    if self.phase != StudyPhase.Failed:
                        continue
                    else:
                        break
                elif current_status.Phase == StudyPhase.Completed:
                    model = self._client.modela.Model(self.namespace, current_status.BestModel)
                    if model.phase not in (ModelPhase.Completed, ModelPhase.Live):
                        continue

                    desc.close()
                    for bar in bars.values():
                        bar.close()

                    if not show_progress_bar:
                        desc.set_description_str("Study completed!")
                        desc.refresh()

                    print("\n\n" + model.details)
                    if self.spec.Search.Trainers <= 2:
                        print("Want quicker training speeds? Get more parallel trainers at https://modela.ai")

                    time.sleep(0.1)
                    return

                time.sleep(0.1)
                if not show_progress_bar:
                    time.sleep(0.9)
                    for model in self.models:
                        if len(model.status.Cv) > 0:
                            if model.get_cv_metric(objective) > cv_top:
                                cv_top, alg_top = model.get_cv_metric(objective), model.spec.Estimator.AlgorithmName

                    continue

                models = self.models
                for model in dict(bars).keys():
                    bar = bars[model]
                    mod = [x for x in models if x.name == model]
                    if len(mod) == 0:  # Model has been garbage collected, clean up the bar
                        if bar.pos == -(len(bars) + 1):  # If the bar is in the last position, then clean it up normally
                            bar.close()
                        else:  # Otherwise, we need to shift all the bars down by one
                            _bars = [[mod, _bar] for mod, _bar in bars.items() if _bar.pos <= bar.pos]
                            if len(_bars) <= 1:  # Not supposed to happen; close the bar and move on
                                bar.close()
                            else:
                                _bars.sort(key=lambda bp: bp[1].pos, reverse=True)
                                for idx in range(len(_bars) - 1):  # Copy bar data down the list and fix indexes
                                    bar_forward, bar_current = _bars[idx + 1][1], _bars[idx][1]
                                    bar_current.desc = bar_forward.desc
                                    bar_current.n = bar_forward.n
                                    bar_current.postfix = bar_forward.postfix
                                    bar_current.refresh()
                                    if idx > 0:
                                        bars[_bars[idx][0]] = _bars[idx - 1][1]

                                bars[_bars[-1][0]] = _bars[-2][1]
                                _bars[-1][1].close()

                        del bars[model]

                for model in models:  # For each model, create a bar/update the bar of it already exists
                    if not (model.name in bars):
                        bars[model.name] = tqdm(total=100, position=len(bars) + 1,
                                                bar_format='{desc} {percentage:3.0f}%|{bar}| {postfix}',
                                                desc=model.name + " [Pending]", ncols=121, initial=0, leave=False)
                    else:
                        status = model.status  # Avoid multiple expensive calls to load configs
                        if bars[model.name].n != status.Progress:
                            bars[model.name].n = status.Progress
                            bars[model.name].refresh()

                        dsc = "{0: <50} [{1}]:".format(model.name + "/" + model.spec.Estimator.AlgorithmName,
                                                       status.Phase.name).ljust(62)
                        postfix = "CV = [Waiting]"
                        if len(status.Cv) > 0:
                            postfix = "CV = {0}".format(model.get_cv_metric(objective))
                            if model.get_cv_metric(objective) > cv_top:
                                cv_top, alg_top = model.get_cv_metric(objective), model.spec.Estimator.AlgorithmName

                        if len(status.Test) > 0:
                            postfix = "CV = {0}, Test = {1}".format(model.get_cv_metric(objective),
                                                                    model.get_test_metric(objective))

                        class unappendable_str:  # Workaround for tqdm appending a comma before the postfix >:(
                            def __init__(self, s):
                                self.s = s

                            def __str__(self):
                                return self.s

                        if bars[model.name].desc != dsc:
                            bars[model.name].set_description_str(dsc)

                        if str(bars[model.name].postfix) != postfix:
                            bars[model.name].postfix = unappendable_str(postfix)
                            bars[model.name].refresh()

        except KeyboardInterrupt:
            pass

    async def wait_until_phase(self, phase: StudyPhase):
        """ Returns a coroutine which blocks until the specified phase is reached, or the Study fails """
        while self.status.Phase not in (phase, StudyPhase.Failed):
            await asyncio.sleep(1/5)


    @property
    def models(self) -> List[Model]:
        """ Get the list of currently active models produced by the Study """
        self.ensure_client_repository()
        return self._client.modela.Models.list(self.namespace, {'study': self.name})

    @property
    def best_model(self) -> Model:
        """ Get the best model selected by the model search process """
        self.ensure_client_repository()
        return self._client.modela.Models.get(self.namespace, self._object.status.bestModel)

    @property
    def phase(self) -> StudyPhase:
        return self.status.Phase


class StudyClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: StudyServiceStub = stub

    def create(self, study: Study) -> bool:
        request = CreateStudyRequest()
        request.study.CopyFrom(study.raw_message)
        try:
            response = self.__stub.CreateStudy(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, study: Study) -> bool:
        request = UpdateStudyRequest()
        request.study.CopyFrom(study.raw_message)
        try:
            self.__stub.UpdateStudy(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Study, bool]:
        request = GetStudyRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetStudy(request)
            return Study(response.study, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteStudyRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteStudy(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str, labels: dict = None) -> Union[List[Study], bool]:
        request = ListStudyRequest()
        request.namespace = namespace
        if labels is not None:
            request.labels.update(labels)

        try:
            response = self.__stub.ListStudies(request)
            return [Study(item, self) for item in response.studies.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def abort(self, namespace: str, name: str) -> bool:
        request = AbortStudyRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.AbortStudy(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def pause(self, namespace: str, name: str) -> bool:
        request = PauseStudyRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.PauseStudy(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def resume(self, namespace: str, name: str) -> bool:
        request = ResumeStudyRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.ResumeStudy(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get_profile(self, namespace: str, name: str, models: int) -> bool:
        request = GetStudyProfileRequest()
        request.namespace = namespace
        request.name = name
        request.models = models
        try:
            response = self.__stub.GetStudyProfile(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def create_profile(self, namespace: str, name: str) -> bool:
        request = CreateStudyProfileRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.CreateStudyProfile(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False
