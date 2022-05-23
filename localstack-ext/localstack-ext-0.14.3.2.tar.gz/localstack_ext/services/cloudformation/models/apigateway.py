from localstack.services.cloudformation.deployment_utils import lambda_keys_to_lower
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class ApiGatewayAuthorizer(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::ApiGateway::Authorizer"
 def fetch_state(self,stack_name,resources):
  props=self.props
  client=aws_stack.connect_to_service("apigateway")
  api_id=self.resolve_refs_recursively(stack_name,props["RestApiId"],resources)
  auth_uri=self.resolve_refs_recursively(stack_name,props.get("AuthorizerUri"),resources)
  authorizers=client.get_authorizers(restApiId=api_id,limit=200)["items"]
  result=[a for a in authorizers if a["type"]==props.get("Type")and a.get("authorizerUri")==auth_uri]
  return(result or[None])[0]
 def get_physical_resource_id(self,attribute=None,**kwargs):
  return self.props.get("id")
 @classmethod
 def get_deploy_templates(cls):
  def _delete_params(params,resource_id,resources,**kwargs):
   resource=cls(resources[resource_id])
   return{"restApiId":resource.props["RestApiId"],"authorizerId":resource.props.get("id")}
  return{"create":{"function":"create_authorizer","parameters":lambda_keys_to_lower()},"delete":{"function":"delete_authorizer","parameters":_delete_params}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
