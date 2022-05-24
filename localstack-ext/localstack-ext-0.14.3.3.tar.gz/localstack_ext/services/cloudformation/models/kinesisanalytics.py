_A='ApplicationName'
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
class KinesisAnalyticsApplicationOutput(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::KinesisAnalytics::ApplicationOutput'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ID_ATTRS:
			C=A.props.get(_A);D=A.props.get('Output',{}).get('Name')
			if C and D:return'%s!%s'%(C,D)
		return super(KinesisAnalyticsApplicationOutput,A).get_cfn_attribute(B)
class KinesisAnalyticsApplication(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::KinesisAnalytics::Application'
	def get_cfn_attribute(A,attribute_name):
		B=attribute_name
		if B in REF_ID_ATTRS:
			C=A.props.get(_A)
			if C:return C
		return super(KinesisAnalyticsApplication,A).get_cfn_attribute(B)