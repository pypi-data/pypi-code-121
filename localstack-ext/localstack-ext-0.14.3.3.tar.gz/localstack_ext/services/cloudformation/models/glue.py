_A='Name'
from localstack.services.cloudformation.service_models import REF_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone
class GlueTrigger(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Glue::Trigger'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ATTRS:return A.props.get(_A)
		return super(GlueTrigger,A).get_cfn_attribute(B)
class GlueWorkflow(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Glue::Workflow'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ATTRS:return A.props.get(_A)
		return super(GlueWorkflow,A).get_cfn_attribute(B)
class GlueJob(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Glue::Job'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ATTRS:return A.props[_A]
		return super(GlueJob,A).get_cfn_attribute(B)
class GlueCrawler(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Glue::Crawler'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ATTRS:return A.props[_A]
		return super(GlueCrawler,A).get_cfn_attribute(B)
	def fetch_state(A,stack_name,resources):B=A.props.get(_A)or A.resource_id;B=A.resolve_refs_recursively(stack_name,B,resources);C=aws_stack.connect_to_service('glue');return C.get_crawler(Name=B)['Crawler']
	@staticmethod
	def get_deploy_templates():
		def A(params,**D):
			C='Role';B='Schedule';A=clone(params)
			if B in A:A[B]=A[B]['ScheduleExpression']
			A[C]=A.get(C)or'_unknown_';return A
		return{'create':{'function':'create_crawler','parameters':A}}
class GlueDatabase(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Glue::Database'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ATTRS:return A.props.get('DatabaseInput',{}).get(_A)
		return super(GlueDatabase,A).get_cfn_attribute(B)
class GlueClassifier(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Glue::Classifier'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ATTRS:
			C=A.props.get('GrokClassifier',{}).get(_A)or A.props.get('CsvClassifier',{}).get(_A)or A.props.get('JsonClassifier',{}).get(_A)or A.props.get('XMLClassifier',{}).get(_A)
			if C:return C
		return super(GlueCrawler,A).get_cfn_attribute(B)
class GlueTable(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Glue::Table'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ATTRS:return A.props.get('TableInput',{}).get(_A)
		return super(GlueTable,A).get_cfn_attribute(B)