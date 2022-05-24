_V='UserIdGroupPairs'
_U='IpPermissions'
_T='DestinationSecurityGroupId'
_S='SourceSecurityGroupId'
_R='SecurityGroups'
_Q='delete'
_P='PublicIp'
_O='SourceSecurityGroupName'
_N='ServiceName'
_M='SubnetId'
_L='RouteTableId'
_K='create'
_J='GroupId'
_I='GroupName'
_H='ToPort'
_G='FromPort'
_F='parameters'
_E='ec2'
_D='function'
_C='VpcId'
_B='IpProtocol'
_A=None
from typing import Tuple
from localstack.services.cloudformation.deployment_utils import param_json_to_str
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone,select_attributes
from localstack_ext.services.cloudformation.service_models import LOG
class EC2VPCEndpoint(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::EC2::VPCEndpoint'
	def fetch_state(B,stack_name,resources):D='Values';C='Name';E=aws_stack.connect_to_service(_E);A=E.describe_vpc_endpoints(Filters=[{C:'service-name',D:[B.props[_N]]},{C:'vpc-id',D:[B.props[_C]]}]);A=A['VpcEndpoints'];return(A or[_A])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get('VpcEndpointId')
	@staticmethod
	def get_deploy_templates():F='PrivateDnsEnabled';E='VpcEndpointType';D='RouteTableIds';C='SubnetIds';B='SecurityGroupIds';A='PolicyDocument';return{_K:{_D:'create_vpc_endpoint',_F:{_N:_N,A:param_json_to_str(A),_C:_C,B:B,C:C,D:D,E:E,F:F}}}
class EC2ElasticIP(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::EC2::EIP'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_P)
	def fetch_state(A,stack_name,resources):
		if A.get_physical_resource_id():return A.state
	@classmethod
	def get_deploy_templates(E):
		def A(resource_id,resources,resource_type,func,stack_name,*G,**C):B=resources;A=E(B[resource_id]);A.fetch_and_update_state(stack_name,B);F=aws_stack.connect_to_service(_E);C=select_attributes(A.props,['Domain','PublicIpv4Pool']);D=F.allocate_address(**C);A.state.update(D);return D
		return{_K:{_D:A},_Q:{_D:'release_address',_F:[_P,'AllocationId']}}
class SubnetRouteTableAssociation(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::EC2::SubnetRouteTableAssociation'
	def get_physical_resource_id(A,attribute,**B):return A.props.get('RouteTableAssociationId')
	def fetch_state(B,stack_name,resources):
		D=resources;C=stack_name;G=aws_stack.connect_to_service(_E);E=B.props;F=B.resolve_refs_recursively(C,E[_L],D);H=B.resolve_refs_recursively(C,E[_M],D);A=G.describe_route_tables(RouteTableIds=[F])['RouteTables'];A=[B for B in A if B[_L]==F]
		if A:I=A[0].get('Associations',[]);J=[A for A in I if A.get(_M)==H];return(J or[_A])[0]
	@staticmethod
	def get_deploy_templates():return{_K:{_D:'associate_route_table',_F:{_L:_L,_M:_M}},_Q:{_D:'disassociate_route_table',_F:{'AssociationId':'PhysicalResourceId'}}}
class SecurityGroupInOrEgress(GenericBaseModel):
	def get_physical_resource_id(B,attribute,**D):
		if attribute in REF_ID_ATTRS:A=B.props;C='%s_%s_%s'%(A.get(_B),A.get(_G),A.get(_H));return C
	def fetch_state(C,stack_name,resources):
		F=aws_stack.connect_to_service(_E);A=C.props;G={'GroupNames':[A.get(_I)]}if A.get(_I)else{'GroupIds':[A[_J]]};E=F.describe_security_groups(**G)[_R];H=A.get(_O);I=A.get(_S);J=A.get(_T)
		if not E:return
		K=E[0].get(_U if C.is_ingress()else'IpPermissionsEgress')
		for B in K:
			if str(B[_B])!=str(A[_B]):continue
			if B.get(_G)!=A.get(_G)or B.get(_H)!=A.get(_H):continue
			if not C.is_ingress():return B
			D=B.get(_V,[]);D=[A for A in D if A.get(_J)in[I,J]or A.get(_I)==H]
			if D:return B
	@classmethod
	def is_ingress(A):return'Ingress'in A.cloudformation_type()
	@classmethod
	def get_vpc_and_name_for_security_group(E,group_id):B=aws_stack.connect_to_service(_E);A=B.describe_security_groups(GroupIds=[group_id])[_R];C=A and A[0].get(_C)or _A;D=A and A[0][_I]or _A;return C,D
	@classmethod
	def get_deploy_templates(B):
		def A(params,**S):
			O='CidrIp';N='CidrIpv6';L=params;G='Description';A=clone(L);M=A.get(_O);H=A.pop(_S,_A);D=_A
			if B.is_ingress()and H and not M:D,P=B.get_vpc_and_name_for_security_group(H);A[_O]=P
			C=A.pop(_T,_A)
			if B.is_ingress()and not C:
				C=A.get(_J)
				if C and not D:D,T=B.get_vpc_and_name_for_security_group(C)
			if not B.is_ingress()and not C:LOG.info('TODO: Add support for DestinationPrefixListId for %s'%B.cloudformation_type())
			if A.get(_B):A[_B]=str(A.get(_B))
			E=A.pop(G,_A);I=A.pop(N,_A)
			if I or D:
				F=A.get(O);F=F or('127.0.0.1/32'if E else F);Q={N:I,G:E};R={O:F,G:E};J=[]
				if H:J.append({_J:H,_I:M,G:E,_C:D})
				if C:J.append({_J:C,G:E,_C:D})
				K={_B:A.get(_B),_V:J,_G:A.get(_G),_H:A.get(_H)};K['IpRanges']=F and[R];K['Ipv6Ranges']=I and[Q];A[_U]=[K]
			else:LOG.debug('Neither "VpcId" nor "CidrIpv6" found in CF params: %s'%L)
			return A
		C='authorize_security_group_ingress'if B.is_ingress()else'authorize_security_group_egress';return{_K:{_D:C,_F:A}}
class SecurityGroupEgress(SecurityGroupInOrEgress):
	@staticmethod
	def cloudformation_type():return'AWS::EC2::SecurityGroupEgress'
class SecurityGroupIngress(SecurityGroupInOrEgress):
	@staticmethod
	def cloudformation_type():return'AWS::EC2::SecurityGroupIngress'