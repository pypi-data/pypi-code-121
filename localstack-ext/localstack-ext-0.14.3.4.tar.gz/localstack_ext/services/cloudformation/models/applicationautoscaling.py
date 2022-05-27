_J='delete'
_I='create'
_H='ScalingTargetId'
_G='application-autoscaling'
_F='parameters'
_E='function'
_D='PolicyName'
_C='ScalableDimension'
_B='ResourceId'
_A='ServiceNamespace'
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes
from localstack_ext.services.cloudformation.models.servicediscovery import ServiceDiscoveryNamespace
class ApplicationAutoScalingPolicy(ServiceDiscoveryNamespace):
	@staticmethod
	def cloudformation_type():return'AWS::ApplicationAutoScaling::ScalingPolicy'
	def fetch_state(B,stack_name,resources):
		E=resources;D=stack_name;G=aws_stack.connect_to_service(_G);C=B.props;A=C.get(_A);F=C.get(_H)
		if F:A=F.split('|')[-1]
		H=B.resolve_refs_recursively(D,C[_D],E);A=B.resolve_refs_recursively(D,A,E);I=G.describe_scaling_policies(ServiceNamespace=A)['ScalingPolicies'];J=[A for A in I if A[_D]==H];return(J or[None])[0]
	def get_physical_resource_id(A,attribute,**B):return A.props.get('PolicyARN')
	@classmethod
	def get_deploy_templates(B):
		def A(params,**F):
			C=params;E=_D,_A,_B,_C,'PolicyType','StepScalingPolicyConfiguration','TargetTrackingScalingPolicyConfiguration';A=select_attributes(C,E);D=C.get(_H)
			if D:B=D.split('|');A.setdefault(_B,B[0]);A.setdefault(_C,B[1]);A.setdefault(_A,B[2])
			return A
		return{_I:{_E:'put_scaling_policy',_F:A},_J:{_E:'delete_scaling_policy',_F:[_D,_A,_B,_C]}}
class ApplicationAutoScalingScalableTarget(ServiceDiscoveryNamespace):
	@staticmethod
	def cloudformation_type():return'AWS::ApplicationAutoScaling::ScalableTarget'
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;F=aws_stack.connect_to_service(_G);D=A.props;G=A.resolve_refs_recursively(B,D[_B],C);H=A.resolve_refs_recursively(B,D[_C],C);E=A.resolve_refs_recursively(B,D[_A],C);I=F.describe_scalable_targets(ServiceNamespace=E)['ScalableTargets'];J=[A for A in I if A[_B]==G and A[_C]==H and A[_A]==E];return(J or[None])[0]
	def get_physical_resource_id(B,attribute,**C):
		if not B.state:return
		A=B.props;return'service/%s|%s|%s'%(A[_B],A[_C],A[_A])
	@classmethod
	def get_deploy_templates(A):return{_I:{_E:'register_scalable_target',_F:[_A,_B,_C,'MinCapacity','MaxCapacity','RoleARN','SuspendedState']},_J:{_E:'deregister_scalable_target',_F:[_A,_B,_C]}}