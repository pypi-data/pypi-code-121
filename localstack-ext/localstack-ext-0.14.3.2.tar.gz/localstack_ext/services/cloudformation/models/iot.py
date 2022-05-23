from typing import Dict
from localstack.services.cloudformation.deployment_utils import(generate_default_name_without_stack,lambda_keys_to_lower,remove_none_values)
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.service_models import lambda_to_json
class IoTCertificate(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::IoT::Certificate"
 def fetch_state(self,stack_name,resources):
  return self.state.get("certificateId")
 def get_physical_resource_id(self,attribute=None,**kwargs):
  return self.props.get("certificateId")
 @classmethod
 def get_deploy_templates(cls):
  def create_certificate_from_csr(resource_id,resources,*args,**kwargs):
   client=aws_stack.connect_to_service("iot")
   resource=cls(resources[resource_id])
   sign_req=resource.props.get("CertificateSigningRequest")
   response=client.create_certificate_from_csr(certificateSigningRequest=sign_req)
   resource.state["certificateId"]=response.get("certificateId")
   return response
  return{"create":{"function":create_certificate_from_csr}}
class IoTThing(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::IoT::Thing"
 @staticmethod
 def add_defaults(resource:Dict,stack_name:str):
  props=resource["Properties"]
  if not props.get("ThingName"):
   props["ThingName"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 def get_physical_resource_id(self,attribute=None,**kwargs):
  return self.props.get("ThingName")
 def fetch_state(self,stack_name,resources):
  thing_name=self.props.get("ThingName")
  iot_client=aws_stack.connect_to_service("iot")
  things=iot_client.list_things(maxResults=500)["things"]
  match=[t for t in things if t.get("thingName")==thing_name]
  return(match or[None])[0]
 @classmethod
 def get_deploy_templates(cls):
  def _get_thing_config(params,**kwargs):
   config={"thingName":params.get("ThingName"),"thingTypeName":params.get("ThingTypeName"),"attributePayload":{"attributes":params.get("AttributePayload",{}).get("Attributes",{})}}
   return remove_none_values(config)
  return{"create":{"function":"create_thing","parameters":_get_thing_config},"delete":{"function":"delete_thing","parameters":{"thingName":"ThingName"}}}
class IoTTopicRule(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::IoT::TopicRule"
 @staticmethod
 def add_defaults(resource:Dict,stack_name:str):
  props=resource["Properties"]
  if not props.get("RuleName"):
   props["RuleName"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 def get_physical_resource_id(self,attribute=None,**kwargs):
  return self.props.get("RuleName")
 def fetch_state(self,stack_name,resources):
  rule_name=self.props.get("RuleName")
  iot_client=aws_stack.connect_to_service("iot")
  rules=iot_client.list_topic_rules()["rules"]
  matches=[r for r in rules if r.get("ruleName")==rule_name]
  return(matches or[None])[0]
 @classmethod
 def get_deploy_templates(cls):
  return{"create":{"function":"create_topic_rule","parameters":{"ruleName":"RuleName","topicRulePayload":lambda_keys_to_lower("TopicRulePayload"),"tags":lambda_keys_to_lower("Tags")},"types":{"ruleDisabled":bool}},"delete":{"function":"delete_topic_rule","parameters":{"ruleName":"RuleName"}}}
class IoTPolicy(GenericBaseModel):
 @staticmethod
 def cloudformation_type():
  return "AWS::IoT::Policy"
 @staticmethod
 def add_defaults(resource:Dict,stack_name:str):
  props=resource["Properties"]
  if not props.get("PolicyName"):
   props["PolicyName"]=generate_default_name_without_stack(resource["LogicalResourceId"])
 def get_physical_resource_id(self,attribute=None,**kwargs):
  return self.props.get("PolicyName")
 def fetch_state(self,stack_name,resources):
  policy_name=self.props.get("PolicyName")
  iot_client=aws_stack.connect_to_service("iot")
  policies=iot_client.list_policies(pageSize=500)["policies"]
  match=[p for p in policies if p.get("policyName")==policy_name]
  return(match or[None])[0]
 @classmethod
 def get_deploy_templates(cls):
  return{"create":{"function":"create_policy","parameters":{"policyName":"PolicyName","policyDocument":lambda_to_json("PolicyDocument")}},"delete":{"function":"delete_policy","parameters":{"policyName":"PolicyName"}}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
