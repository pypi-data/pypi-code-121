_H='parameters'
_G='delete'
_F='create'
_E='timestream-write'
_D='Properties'
_C='function'
_B='TableName'
_A='DatabaseName'
from typing import Dict
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import short_uid
class TimestreamDatabase(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Timestream::Database'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_D]
		if not B.get(_A):B[_A]=generate_default_name_without_stack(A['LogicalResourceId'])
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_E);C=A.resolve_refs_recursively(stack_name,A.props.get(_A),resources);D=B.describe_database(DatabaseName=C);return D['Database']
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_A)
	@staticmethod
	def get_deploy_templates():return{_F:{_C:'create_database'},_G:{_C:'delete_database',_H:[_A]}}
class TimestreamTable(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Timestream::Table'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource[_D]
		if not A.get(_B):A[_B]=f"t{short_uid()}"
	def fetch_state(A,stack_name,resources):
		C=resources;B=stack_name;E=aws_stack.connect_to_service(_E);D=A.resolve_refs_recursively(B,A.props.get(_A),C);F=A.resolve_refs_recursively(B,A.props.get(_B),C)
		if not D:return
		G=E.describe_table(DatabaseName=D,TableName=F);return G['Table']
	def get_physical_resource_id(B,attribute,**C):A=B.props;return f"{A.get(_A)}|{A.get(_B)}"
	@staticmethod
	def get_deploy_templates():return{_F:{_C:'create_table'},_G:{_C:'delete_table',_H:[_A,_B]}}