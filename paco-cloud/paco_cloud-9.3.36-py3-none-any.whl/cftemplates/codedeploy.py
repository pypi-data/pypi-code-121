from paco.cftemplates.cftemplates import StackTemplate
from paco.models import registry


class CodeDeploy(StackTemplate):
    def __init__(
        self,
        stack,
        paco_ctx,
        base_aws_name,
        app_name,
        action_config,
        artifacts_bucket_name
    ):
        pipeline_config = stack.resource
        cpbd_config_ref = action_config.paco_ref_parts
        super().__init__(stack, paco_ctx, iam_capabilities=["CAPABILITY_NAMED_IAM"])
        self.set_aws_name('CodeDeploy', self.resource_group_name, self.resource.name)
        self.res_name_prefix = self.create_resource_name_join(
            name_list=[base_aws_name, app_name, self.resource_group_name, self.resource.name],
            separator='-',
            camel_case=True
        )
        if not action_config.is_enabled():
            self.init_template('Code Deploy')
            self.set_template(self.template.to_yaml())
            return

        self.codedeploy_tools_delegate_role_name = self.get_tools_delegate_role_name()
        self.codedeploy_service_role_name = self.get_role_name()
        self.application_name = self.res_name_prefix

        # Initialize Parameters
        self.set_parameter('ResourceNamePrefix', self.res_name_prefix)
        self.set_parameter('ApplicationName', self.application_name)

        # Service Hook Configuration
        if action_config.paco_service_hook != None and registry.CODEPIPELINE_CODEDEPLOY_CF_TEMPLATE_HOOK != None:
          registry.CODEPIPELINE_CODEDEPLOY_CF_TEMPLATE_HOOK(self, action_config)
        else:
          # Default Paco Configuration
          self.set_parameter('CodeDeployASGName', action_config.auto_scaling_group+'.name')
          self.set_parameter('CodeDeployStyleOption', action_config.deploy_style_option)
          self.set_parameter('CodeDeployDeploymentType', 'IN_PLACE')
          self.set_parameter('CodeDeployConfigType', action_config.minimum_healthy_hosts.type)
          self.set_parameter('CodeDeployConfigValue', action_config.minimum_healthy_hosts.value)
          self.set_parameter('BlueTargetInstanceRoleName', action_config.auto_scaling_group+'.instance_iam_role.name')

        # Universal Configuration
        self.set_parameter('ELBName', action_config.elb_name)
        if action_config.alb_target_group == None:
            alb_target_group_name = ""
        else:
            alb_target_group_name = action_config.alb_target_group+'.name'
        self.set_parameter('ALBTargetGroupName', alb_target_group_name)
        self.set_parameter('ArtifactsBucketName', artifacts_bucket_name)
        self.set_parameter('CodeDeployAutoRollbackEnabled', action_config.auto_rollback_enabled)
        if pipeline_config.configuration.account == None:
          account_id_ref = f'paco.ref accounts.{self.account_ctx.get_name()}'
        else:
          account_id_ref = pipeline_config.configuration.account
        self.set_parameter('PipelineAccountId', account_id_ref + '.id')
        deploy_kms_ref = pipeline_config.paco_ref + '.kms.arn'
        self.set_parameter('CMKArn', deploy_kms_ref)

        # Load Balancer
        load_balancer_info_yaml = ""
        if action_config.elb_name != None and action_config.elb_name != '':
          load_balancer_info_yaml = """
      LoadBalancerInfo:
        ElbInfoList:
          - Name: !Ref ELBName
"""
        # Deployment Style
        deployment_style_yaml = ""
        if action_config.paco_service_hook == None or action_config.paco_service_hook.config['type'] == 'Deploy.AMI_BUILDER':
          deployment_style_yaml = f"""
      DeploymentStyle:
        DeploymentOption: !Ref CodeDeployStyleOption
        DeploymentType: !Ref CodeDeployDeploymentType
      {load_balancer_info_yaml}
        TargetGroupInfoList:
          !If
            - ALBTargetGroupNameIsEmpty
            - !Ref AWS::NoValue
            - - Name: !Ref ALBTargetGroupName
"""
        blue_green_deploy_config_yaml = ""
        # TODO: Move this into an override hook
        if action_config.paco_service_hook != None and action_config.paco_service_hook.config['type'] == 'Deploy.BLUE_GREEN':
          blue_green_deploy_config_yaml = """
      BlueGreenDeploymentConfiguration:
        DeploymentReadyOption:
          ActionOnTimeout: CONTINUE_DEPLOYMENT
        GreenFleetProvisioningOption:
          Action: DISCOVER_EXISTING
        TerminateBlueInstancesOnDeploymentSuccess:
          Action: TERMINATE
          TerminationWaitTimeInMinutes: 300
"""


        # Define the Template
        template_yaml = f"""
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Code Deploy'

Parameters:

  ResourceNamePrefix:
    Description: The name to prefix to AWS resources
    Type: String

  ApplicationName:
    Description: The name of the CodeDeploy Application
    Type: String

  ArtifactsBucketName:
    Description: The bname of the S3 Bucket to create that will hold deployment artifacts
    Type: String

  CodeDeployASGName:
    Description: The name of the AutoScaling Group of the deployment workload
    Type: String
    Default: ""

  CodeDeployDeploymentType:
    Description: The Type of Deployment IN_PLACE or BLUE_GREEN
    Type: String
    Default: ""

  CodeDeployAutoRollbackEnabled:
    Description: Boolean indicating whether CodeDeploy will rollback a deployment if an error is encountered
    Type: String
    AllowedValues:
      - true
      - false

  CodeDeployConfigType:
    Description: The minimum healthy instance type HOST_COUNT or FLEET_PERCENT
    Type: String
    AllowedValues:
      - HOST_COUNT
      - FLEET_PERCENT

  CodeDeployStyleOption:
    Description: Either WITH_TRAFFIC_CONTROL or WITHOUT_TRAFFIC_CONTROL
    Type: String
    Default: ""

  CodeDeployConfigValue:
    Description: The minimum number or percent of healthy hosts relevant to the chosen ConfigType
    Type: String

  ELBName:
    Description: The name of the ELB that will be managed by CodeDeploy during deployment
    Type: String

  ALBTargetGroupName:
    Description: The name of the target group that will be managed by CodeDeploy during deployment
    Type: String

  PipelineAccountId:
    Description: The AWS Account ID of the CodePipeline
    Type: String

  CMKArn:
    Description: The KMS CMK Arn of the key used to encrypt deployment artifacts
    Type: String

  BlueTargetInstanceRoleName:
    Description: The ARN of the Role attached to the ASG CodeDeploy deploys to
    Type: String

  GreenTargetInstanceRoleName:
    Description: The ARN of the Role attached to the Green ASG CodeDeploy deploys to
    Type: String
    Default: ""

Conditions:
  ELBNameIsEmpty: !Equals [!Ref ELBName, ""]
  ALBTargetGroupNameIsEmpty: !Equals [!Ref ALBTargetGroupName, ""]
  GreenTargetInstanceRoleNameIsEmpty: !Equals [!Ref GreenTargetInstanceRoleName, ""]
  CodeDeployASGNameIsEmpty: !Equals [!Ref CodeDeployASGName, ""]
  CodeDeployStyleOptionIsEmpty: !Equals [!Ref CodeDeployStyleOption, ""]

Resources:

# ----------------------------------------------------------------------------
# CodeDeploy

  ToolsDelegateRole:
    Type: AWS::IAM::Role
    DependsOn:
      - CodeDeployGroup
      - CodeDeployConfiguration
      - CodeDeployApplication
    Properties:
      RoleName: {self.codedeploy_tools_delegate_role_name}
      AssumeRolePolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Principal:
              AWS:
                - !Ref PipelineAccountId
            Action:
              - sts:AssumeRole
      Path: /
      Policies:
        - PolicyName: CodeDeploy
          PolicyDocument:
            Version: 2012-10-17
            Statement:
              - Effect: Allow
                Action:
                  - 'codedeploy:CreateDeployment'
                  - 'codedeploy:GetDeployment'
                  - 'codedeploy:GetDeploymentConfig'
                  - 'codedeploy:GetApplicationRevision'
                  - 'codedeploy:RegisterApplicationRevision'
                Resource:
                  - !Sub 'arn:aws:codedeploy:${{AWS::Region}}:${{AWS::AccountId}}:deploymentgroup:${{CodeDeployApplication}}/${{CodeDeployGroup}}'
                  - !Sub 'arn:aws:codedeploy:${{AWS::Region}}:${{AWS::AccountId}}:application:${{CodeDeployApplication}}'
                  - !Sub 'arn:aws:codedeploy:${{AWS::Region}}:${{AWS::AccountId}}:deploymentconfig:${{CodeDeployConfiguration}}'
              - Sid: KMSCMK
                Effect: Allow
                Action:
                  - 'kms:DescribeKey'
                  - 'kms:GenerateDataKey*'
                  - 'kms:Encrypt'
                  - 'kms:ReEncrypt*'
                  - 'kms:Decrypt'
                Resource: !Ref CMKArn
              - Sid: S3ArtifactsBucket
                Effect: Allow
                Action:
                  - 's3:GetObject*'
                  - 's3:PutObject'
                  - 's3:PutObjectAcl'
                Resource:
                  - !Sub 'arn:aws:s3:::${{ArtifactsBucketName}}/*'
                  - !Sub 'arn:aws:s3:::${{ArtifactsBucketName}}'

  CodeDeployServiceRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: {self.codedeploy_service_role_name}
      AssumeRolePolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - codedeploy.amazonaws.com
            Action:
              - sts:AssumeRole
      Path: /

  CodeDeployServicePolicy:
    Type: AWS::IAM::Policy
    DependsOn:
      - CodeDeployServiceRole
    Properties:
      PolicyName: CodeDeployService
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - autoscaling:CompleteLifecycleAction
              - autoscaling:DeleteLifecycleHook
              - autoscaling:DescribeAutoScalingGroups
              - autoscaling:DescribeLifecycleHooks
              - autoscaling:PutLifecycleHook
              - autoscaling:RecordLifecycleActionHeartbeat
              - autoscaling:CreateAutoScalingGroup
              - autoscaling:UpdateAutoScalingGroup
              - autoscaling:EnableMetricsCollection
              - autoscaling:DescribeAutoScalingGroups
              - autoscaling:DescribePolicies
              - autoscaling:DescribeScheduledActions
              - autoscaling:DescribeNotificationConfigurations
              - autoscaling:DescribeLifecycleHooks
              - autoscaling:SuspendProcesses
              - autoscaling:ResumeProcesses
              - autoscaling:AttachLoadBalancers
              - autoscaling:PutScalingPolicy
              - autoscaling:PutScheduledUpdateGroupAction
              - autoscaling:PutNotificationConfiguration
              - autoscaling:PutLifecycleHook
              - autoscaling:DescribeScalingActivities
              - autoscaling:DeleteAutoScalingGroup
              - ec2:DescribeInstances
              - ec2:DescribeInstanceStatus
              - ec2:TerminateInstances
              - tag:GetTags
              - tag:GetResources
              - sns:Publish
              - cloudwatch:DescribeAlarms
              - cloudwatch:PutMetricAlarm
              - elasticloadbalancing:DescribeLoadBalancers
              - elasticloadbalancing:DescribeInstanceHealth
              - elasticloadbalancing:RegisterInstancesWithLoadBalancer
              - elasticloadbalancing:DeregisterInstancesFromLoadBalancer
              - elasticloadbalancing:DescribeTargetGroups
              - elasticloadbalancing:DescribeTargetHealth
              - elasticloadbalancing:RegisterTargets
              - elasticloadbalancing:DeregisterTargets
            Resource: "*"
      Roles:
        - !Ref CodeDeployServiceRole

  CodeDeployTargetInstancePolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - 'kms:DescribeKey'
              - 'kms:GenerateDataKey*'
              - 'kms:Encrypt'
              - 'kms:ReEncrypt*'
              - 'kms:Decrypt'
            Resource:
              - !Ref CMKArn
          - Effect: Allow
            Action:
              - 's3:Get*'
            Resource:
              - !Sub 'arn:aws:s3:::${{ArtifactsBucketName}}/*'
              - !Sub 'arn:aws:s3:::aws-codedeploy-${{AWS::Region}}/*'
          - Effect: Allow
            Action:
              - 'autoscaling:DescribeAutoScalingGroups'
              - 'autoscaling:DescribeAutoScalingInstances'
            Resource:
              - '*' # XXX: Secure this
          - Effect: Allow
            Action:
              - 'autoscaling:UpdateAutoScalingGroup'
              - 'autoscaling:EnterStandby'
              - 'autoscaling:ExitStandby'
            Resource:
              - '*' # XXX: Secure this
      Roles:
        - !Ref BlueTargetInstanceRoleName
        - !If
            - GreenTargetInstanceRoleNameIsEmpty
            - !Ref AWS::NoValue
            - !Ref GreenTargetInstanceRoleName

  CodeDeployApplication:
    Type: AWS::CodeDeploy::Application
    Properties:
      ApplicationName: !Ref ApplicationName
      ComputePlatform: Server

  CodeDeployConfiguration:
    Type: AWS::CodeDeploy::DeploymentConfig
    Properties:
      MinimumHealthyHosts:
        Type: !Ref CodeDeployConfigType
        Value: !Ref CodeDeployConfigValue

  CodeDeployGroup:
    Type: AWS::CodeDeploy::DeploymentGroup
    DependsOn:
      - CodeDeployServicePolicy
      - CodeDeployServiceRole
      - CodeDeployApplication
      - CodeDeployConfiguration
    Properties:
      DeploymentGroupName: !Sub '${{ResourceNamePrefix}}-Group'
      ApplicationName: !Ref CodeDeployApplication
      AutoScalingGroups:
        - !If
            - CodeDeployASGNameIsEmpty
            - !Ref AWS::NoValue
            - !Ref CodeDeployASGName
      AutoRollbackConfiguration:
        Enabled: !Ref CodeDeployAutoRollbackEnabled
        Events:
          - DEPLOYMENT_FAILURE
          - DEPLOYMENT_STOP_ON_ALARM
          - DEPLOYMENT_STOP_ON_REQUEST
      DeploymentConfigName: !Ref CodeDeployConfiguration
      ServiceRoleArn: !GetAtt CodeDeployServiceRole.Arn
      {deployment_style_yaml}
      {blue_green_deploy_config_yaml}

Outputs:
  DeploymentGroupName:
     Value: !Ref CodeDeployGroup

  ApplicationName:
     Value: !Ref CodeDeployApplication

"""

        self.stack.register_stack_output_config(cpbd_config_ref+'.deployment_group.name', 'DeploymentGroupName')
        self.stack.register_stack_output_config(cpbd_config_ref+'.application.name', 'ApplicationName')

        self.set_template(template_yaml)

    def get_role_name(self):
        return self.create_iam_resource_name(
            name_list=[self.res_name_prefix, 'CodeDeploy-Service'],
            filter_id='IAM.Role.RoleName'
        )

    def get_role_arn(self):
        account_id = self.account_ctx.get_id()

        return "arn:aws:iam::{0}:role/{1}".format(
            account_id,
            self.codedeploy_service_role_name
        )

    def get_tools_delegate_role_name(self):
        return self.create_iam_resource_name(
            name_list=[self.res_name_prefix, 'CodeDeploy-Tools-Delegate'],
            filter_id='IAM.Role.RoleName'
        )

    def get_tools_delegate_role_arn(self):
        account_id = self.account_ctx.get_id()
        return "arn:aws:iam::{0}:role/{1}".format(
            account_id,
            self.codedeploy_tools_delegate_role_name
        )

    def get_application_name(self):
        return self.application_name

    def get_deployment_group_name(self):
        return f'{self.application_name}-Group'

