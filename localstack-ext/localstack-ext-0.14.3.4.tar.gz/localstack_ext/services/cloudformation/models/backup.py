_A='BackupPlanId'
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
class BackupPlan(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Backup::BackupPlan'
	def fetch_state(A,stack_name,resources):B='BackupPlanName';C=aws_stack.connect_to_service('backup');D=C.list_backup_plans().get('BackupPlansList',[]);E=A.resolve_refs_recursively(stack_name,A.props[B],resources);F=[A for A in D if A[B]==E];return(F or[None])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_A)
	@staticmethod
	def get_deploy_templates():A='function';return{'create':{A:'create_backup_plan'},'delete':{A:'delete_backup_plan','parameters':[_A]}}