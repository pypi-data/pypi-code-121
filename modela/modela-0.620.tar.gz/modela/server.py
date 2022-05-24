import subprocess
import socket
from contextlib import closing

from typing import Callable

from github.com.metaprov.modelaapi.services.account.v1.account_pb2 import AccountLoginRequest
from github.com.metaprov.modelaapi.services.datapipelinerun.v1 import datapipelinerun_pb2_grpc
from github.com.metaprov.modelaapi.services.datapipeline.v1 import datapipeline_pb2_grpc
from github.com.metaprov.modelaapi.services.dataproduct.v1 import dataproduct_pb2_grpc
from github.com.metaprov.modelaapi.services.dataproductversion.v1 import dataproductversion_pb2_grpc
from github.com.metaprov.modelaapi.services.dataset.v1 import dataset_pb2_grpc
from github.com.metaprov.modelaapi.services.datasource.v1 import datasource_pb2_grpc
from github.com.metaprov.modelaapi.services.entity.v1 import entity_pb2_grpc
from github.com.metaprov.modelaapi.services.featurehistogram.v1 import featurehistogram_pb2_grpc
from github.com.metaprov.modelaapi.services.featurepipelinerun.v1 import featurepipelinerun_pb2_grpc
from github.com.metaprov.modelaapi.services.featurepipeline.v1 import featurepipeline_pb2_grpc
from github.com.metaprov.modelaapi.services.feature.v1 import feature_pb2_grpc
from github.com.metaprov.modelaapi.services.featureset.v1 import featureset_pb2_grpc
from github.com.metaprov.modelaapi.services.labelingpipelinerun.v1 import labelingpipelinerun_pb2_grpc
from github.com.metaprov.modelaapi.services.labelingpipeline.v1 import labelingpipeline_pb2_grpc
from github.com.metaprov.modelaapi.services.reciperun.v1 import reciperun_pb2_grpc
from github.com.metaprov.modelaapi.services.recipe.v1 import recipe_pb2_grpc
from github.com.metaprov.modelaapi.services.sqlquery.v1 import sqlquery_pb2_grpc
from github.com.metaprov.modelaapi.services.sqlqueryrun.v1 import sqlqueryrun_pb2_grpc
from github.com.metaprov.modelaapi.services.webrequestrun.v1 import webrequestrun_pb2_grpc
from github.com.metaprov.modelaapi.services.webrequest.v1 import webrequest_pb2_grpc
from github.com.metaprov.modelaapi.services.cronprediction.v1 import cronprediction_pb2_grpc
from github.com.metaprov.modelaapi.services.fileservices.v1 import fileservices_pb2_grpc
from github.com.metaprov.modelaapi.services.curtain.v1 import curtain_pb2_grpc
from github.com.metaprov.modelaapi.services.dataapp.v1 import dataapp_pb2_grpc
from github.com.metaprov.modelaapi.services.prediction.v1 import prediction_pb2_grpc
from github.com.metaprov.modelaapi.services.predictor.v1 import predictor_pb2_grpc
from github.com.metaprov.modelaapi.services.account.v1 import account_pb2_grpc
from github.com.metaprov.modelaapi.services.alert.v1 import alert_pb2_grpc
from github.com.metaprov.modelaapi.services.apitoken.v1 import apitoken_pb2_grpc
from github.com.metaprov.modelaapi.services.attachment.v1 import attachment_pb2_grpc
from github.com.metaprov.modelaapi.services.commit.v1 import commit_pb2_grpc
from github.com.metaprov.modelaapi.services.connection.v1 import connection_pb2_grpc
from github.com.metaprov.modelaapi.services.lab.v1 import lab_pb2_grpc
from github.com.metaprov.modelaapi.services.license.v1 import license_pb2_grpc
from github.com.metaprov.modelaapi.services.modelasystem.v1 import modelasystem_pb2_grpc
from github.com.metaprov.modelaapi.services.notifier.v1 import notifier_pb2_grpc
from github.com.metaprov.modelaapi.services.servingsite.v1 import servingsite_pb2_grpc
from github.com.metaprov.modelaapi.services.tenant.v1 import tenant_pb2_grpc
from github.com.metaprov.modelaapi.services.virtualbucket.v1 import virtualbucket_pb2_grpc
from github.com.metaprov.modelaapi.services.virtualcluster.v1 import virtualcluster_pb2_grpc
from github.com.metaprov.modelaapi.services.virtualvolume.v1 import virtualvolume_pb2_grpc
from github.com.metaprov.modelaapi.services.userroleclass.v1 import userroleclass_pb2_grpc
from github.com.metaprov.modelaapi.services.meeting.v1 import meeting_pb2_grpc
from github.com.metaprov.modelaapi.services.postmortem.v1 import postmortem_pb2_grpc
from github.com.metaprov.modelaapi.services.review.v1 import review_pb2_grpc
from github.com.metaprov.modelaapi.services.runbook.v1 import runbook_pb2_grpc
from github.com.metaprov.modelaapi.services.todo.v1 import todo_pb2_grpc
from github.com.metaprov.modelaapi.services.cronreport.v1 import cronreport_pb2_grpc
from github.com.metaprov.modelaapi.services.modelautobuilder.v1 import modelautobuilder_pb2_grpc
from github.com.metaprov.modelaapi.services.modelcompilerrun.v1 import modelcompilerrun_pb2_grpc
from github.com.metaprov.modelaapi.services.modelpipelinerun.v1 import modelpipelinerun_pb2_grpc
from github.com.metaprov.modelaapi.services.modelpipeline.v1 import modelpipeline_pb2_grpc
from github.com.metaprov.modelaapi.services.model.v1 import model_pb2_grpc
from github.com.metaprov.modelaapi.services.notebookrun.v1 import notebookrun_pb2_grpc
from github.com.metaprov.modelaapi.services.notebook.v1 import notebook_pb2_grpc
from github.com.metaprov.modelaapi.services.report.v1 import report_pb2_grpc
from github.com.metaprov.modelaapi.services.study.v1 import study_pb2_grpc

from modela.data.DataPipelineRun import *
from modela.data.DataPipeline import *
from modela.data.DataProduct import *
from modela.data.DataProductVersion import *
from modela.data.Dataset import *
from modela.data.DataSource import *
from modela.data.Entity import *
from modela.data.FeatureHistogram import *
from modela.data.FeaturePipelineRun import *
from modela.data.FeaturePipeline import *
from modela.data.Feature import *
from modela.data.Featureset import *
from modela.data.LabelingPipelineRun import *
from modela.data.LabelingPipeline import *
from modela.data.RecipeRun import *
from modela.data.Recipe import *
from modela.data.SqlQuery import *
from modela.data.SqlQueryRun import *
from modela.data.WebRequestRun import *
from modela.data.WebRequest import *
from modela.inference.CronPrediction import *
from modela.inference.Curtain import *
from modela.inference.DataApp import *
from modela.inference.Prediction import *
from modela.inference.Predictor import *
from modela.inference.InferenceService import *
from modela.infra.FileService import *
from modela.infra.Account import *
from modela.infra.Alert import *
from modela.infra.ApiToken import *
from modela.infra.Attachment import *
from modela.infra.Commit import *
from modela.infra.Connection import *
from modela.infra.Lab import *
from modela.infra.License import *
from modela.infra.ModelaSystem import *
from modela.infra.Notifier import *
from modela.infra.ServingSite import *
from modela.infra.Tenant import *
from modela.infra.VirtualBucket import *
from modela.infra.VirtualCluster import *
from modela.infra.VirtualVolume import *
from modela.infra.UserRoleClass import *
from modela.team.Meeting import *
from modela.team.PostMortem import *
from modela.team.Review import *
from modela.team.RunBook import *
from modela.team.Todo import *
from modela.training.CronReport import *
from modela.training.ModelAutobuilder import *
from modela.training.ModelCompilerRun import *
from modela.training.ModelPipelineRun import *
from modela.training.ModelPipeline import *
from modela.training.Model import *
from modela.training.NotebookRun import *
from modela.training.Notebook import *
from modela.training.Report import *
from modela.training.Study import *
from grpc_interceptor import ClientCallDetails, ClientInterceptor


class AuthClientInterceptor(ClientInterceptor):
    def __init__(self, token: str):
        self.token = token

    def intercept(
            self,
            method: Callable,
            request_or_iterator,
            call_details: grpc.ClientCallDetails,
    ):
        new_details = ClientCallDetails(
            call_details.method,
            call_details.timeout,
            [("authorization", self.token)],
            call_details.credentials,
            call_details.wait_for_ready,
            call_details.compression,
        )

        return method(request_or_iterator, new_details)


class Modela:
    """
    The Modela class provides an interface for connecting to your Modela API Gateway and accessing the Modela custom
    resources on your cluster. The class provides you with a directory for all resource API clients, and functions to
    fetch or create each resource.
    """

    def __init__(
            self,
            host="localhost",
            port=3000,
            username: str = "admin",
            password: str = "admin",
            secure=False,
            tls_cert=None,
            tenant="default-tenant",
            port_forward=False,
    ):
        """
        Connect to the Modela API gateway.

        :param host: The DNS name or IP that hosts the API gateway.
        :param port: The port which exposes the API gateway.
        :param username: Username for your Modela account that has permissions to use the specified tenant.
        :param password: Password for your Modela account.
        :param secure: If connecting through gRPC ingress, secure must be enabled and a TLS public key must be supplied.
        :param tls_cert: The TLS public key of the ingress that exposes the API gateway gRPC service.
        :param tenant: The tenant that Modela SDK objects will utilize by default (default: `default-tenant`)
        :param port_forward: If enabled, the SDK will attempt to port forward the API gateway using kubectl. Kubectl
            must be installed and must be connected to a cluster with Modela installed.
        """

        self.tenant = tenant
        if port_forward:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(('', 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]

            self.pf_process = subprocess.Popen(
                "kubectl port-forward svc/modela-api-gateway %d:8080 -n modela-system" % port,
                shell=True, stderr=subprocess.STDOUT)

            time.sleep(1 / 4)
            secure, host = False, "localhost"

        if secure:
            with open(tls_cert, 'rb') as f:
                credentials = grpc.ssl_channel_credentials(f.read())

            self._channel = grpc.secure_channel(f'{host}', credentials)
        else:
            if port != None:
                self._channel = grpc.insecure_channel(f'{host}:{port}')
            else:
                self._channel = grpc.insecure_channel(f'{host}')

        # if interceptors:
        #     self._channel = grpc.intercept_channel(  # type: ignore
        #         self._channel, *interceptors
        #     )

        self.__account_stub = account_pb2_grpc.AccountServiceStub(self._channel)
        self.__account_client = AccountClient(self.__account_stub, self)

        if username is not None:
            login_request = AccountLoginRequest(namespace=tenant, name=username, password=password)
            token = self.__account_stub.Login(login_request).token
            self._channel = grpc.intercept_channel(self._channel, AuthClientInterceptor(token))

        self.__account_stub = account_pb2_grpc.AccountServiceStub(self._channel)
        self.__account_client = AccountClient(self.__account_stub, self)

        self.__fileservice_stub = fileservices_pb2_grpc.FileServicesServiceStub(self._channel)
        self.__fileservice_client = FileService(self.__fileservice_stub)

        self.__datapipelinerun_stub = datapipelinerun_pb2_grpc.DataPipelineRunServiceStub(self._channel)
        self.__datapipelinerun_client = DataPipelineRunClient(self.__datapipelinerun_stub, self)

        self.__datapipeline_stub = datapipeline_pb2_grpc.DataPipelineServiceStub(self._channel)
        self.__datapipeline_client = DataPipelineClient(self.__datapipeline_stub, self)

        self.__dataproduct_stub = dataproduct_pb2_grpc.DataProductServiceStub(self._channel)
        self.__dataproduct_client = DataProductClient(self.__dataproduct_stub, self)

        self.__dataproductversion_stub = dataproductversion_pb2_grpc.DataProductVersionServiceStub(self._channel)
        self.__dataproductversion_client = DataProductVersionClient(self.__dataproductversion_stub, self)

        self.__dataset_stub = dataset_pb2_grpc.DatasetServiceStub(self._channel)
        self.__dataset_client = DatasetClient(self.__dataset_stub, self)

        self.__datasource_stub = datasource_pb2_grpc.DataSourceServiceStub(self._channel)
        self.__datasource_client = DataSourceClient(self.__datasource_stub, self)

        self.__entity_stub = entity_pb2_grpc.EntityServiceStub(self._channel)
        self.__entity_client = EntityClient(self.__entity_stub, self)

        self.__featurehistogram_stub = featurehistogram_pb2_grpc.FeatureHistogramServiceStub(self._channel)
        self.__featurehistogram_client = FeatureHistogramClient(self.__featurehistogram_stub, self)

        self.__featurepipelinerun_stub = featurepipelinerun_pb2_grpc.FeaturePipelineRunServiceStub(self._channel)
        self.__featurepipelinerun_client = FeaturePipelineRunClient(self.__featurepipelinerun_stub, self)

        self.__featurepipeline_stub = featurepipeline_pb2_grpc.FeaturePipelineServiceStub(self._channel)
        self.__featurepipeline_client = FeaturePipelineClient(self.__featurepipeline_stub, self)

        self.__feature_stub = feature_pb2_grpc.FeatureServiceStub(self._channel)
        self.__feature_client = FeatureClient(self.__feature_stub, self)

        self.__featureset_stub = featureset_pb2_grpc.FeaturesetServiceStub(self._channel)
        self.__featureset_client = FeaturesetClient(self.__featureset_stub, self)

        self.__labelingpipelinerun_stub = labelingpipelinerun_pb2_grpc.LabelingPipelineRunServiceStub(self._channel)
        self.__labelingpipelinerun_client = LabelingPipelineRunClient(self.__labelingpipelinerun_stub, self)

        self.__labelingpipeline_stub = labelingpipeline_pb2_grpc.LabelingPipelineServiceStub(self._channel)
        self.__labelingpipeline_client = LabelingPipelineClient(self.__labelingpipeline_stub, self)

        self.__reciperun_stub = reciperun_pb2_grpc.RecipeRunServiceStub(self._channel)
        self.__reciperun_client = RecipeRunClient(self.__reciperun_stub, self)

        self.__recipe_stub = recipe_pb2_grpc.RecipeServiceStub(self._channel)
        self.__recipe_client = RecipeClient(self.__recipe_stub, self)

        self.__sqlquery_stub = sqlquery_pb2_grpc.SqlQueryServiceStub(self._channel)
        self.__sqlquery_client = SqlQueryClient(self.__sqlquery_stub, self)

        self.__sqlqueryrun_stub = sqlqueryrun_pb2_grpc.SqlQueryRunServiceStub(self._channel)
        self.__sqlqueryrun_client = SqlQueryRunClient(self.__sqlqueryrun_stub, self)

        self.__webrequestrun_stub = webrequestrun_pb2_grpc.WebRequestRunServiceStub(self._channel)
        self.__webrequestrun_client = WebRequestRunClient(self.__webrequestrun_stub, self)

        self.__webrequest_stub = webrequest_pb2_grpc.WebRequestServiceStub(self._channel)
        self.__webrequest_client = WebRequestClient(self.__webrequest_stub, self)

        self.__cronprediction_stub = cronprediction_pb2_grpc.CronPredictionServiceStub(self._channel)
        self.__cronprediction_client = CronPredictionClient(self.__cronprediction_stub, self)

        self.__curtain_stub = curtain_pb2_grpc.CurtainServiceStub(self._channel)
        self.__curtain_client = CurtainClient(self.__curtain_stub, self)

        self.__dataapp_stub = dataapp_pb2_grpc.DataAppServiceStub(self._channel)
        self.__dataapp_client = DataAppClient(self.__dataapp_stub, self)

        self.__prediction_stub = prediction_pb2_grpc.PredictionServiceStub(self._channel)
        self.__prediction_client = PredictionClient(self.__prediction_stub, self)

        self.__predictor_stub = predictor_pb2_grpc.PredictorServiceStub(self._channel)
        self.__predictor_client = PredictorClient(self.__predictor_stub, self)

        self.__alert_stub = alert_pb2_grpc.AlertServiceStub(self._channel)
        self.__alert_client = AlertClient(self.__alert_stub, self)

        self.__apitoken_stub = apitoken_pb2_grpc.ApiTokenServiceStub(self._channel)
        self.__apitoken_client = ApiTokenClient(self.__apitoken_stub, self)

        self.__attachment_stub = attachment_pb2_grpc.AttachmentServiceStub(self._channel)
        self.__attachment_client = AttachmentClient(self.__attachment_stub, self)

        self.__commit_stub = commit_pb2_grpc.CommitServiceStub(self._channel)
        self.__commit_client = CommitClient(self.__commit_stub, self)

        self.__connection_stub = connection_pb2_grpc.ConnectionServiceStub(self._channel)
        self.__connection_client = ConnectionClient(self.__connection_stub, self)

        self.__lab_stub = lab_pb2_grpc.LabServiceStub(self._channel)
        self.__lab_client = LabClient(self.__lab_stub, self)

        self.__license_stub = license_pb2_grpc.LicenseServiceStub(self._channel)
        self.__license_client = LicenseClient(self.__license_stub, self)

        self.__modelasystem_stub = modelasystem_pb2_grpc.ModelaSystemServiceStub(self._channel)
        self.__modelasystem_client = ModelaSystemClient(self.__modelasystem_stub, self)

        self.__notifier_stub = notifier_pb2_grpc.NotifierServiceStub(self._channel)
        self.__notifier_client = NotifierClient(self.__notifier_stub, self)

        self.__servingsite_stub = servingsite_pb2_grpc.ServingSiteServiceStub(self._channel)
        self.__servingsite_client = ServingSiteClient(self.__servingsite_stub, self)

        self.__tenant_stub = tenant_pb2_grpc.TenantServiceStub(self._channel)
        self.__tenant_client = TenantClient(self.__tenant_stub, self)

        self.__virtualbucket_stub = virtualbucket_pb2_grpc.VirtualBucketServiceStub(self._channel)
        self.__virtualbucket_client = VirtualBucketClient(self.__virtualbucket_stub, self)

        self.__virtualcluster_stub = virtualcluster_pb2_grpc.VirtualClusterServiceStub(self._channel)
        self.__virtualcluster_client = VirtualClusterClient(self.__virtualcluster_stub, self)

        self.__virtualvolume_stub = virtualvolume_pb2_grpc.VirtualVolumeServiceStub(self._channel)
        self.__virtualvolume_client = VirtualVolumeClient(self.__virtualvolume_stub, self)

        self.__userroleclass_stub = userroleclass_pb2_grpc.UserRoleClassServiceStub(self._channel)
        self.__userroleclass_client = UserRoleClassClient(self.__userroleclass_stub, self)

        self.__meeting_stub = meeting_pb2_grpc.MeetingServiceStub(self._channel)
        self.__meeting_client = MeetingClient(self.__meeting_stub, self)

        self.__postmortem_stub = postmortem_pb2_grpc.PostMortemServiceStub(self._channel)
        self.__postmortem_client = PostMortemClient(self.__postmortem_stub, self)

        self.__review_stub = review_pb2_grpc.ReviewServiceStub(self._channel)
        self.__review_client = ReviewClient(self.__review_stub, self)

        self.__runbook_stub = runbook_pb2_grpc.RunBookServiceStub(self._channel)
        self.__runbook_client = RunBookClient(self.__runbook_stub, self)

        self.__todo_stub = todo_pb2_grpc.TodoServiceStub(self._channel)
        self.__todo_client = TodoClient(self.__todo_stub, self)

        self.__cronreport_stub = cronreport_pb2_grpc.CronReportServiceStub(self._channel)
        self.__cronreport_client = CronReportClient(self.__cronreport_stub, self)

        self.__modelautobuilder_stub = modelautobuilder_pb2_grpc.ModelAutobuilderServiceStub(self._channel)
        self.__modelautobuilder_client = ModelAutobuilderClient(self.__modelautobuilder_stub, self)

        self.__modelcompilerrun_stub = modelcompilerrun_pb2_grpc.ModelCompilerRunServiceStub(self._channel)
        self.__modelcompilerrun_client = ModelCompilerRunClient(self.__modelcompilerrun_stub, self)

        self.__modelpipelinerun_stub = modelpipelinerun_pb2_grpc.ModelPipelineRunServiceStub(self._channel)
        self.__modelpipelinerun_client = ModelPipelineRunClient(self.__modelpipelinerun_stub, self)

        self.__modelpipeline_stub = modelpipeline_pb2_grpc.ModelPipelineServiceStub(self._channel)
        self.__modelpipeline_client = ModelPipelineClient(self.__modelpipeline_stub, self)

        self.__model_stub = model_pb2_grpc.ModelServiceStub(self._channel)
        self.__model_client = ModelClient(self.__model_stub, self)

        self.__notebookrun_stub = notebookrun_pb2_grpc.NotebookRunServiceStub(self._channel)
        self.__notebookrun_client = NotebookRunClient(self.__notebookrun_stub, self)

        self.__notebook_stub = notebook_pb2_grpc.NotebookServiceStub(self._channel)
        self.__notebook_client = NotebookClient(self.__notebook_stub, self)

        self.__report_stub = report_pb2_grpc.ReportServiceStub(self._channel)
        self.__report_client = ReportClient(self.__report_stub, self)

        self.__study_stub = study_pb2_grpc.StudyServiceStub(self._channel)
        self.__study_client = StudyClient(self.__study_stub, self)

    @property
    def Accounts(self) -> AccountClient:
        return self.__account_client

    def Account(self, namespace="", name="") -> Account:
        return Account(MDAccount(), self.Accounts, namespace=namespace, name=name)

    @property
    def DataProducts(self) -> DataProductClient:
        return self.__dataproduct_client

    def DataProduct(self, namespace="", name="", serving_site: Union[ServingSite, str] = None,
                    lab: Union[Lab, str] = None,
                    public: bool = None, task_type: TaskType = None, default_training_workload: Workload = None,
                    default_serving_workload: Workload = None, default_bucket: str = None,
                    notification_settings: NotificationSettings = None,
                    permissions: Permissions = None) -> DataProduct:
        """
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param serving_site: The default Serving Site of the Data Product.
        :param lab: The default Lab of the Data Product.
        :param public: If enabled, the Data Product will be publicly accessible by all users without permissions.
        :param task_type: The default task type for child resources of the Data Product.
        :param default_training_workload: The default workload for training Jobs under the Data Product
        :param default_serving_workload: The default workload for model serving Jobs under the Data Product.
        :param default_bucket: The default bucket used for child resources of the Data Product.
        :param notification_settings: The default notification settings used for child resources of the Data Product.
        :param permissions: The permission specification that dictates which users can access the resources under
          the Data Product and what actions they can perform.
        """
        return DataProduct(MDDataProduct(), self.DataProducts, namespace, name, serving_site, lab, public,
                           task_type, default_training_workload, default_serving_workload, default_bucket,
                           notification_settings, permissions)

    @property
    def DataSources(self) -> DataSourceClient:
        return self.__datasource_client

    def DataSource(self, namespace="", name="", version=Resource.DefaultVersion, bucket: str = "default-minio-bucket",
                   infer_file: str = None, infer_dataframe: pandas.DataFrame = None, infer_bytes: bytes = None,
                   target_column: str = "", file_type: FlatFileType = None,
                   task_type: TaskType = None, csv_config: CsvFileFormat = None,
                   excel_config: ExcelNotebookFormat = None) -> DataSource:
        """
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param bucket: If data is provided for inference then a bucket must be provided.
        :param infer_file: If specified, the SDK will attempt read a file with the given path and will upload it to
            analyse the columns and generate a schema that will be applied to the resource.
        :param infer_dataframe: If specified, the Pandas DataFrame will be serialized and uploaded to analyse
            the columns and generate a schema that will be applied to the resource.
        :param infer_bytes: If specified, the raw byte data will be uploaded to analyse
            the columns and generate a schema that will be applied to the resource.
        :param target_column: The name of the target column used when training a model. This parameter only has effect
            when data is uploaded to infer a schema.
        :param file_type: The file type of raw data, used when ingesting a Dataset from a file, or creating a data snapshot
            from a database source. If inferring from a dataframe, the file type will default to CSV.
        :param task_type: The target task type in relation to the data being used.
        :param csv_config: The CSV file format of the raw data.
        :param excel_config: The Excel file format of the raw data.
        """

        return DataSource(MDDataSource(), self.DataSources, namespace, name, version, bucket, infer_file,
                          infer_dataframe, infer_bytes, target_column, file_type, task_type, csv_config, excel_config)

    @property
    def DataPipelineRuns(self) -> DataPipelineRunClient:
        return self.__datapipelinerun_client

    def DataPipelineRun(self, namespace="", name="") -> DataPipelineRun:
        return DataPipelineRun(MDDataPipelineRun(), self.DataPipelineRuns, namespace, name)

    @property
    def DataPipelines(self) -> DataPipelineClient:
        return self.__datapipeline_client

    def DataPipeline(self, namespace="", name="") -> DataPipeline:
        return DataPipeline(MDDataPipeline(), self.DataPipelines, namespace, name)

    @property
    def DataProductVersions(self) -> DataProductVersionClient:
        return self.__dataproductversion_client

    def DataProductVersion(self, namespace="", name="", baseline: bool = False,
                           previous_version: str = None) -> DataProductVersion:
        """
        Fetch or create a new Data Product Version resource

        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param baseline: If this version is baseline, then the objects of previous version will be garbage collected.
        :param previous_version: The name of the previous version.
        """
        return DataProductVersion(MDDataProductVersion(), self.DataProductVersions, namespace, name, baseline,
                                  previous_version)

    @property
    def Datasets(self) -> DatasetClient:
        return self.__dataset_client

    def Dataset(self, namespace="", name="", version=Resource.DefaultVersion, gen_datasource: bool = False,
                lab: Union[ObjectReference, Lab, str] = "default-lab",
                target_column: str = None, datasource: Union[DataSource, str] = "",
                bucket: Union[VirtualBucket, str] = "default-minio-bucket",
                dataframe: pandas.DataFrame = None, data_file: str = None, data_bytes: bytes = None,
                workload: Workload = Workload("general-large"), fast: bool = False,
                sample: SampleSettings = None, task_type: TaskType = None,
                notification: NotificationSettings = None) -> Dataset:
        """
        Fetch or create a new Dataset resource

        :param client: The Dataset client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param lab: The object reference, Lab object, or lab name under the tenant of the resource for which all
            Dataset-related workloads will be performed under.
        :param gen_datasource: If true, a Datasource resource will be created from the uploaded dataset and applied to
            the Dataset resource.
        :param target_column: If gen_datasource is enabled, then the target column of the data source must be specified.
        :param datasource: If specified as a string, the SDK will attempt to find a Data Source resource with the given name.
            If specified as a Data Source, or if one was found with the given name, it will be applied to the Dataset.
        :param bucket: The bucket which the raw dataset data will be uploaded to.
        :param dataframe: The Pandas Dataframe will be serialized and uploaded for ingestion with the Dataset resource.
        :param data_file: The file path which will be read and uploaded for ingestion with the Dataset resource.
        :param data_bytes: The raw data as bytes that will be uploaded for  ingestion with the Dataset resource.
        :param workload: The resource requirements which will be allocated for Dataset ingestion.
        :param fast: If enabled, the Dataset will skip validation, profiling, and reporting.
        :param sample: The sample settings of the dataset, which if enabled will select only a portion of the Dataset
          for further processing.
        :param task_type: The target task type in relation to the data being used.
        :param notification: The notification settings, which if enabled will forward events about this resource to a notifier.
        """
        return Dataset(MDDataset(), self.Datasets, namespace, name, version, lab, gen_datasource, target_column,
                       datasource, bucket, dataframe, data_file, data_bytes, workload, fast,
                       sample, task_type, notification)

    @property
    def FileService(self) -> FileService:
        return self.__fileservice_client

    @property
    def Entities(self) -> EntityClient:
        return self.__entity_client

    def Entity(self, namespace="", name="") -> Entity:
        return Entity(MDEntity(), self.Entities, namespace, name)

    @property
    def FeatureHistograms(self) -> FeatureHistogramClient:
        return self.__featurehistogram_client

    def FeatureHistogram(self, namespace="", name="") -> FeatureHistogram:
        return FeatureHistogram(MDFeatureHistogram(), self.FeatureHistograms, namespace, name)

    @property
    def FeaturePipelineRuns(self) -> FeaturePipelineClient:
        return self.__featurepipelinerun_client

    def FeaturePipelineRun(self, namespace="", name="") -> FeaturePipelineRun:
        return FeaturePipelineRun(MDFeaturePipelineRun(), self.FeaturePipelineRuns, namespace, name)

    @property
    def FeaturePipelines(self) -> FeaturePipelineClient:
        return self.__featurepipeline_client

    def FeaturePipeline(self, namespace="", name="") -> FeaturePipeline:
        return FeaturePipeline(MDFeaturePipeline(), self.FeaturePipelines, namespace, name)

    @property
    def Features(self) -> FeatureClient:
        return self.__feature_client

    def Feature(self, namespace="", name="") -> Feature:
        return Feature(MDFeature(), self.Features, namespace, name)

    @property
    def Featuresets(self) -> FeaturesetClient:
        return self.__featureset_client

    def Featureset(self, namespace="", name="") -> Featureset:
        return Featureset(MDFeatureset(), self.Featuresets, namespace, name)

    @property
    def LabelingPipelineRuns(self) -> LabelingPipelineRunClient:
        return self.__labelingpipelinerun_client

    def LabelingPipelineRun(self, namespace="", name="") -> LabelingPipelineRun:
        return LabelingPipelineRun(MDLabelingPipelineRun(), self.LabelingPipelineRuns, namespace, name)

    @property
    def LabelingPipelines(self) -> LabelingPipelineClient:
        return self.__labelingpipeline_client

    def LabelingPipeline(self, namespace="", name="") -> LabelingPipeline:
        return LabelingPipeline(MDLabelingPipeline(), self.LabelingPipelines, namespace, name)

    @property
    def RecipeRuns(self) -> RecipeRunClient:
        return self.__reciperun_client

    def RecipeRun(self, namespace="", name="") -> RecipeRun:
        return RecipeRun(MDRecipeRun(), self.RecipeRuns, namespace, name)

    @property
    def Recipes(self) -> RecipeClient:
        return self.__recipe_client

    def Recipe(self, namespace="", name="") -> Recipe:
        return Recipe(MDRecipe(), self.Recipes, namespace, name)

    @property
    def SqlQuerys(self) -> SqlQueryClient:
        return self.__sqlquery_client

    def SqlQuery(self, namespace="", name="") -> SqlQuery:
        return SqlQuery(MDSqlQuery(), self.SqlQuerys, namespace, name)

    @property
    def SqlQueryRuns(self) -> SqlQueryRunClient:
        return self.__sqlqueryrun_client

    def SqlQueryRun(self, namespace="", name="") -> SqlQueryRun:
        return SqlQueryRun(MDSqlQueryRun(), self.SqlQueryRuns, namespace, name)

    @property
    def WebRequestRuns(self) -> WebRequestRunClient:
        return self.__webrequestrun_client

    def WebRequestRun(self, namespace="", name="") -> WebRequestRun:
        return WebRequestRun(MDWebRequestRun(), self.WebRequestRuns, namespace, name)

    @property
    def WebRequests(self) -> WebRequestClient:
        return self.__webrequest_client

    def WebRequest(self, namespace="", name="") -> WebRequest:
        return WebRequest(MDWebRequest(), self.WebRequests, namespace, name)

    @property
    def CronPredictions(self) -> CronPredictionClient:
        return self.__cronprediction_client

    def CronPrediction(self, namespace="", name="") -> CronPrediction:
        return CronPrediction(MDCronPrediction(), self.CronPredictions, namespace, name)

    @property
    def Curtains(self) -> CurtainClient:
        return self.__curtain_client

    def Curtain(self, namespace="", name="") -> Curtain:
        return Curtain(MDCurtain(), self.Curtains, namespace, name)

    @property
    def DataApps(self) -> DataAppClient:
        return self.__dataapp_client

    def DataApp(self, namespace="", name="") -> DataApp:
        return DataApp(MDDataApp(), self.DataApps, namespace, name)

    @property
    def Predictions(self) -> PredictionClient:
        return self.__prediction_client

    def Prediction(self, namespace="", name="") -> Prediction:
        return Prediction(MDPrediction(), self.Predictions, namespace, name)

    @property
    def Predictors(self) -> PredictorClient:
        return self.__predictor_client

    def Predictor(self, namespace="", name="", version=Resource.DefaultVersion,
                  serving_site: Union[ObjectReference, ServingSite, str] = "default-serving-site",
                  model: Union[Model, str] = None, models: List[ModelDeploymentSpec] = None, port: int = 3000,
                  path: str = None, access_type: AccessType = None, replicas: int = 0, autoscale: AutoScaling = None,
                  workload: Workload = None) -> Predictor:
        """
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param serving_site: The object reference, Serving Site object, or name under the tenant of the resource for which the
            predictor will be deployed under.
        :param model: The Model object or name that the predictor will serve predictions for. This parameter
            will instantiate the predictor with a singe default deployment specification for the model.
        :param models: The list of model deployment specifications that will be applied to the predictor.
        :param port: The port of the predictor, which if applicable will expose the service internally or externally.
        :param path: The path that the predictor will expose a service on. If this parameter is not specified, then
            a path will be generated based on the access type and predictor name.
        :param access_type: The access type of the Predictor. See https://www.modela.ai/docs/docs/serving/production/
            for documentation on how different access types expose the Predictor service
        :param replicas: The amount of replicas for the predictor, which if greater than zero will serve the prediction
            service on multiple pods.
        :param autoscale: If set to true, the predictor's deployment will scale based on the amount of incoming traffic
            to the service.
        :param workload: The workload specification which determines the resources which will be allocated to the
            prediction service.
        """
        return Predictor(MDPredictor(), self.Predictors, namespace, name, version, serving_site, model, models,
                         port, path, access_type, replicas, autoscale, workload)

    @property
    def Alerts(self) -> AlertClient:
        return self.__alert_client

    def Alert(self, namespace="", name="") -> Alert:
        return Alert(MDAlert(), self.Alerts, namespace, name)

    @property
    def ApiTokens(self) -> ApiTokenClient:
        return self.__apitoken_client

    def ApiToken(self, namespace="", name="") -> ApiToken:
        return ApiToken(MDApiToken(), self.ApiTokens, namespace, name)

    @property
    def Attachments(self) -> AttachmentClient:
        return self.__attachment_client

    def Attachment(self, namespace="", name="") -> Attachment:
        return Attachment(MDAttachment(), self.Attachments, namespace, name)

    @property
    def Commits(self) -> CommitClient:
        return self.__commit_client

    def Commit(self, namespace="", name="") -> Commit:
        return Commit(MDCommit(), self.Commits, namespace, name)

    @property
    def Connections(self) -> ConnectionClient:
        return self.__connection_client

    def Connection(self, namespace="", name="") -> Connection:
        return Connection(MDConnection(), self.Connections, namespace, name)

    @property
    def Labs(self) -> LabClient:
        return self.__lab_client

    def Lab(self, namespace="", name="") -> Lab:
        return Lab(MDLab(), self.Labs, namespace, name)

    @property
    def Licenses(self) -> LicenseClient:
        return self.__license_client

    def License(self, namespace="", name="") -> License:
        return License(MDLicense(), self.Licenses, namespace, name)

    @property
    def ModelaSystems(self) -> ModelaSystemClient:
        return self.__modelasystem_client

    def ModelaSystem(self, namespace="", name="") -> ModelaSystem:
        return ModelaSystem(MDModelaSystem(), self.ModelaSystems, namespace, name)

    @property
    def Notifiers(self) -> NotifierClient:
        return self.__notifier_client

    def Notifier(self, namespace="", name="") -> Notifier:
        return Notifier(MDNotifier(), self.Notifiers, namespace, name)

    @property
    def ServingSites(self) -> ServingSiteClient:
        return self.__servingsite_client

    def ServingSite(self, namespace="", name="") -> ServingSite:
        return ServingSite(MDServingSite(), self.ServingSites, namespace, name)

    @property
    def Tenants(self) -> TenantClient:
        return self.__tenant_client

    def Tenant(self, namespace="", name="") -> Tenant:
        return Tenant(MDTenant(), self.Tenants, namespace, name)

    @property
    def VirtualBuckets(self) -> VirtualBucketClient:
        return self.__virtualbucket_client

    def VirtualBucket(self, namespace="", name="") -> VirtualBucket:
        return VirtualBucket(MDVirtualBucket(), self.VirtualBuckets, namespace, name)

    @property
    def VirtualClusters(self) -> VirtualClusterClient:
        return self.__virtualcluster_client

    def VirtualCluster(self, namespace="", name="") -> VirtualCluster:
        return VirtualCluster(MDVirtualCluster(), self.VirtualClusters, namespace, name)

    @property
    def VirtualVolumes(self) -> VirtualVolumeClient:
        return self.__virtualvolume_client

    def VirtualVolume(self, namespace="", name="") -> VirtualVolume:
        return VirtualVolume(MDVirtualVolume(), self.VirtualVolumes, namespace, name)

    @property
    def UserRoleClasses(self) -> UserRoleClassClient:
        return self.__userroleclass_client

    def UserRoleClass(self, namespace="", name="", rules: List[Rule] = None) -> UserRoleClass:
        """
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param rules: The list of rules which any Account associated with the User Role Class resource may perform.
        """
        return UserRoleClass(MDUserRoleClass(), self.UserRoleClasses, namespace, name, rules)

    @property
    def Meetings(self) -> MeetingClient:
        return self.__meeting_client

    def Meeting(self, namespace="", name="") -> Meeting:
        return Meeting(MDMeeting(), self.Meetings, namespace, name)

    @property
    def PostMortems(self) -> PostMortemClient:
        return self.__postmortem_client

    def PostMortem(self, namespace="", name="") -> PostMortem:
        return PostMortem(MDPostMortem(), self.PostMortems, namespace, name)

    @property
    def Reviews(self) -> ReviewClient:
        return self.__review_client

    def Review(self, namespace="", name="") -> Review:
        return Review(MDReview(), self.Reviews, namespace, name)

    @property
    def RunBooks(self) -> RunBookClient:
        return self.__runbook_client

    def RunBook(self, namespace="", name="") -> RunBook:
        return RunBook(MDRunBook(), self.RunBooks, namespace, name)

    @property
    def Todos(self) -> TodoClient:
        return self.__todo_client

    def Todo(self, namespace="", name="") -> Todo:
        return Todo(MDTodo(), self.Todos, namespace, name)

    @property
    def CronReports(self) -> CronReportClient:
        return self.__cronreport_client

    def CronReport(self, namespace="", name="") -> CronReport:
        return CronReport(MDCronReport(), self.CronReports, namespace, name)

    @property
    def ModelAutobuilders(self) -> ModelAutobuilderClient:
        return self.__modelautobuilder_client

    def ModelAutobuilder(self, namespace="", name="", version=Resource.DefaultVersion,
                         lab: Union[ObjectReference, Lab, str] = "default-lab",
                         serving_site: Union[ObjectReference, ServingSite, str] = "default-serving-site",
                         task_type: TaskType = TaskType.BinaryClassification, workload: Workload = Workload("general-large"),
                         bucket: Union[ObjectReference, VirtualBucket, str] = "default-minio-bucket",
                         dataframe: pandas.DataFrame = None, data_file: str = None, data_bytes: bytes = None,
                         target_column: str = None, objective: Metric = Metric.Accuracy,
                         feature_selection: bool = False, feature_engineering: bool = False, max_models: int = 1,
                         max_time: int = 512, trainers: int = 1, predictor_access_type: AccessType = AccessType.ClusterIP,
                         predictor_autoscale: bool = False, create_data_app: bool = False) -> ModelAutobuilder:
        """
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param lab: The object reference, Lab object, or lab name under the tenant of the resource for which all
            data science workloads will be performed under.
        :param serving_site: The object reference, Serving Site object, or name under the tenant of the resource for which
            the created Predictor will be deployed under.
        :param task_type: The target task type in relation to the data being used.
        :param workload: The workload specification which determines the resources which will be allocated for training
            and serving workloads.
        :param bucket: The bucket which the raw dataset data will be uploaded to.
        :param dataframe: The Pandas Dataframe will be serialized and uploaded to create a new Dataset resource.
        :param data_file: The file path which will be read and uploaded to create a new Dataset resource.
        :param data_bytes: The raw data as bytes that will be uploaded to create a new Dataset resource.
        :param target_column: The target column of the Dataset to be created.
        :param objective: The objective metric to be used when determining the best model from the Study.
        :param feature_selection: If True feature selection will be performed on the Dataset before the model search.
        :param feature_engineering: If True feature engineering will be performed on the Dataset before the model search.
        :param max_models: The maximum number of models to sample before selecting the best model.
        :param max_time: The maximum amount of time in seconds which the model search can run for.
        :param trainers: The number of parallel trainers to allocate during the model search
        :param predictor_access_type: The access type of the Predictor to be created. See https://www.modela.ai/docs/docs/serving/production/
            for documentation on how different access types expose the Predictor service
        :param predictor_autoscale: If true the created Predictor will automatically scale for traffic
        :param create_data_app: If true a Data Application will be created to serve a live model dashboard
        """
        return ModelAutobuilder(MDModelAutobuilder(), self.ModelAutobuilders, namespace, name, version, lab,
                                serving_site, task_type, workload, bucket, dataframe, data_file, data_bytes,
                                target_column, objective, feature_selection, feature_engineering, max_models,
                                max_time, trainers, predictor_access_type, predictor_autoscale, create_data_app)

    @property
    def ModelCompilerRuns(self) -> ModelCompilerRunClient:
        return self.__modelcompilerrun_client

    def ModelCompilerRun(self, namespace="", name="") -> ModelCompilerRun:
        return ModelCompilerRun(MDModelCompilerRun(), self.ModelCompilerRuns, namespace, name)

    @property
    def ModelPipelineRuns(self) -> ModelPipelineRunClient:
        return self.__modelpipelinerun_client

    def ModelPipelineRun(self, namespace="", name="") -> ModelPipelineRun:
        return ModelPipelineRun(MDModelPipelineRun(), self.ModelPipelineRuns, namespace, name)

    @property
    def ModelPipelines(self) -> ModelPipelineClient:
        return self.__modelpipeline_client

    def ModelPipeline(self, namespace="", name="") -> ModelPipeline:
        return ModelPipeline(MDModelPipeline(), self.ModelPipelines, namespace, name)

    @property
    def Models(self) -> ModelClient:
        return self.__model_client

    def Model(self, namespace="", name="") -> Model:
        return Model(MDModel(), self.Models, namespace, name)

    @property
    def NotebookRuns(self) -> NotebookRunClient:
        return self.__notebookrun_client

    def NotebookRun(self, namespace="", name="") -> NotebookRun:
        return NotebookRun(MDNotebookRun(), self.NotebookRuns, namespace, name)

    @property
    def Notebooks(self) -> NotebookClient:
        return self.__notebook_client

    def Notebook(self, namespace="", name="") -> Notebook:
        return Notebook(MDNotebook(), self.Notebooks, namespace, name)

    @property
    def Reports(self) -> ReportClient:
        return self.__report_client

    def Report(self, namespace="", name="") -> Report:
        """
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param entity: An object reference to an existing resource on the cluster.
        :param report_type: The type of report being generated; this should correspond with the type of entity being
            referenced (e.g. RegressionModelReport for a regression Model resource)
        """
        return Report(MDReport(), self.Reports, namespace, name)

    @property
    def Studies(self) -> StudyClient:
        return self.__study_client

    def Study(self, namespace="", name="", version=Resource.DefaultVersion, dataset: Union[str, Dataset] = "",
              test_dataset: Union[str, Dataset] = "",
              lab: Union[ObjectReference, Lab, str] = "default-lab", bucket: Union[VirtualBucket, str] = None,
              objective: Metric = Metric.Accuracy, search: ModelSearch = None,
              fe_search: FeatureEngineeringSearch = None, baseline: BaselineSettings = None,
              ensemble: Ensemble = None, trainer_template: Training = None, interpretability: Interpretability = None,
              schedule: StudySchedule = None, notification: NotificationSettings = None, garbage_collect: bool = True,
              keep_best_models: bool = True, fast: bool = False, timeout: int = 600, template: bool = False) -> Study:
        """
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param dataset: If specified as a string, the SDK will attempt to find a Dataset resource with the given name.
            If specified as a Dataset object, or if one was found with the given name, it will be used in the Study.
        :param test_dataset: If specified, the Dataset will be used as the test dataset and the Dataset specified by
            the `dataset` field will be used solely as the training dataset
        :param lab: The object reference, Lab object, or lab name under the default-tenant for which all Study-related
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
        :param schedule: The schedule for the study to run chronically.
        :param notification: The notification settings, which if enabled will forward events about this resource to a notifier.
        :param garbage_collect: If enabled, models which did not move past the testing stage will be garbage collected by
            the system.
        :param keep_best_models: If enabled, the best models from each algorithm will not be garbage collected.
        :param fast: If enabled, the Study will skip profiling, explaining, and reporting.
        :param timeout: The timeout in seconds after which the Study will fail.
        :param template: If the Study is a template it will not start a search and can only be used as a template for
            other studies.
        """
        return Study(MDStudy(), self.Studies, namespace, name, version, dataset, test_dataset, lab, bucket, objective,
                     search, fe_search, baseline, ensemble, trainer_template, interpretability, schedule,
                     notification, garbage_collect, keep_best_models, fast, timeout, template)

    def close(self):
        if hasattr(self, 'pf_process'):
            self.pf_process.kill()

        if self._channel:
            self._channel.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
