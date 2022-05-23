from localstack.utils.aws import aws_models
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  super(LambdaLayer,self).__init__(arn)
  self.cwd=None
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.id.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,id,env=None):
  super(RDSDatabase,self).__init__(id,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,id,env=None):
  super(RDSCluster,self).__init__(id,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,id,env=None):
  super(AppSyncAPI,self).__init__(id,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,id,env=None):
  super(AmplifyApp,self).__init__(id,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,id,env=None):
  super(ElastiCacheCluster,self).__init__(id,env=env)
class TransferServer(BaseComponent):
 def __init__(self,id,env=None):
  super(TransferServer,self).__init__(id,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,id,env=None):
  super(CloudFrontDistribution,self).__init__(id,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,id,env=None):
  super(CodeCommitRepository,self).__init__(id,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
