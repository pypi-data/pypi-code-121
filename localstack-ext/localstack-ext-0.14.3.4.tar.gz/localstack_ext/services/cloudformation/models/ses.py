_M='LogicalResourceId'
_L='parameters'
_K='delete'
_J='create'
_I='Properties'
_H='Rule'
_G='Template'
_F='Name'
_E='TemplateName'
_D='ses'
_C='RuleSetName'
_B='function'
_A=None
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class SESTemplate(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::SES::Template'
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_D);C=A.props.get(_G,{}).get(_E);D=A.resolve_refs_recursively(stack_name,C,resources);E=B.list_templates().get('TemplatesMetadata',[]);F=[A for A in E if A[_F]==D];return(F or[_A])[0]
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_G,{}).get(_E)
	def update_resource(E,new_resource,stack_name,resources):
		A=aws_stack.connect_to_service(_D);B=new_resource[_I];C=B.get(_G,{});D=A.get_template(TemplateName=C[_E])[_G]
		if all((D.get(A,'')==C.get(A,'')for A in['SubjectPart','TextPart','HtmlPart'])):return
		return A.update_template(**B)
	@staticmethod
	def get_deploy_templates():return{_J:{_B:'create_template'},_K:{_B:'delete_template',_L:{_E:_E}}}
class SESReceiptRuleSet(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::SES::ReceiptRuleSet'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_C)
	def get_cfn_attribute(A,attribute):return super(SESReceiptRuleSet,A).get_cfn_attribute(attribute)
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_I]
		if not B.get(_C):B[_C]=generate_default_name_without_stack(A[_M])
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service(_D);A=B.props.get(_C);A=B.resolve_refs_recursively(stack_name,A,resources);D=C.describe_receipt_rule_set(RuleSetName=A);return D or _A
	@classmethod
	def fetch_details(C,rule_set_name):A=aws_stack.connect_to_service(_D);B=A.describe_receipt_rule_set(RuleSetName=rule_set_name);return B or _A
	@staticmethod
	def get_deploy_templates():return{_J:{_B:'create_receipt_rule_set'},_K:{_B:'delete_receipt_rule_set'}}
class SESReceiptRule(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::SES::ReceiptRule'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_H,{}).get(_F)
	def get_cfn_attribute(A,attribute):return super(SESReceiptRule,A).get_cfn_attribute(attribute)
	@classmethod
	def fetch_details(C,rule_set_name,rule_name):A=aws_stack.connect_to_service(_D);B=A.describe_receipt_rule(RuleSetName=rule_set_name,RuleName=rule_name).get(_H);return B or _A
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_I][_H]
		if not B.get(_F):B[_F]=generate_default_name_without_stack(A[_M])
	@staticmethod
	def get_deploy_templates():return{_J:{_B:'create_receipt_rule'},_K:{_B:'delete_receipt_rule',_L:{_C:_C,'RuleName':lambda params,**A:params[_H][_F]}}}