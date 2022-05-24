_M='LoadBalancerName'
_L='LoadBalancers'
_K='ListenerArn'
_J='Protocol'
_I='TargetGroupArn'
_H='parameters'
_G='create'
_F=None
_E='LoadBalancerArn'
_D='Name'
_C='function'
_B='Port'
_A='elbv2'
from localstack import config
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import clone,items_equivalent
from localstack_ext import config as ext_config
from localstack_ext.services.cloudformation.service_models import LOG
class ELBV2TargetGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElasticLoadBalancingV2::TargetGroup'
	def get_physical_resource_id(A,attribute=_F,**B):return A.props.get(_I)
	def fetch_state(B,stack_name,resources):C=aws_stack.connect_to_service(_A);D=B.resolve_refs_recursively(stack_name,B.props.get(_D),resources);A=C.describe_target_groups()['TargetGroups'];A=[B for B in A if B.get('TargetGroupName')==D];return(A or[_F])[0]
	@classmethod
	def get_deploy_templates(B):
		def A(resource_id,resources,resource_type,func,stack_name,*H,**I):
			A=resources;C=B(A[resource_id]);C.fetch_and_update_state(stack_name,A);D=C.props;E=D.get('Targets')
			if E:F=aws_stack.connect_to_service(_A);G=D.get(_I);F.register_targets(TargetGroupArn=G,Targets=E)
		def C(resource_id,resources,*I,**J):
			E='Value';F=B(resources[resource_id]);C=F.props;A=C.get('TargetGroupAttributes')
			if A:
				G=aws_stack.connect_to_service(_A);H=C.get(_I)
				for D in A:D[E]=str(D.get(E,''))
				G.modify_target_group_attributes(TargetGroupArn=H,Attributes=A)
		D=[_D,_J,'ProtocolVersion',_B,'VpcId','HealthCheckProtocol','HealthCheckPort','HealthCheckEnabled','HealthCheckPath','HealthCheckIntervalSeconds','HealthCheckTimeoutSeconds','HealthyThresholdCount','UnhealthyThresholdCount','Matcher','TargetType','Tags'];return{_G:[{_C:'create_target_group',_H:D},{_C:A},{_C:C}]}
class ELBV2ListenerRule(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElasticLoadBalancingV2::ListenerRule'
	def get_physical_resource_id(A,attribute,**B):return A.props.get('RuleArn')
	def fetch_state(D,stack_name,resources):
		F='Conditions';E='Actions';B=False
		def G(rule):
			def A(action,_action):
				E='AuthenticateCognitoConfig';D=_action;C=action;F=C.get(E,{})
				for A in ['Type','Order']:
					if C.get(A)!=D.get(A):return B
				G=D.get(E,{})
				for A in ['UserPoolArn','UserPoolClientId','UserPoolDomain']:
					if F.get(A)!=G.get(A):return B
				return True
			C=rule.get(E,[]);return items_equivalent(K,C,A)
		def H(rule):
			def A(cond,_cond):
				F='Values';E='Field';C=cond;A=_cond;G=([C.get(A)for A in D if C.get(A)]+[C])[0]
				if C.get(E)!=A.get(E):return B
				for H in D:A=A.get(H)or A
				I=G.get(F,[])
				if I!=A.get(F):return B
				return True
			C=rule.get(F,[]);D=['HostHeaderConfig','HttpHeaderConfig','HttpRequestMethodConfig','PathPatternConfig','QueryStringConfig','SourceIpConfig'];return items_equivalent(J,C,A)
		I=aws_stack.connect_to_service(_A);A=D.props;J=A.get(F,[]);K=A.get(E,[]);L=D.resolve_refs_recursively(stack_name,A.get(_K),resources);C=I.describe_rules(ListenerArn=L)['Rules'];C=[A for A in C if G(A)and H(A)];return(C or[_F])[0]
	@staticmethod
	def get_deploy_templates():return{_G:{_C:'create_rule'}}
class ELBV2Listener(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElasticLoadBalancingV2::Listener'
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_K)
	def fetch_state(A,stack_name,resources):
		D=resources;C=stack_name;H=aws_stack.connect_to_service(_A);B=A.props;F=A.resolve_refs_recursively(C,B.get(_E),D);I=A.resolve_refs_recursively(C,B.get(_J),D);J=A.resolve_refs_recursively(C,B.get(_B),D);E=H.describe_listeners(LoadBalancerArn=F)['Listeners'];K=[str(config.EDGE_PORT),str(config.EDGE_PORT_HTTP)];G=[A for A in E if A.get(_E)==F and(str(J or'')in[str(A.get(_B)),'']or str(A.get(_B))in K)and A.get(_J)==I]
		if E and not G:LOG.debug('No matching entry when filtering ELBv2 listeners %s for props %s'%(E,B))
		return(G or[_F])[0]
	@staticmethod
	def get_deploy_templates():
		def A(params,**E):
			C='StatusCode';B=clone(params)
			for D in B.get('DefaultActions',[]):A=D.get('RedirectConfig',{});A[C]=A.get(C)or'HTTP_301';A[_B]=A.get(_B)and str(A[_B])
			return B
		return{_G:{_C:'create_listener',_H:A}}
class ELBV2LoadBalancer(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::ElasticLoadBalancingV2::LoadBalancer'
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_E)
	def fetch_state(C,stack_name,resources):A=C.props.get(_D);A=C.resolve_refs_recursively(stack_name,A,resources);D=aws_stack.connect_to_service(_A);B=D.describe_load_balancers()[_L];B=[C for C in B if C[_M]==A];return(B or[_F])[0]
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B=='DNSName':C=A.props.get(_E);return'%s.elb.%s'%(C.split('/')[2],ext_config.RESOURCES_BASE_DOMAIN_NAME)
		return super(ELBV2LoadBalancer,A).get_cfn_attribute(B)
	@staticmethod
	def get_deploy_templates():
		C='resource_id';B='LoadBalancerAttributes'
		def A(params,**D):A=clone(params);A.pop(B,[]);A[_D]=A.get(_D)or D.get(C);return A
		def D(params,**F):D=params;E=D.get(_D)or F.get(C);A=aws_stack.connect_to_service(_A).describe_load_balancers()[_L];A=[B for B in A if B[_M]==E];A={_E:A and A[0][_E]or E,'Attributes':D.get(B,[])};return A
		return{_G:[{_C:'create_load_balancer',_H:A},{_C:'modify_load_balancer_attributes',_H:D}]}