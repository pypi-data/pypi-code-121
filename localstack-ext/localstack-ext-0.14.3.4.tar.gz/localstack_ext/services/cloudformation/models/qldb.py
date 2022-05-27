_B='Properties'
_A='Name'
from typing import Dict
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack,params_list_to_dict
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.collections import select_attributes
from localstack.utils.objects import not_none_or
class QLDBLedger(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::QLDB::Ledger'
	def get_physical_resource_id(A,attribute=None,**B):return A.props.get(_A)
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service('qldb');C=A.resolve_refs_recursively(stack_name,A.props.get(_A),resources);D=B.describe_ledger(Name=C);return D
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_B]
		if not B.get(_A):B[_A]=generate_default_name_without_stack(A['LogicalResourceId'])
	@staticmethod
	def get_deploy_templates():
		A='function'
		def B(resource_id,resources,*D,**E):A=aws_stack.connect_to_service('qldb');C=resources[resource_id][_B];B=C.get(_A);A.update_ledger(Name=B,DeletionProtection=False);A.delete_ledger(Name=B)
		def C(params,*E,**F):
			B='Tags';A=params;C=select_attributes(A,['DeletionProtection','KmsKey',_A,'PermissionsMode'])
			if A.get(B):D=params_list_to_dict(B)(A);C[B]={A:str(not_none_or(B,''))for(A,B)in D.items()}
			return C
		return{'create':{A:'create_ledger','parameters':C},'delete':{A:B}}