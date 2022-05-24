_k='DomainIAMRoleName'
_j='Domain'
_i='CopyTagsToSnapshot'
_h='DeletionProtection'
_g='EnableCloudwatchLogsExports'
_f='EnableIAMDatabaseAuthentication'
_e='KmsKeyId'
_d='StorageEncrypted'
_c='PreferredMaintenanceWindow'
_b='PreferredBackupWindow'
_a='OptionGroupName'
_Z='MasterUserPassword'
_Y='MasterUsername'
_X='EngineVersion'
_W='Engine'
_V='VpcSecurityGroupIds'
_U='CharacterSetName'
_T='Endpoint'
_S='Endpoint.Port'
_R='localhost'
_Q='Endpoint.Address'
_P='Properties'
_O='Family'
_N='BackupRetentionPeriod'
_M='Description'
_L='Tags'
_K='delete'
_J='create'
_I='rds'
_H='DBParameterGroupName'
_G='DBInstanceIdentifier'
_F='parameters'
_E='DBSubnetGroupName'
_D='Port'
_C='DBClusterIdentifier'
_B='function'
_A=None
from typing import Dict
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import short_uid
class RDSDBSubnetGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBSubnetGroup'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_E)
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_I);C=A.resolve_refs_recursively(stack_name,A.props.get(_E),resources);D=B.describe_db_subnet_groups()['DBSubnetGroups'];E=[A for A in D if A[_E]==C];return(E or[_A])[0]
	@staticmethod
	def get_deploy_templates():return{_J:{_B:'create_db_subnet_group'},_K:{_B:'delete_db_subnet_group',_F:{_E:_E}}}
class RDSDBCluster(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBCluster'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource[_P]
		if not A.get(_C):A[_C]=f"dbc-{short_uid()}"
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_C)
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_I);C=B.describe_db_clusters().get('DBClusters',[]);D=A.resolve_refs_recursively(stack_name,A.props.get(_C),resources);E=[A for A in C if A[_C]==D];return(E or[_A])[0]
	def get_cfn_attribute(B,attribute):
		A=attribute
		if A==_Q:return _R
		C=B.props
		if A==_S:return C.get(_D)or C.get(_T,{}).get(_D)
		return super(RDSDBCluster,B).get_cfn_attribute(A)
	@staticmethod
	def get_deploy_templates():
		E='ScalingConfiguration';F=['AvailabilityZones',_N,_U,'DatabaseName',_C,'DBClusterParameterGroupName',_V,_E,_W,_X,_D,_Y,_Z,_a,_b,_c,'ReplicationSourceIdentifier',_L,_d,_e,'PreSignedUrl',_f,'BacktrackWindow',_g,'EngineMode',E,_h,'GlobalClusterIdentifier','EnableHttpEndpoint',_i,_j,_k,'EnableGlobalWriteForwarding','SourceRegion']
		def A(params,**G):
			D='MaxCapacity';C='MinCapacity';B=params;B={A:C for(A,C)in B.items()if A in F};A=B.get(E)
			if A:
				if C in A:A[C]=int(A[C])
				if D in A:A[D]=int(A[D])
			return B
		B={_J:{_B:'create_db_cluster',_F:A,'types':{_N:int,_D:int}},_K:{_B:'delete_db_cluster',_F:[_C]}};return B
class RDSDBParameterGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBParameterGroup'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_H)
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_I);D=A.props;F=A.resolve_refs_recursively(B,D.get(_M),C);G=A.resolve_refs_recursively(B,D.get(_O),C);H=E.describe_db_parameter_groups()['DBParameterGroups'];I=[A for A in H if A[_O]==G and A[_M]==F];return(I or[_A])[0]
	@staticmethod
	def get_deploy_templates():return{_J:{_B:'create_db_parameter_group',_F:{_H:_H,'DBParameterGroupFamily':_O,_M:_M,_L:_L}},_K:{_B:'delete_db_parameter_group',_F:[_H]}}
class RDSDBInstance(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBInstance'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource[_P]
		if not A.get(_G):A[_G]=f"db-{short_uid()}"
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_G)
	def get_cfn_attribute(B,attribute):
		A=attribute
		if A==_Q:return _R
		C=B.props
		if A==_S:return C.get(_T,{}).get(_D)or C.get(_D)
		return super(RDSDBInstance,B).get_cfn_attribute(A)
	def fetch_state(B,stack_name,resources):A=B.props.get(_G);A=B.resolve_refs_recursively(stack_name,A,resources);C=aws_stack.connect_to_service(_I);D=C.describe_db_instances()['DBInstances'];E=[B for B in D if B[_G]==A];return(E or[_A])[0]
	@staticmethod
	def get_deploy_templates():A='AllocatedStorage';B=['DBName',_G,A,'DBInstanceClass',_W,_Y,_Z,'DBSecurityGroups','AvailabilityZone',_E,_c,_H,_N,_b,_D,'MultiAZ',_X,'AutoMinorVersionUpgrade','LicenseModel','Iops',_a,_U,'NcharCharacterSetName','PubliclyAccessible',_L,_C,'StorageType','TdeCredentialArn','TdeCredentialPassword',_d,_e,_j,_i,'MonitoringInterval','MonitoringRoleArn',_k,'PromotionTier','Timezone',_f,'EnablePerformanceInsights','PerformanceInsightsKMSKeyId','PerformanceInsightsRetentionPeriod',_g,'ProcessorFeatures',_h,'MaxAllocatedStorage','EnableCustomerOwnedIp'];return{_J:{_B:'create_db_instance',_F:B+[{_V:'VPCSecurityGroups'}],'types':{A:int,_D:int}},_K:{_B:'delete_db_instance',_F:[_G]}}