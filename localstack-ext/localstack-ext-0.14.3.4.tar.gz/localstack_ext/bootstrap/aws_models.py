_A=None
from localstack.utils.aws import aws_models
class LambdaLayer(aws_models.LambdaFunction):
	def __init__(A,arn):super(LambdaLayer,A).__init__(arn);A.cwd=_A;A.runtime='';A.handler='';A.envvars={};A.versions={}
class BaseComponent(aws_models.Component):
	def name(A):return A.id.split(':')[-1]
class RDSDatabase(BaseComponent):
	def __init__(A,id,env=_A):super(RDSDatabase,A).__init__(id,env=env)
class RDSCluster(BaseComponent):
	def __init__(A,id,env=_A):super(RDSCluster,A).__init__(id,env=env)
class AppSyncAPI(BaseComponent):
	def __init__(A,id,env=_A):super(AppSyncAPI,A).__init__(id,env=env)
class AmplifyApp(BaseComponent):
	def __init__(A,id,env=_A):super(AmplifyApp,A).__init__(id,env=env)
class ElastiCacheCluster(BaseComponent):
	def __init__(A,id,env=_A):super(ElastiCacheCluster,A).__init__(id,env=env)
class TransferServer(BaseComponent):
	def __init__(A,id,env=_A):super(TransferServer,A).__init__(id,env=env)
class CloudFrontDistribution(BaseComponent):
	def __init__(A,id,env=_A):super(CloudFrontDistribution,A).__init__(id,env=env)
class CodeCommitRepository(BaseComponent):
	def __init__(A,id,env=_A):super(CodeCommitRepository,A).__init__(id,env=env)