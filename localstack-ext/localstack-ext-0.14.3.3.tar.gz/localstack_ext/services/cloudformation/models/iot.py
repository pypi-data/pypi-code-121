_O='policyName'
_N='ruleName'
_M='delete'
_L='thingName'
_K='LogicalResourceId'
_J='Properties'
_I='create'
_H='iot'
_G='certificateId'
_F='PolicyName'
_E='RuleName'
_D='parameters'
_C='ThingName'
_B='function'
_A=None
from typing import Dict
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack,lambda_keys_to_lower,remove_none_values
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.service_models import lambda_to_json
class IoTCertificate(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoT::Certificate'
	def fetch_state(A,stack_name,resources):return A.state.get(_G)
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_G)
	@classmethod
	def get_deploy_templates(C):
		def A(resource_id,resources,*F,**G):D=aws_stack.connect_to_service(_H);A=C(resources[resource_id]);E=A.props.get('CertificateSigningRequest');B=D.create_certificate_from_csr(certificateSigningRequest=E);A.state[_G]=B.get(_G);return B
		return{_I:{_B:A}}
class IoTThing(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoT::Thing'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_J]
		if not B.get(_C):B[_C]=generate_default_name_without_stack(A[_K])
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_C)
	def fetch_state(A,stack_name,resources):B=A.props.get(_C);C=aws_stack.connect_to_service(_H);D=C.list_things(maxResults=500)['things'];E=[A for A in D if A.get(_L)==B];return(E or[_A])[0]
	@classmethod
	def get_deploy_templates(B):
		def A(params,**C):A=params;B={_L:A.get(_C),'thingTypeName':A.get('ThingTypeName'),'attributePayload':{'attributes':A.get('AttributePayload',{}).get('Attributes',{})}};return remove_none_values(B)
		return{_I:{_B:'create_thing',_D:A},_M:{_B:'delete_thing',_D:{_L:_C}}}
class IoTTopicRule(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoT::TopicRule'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_J]
		if not B.get(_E):B[_E]=generate_default_name_without_stack(A[_K])
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_E)
	def fetch_state(A,stack_name,resources):B=A.props.get(_E);C=aws_stack.connect_to_service(_H);D=C.list_topic_rules()['rules'];E=[A for A in D if A.get(_N)==B];return(E or[_A])[0]
	@classmethod
	def get_deploy_templates(A):return{_I:{_B:'create_topic_rule',_D:{_N:_E,'topicRulePayload':lambda_keys_to_lower('TopicRulePayload'),'tags':lambda_keys_to_lower('Tags')},'types':{'ruleDisabled':bool}},_M:{_B:'delete_topic_rule',_D:{_N:_E}}}
class IoTPolicy(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::IoT::Policy'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_J]
		if not B.get(_F):B[_F]=generate_default_name_without_stack(A[_K])
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_F)
	def fetch_state(A,stack_name,resources):B=A.props.get(_F);C=aws_stack.connect_to_service(_H);D=C.list_policies(pageSize=500)['policies'];E=[A for A in D if A.get(_O)==B];return(E or[_A])[0]
	@classmethod
	def get_deploy_templates(A):return{_I:{_B:'create_policy',_D:{_O:_F,'policyDocument':lambda_to_json('PolicyDocument')}},_M:{_B:'delete_policy',_D:{_O:_F}}}