'''
# AWS Batch Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

> All classes with the `Cfn` prefix in this module ([CFN Resources](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) are always stable and safe to use.

![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

AWS Batch is a batch processing tool for efficiently running hundreds of thousands computing jobs in AWS. Batch can dynamically provision different types of compute resources based on the resource requirements of submitted jobs.

AWS Batch simplifies the planning, scheduling, and executions of your batch workloads across a full range of compute services like [Amazon EC2](https://aws.amazon.com/ec2/) and [Spot Resources](https://aws.amazon.com/ec2/spot/).

Batch achieves this by utilizing queue processing of batch job requests. To successfully submit a job for execution, you need the following resources:

1. [Job Definition](#job-definition) - *Group various job properties (container image, resource requirements, env variables...) into a single definition. These definitions are used at job submission time.*
2. [Compute Environment](#compute-environment) - *the execution runtime of submitted batch jobs*
3. [Job Queue](#job-queue) - *the queue where batch jobs can be submitted to via AWS SDK/CLI*

For more information on **AWS Batch** visit the [AWS Docs for Batch](https://docs.aws.amazon.com/batch/index.html).

## Compute Environment

At the core of AWS Batch is the compute environment. All batch jobs are processed within a compute environment, which uses resource like OnDemand/Spot EC2 instances or Fargate.

In **MANAGED** mode, AWS will handle the provisioning of compute resources to accommodate the demand. Otherwise, in **UNMANAGED** mode, you will need to manage the provisioning of those resources.

Below is an example of each available type of compute environment:

```python
# vpc: ec2.Vpc


# default is managed
aws_managed_environment = batch.ComputeEnvironment(self, "AWS-Managed-Compute-Env",
    compute_resources=batch.ComputeResources(
        vpc=vpc
    )
)

customer_managed_environment = batch.ComputeEnvironment(self, "Customer-Managed-Compute-Env",
    managed=False
)
```

### Spot-Based Compute Environment

It is possible to have AWS Batch submit spotfleet requests for obtaining compute resources. Below is an example of how this can be done:

```python
vpc = ec2.Vpc(self, "VPC")

spot_environment = batch.ComputeEnvironment(self, "MySpotEnvironment",
    compute_resources=batch.ComputeResources(
        type=batch.ComputeResourceType.SPOT,
        bid_percentage=75,  # Bids for resources at 75% of the on-demand price
        vpc=vpc
    )
)
```

### Fargate Compute Environment

It is possible to have AWS Batch submit jobs to be run on Fargate compute resources. Below is an example of how this can be done:

```python
vpc = ec2.Vpc(self, "VPC")

fargate_spot_environment = batch.ComputeEnvironment(self, "MyFargateEnvironment",
    compute_resources=batch.ComputeResources(
        type=batch.ComputeResourceType.FARGATE_SPOT,
        vpc=vpc
    )
)
```

### Understanding Progressive Allocation Strategies

AWS Batch uses an [allocation strategy](https://docs.aws.amazon.com/batch/latest/userguide/allocation-strategies.html) to determine what compute resource will efficiently handle incoming job requests. By default, **BEST_FIT** will pick an available compute instance based on vCPU requirements. If none exist, the job will wait until resources become available. However, with this strategy, you may have jobs waiting in the queue unnecessarily despite having more powerful instances available. Below is an example of how that situation might look like:

```plaintext
Compute Environment:

1. m5.xlarge => 4 vCPU
2. m5.2xlarge => 8 vCPU
```

```plaintext
Job Queue:
---------
| A | B |
---------

Job Requirements:
A => 4 vCPU - ALLOCATED TO m5.xlarge
B => 2 vCPU - WAITING
```

In this situation, Batch will allocate **Job A** to compute resource #1 because it is the most cost efficient resource that matches the vCPU requirement. However, with this `BEST_FIT` strategy, **Job B** will not be allocated to our other available compute resource even though it is strong enough to handle it. Instead, it will wait until the first job is finished processing or wait a similar `m5.xlarge` resource to be provisioned.

The alternative would be to use the `BEST_FIT_PROGRESSIVE` strategy in order for the remaining job to be handled in larger containers regardless of vCPU requirement and costs.

### Launch template support

Simply define your Launch Template:

```text
// This example is only available in TypeScript
const myLaunchTemplate = new ec2.CfnLaunchTemplate(this, 'LaunchTemplate', {
  launchTemplateName: 'extra-storage-template',
  launchTemplateData: {
    blockDeviceMappings: [
      {
        deviceName: '/dev/xvdcz',
        ebs: {
          encrypted: true,
          volumeSize: 100,
          volumeType: 'gp2',
        },
      },
    ],
  },
});
```

and use it:

```python
# vpc: ec2.Vpc
# my_launch_template: ec2.CfnLaunchTemplate


my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
    compute_resources=batch.ComputeResources(
        launch_template=batch.LaunchTemplateSpecification(
            launch_template_name=my_launch_template.launch_template_name
        ),
        vpc=vpc
    ),
    compute_environment_name="MyStorageCapableComputeEnvironment"
)
```

### Importing an existing Compute Environment

To import an existing batch compute environment, call `ComputeEnvironment.fromComputeEnvironmentArn()`.

Below is an example:

```python
compute_env = batch.ComputeEnvironment.from_compute_environment_arn(self, "imported-compute-env", "arn:aws:batch:us-east-1:555555555555:compute-environment/My-Compute-Env")
```

### Change the baseline AMI of the compute resources

Occasionally, you will need to deviate from the default processing AMI.

ECS Optimized Amazon Linux 2 example:

```python
# vpc: ec2.Vpc

my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
    compute_resources=batch.ComputeResources(
        image=ecs.EcsOptimizedAmi(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        ),
        vpc=vpc
    )
)
```

Custom based AMI example:

```python
# vpc: ec2.Vpc

my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
    compute_resources=batch.ComputeResources(
        image=ec2.MachineImage.generic_linux({
            "[aws-region]": "[ami-ID]"
        }),
        vpc=vpc
    )
)
```

## Job Queue

Jobs are always submitted to a specific queue. This means that you have to create a queue before you can start submitting jobs. Each queue is mapped to at least one (and no more than three) compute environment. When the job is scheduled for execution, AWS Batch will select the compute environment based on ordinal priority and available capacity in each environment.

```python
# compute_environment: batch.ComputeEnvironment

job_queue = batch.JobQueue(self, "JobQueue",
    compute_environments=[batch.JobQueueComputeEnvironment(
        # Defines a collection of compute resources to handle assigned batch jobs
        compute_environment=compute_environment,
        # Order determines the allocation order for jobs (i.e. Lower means higher preference for job assignment)
        order=1
    )
    ]
)
```

### Priorty-Based Queue Example

Sometimes you might have jobs that are more important than others, and when submitted, should take precedence over the existing jobs. To achieve this, you can create a priority based execution strategy, by assigning each queue its own priority:

```python
# shared_compute_envs: batch.ComputeEnvironment

high_prio_queue = batch.JobQueue(self, "JobQueue",
    compute_environments=[batch.JobQueueComputeEnvironment(
        compute_environment=shared_compute_envs,
        order=1
    )],
    priority=2
)

low_prio_queue = batch.JobQueue(self, "JobQueue",
    compute_environments=[batch.JobQueueComputeEnvironment(
        compute_environment=shared_compute_envs,
        order=1
    )],
    priority=1
)
```

By making sure to use the same compute environments between both job queues, we will give precedence to the `highPrioQueue` for the assigning of jobs to available compute environments.

### Importing an existing Job Queue

To import an existing batch job queue, call `JobQueue.fromJobQueueArn()`.

Below is an example:

```python
job_queue = batch.JobQueue.from_job_queue_arn(self, "imported-job-queue", "arn:aws:batch:us-east-1:555555555555:job-queue/High-Prio-Queue")
```

## Job Definition

A Batch Job definition helps AWS Batch understand important details about how to run your application in the scope of a Batch Job. This involves key information like resource requirements, what containers to run, how the compute environment should be prepared, and more. Below is a simple example of how to create a job definition:

```python
import aws_cdk.aws_ecr as ecr


repo = ecr.Repository.from_repository_name(self, "batch-job-repo", "todo-list")

batch.JobDefinition(self, "batch-job-def-from-ecr",
    container=batch.JobDefinitionContainer(
        image=ecs.EcrImage(repo, "latest")
    )
)
```

### Using a local Docker project

Below is an example of how you can create a Batch Job Definition from a local Docker application.

```python
batch.JobDefinition(self, "batch-job-def-from-local",
    container=batch.JobDefinitionContainer(
        # todo-list is a directory containing a Dockerfile to build the application
        image=ecs.ContainerImage.from_asset("../todo-list")
    )
)
```

### Providing custom log configuration

You can provide custom log driver and its configuration for the container.

```python
import aws_cdk.aws_ssm as ssm


batch.JobDefinition(self, "job-def",
    container=batch.JobDefinitionContainer(
        image=ecs.EcrImage.from_registry("docker/whalesay"),
        log_configuration=batch.LogConfiguration(
            log_driver=batch.LogDriver.AWSLOGS,
            options={"awslogs-region": "us-east-1"},
            secret_options=[
                batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
            ]
        )
    )
)
```

### Importing an existing Job Definition

#### From ARN

To import an existing batch job definition from its ARN, call `JobDefinition.fromJobDefinitionArn()`.

Below is an example:

```python
job = batch.JobDefinition.from_job_definition_arn(self, "imported-job-definition", "arn:aws:batch:us-east-1:555555555555:job-definition/my-job-definition")
```

#### From Name

To import an existing batch job definition from its name, call `JobDefinition.fromJobDefinitionName()`.
If name is specified without a revision then the latest active revision is used.

Below is an example:

```python
# Without revision
job1 = batch.JobDefinition.from_job_definition_name(self, "imported-job-definition", "my-job-definition")

# With revision
job2 = batch.JobDefinition.from_job_definition_name(self, "imported-job-definition", "my-job-definition:3")
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_iam
import aws_cdk.aws_secretsmanager
import aws_cdk.aws_ssm
import aws_cdk.core
import constructs


@jsii.enum(jsii_type="@aws-cdk/aws-batch.AllocationStrategy")
class AllocationStrategy(enum.Enum):
    '''(experimental) Properties for how to prepare compute resources that are provisioned for a compute environment.

    :stability: experimental
    '''

    BEST_FIT = "BEST_FIT"
    '''(experimental) Batch will use the best fitting instance type will be used when assigning a batch job in this compute environment.

    :stability: experimental
    '''
    BEST_FIT_PROGRESSIVE = "BEST_FIT_PROGRESSIVE"
    '''(experimental) Batch will select additional instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types with a lower cost per unit vCPU.

    :stability: experimental
    '''
    SPOT_CAPACITY_OPTIMIZED = "SPOT_CAPACITY_OPTIMIZED"
    '''(experimental) This is only available for Spot Instance compute resources and will select additional instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types that are less likely to be interrupted.

    :stability: experimental
    '''


@jsii.implements(aws_cdk.core.IInspectable)
class CfnComputeEnvironment(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment",
):
    '''A CloudFormation ``AWS::Batch::ComputeEnvironment``.

    The ``AWS::Batch::ComputeEnvironment`` resource defines your AWS Batch compute environment. You can define ``MANAGED`` or ``UNMANAGED`` compute environments. ``MANAGED`` compute environments can use Amazon EC2 or AWS Fargate resources. ``UNMANAGED`` compute environments can only use EC2 resources. For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the ** .

    In a managed compute environment, AWS Batch manages the capacity and instance types of the compute resources within the environment. This is based on the compute resource specification that you define or the `launch template <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html>`_ that you specify when you create the compute environment. You can choose either to use EC2 On-Demand Instances and EC2 Spot Instances, or to use Fargate and Fargate Spot capacity in your managed compute environment. You can optionally set a maximum price so that Spot Instances only launch when the Spot Instance price is below a specified percentage of the On-Demand price.
    .. epigraph::

       Multi-node parallel jobs are not supported on Spot Instances.

    In an unmanaged compute environment, you can manage your own EC2 compute resources and have a lot of flexibility with how you configure your compute resources. For example, you can use custom AMI. However, you need to verify that your AMI meets the Amazon ECS container instance AMI specification. For more information, see `container instance AMIs <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container_instance_AMIs.html>`_ in the *Amazon Elastic Container Service Developer Guide* . After you have created your unmanaged compute environment, you can use the `DescribeComputeEnvironments <https://docs.aws.amazon.com/batch/latest/APIReference/API_DescribeComputeEnvironments.html>`_ operation to find the Amazon ECS cluster that is associated with it. Then, manually launch your container instances into that Amazon ECS cluster. For more information, see `Launching an Amazon ECS container instance <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_container_instance.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
    .. epigraph::

       AWS Batch doesn't upgrade the AMIs in a compute environment after it's created except under specific conditions. For example, it doesn't automatically update the AMIs when a newer version of the Amazon ECS optimized AMI is available. Therefore, you're responsible for the management of the guest operating system (including updates and security patches) and any additional application software or utilities that you install on the compute resources. There are two ways to use a new AMI for your AWS Batch jobs. The original method is to complete these steps:

       - Create a new compute environment with the new AMI.
       - Add the compute environment to an existing job queue.
       - Remove the earlier compute environment from your job queue.
       - Delete the earlier compute environment.

       In April 2022, AWS Batch added enhanced support for updating compute environments. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . To use the enhanced updating of compute environments to update AMIs, follow these rules:

       - Either do not set the `ServiceRole <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole>`_ property or set it to the *AWSServiceRoleForBatch* service-linked role.
       - Set the `AllocationStrategy <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-allocationstrategy>`_ property to ``BEST_FIT_PROGRESSIVE`` or ``SPOT_CAPACITY_OPTIMIZED`` .
       - Set the `ReplaceComputeEnvironment <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-replacecomputeenvironment>`_ property to ``false`` .
       - Set the `UpdateToLatestImageVersion <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-updatetolatestimageversion>`_ property to ``true`` .
       - Either do not specify an image ID in `ImageId <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid>`_ or `ImageIdOverride <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-ec2configurationobject.html#cfn-batch-computeenvironment-ec2configurationobject-imageidoverride>`_ properties, or in the launch template identified by the `Launch Template <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate>`_ property. In that case AWS Batch will select the latest Amazon ECS optimized AMI supported by AWS Batch at the time the infrastructure update is initiated. Alternatively you can specify the AMI ID in the ``ImageId`` or ``ImageIdOverride`` properties, or the launch template identified by the ``LaunchTemplate`` properties. Changing any of these properties will trigger an infrastructure update.

       If these rules are followed, any update that triggers an infrastructure update will cause the AMI ID to be re-selected. If the `Version <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-version>`_ property of the `LaunchTemplateSpecification <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html>`_ is set to ``$Latest`` or ``$Default`` , the latest or default version of the launch template will be evaluated up at the time of the infrastructure update, even if the ``LaunchTemplateSpecification`` was not updated.

    :cloudformationResource: AWS::Batch::ComputeEnvironment
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_batch as batch
        
        cfn_compute_environment = batch.CfnComputeEnvironment(self, "MyCfnComputeEnvironment",
            type="type",
        
            # the properties below are optional
            compute_environment_name="computeEnvironmentName",
            compute_resources=batch.CfnComputeEnvironment.ComputeResourcesProperty(
                maxv_cpus=123,
                subnets=["subnets"],
                type="type",
        
                # the properties below are optional
                allocation_strategy="allocationStrategy",
                bid_percentage=123,
                desiredv_cpus=123,
                ec2_configuration=[batch.CfnComputeEnvironment.Ec2ConfigurationObjectProperty(
                    image_type="imageType",
        
                    # the properties below are optional
                    image_id_override="imageIdOverride"
                )],
                ec2_key_pair="ec2KeyPair",
                image_id="imageId",
                instance_role="instanceRole",
                instance_types=["instanceTypes"],
                launch_template=batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty(
                    launch_template_id="launchTemplateId",
                    launch_template_name="launchTemplateName",
                    version="version"
                ),
                minv_cpus=123,
                placement_group="placementGroup",
                security_group_ids=["securityGroupIds"],
                spot_iam_fleet_role="spotIamFleetRole",
                tags={
                    "tags_key": "tags"
                },
                update_to_latest_image_version=False
            ),
            replace_compute_environment=False,
            service_role="serviceRole",
            state="state",
            tags={
                "tags_key": "tags"
            },
            unmanagedv_cpus=123,
            update_policy=batch.CfnComputeEnvironment.UpdatePolicyProperty(
                job_execution_timeout_minutes=123,
                terminate_jobs_on_update=False
            )
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        type: builtins.str,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional[typing.Union["CfnComputeEnvironment.ComputeResourcesProperty", aws_cdk.core.IResolvable]] = None,
        replace_compute_environment: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        service_role: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        unmanagedv_cpus: typing.Optional[jsii.Number] = None,
        update_policy: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.UpdatePolicyProperty"]] = None,
    ) -> None:
        '''Create a new ``AWS::Batch::ComputeEnvironment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param type: The type of the compute environment: ``MANAGED`` or ``UNMANAGED`` . For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the *AWS Batch User Guide* .
        :param compute_environment_name: The name for your compute environment. It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).
        :param compute_resources: The ComputeResources property type specifies details of the compute resources managed by the compute environment. This parameter is required for managed compute environments. For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the ** .
        :param replace_compute_environment: Specifies whether the compute environment should be replaced if an update is made that requires replacing the instances in the compute environment. The default value is ``true`` . To enable more properties to be updated, set this property to ``false`` . When changing the value of this property to ``false`` , no other properties should be changed at the same time. If other properties are changed at the same time, and the change needs to be rolled back but it can't, it's possible for the stack to go into the ``UPDATE_ROLLBACK_FAILED`` state. You can't update a stack that is in the ``UPDATE_ROLLBACK_FAILED`` state. However, if you can continue to roll it back, you can return the stack to its original settings and then try to update it again. For more information, see `Continue rolling back an update <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-continueupdaterollback.html>`_ in the *AWS CloudFormation User Guide* . The properties that can't be changed without replacing the compute environment are in the ```ComputeResources`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html>`_ property type: ```AllocationStrategy`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-allocationstrategy>`_ , ```BidPercentage`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage>`_ , ```Ec2Configuration`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2configuration>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```ImageId`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid>`_ , ```InstanceRole`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole>`_ , ```InstanceTypes`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes>`_ , ```LaunchTemplate`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate>`_ , ```MaxvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus>`_ , ```MinvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus>`_ , ```PlacementGroup`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup>`_ , ```SecurityGroupIds`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids>`_ , ```Subnets`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets>`_ , `Tags <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags>`_ , ```Type`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type>`_ , and ```UpdateToLatestImageVersion`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-updatetolatestimageversion>`_ .
        :param service_role: The full Amazon Resource Name (ARN) of the IAM role that allows AWS Batch to make calls to other AWS services on your behalf. For more information, see `AWS Batch service IAM role <https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html>`_ in the *AWS Batch User Guide* . .. epigraph:: If your account already created the AWS Batch service-linked role, that role is used by default for your compute environment unless you specify a different role here. If the AWS Batch service-linked role doesn't exist in your account, and no role is specified here, the service attempts to create the AWS Batch service-linked role in your account. If your specified role has a path other than ``/`` , then you must specify either the full role ARN (recommended) or prefix the role name with the path. For example, if a role with the name ``bar`` has a path of ``/foo/`` then you would specify ``/foo/bar`` as the role name. For more information, see `Friendly names and paths <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-friendly-names>`_ in the *IAM User Guide* . .. epigraph:: Depending on how you created your AWS Batch service role, its ARN might contain the ``service-role`` path prefix. When you only specify the name of the service role, AWS Batch assumes that your ARN doesn't use the ``service-role`` path prefix. Because of this, we recommend that you specify the full ARN of your service role when you create compute environments.
        :param state: The state of the compute environment. If the state is ``ENABLED`` , then the compute environment accepts jobs from a queue and can scale out automatically based on queues. If the state is ``ENABLED`` , then the AWS Batch scheduler can attempt to place jobs from an associated job queue on the compute resources within the environment. If the compute environment is managed, then it can scale its instances out or in automatically, based on the job queue demand. If the state is ``DISABLED`` , then the AWS Batch scheduler doesn't attempt to place jobs within the environment. Jobs in a ``STARTING`` or ``RUNNING`` state continue to progress normally. Managed compute environments in the ``DISABLED`` state don't scale out. However, they scale in to ``minvCpus`` value after instances become idle.
        :param tags: The tags applied to the compute environment.
        :param unmanagedv_cpus: The maximum number of vCPUs for an unmanaged compute environment. This parameter is only used for fair share scheduling to reserve vCPU capacity for new share identifiers. If this parameter isn't provided for a fair share job queue, no vCPU capacity is reserved. .. epigraph:: This parameter is only supported when the ``type`` parameter is set to ``UNMANAGED`` .
        :param update_policy: Specifies the infrastructure update policy for the compute environment. For more information about infrastructure updates, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
        '''
        props = CfnComputeEnvironmentProps(
            type=type,
            compute_environment_name=compute_environment_name,
            compute_resources=compute_resources,
            replace_compute_environment=replace_compute_environment,
            service_role=service_role,
            state=state,
            tags=tags,
            unmanagedv_cpus=unmanagedv_cpus,
            update_policy=update_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrComputeEnvironmentArn")
    def attr_compute_environment_arn(self) -> builtins.str:
        '''Returns the compute environment ARN, such as ``batch: *us-east-1* : *111122223333* :compute-environment/ *ComputeEnvironmentName*`` .

        :cloudformationAttribute: ComputeEnvironmentArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrComputeEnvironmentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''The tags applied to the compute environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of the compute environment: ``MANAGED`` or ``UNMANAGED`` .

        For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-type
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> typing.Optional[builtins.str]:
        '''The name for your compute environment.

        It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeenvironmentname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeEnvironmentName"))

    @compute_environment_name.setter
    def compute_environment_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "computeEnvironmentName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeResources")
    def compute_resources(
        self,
    ) -> typing.Optional[typing.Union["CfnComputeEnvironment.ComputeResourcesProperty", aws_cdk.core.IResolvable]]:
        '''The ComputeResources property type specifies details of the compute resources managed by the compute environment.

        This parameter is required for managed compute environments. For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the ** .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
        '''
        return typing.cast(typing.Optional[typing.Union["CfnComputeEnvironment.ComputeResourcesProperty", aws_cdk.core.IResolvable]], jsii.get(self, "computeResources"))

    @compute_resources.setter
    def compute_resources(
        self,
        value: typing.Optional[typing.Union["CfnComputeEnvironment.ComputeResourcesProperty", aws_cdk.core.IResolvable]],
    ) -> None:
        jsii.set(self, "computeResources", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replaceComputeEnvironment")
    def replace_compute_environment(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        '''Specifies whether the compute environment should be replaced if an update is made that requires replacing the instances in the compute environment.

        The default value is ``true`` . To enable more properties to be updated, set this property to ``false`` . When changing the value of this property to ``false`` , no other properties should be changed at the same time. If other properties are changed at the same time, and the change needs to be rolled back but it can't, it's possible for the stack to go into the ``UPDATE_ROLLBACK_FAILED`` state. You can't update a stack that is in the ``UPDATE_ROLLBACK_FAILED`` state. However, if you can continue to roll it back, you can return the stack to its original settings and then try to update it again. For more information, see `Continue rolling back an update <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-continueupdaterollback.html>`_ in the *AWS CloudFormation User Guide* .

        The properties that can't be changed without replacing the compute environment are in the ```ComputeResources`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html>`_ property type: ```AllocationStrategy`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-allocationstrategy>`_ , ```BidPercentage`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage>`_ , ```Ec2Configuration`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2configuration>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```ImageId`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid>`_ , ```InstanceRole`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole>`_ , ```InstanceTypes`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes>`_ , ```LaunchTemplate`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate>`_ , ```MaxvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus>`_ , ```MinvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus>`_ , ```PlacementGroup`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup>`_ , ```SecurityGroupIds`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids>`_ , ```Subnets`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets>`_ , `Tags <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags>`_ , ```Type`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type>`_ , and ```UpdateToLatestImageVersion`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-updatetolatestimageversion>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-replacecomputeenvironment
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], jsii.get(self, "replaceComputeEnvironment"))

    @replace_compute_environment.setter
    def replace_compute_environment(
        self,
        value: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]],
    ) -> None:
        jsii.set(self, "replaceComputeEnvironment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> typing.Optional[builtins.str]:
        '''The full Amazon Resource Name (ARN) of the IAM role that allows AWS Batch to make calls to other AWS services on your behalf.

        For more information, see `AWS Batch service IAM role <https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html>`_ in the *AWS Batch User Guide* .
        .. epigraph::

           If your account already created the AWS Batch service-linked role, that role is used by default for your compute environment unless you specify a different role here. If the AWS Batch service-linked role doesn't exist in your account, and no role is specified here, the service attempts to create the AWS Batch service-linked role in your account.

        If your specified role has a path other than ``/`` , then you must specify either the full role ARN (recommended) or prefix the role name with the path. For example, if a role with the name ``bar`` has a path of ``/foo/`` then you would specify ``/foo/bar`` as the role name. For more information, see `Friendly names and paths <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-friendly-names>`_ in the *IAM User Guide* .
        .. epigraph::

           Depending on how you created your AWS Batch service role, its ARN might contain the ``service-role`` path prefix. When you only specify the name of the service role, AWS Batch assumes that your ARN doesn't use the ``service-role`` path prefix. Because of this, we recommend that you specify the full ARN of your service role when you create compute environments.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "serviceRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[builtins.str]:
        '''The state of the compute environment.

        If the state is ``ENABLED`` , then the compute environment accepts jobs from a queue and can scale out automatically based on queues.

        If the state is ``ENABLED`` , then the AWS Batch scheduler can attempt to place jobs from an associated job queue on the compute resources within the environment. If the compute environment is managed, then it can scale its instances out or in automatically, based on the job queue demand.

        If the state is ``DISABLED`` , then the AWS Batch scheduler doesn't attempt to place jobs within the environment. Jobs in a ``STARTING`` or ``RUNNING`` state continue to progress normally. Managed compute environments in the ``DISABLED`` state don't scale out. However, they scale in to ``minvCpus`` value after instances become idle.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "state"))

    @state.setter
    def state(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "state", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unmanagedvCpus")
    def unmanagedv_cpus(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of vCPUs for an unmanaged compute environment.

        This parameter is only used for fair share scheduling to reserve vCPU capacity for new share identifiers. If this parameter isn't provided for a fair share job queue, no vCPU capacity is reserved.
        .. epigraph::

           This parameter is only supported when the ``type`` parameter is set to ``UNMANAGED`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-unmanagedvcpus
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "unmanagedvCpus"))

    @unmanagedv_cpus.setter
    def unmanagedv_cpus(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "unmanagedvCpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.UpdatePolicyProperty"]]:
        '''Specifies the infrastructure update policy for the compute environment.

        For more information about infrastructure updates, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-updatepolicy
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.UpdatePolicyProperty"]], jsii.get(self, "updatePolicy"))

    @update_policy.setter
    def update_policy(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.UpdatePolicyProperty"]],
    ) -> None:
        jsii.set(self, "updatePolicy", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.ComputeResourcesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "maxv_cpus": "maxvCpus",
            "subnets": "subnets",
            "type": "type",
            "allocation_strategy": "allocationStrategy",
            "bid_percentage": "bidPercentage",
            "desiredv_cpus": "desiredvCpus",
            "ec2_configuration": "ec2Configuration",
            "ec2_key_pair": "ec2KeyPair",
            "image_id": "imageId",
            "instance_role": "instanceRole",
            "instance_types": "instanceTypes",
            "launch_template": "launchTemplate",
            "minv_cpus": "minvCpus",
            "placement_group": "placementGroup",
            "security_group_ids": "securityGroupIds",
            "spot_iam_fleet_role": "spotIamFleetRole",
            "tags": "tags",
            "update_to_latest_image_version": "updateToLatestImageVersion",
        },
    )
    class ComputeResourcesProperty:
        def __init__(
            self,
            *,
            maxv_cpus: jsii.Number,
            subnets: typing.Sequence[builtins.str],
            type: builtins.str,
            allocation_strategy: typing.Optional[builtins.str] = None,
            bid_percentage: typing.Optional[jsii.Number] = None,
            desiredv_cpus: typing.Optional[jsii.Number] = None,
            ec2_configuration: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.Ec2ConfigurationObjectProperty"]]]] = None,
            ec2_key_pair: typing.Optional[builtins.str] = None,
            image_id: typing.Optional[builtins.str] = None,
            instance_role: typing.Optional[builtins.str] = None,
            instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
            launch_template: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]] = None,
            minv_cpus: typing.Optional[jsii.Number] = None,
            placement_group: typing.Optional[builtins.str] = None,
            security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
            spot_iam_fleet_role: typing.Optional[builtins.str] = None,
            tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
            update_to_latest_image_version: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        ) -> None:
            '''Details about the compute resources managed by the compute environment.

            This parameter is required for managed compute environments. For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the *AWS Batch User Guide* .

            :param maxv_cpus: The maximum number of Amazon EC2 vCPUs that an environment can reach. .. epigraph:: With both ``BEST_FIT_PROGRESSIVE`` and ``SPOT_CAPACITY_OPTIMIZED`` allocation strategies, AWS Batch might need to exceed ``maxvCpus`` to meet your capacity requirements. In this event, AWS Batch never exceeds ``maxvCpus`` by more than a single instance. That is, no more than a single instance from among those specified in your compute environment.
            :param subnets: The VPC subnets where the compute resources are launched. Fargate compute resources can contain up to 16 subnets. For Fargate compute resources, providing an empty list will be handled as if this parameter wasn't specified and no change is made. For EC2 compute resources, providing an empty list removes the VPC subnets from the compute resource. For more information, see `VPCs and subnets <https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html>`_ in the *Amazon VPC User Guide* . When updating a compute environment, changing the VPC subnets requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            :param type: The type of compute environment: ``EC2`` , ``SPOT`` , ``FARGATE`` , or ``FARGATE_SPOT`` . For more information, see `Compute environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the *AWS Batch User Guide* . If you choose ``SPOT`` , you must also specify an Amazon EC2 Spot Fleet role with the ``spotIamFleetRole`` parameter. For more information, see `Amazon EC2 spot fleet role <https://docs.aws.amazon.com/batch/latest/userguide/spot_fleet_IAM_role.html>`_ in the *AWS Batch User Guide* . When updating compute environment, changing the type of a compute environment requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . When updating the type of a compute environment, changing between ``EC2`` and ``SPOT`` or between ``FARGATE`` and ``FARGATE_SPOT`` will initiate an infrastructure update, but if you switch between ``EC2`` and ``FARGATE`` , AWS CloudFormation will create a new compute environment.
            :param allocation_strategy: The allocation strategy to use for the compute resource if not enough instances of the best fitting instance type can be allocated. This might be because of availability of the instance type in the Region or `Amazon EC2 service limits <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html>`_ . For more information, see `Allocation strategies <https://docs.aws.amazon.com/batch/latest/userguide/allocation-strategies.html>`_ in the *AWS Batch User Guide* . When updating a compute environment, changing the allocation strategy requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . ``BEST_FIT`` is not supported when updating a compute environment. .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified. - **BEST_FIT (default)** - AWS Batch selects an instance type that best fits the needs of the jobs with a preference for the lowest-cost instance type. If additional instances of the selected instance type aren't available, AWS Batch waits for the additional instances to be available. If there aren't enough instances available, or if the user is reaching `Amazon EC2 service limits <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html>`_ then additional jobs aren't run until the currently running jobs have completed. This allocation strategy keeps costs lower but can limit scaling. If you are using Spot Fleets with ``BEST_FIT`` then the Spot Fleet IAM role must be specified. - **BEST_FIT_PROGRESSIVE** - AWS Batch will select additional instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types with a lower cost per unit vCPU. If additional instances of the previously selected instance types aren't available, AWS Batch will select new instance types. - **SPOT_CAPACITY_OPTIMIZED** - AWS Batch will select one or more instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types that are less likely to be interrupted. This allocation strategy is only available for Spot Instance compute resources. With both ``BEST_FIT_PROGRESSIVE`` and ``SPOT_CAPACITY_OPTIMIZED`` strategies, AWS Batch might need to go above ``maxvCpus`` to meet your capacity requirements. In this event, AWS Batch never exceeds ``maxvCpus`` by more than a single instance.
            :param bid_percentage: The maximum percentage that a Spot Instance price can be when compared with the On-Demand price for that instance type before instances are launched. For example, if your maximum percentage is 20%, then the Spot price must be less than 20% of the current On-Demand price for that Amazon EC2 instance. You always pay the lowest (market) price and never more than your maximum percentage. When updating a compute environment, changing the bid percentage requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param desiredv_cpus: The desired number of Amazon EC2 vCPUS in the compute environment. AWS Batch modifies this value between the minimum and maximum values based on job queue demand. .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param ec2_configuration: Provides information used to select Amazon Machine Images (AMIs) for EC2 instances in the compute environment. If ``Ec2Configuration`` isn't specified, the default is ``ECS_AL2`` . When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . To remove the EC2 configuration and any custom AMI ID specified in ``imageIdOverride`` , set this value to an empty string. One or two values can be provided. .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param ec2_key_pair: The Amazon EC2 key pair that's used for instances launched in the compute environment. You can use this key pair to log in to your instances with SSH. To remove the Amazon EC2 key pair, set this value to an empty string. When updating a compute environment, changing the EC2 key pair requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param image_id: The Amazon Machine Image (AMI) ID used for instances launched in the compute environment. This parameter is overridden by the ``imageIdOverride`` member of the ``Ec2Configuration`` structure. To remove the custom AMI ID and use the default AMI ID, set this value to an empty string. When updating a compute environment, changing the AMI ID requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified. > The AMI that you choose for a compute environment must match the architecture of the instance types that you intend to use for that compute environment. For example, if your compute environment uses A1 instance types, the compute resource AMI that you choose must support ARM instances. Amazon ECS vends both x86 and ARM versions of the Amazon ECS-optimized Amazon Linux 2 AMI. For more information, see `Amazon ECS-optimized Amazon Linux 2 AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#ecs-optimized-ami-linux-variants.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
            :param instance_role: The Amazon ECS instance profile applied to Amazon EC2 instances in a compute environment. You can specify the short name or full Amazon Resource Name (ARN) of an instance profile. For example, ``*ecsInstanceRole*`` or ``arn:aws:iam:: *<aws_account_id>* :instance-profile/ *ecsInstanceRole*`` . For more information, see `Amazon ECS instance role <https://docs.aws.amazon.com/batch/latest/userguide/instance_IAM_role.html>`_ in the *AWS Batch User Guide* . When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param instance_types: The instances types that can be launched. You can specify instance families to launch any instance type within those families (for example, ``c5`` or ``p3`` ), or you can specify specific sizes within a family (such as ``c5.8xlarge`` ). You can also choose ``optimal`` to select instance types (from the C4, M4, and R4 instance families) that match the demand of your job queues. When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified. > When you create a compute environment, the instance types that you select for the compute environment must share the same architecture. For example, you can't mix x86 and ARM instances in the same compute environment. > Currently, ``optimal`` uses instance types from the C4, M4, and R4 instance families. In Regions that don't have instance types from those instance families, instance types from the C5, M5. and R5 instance families are used.
            :param launch_template: The launch template to use for your compute resources. Any other compute resource parameters that you specify in a `CreateComputeEnvironment <https://docs.aws.amazon.com/batch/latest/APIReference/API_CreateComputeEnvironment.html>`_ API operation override the same parameters in the launch template. You must specify either the launch template ID or launch template name in the request, but not both. For more information, see `Launch Template Support <https://docs.aws.amazon.com/batch/latest/userguide/launch-templates.html>`_ in the ** . .. epigraph:: This parameter isn't applicable to jobs running on Fargate resources, and shouldn't be specified.
            :param minv_cpus: The minimum number of Amazon EC2 vCPUs that an environment should maintain (even if the compute environment is ``DISABLED`` ). .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param placement_group: The Amazon EC2 placement group to associate with your compute resources. If you intend to submit multi-node parallel jobs to your compute environment, you should consider creating a cluster placement group and associate it with your compute resources. This keeps your multi-node parallel job on a logical grouping of instances within a single Availability Zone with high network flow potential. For more information, see `Placement groups <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html>`_ in the *Amazon EC2 User Guide for Linux Instances* . When updating a compute environment, changing the placement group requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param security_group_ids: The Amazon EC2 security groups associated with instances launched in the compute environment. This parameter is required for Fargate compute resources, where it can contain up to 5 security groups. For Fargate compute resources, providing an empty list is handled as if this parameter wasn't specified and no change is made. For EC2 compute resources, providing an empty list removes the security groups from the compute resource. When updating a compute environment, changing the EC2 security groups requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            :param spot_iam_fleet_role: The Amazon Resource Name (ARN) of the Amazon EC2 Spot Fleet IAM role applied to a ``SPOT`` compute environment. This role is required if the allocation strategy set to ``BEST_FIT`` or if the allocation strategy isn't specified. For more information, see `Amazon EC2 spot fleet role <https://docs.aws.amazon.com/batch/latest/userguide/spot_fleet_IAM_role.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified. > To tag your Spot Instances on creation, the Spot Fleet IAM role specified here must use the newer *AmazonEC2SpotFleetTaggingRole* managed policy. The previously recommended *AmazonEC2SpotFleetRole* managed policy doesn't have the required permissions to tag Spot Instances. For more information, see `Spot instances not tagged on creation <https://docs.aws.amazon.com/batch/latest/userguide/troubleshooting.html#spot-instance-no-tag>`_ in the *AWS Batch User Guide* .
            :param tags: Key-value pair tags to be applied to EC2 resources that are launched in the compute environment. For AWS Batch , these take the form of "String1": "String2", where String1 is the tag key and String2 is the tag value−for example, ``{ "Name": "Batch Instance - C4OnDemand" }`` . This is helpful for recognizing your AWS Batch instances in the Amazon EC2 console. These tags aren't seen when using the AWS Batch ``ListTagsForResource`` API operation. When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.
            :param update_to_latest_image_version: Specifies whether the AMI ID is updated to the latest one that's supported by AWS Batch when the compute environment has an infrastructure update. The default value is ``false`` . .. epigraph:: If an AMI ID is specified in the ``imageId`` or ``imageIdOverride`` parameters or by the launch template specified in the ``launchTemplate`` parameter, this parameter is ignored. For more information on updating AMI IDs during an infrastructure update, see `Updating the AMI ID <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html#updating-compute-environments-ami>`_ in the *AWS Batch User Guide* . When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                compute_resources_property = batch.CfnComputeEnvironment.ComputeResourcesProperty(
                    maxv_cpus=123,
                    subnets=["subnets"],
                    type="type",
                
                    # the properties below are optional
                    allocation_strategy="allocationStrategy",
                    bid_percentage=123,
                    desiredv_cpus=123,
                    ec2_configuration=[batch.CfnComputeEnvironment.Ec2ConfigurationObjectProperty(
                        image_type="imageType",
                
                        # the properties below are optional
                        image_id_override="imageIdOverride"
                    )],
                    ec2_key_pair="ec2KeyPair",
                    image_id="imageId",
                    instance_role="instanceRole",
                    instance_types=["instanceTypes"],
                    launch_template=batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty(
                        launch_template_id="launchTemplateId",
                        launch_template_name="launchTemplateName",
                        version="version"
                    ),
                    minv_cpus=123,
                    placement_group="placementGroup",
                    security_group_ids=["securityGroupIds"],
                    spot_iam_fleet_role="spotIamFleetRole",
                    tags={
                        "tags_key": "tags"
                    },
                    update_to_latest_image_version=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "maxv_cpus": maxv_cpus,
                "subnets": subnets,
                "type": type,
            }
            if allocation_strategy is not None:
                self._values["allocation_strategy"] = allocation_strategy
            if bid_percentage is not None:
                self._values["bid_percentage"] = bid_percentage
            if desiredv_cpus is not None:
                self._values["desiredv_cpus"] = desiredv_cpus
            if ec2_configuration is not None:
                self._values["ec2_configuration"] = ec2_configuration
            if ec2_key_pair is not None:
                self._values["ec2_key_pair"] = ec2_key_pair
            if image_id is not None:
                self._values["image_id"] = image_id
            if instance_role is not None:
                self._values["instance_role"] = instance_role
            if instance_types is not None:
                self._values["instance_types"] = instance_types
            if launch_template is not None:
                self._values["launch_template"] = launch_template
            if minv_cpus is not None:
                self._values["minv_cpus"] = minv_cpus
            if placement_group is not None:
                self._values["placement_group"] = placement_group
            if security_group_ids is not None:
                self._values["security_group_ids"] = security_group_ids
            if spot_iam_fleet_role is not None:
                self._values["spot_iam_fleet_role"] = spot_iam_fleet_role
            if tags is not None:
                self._values["tags"] = tags
            if update_to_latest_image_version is not None:
                self._values["update_to_latest_image_version"] = update_to_latest_image_version

        @builtins.property
        def maxv_cpus(self) -> jsii.Number:
            '''The maximum number of Amazon EC2 vCPUs that an environment can reach.

            .. epigraph::

               With both ``BEST_FIT_PROGRESSIVE`` and ``SPOT_CAPACITY_OPTIMIZED`` allocation strategies, AWS Batch might need to exceed ``maxvCpus`` to meet your capacity requirements. In this event, AWS Batch never exceeds ``maxvCpus`` by more than a single instance. That is, no more than a single instance from among those specified in your compute environment.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus
            '''
            result = self._values.get("maxv_cpus")
            assert result is not None, "Required property 'maxv_cpus' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def subnets(self) -> typing.List[builtins.str]:
            '''The VPC subnets where the compute resources are launched.

            Fargate compute resources can contain up to 16 subnets. For Fargate compute resources, providing an empty list will be handled as if this parameter wasn't specified and no change is made. For EC2 compute resources, providing an empty list removes the VPC subnets from the compute resource. For more information, see `VPCs and subnets <https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html>`_ in the *Amazon VPC User Guide* .

            When updating a compute environment, changing the VPC subnets requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets
            '''
            result = self._values.get("subnets")
            assert result is not None, "Required property 'subnets' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of compute environment: ``EC2`` , ``SPOT`` , ``FARGATE`` , or ``FARGATE_SPOT`` .

            For more information, see `Compute environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the *AWS Batch User Guide* .

            If you choose ``SPOT`` , you must also specify an Amazon EC2 Spot Fleet role with the ``spotIamFleetRole`` parameter. For more information, see `Amazon EC2 spot fleet role <https://docs.aws.amazon.com/batch/latest/userguide/spot_fleet_IAM_role.html>`_ in the *AWS Batch User Guide* .

            When updating compute environment, changing the type of a compute environment requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

            When updating the type of a compute environment, changing between ``EC2`` and ``SPOT`` or between ``FARGATE`` and ``FARGATE_SPOT`` will initiate an infrastructure update, but if you switch between ``EC2`` and ``FARGATE`` , AWS CloudFormation will create a new compute environment.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def allocation_strategy(self) -> typing.Optional[builtins.str]:
            '''The allocation strategy to use for the compute resource if not enough instances of the best fitting instance type can be allocated.

            This might be because of availability of the instance type in the Region or `Amazon EC2 service limits <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html>`_ . For more information, see `Allocation strategies <https://docs.aws.amazon.com/batch/latest/userguide/allocation-strategies.html>`_ in the *AWS Batch User Guide* .

            When updating a compute environment, changing the allocation strategy requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . ``BEST_FIT`` is not supported when updating a compute environment.
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            - **BEST_FIT (default)** - AWS Batch selects an instance type that best fits the needs of the jobs with a preference for the lowest-cost instance type. If additional instances of the selected instance type aren't available, AWS Batch waits for the additional instances to be available. If there aren't enough instances available, or if the user is reaching `Amazon EC2 service limits <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html>`_ then additional jobs aren't run until the currently running jobs have completed. This allocation strategy keeps costs lower but can limit scaling. If you are using Spot Fleets with ``BEST_FIT`` then the Spot Fleet IAM role must be specified.
            - **BEST_FIT_PROGRESSIVE** - AWS Batch will select additional instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types with a lower cost per unit vCPU. If additional instances of the previously selected instance types aren't available, AWS Batch will select new instance types.
            - **SPOT_CAPACITY_OPTIMIZED** - AWS Batch will select one or more instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types that are less likely to be interrupted. This allocation strategy is only available for Spot Instance compute resources.

            With both ``BEST_FIT_PROGRESSIVE`` and ``SPOT_CAPACITY_OPTIMIZED`` strategies, AWS Batch might need to go above ``maxvCpus`` to meet your capacity requirements. In this event, AWS Batch never exceeds ``maxvCpus`` by more than a single instance.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-allocationstrategy
            '''
            result = self._values.get("allocation_strategy")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def bid_percentage(self) -> typing.Optional[jsii.Number]:
            '''The maximum percentage that a Spot Instance price can be when compared with the On-Demand price for that instance type before instances are launched.

            For example, if your maximum percentage is 20%, then the Spot price must be less than 20% of the current On-Demand price for that Amazon EC2 instance. You always pay the lowest (market) price and never more than your maximum percentage.

            When updating a compute environment, changing the bid percentage requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage
            '''
            result = self._values.get("bid_percentage")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def desiredv_cpus(self) -> typing.Optional[jsii.Number]:
            '''The desired number of Amazon EC2 vCPUS in the compute environment.

            AWS Batch modifies this value between the minimum and maximum values based on job queue demand.
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-desiredvcpus
            '''
            result = self._values.get("desiredv_cpus")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def ec2_configuration(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.Ec2ConfigurationObjectProperty"]]]]:
            '''Provides information used to select Amazon Machine Images (AMIs) for EC2 instances in the compute environment.

            If ``Ec2Configuration`` isn't specified, the default is ``ECS_AL2`` .

            When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . To remove the EC2 configuration and any custom AMI ID specified in ``imageIdOverride`` , set this value to an empty string.

            One or two values can be provided.
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2configuration
            '''
            result = self._values.get("ec2_configuration")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.Ec2ConfigurationObjectProperty"]]]], result)

        @builtins.property
        def ec2_key_pair(self) -> typing.Optional[builtins.str]:
            '''The Amazon EC2 key pair that's used for instances launched in the compute environment.

            You can use this key pair to log in to your instances with SSH. To remove the Amazon EC2 key pair, set this value to an empty string.

            When updating a compute environment, changing the EC2 key pair requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair
            '''
            result = self._values.get("ec2_key_pair")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def image_id(self) -> typing.Optional[builtins.str]:
            '''The Amazon Machine Image (AMI) ID used for instances launched in the compute environment.

            This parameter is overridden by the ``imageIdOverride`` member of the ``Ec2Configuration`` structure. To remove the custom AMI ID and use the default AMI ID, set this value to an empty string.

            When updating a compute environment, changing the AMI ID requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified. > The AMI that you choose for a compute environment must match the architecture of the instance types that you intend to use for that compute environment. For example, if your compute environment uses A1 instance types, the compute resource AMI that you choose must support ARM instances. Amazon ECS vends both x86 and ARM versions of the Amazon ECS-optimized Amazon Linux 2 AMI. For more information, see `Amazon ECS-optimized Amazon Linux 2 AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#ecs-optimized-ami-linux-variants.html>`_ in the *Amazon Elastic Container Service Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid
            '''
            result = self._values.get("image_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def instance_role(self) -> typing.Optional[builtins.str]:
            '''The Amazon ECS instance profile applied to Amazon EC2 instances in a compute environment.

            You can specify the short name or full Amazon Resource Name (ARN) of an instance profile. For example, ``*ecsInstanceRole*`` or ``arn:aws:iam:: *<aws_account_id>* :instance-profile/ *ecsInstanceRole*`` . For more information, see `Amazon ECS instance role <https://docs.aws.amazon.com/batch/latest/userguide/instance_IAM_role.html>`_ in the *AWS Batch User Guide* .

            When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole
            '''
            result = self._values.get("instance_role")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
            '''The instances types that can be launched.

            You can specify instance families to launch any instance type within those families (for example, ``c5`` or ``p3`` ), or you can specify specific sizes within a family (such as ``c5.8xlarge`` ). You can also choose ``optimal`` to select instance types (from the C4, M4, and R4 instance families) that match the demand of your job queues.

            When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified. > When you create a compute environment, the instance types that you select for the compute environment must share the same architecture. For example, you can't mix x86 and ARM instances in the same compute environment. > Currently, ``optimal`` uses instance types from the C4, M4, and R4 instance families. In Regions that don't have instance types from those instance families, instance types from the C5, M5. and R5 instance families are used.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes
            '''
            result = self._values.get("instance_types")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def launch_template(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]]:
            '''The launch template to use for your compute resources.

            Any other compute resource parameters that you specify in a `CreateComputeEnvironment <https://docs.aws.amazon.com/batch/latest/APIReference/API_CreateComputeEnvironment.html>`_ API operation override the same parameters in the launch template. You must specify either the launch template ID or launch template name in the request, but not both. For more information, see `Launch Template Support <https://docs.aws.amazon.com/batch/latest/userguide/launch-templates.html>`_ in the ** .
            .. epigraph::

               This parameter isn't applicable to jobs running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate
            '''
            result = self._values.get("launch_template")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]], result)

        @builtins.property
        def minv_cpus(self) -> typing.Optional[jsii.Number]:
            '''The minimum number of Amazon EC2 vCPUs that an environment should maintain (even if the compute environment is ``DISABLED`` ).

            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus
            '''
            result = self._values.get("minv_cpus")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def placement_group(self) -> typing.Optional[builtins.str]:
            '''The Amazon EC2 placement group to associate with your compute resources.

            If you intend to submit multi-node parallel jobs to your compute environment, you should consider creating a cluster placement group and associate it with your compute resources. This keeps your multi-node parallel job on a logical grouping of instances within a single Availability Zone with high network flow potential. For more information, see `Placement groups <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html>`_ in the *Amazon EC2 User Guide for Linux Instances* .

            When updating a compute environment, changing the placement group requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup
            '''
            result = self._values.get("placement_group")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
            '''The Amazon EC2 security groups associated with instances launched in the compute environment.

            This parameter is required for Fargate compute resources, where it can contain up to 5 security groups. For Fargate compute resources, providing an empty list is handled as if this parameter wasn't specified and no change is made. For EC2 compute resources, providing an empty list removes the security groups from the compute resource.

            When updating a compute environment, changing the EC2 security groups requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids
            '''
            result = self._values.get("security_group_ids")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def spot_iam_fleet_role(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) of the Amazon EC2 Spot Fleet IAM role applied to a ``SPOT`` compute environment.

            This role is required if the allocation strategy set to ``BEST_FIT`` or if the allocation strategy isn't specified. For more information, see `Amazon EC2 spot fleet role <https://docs.aws.amazon.com/batch/latest/userguide/spot_fleet_IAM_role.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified. > To tag your Spot Instances on creation, the Spot Fleet IAM role specified here must use the newer *AmazonEC2SpotFleetTaggingRole* managed policy. The previously recommended *AmazonEC2SpotFleetRole* managed policy doesn't have the required permissions to tag Spot Instances. For more information, see `Spot instances not tagged on creation <https://docs.aws.amazon.com/batch/latest/userguide/troubleshooting.html#spot-instance-no-tag>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-spotiamfleetrole
            '''
            result = self._values.get("spot_iam_fleet_role")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
            '''Key-value pair tags to be applied to EC2 resources that are launched in the compute environment.

            For AWS Batch , these take the form of "String1": "String2", where String1 is the tag key and String2 is the tag value−for example, ``{ "Name": "Batch Instance - C4OnDemand" }`` . This is helpful for recognizing your AWS Batch instances in the Amazon EC2 console. These tags aren't seen when using the AWS Batch ``ListTagsForResource`` API operation.

            When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources, and shouldn't be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags
            '''
            result = self._values.get("tags")
            return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

        @builtins.property
        def update_to_latest_image_version(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            '''Specifies whether the AMI ID is updated to the latest one that's supported by AWS Batch when the compute environment has an infrastructure update.

            The default value is ``false`` .
            .. epigraph::

               If an AMI ID is specified in the ``imageId`` or ``imageIdOverride`` parameters or by the launch template specified in the ``launchTemplate`` parameter, this parameter is ignored. For more information on updating AMI IDs during an infrastructure update, see `Updating the AMI ID <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html#updating-compute-environments-ami>`_ in the *AWS Batch User Guide* .

            When updating a compute environment, changing this setting requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-updatetolatestimageversion
            '''
            result = self._values.get("update_to_latest_image_version")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ComputeResourcesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.Ec2ConfigurationObjectProperty",
        jsii_struct_bases=[],
        name_mapping={
            "image_type": "imageType",
            "image_id_override": "imageIdOverride",
        },
    )
    class Ec2ConfigurationObjectProperty:
        def __init__(
            self,
            *,
            image_type: builtins.str,
            image_id_override: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Provides information used to select Amazon Machine Images (AMIs) for instances in the compute environment.

            If ``Ec2Configuration`` isn't specified, the default is ``ECS_AL2`` ( `Amazon Linux 2 <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#al2ami>`_ ).
            .. epigraph::

               This object isn't applicable to jobs that are running on Fargate resources.

            :param image_type: The image type to match with the instance type to select an AMI. If the ``imageIdOverride`` parameter isn't specified, then a recent `Amazon ECS-optimized Amazon Linux 2 AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#al2ami>`_ ( ``ECS_AL2`` ) is used. If a new image type is specified in an update, but neither an ``imageId`` nor a ``imageIdOverride`` parameter is specified, then the latest Amazon ECS optimized AMI for that image type that's supported by AWS Batch is used. - **ECS_AL2** - `Amazon Linux 2 <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#al2ami>`_ − Default for all non-GPU instance families. - **ECS_AL2_NVIDIA** - `Amazon Linux 2 (GPU) <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#gpuami>`_ −Default for all GPU instance families (for example ``P4`` and ``G4`` ) and can be used for all non AWS Graviton-based instance types. - **ECS_AL1** - `Amazon Linux <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#alami>`_ . Amazon Linux is reaching the end-of-life of standard support. For more information, see `Amazon Linux AMI <https://docs.aws.amazon.com/amazon-linux-ami/>`_ .
            :param image_id_override: The AMI ID used for instances launched in the compute environment that match the image type. This setting overrides the ``imageId`` set in the ``computeResource`` object. .. epigraph:: The AMI that you choose for a compute environment must match the architecture of the instance types that you intend to use for that compute environment. For example, if your compute environment uses A1 instance types, the compute resource AMI that you choose must support ARM instances. Amazon ECS vends both x86 and ARM versions of the Amazon ECS-optimized Amazon Linux 2 AMI. For more information, see `Amazon ECS-optimized Amazon Linux 2 AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#ecs-optimized-ami-linux-variants.html>`_ in the *Amazon Elastic Container Service Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-ec2configurationobject.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                ec2_configuration_object_property = batch.CfnComputeEnvironment.Ec2ConfigurationObjectProperty(
                    image_type="imageType",
                
                    # the properties below are optional
                    image_id_override="imageIdOverride"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "image_type": image_type,
            }
            if image_id_override is not None:
                self._values["image_id_override"] = image_id_override

        @builtins.property
        def image_type(self) -> builtins.str:
            '''The image type to match with the instance type to select an AMI.

            If the ``imageIdOverride`` parameter isn't specified, then a recent `Amazon ECS-optimized Amazon Linux 2 AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#al2ami>`_ ( ``ECS_AL2`` ) is used. If a new image type is specified in an update, but neither an ``imageId`` nor a ``imageIdOverride`` parameter is specified, then the latest Amazon ECS optimized AMI for that image type that's supported by AWS Batch is used.

            - **ECS_AL2** - `Amazon Linux 2 <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#al2ami>`_ − Default for all non-GPU instance families.
            - **ECS_AL2_NVIDIA** - `Amazon Linux 2 (GPU) <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#gpuami>`_ −Default for all GPU instance families (for example ``P4`` and ``G4`` ) and can be used for all non AWS Graviton-based instance types.
            - **ECS_AL1** - `Amazon Linux <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#alami>`_ . Amazon Linux is reaching the end-of-life of standard support. For more information, see `Amazon Linux AMI <https://docs.aws.amazon.com/amazon-linux-ami/>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-ec2configurationobject.html#cfn-batch-computeenvironment-ec2configurationobject-imagetype
            '''
            result = self._values.get("image_type")
            assert result is not None, "Required property 'image_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def image_id_override(self) -> typing.Optional[builtins.str]:
            '''The AMI ID used for instances launched in the compute environment that match the image type.

            This setting overrides the ``imageId`` set in the ``computeResource`` object.
            .. epigraph::

               The AMI that you choose for a compute environment must match the architecture of the instance types that you intend to use for that compute environment. For example, if your compute environment uses A1 instance types, the compute resource AMI that you choose must support ARM instances. Amazon ECS vends both x86 and ARM versions of the Amazon ECS-optimized Amazon Linux 2 AMI. For more information, see `Amazon ECS-optimized Amazon Linux 2 AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#ecs-optimized-ami-linux-variants.html>`_ in the *Amazon Elastic Container Service Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-ec2configurationobject.html#cfn-batch-computeenvironment-ec2configurationobject-imageidoverride
            '''
            result = self._values.get("image_id_override")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "Ec2ConfigurationObjectProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "launch_template_id": "launchTemplateId",
            "launch_template_name": "launchTemplateName",
            "version": "version",
        },
    )
    class LaunchTemplateSpecificationProperty:
        def __init__(
            self,
            *,
            launch_template_id: typing.Optional[builtins.str] = None,
            launch_template_name: typing.Optional[builtins.str] = None,
            version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''An object representing a launch template associated with a compute resource.

            You must specify either the launch template ID or launch template name in the request, but not both.

            If security groups are specified using both the ``securityGroupIds`` parameter of ``CreateComputeEnvironment`` and the launch template, the values in the ``securityGroupIds`` parameter of ``CreateComputeEnvironment`` will be used.
            .. epigraph::

               This object isn't applicable to jobs that are running on Fargate resources.

            :param launch_template_id: The ID of the launch template.
            :param launch_template_name: The name of the launch template.
            :param version: The version number of the launch template, ``$Latest`` , or ``$Default`` . If the value is ``$Latest`` , the latest version of the launch template is used. If the value is ``$Default`` , the default version of the launch template is used. .. epigraph:: If the AMI ID that's used in a compute environment is from the launch template, the AMI isn't changed when the compute environment is updated. It's only changed if the ``updateToLatestImageVersion`` parameter for the compute environment is set to ``true`` . During an infrastructure update, if either ``$Latest`` or ``$Default`` is specified, AWS Batch re-evaluates the launch template version, and it might use a different version of the launch template. This is the case even if the launch template isn't specified in the update. When updating a compute environment, changing the launch template requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* . Default: ``$Default`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                launch_template_specification_property = batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty(
                    launch_template_id="launchTemplateId",
                    launch_template_name="launchTemplateName",
                    version="version"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if launch_template_id is not None:
                self._values["launch_template_id"] = launch_template_id
            if launch_template_name is not None:
                self._values["launch_template_name"] = launch_template_name
            if version is not None:
                self._values["version"] = version

        @builtins.property
        def launch_template_id(self) -> typing.Optional[builtins.str]:
            '''The ID of the launch template.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplateid
            '''
            result = self._values.get("launch_template_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def launch_template_name(self) -> typing.Optional[builtins.str]:
            '''The name of the launch template.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplatename
            '''
            result = self._values.get("launch_template_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def version(self) -> typing.Optional[builtins.str]:
            '''The version number of the launch template, ``$Latest`` , or ``$Default`` .

            If the value is ``$Latest`` , the latest version of the launch template is used. If the value is ``$Default`` , the default version of the launch template is used.
            .. epigraph::

               If the AMI ID that's used in a compute environment is from the launch template, the AMI isn't changed when the compute environment is updated. It's only changed if the ``updateToLatestImageVersion`` parameter for the compute environment is set to ``true`` . During an infrastructure update, if either ``$Latest`` or ``$Default`` is specified, AWS Batch re-evaluates the launch template version, and it might use a different version of the launch template. This is the case even if the launch template isn't specified in the update. When updating a compute environment, changing the launch template requires an infrastructure update of the compute environment. For more information, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

            Default: ``$Default`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-version
            '''
            result = self._values.get("version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LaunchTemplateSpecificationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.UpdatePolicyProperty",
        jsii_struct_bases=[],
        name_mapping={
            "job_execution_timeout_minutes": "jobExecutionTimeoutMinutes",
            "terminate_jobs_on_update": "terminateJobsOnUpdate",
        },
    )
    class UpdatePolicyProperty:
        def __init__(
            self,
            *,
            job_execution_timeout_minutes: typing.Optional[jsii.Number] = None,
            terminate_jobs_on_update: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        ) -> None:
            '''Specifies the infrastructure update policy for the compute environment.

            For more information about infrastructure updates, see `Infrastructure updates <https://docs.aws.amazon.com/batch/latest/userguide/infrastructure-updates.html>`_ in the *AWS Batch User Guide* .

            :param job_execution_timeout_minutes: Specifies the job timeout, in minutes, when the compute environment infrastructure is updated. The default value is 30.
            :param terminate_jobs_on_update: Specifies whether jobs are automatically terminated when the computer environment infrastructure is updated. The default value is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-updatepolicy.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                update_policy_property = batch.CfnComputeEnvironment.UpdatePolicyProperty(
                    job_execution_timeout_minutes=123,
                    terminate_jobs_on_update=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if job_execution_timeout_minutes is not None:
                self._values["job_execution_timeout_minutes"] = job_execution_timeout_minutes
            if terminate_jobs_on_update is not None:
                self._values["terminate_jobs_on_update"] = terminate_jobs_on_update

        @builtins.property
        def job_execution_timeout_minutes(self) -> typing.Optional[jsii.Number]:
            '''Specifies the job timeout, in minutes, when the compute environment infrastructure is updated.

            The default value is 30.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-updatepolicy.html#cfn-batch-computeenvironment-updatepolicy-jobexecutiontimeoutminutes
            '''
            result = self._values.get("job_execution_timeout_minutes")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def terminate_jobs_on_update(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            '''Specifies whether jobs are automatically terminated when the computer environment infrastructure is updated.

            The default value is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-updatepolicy.html#cfn-batch-computeenvironment-updatepolicy-terminatejobsonupdate
            '''
            result = self._values.get("terminate_jobs_on_update")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "UpdatePolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "compute_environment_name": "computeEnvironmentName",
        "compute_resources": "computeResources",
        "replace_compute_environment": "replaceComputeEnvironment",
        "service_role": "serviceRole",
        "state": "state",
        "tags": "tags",
        "unmanagedv_cpus": "unmanagedvCpus",
        "update_policy": "updatePolicy",
    },
)
class CfnComputeEnvironmentProps:
    def __init__(
        self,
        *,
        type: builtins.str,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional[typing.Union[CfnComputeEnvironment.ComputeResourcesProperty, aws_cdk.core.IResolvable]] = None,
        replace_compute_environment: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        service_role: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        unmanagedv_cpus: typing.Optional[jsii.Number] = None,
        update_policy: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnComputeEnvironment.UpdatePolicyProperty]] = None,
    ) -> None:
        '''Properties for defining a ``CfnComputeEnvironment``.

        :param type: The type of the compute environment: ``MANAGED`` or ``UNMANAGED`` . For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the *AWS Batch User Guide* .
        :param compute_environment_name: The name for your compute environment. It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).
        :param compute_resources: The ComputeResources property type specifies details of the compute resources managed by the compute environment. This parameter is required for managed compute environments. For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the ** .
        :param replace_compute_environment: Specifies whether the compute environment should be replaced if an update is made that requires replacing the instances in the compute environment. The default value is ``true`` . To enable more properties to be updated, set this property to ``false`` . When changing the value of this property to ``false`` , no other properties should be changed at the same time. If other properties are changed at the same time, and the change needs to be rolled back but it can't, it's possible for the stack to go into the ``UPDATE_ROLLBACK_FAILED`` state. You can't update a stack that is in the ``UPDATE_ROLLBACK_FAILED`` state. However, if you can continue to roll it back, you can return the stack to its original settings and then try to update it again. For more information, see `Continue rolling back an update <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-continueupdaterollback.html>`_ in the *AWS CloudFormation User Guide* . The properties that can't be changed without replacing the compute environment are in the ```ComputeResources`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html>`_ property type: ```AllocationStrategy`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-allocationstrategy>`_ , ```BidPercentage`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage>`_ , ```Ec2Configuration`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2configuration>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```ImageId`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid>`_ , ```InstanceRole`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole>`_ , ```InstanceTypes`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes>`_ , ```LaunchTemplate`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate>`_ , ```MaxvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus>`_ , ```MinvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus>`_ , ```PlacementGroup`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup>`_ , ```SecurityGroupIds`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids>`_ , ```Subnets`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets>`_ , `Tags <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags>`_ , ```Type`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type>`_ , and ```UpdateToLatestImageVersion`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-updatetolatestimageversion>`_ .
        :param service_role: The full Amazon Resource Name (ARN) of the IAM role that allows AWS Batch to make calls to other AWS services on your behalf. For more information, see `AWS Batch service IAM role <https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html>`_ in the *AWS Batch User Guide* . .. epigraph:: If your account already created the AWS Batch service-linked role, that role is used by default for your compute environment unless you specify a different role here. If the AWS Batch service-linked role doesn't exist in your account, and no role is specified here, the service attempts to create the AWS Batch service-linked role in your account. If your specified role has a path other than ``/`` , then you must specify either the full role ARN (recommended) or prefix the role name with the path. For example, if a role with the name ``bar`` has a path of ``/foo/`` then you would specify ``/foo/bar`` as the role name. For more information, see `Friendly names and paths <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-friendly-names>`_ in the *IAM User Guide* . .. epigraph:: Depending on how you created your AWS Batch service role, its ARN might contain the ``service-role`` path prefix. When you only specify the name of the service role, AWS Batch assumes that your ARN doesn't use the ``service-role`` path prefix. Because of this, we recommend that you specify the full ARN of your service role when you create compute environments.
        :param state: The state of the compute environment. If the state is ``ENABLED`` , then the compute environment accepts jobs from a queue and can scale out automatically based on queues. If the state is ``ENABLED`` , then the AWS Batch scheduler can attempt to place jobs from an associated job queue on the compute resources within the environment. If the compute environment is managed, then it can scale its instances out or in automatically, based on the job queue demand. If the state is ``DISABLED`` , then the AWS Batch scheduler doesn't attempt to place jobs within the environment. Jobs in a ``STARTING`` or ``RUNNING`` state continue to progress normally. Managed compute environments in the ``DISABLED`` state don't scale out. However, they scale in to ``minvCpus`` value after instances become idle.
        :param tags: The tags applied to the compute environment.
        :param unmanagedv_cpus: The maximum number of vCPUs for an unmanaged compute environment. This parameter is only used for fair share scheduling to reserve vCPU capacity for new share identifiers. If this parameter isn't provided for a fair share job queue, no vCPU capacity is reserved. .. epigraph:: This parameter is only supported when the ``type`` parameter is set to ``UNMANAGED`` .
        :param update_policy: Specifies the infrastructure update policy for the compute environment. For more information about infrastructure updates, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_batch as batch
            
            cfn_compute_environment_props = batch.CfnComputeEnvironmentProps(
                type="type",
            
                # the properties below are optional
                compute_environment_name="computeEnvironmentName",
                compute_resources=batch.CfnComputeEnvironment.ComputeResourcesProperty(
                    maxv_cpus=123,
                    subnets=["subnets"],
                    type="type",
            
                    # the properties below are optional
                    allocation_strategy="allocationStrategy",
                    bid_percentage=123,
                    desiredv_cpus=123,
                    ec2_configuration=[batch.CfnComputeEnvironment.Ec2ConfigurationObjectProperty(
                        image_type="imageType",
            
                        # the properties below are optional
                        image_id_override="imageIdOverride"
                    )],
                    ec2_key_pair="ec2KeyPair",
                    image_id="imageId",
                    instance_role="instanceRole",
                    instance_types=["instanceTypes"],
                    launch_template=batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty(
                        launch_template_id="launchTemplateId",
                        launch_template_name="launchTemplateName",
                        version="version"
                    ),
                    minv_cpus=123,
                    placement_group="placementGroup",
                    security_group_ids=["securityGroupIds"],
                    spot_iam_fleet_role="spotIamFleetRole",
                    tags={
                        "tags_key": "tags"
                    },
                    update_to_latest_image_version=False
                ),
                replace_compute_environment=False,
                service_role="serviceRole",
                state="state",
                tags={
                    "tags_key": "tags"
                },
                unmanagedv_cpus=123,
                update_policy=batch.CfnComputeEnvironment.UpdatePolicyProperty(
                    job_execution_timeout_minutes=123,
                    terminate_jobs_on_update=False
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if compute_environment_name is not None:
            self._values["compute_environment_name"] = compute_environment_name
        if compute_resources is not None:
            self._values["compute_resources"] = compute_resources
        if replace_compute_environment is not None:
            self._values["replace_compute_environment"] = replace_compute_environment
        if service_role is not None:
            self._values["service_role"] = service_role
        if state is not None:
            self._values["state"] = state
        if tags is not None:
            self._values["tags"] = tags
        if unmanagedv_cpus is not None:
            self._values["unmanagedv_cpus"] = unmanagedv_cpus
        if update_policy is not None:
            self._values["update_policy"] = update_policy

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the compute environment: ``MANAGED`` or ``UNMANAGED`` .

        For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute_environment_name(self) -> typing.Optional[builtins.str]:
        '''The name for your compute environment.

        It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeenvironmentname
        '''
        result = self._values.get("compute_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compute_resources(
        self,
    ) -> typing.Optional[typing.Union[CfnComputeEnvironment.ComputeResourcesProperty, aws_cdk.core.IResolvable]]:
        '''The ComputeResources property type specifies details of the compute resources managed by the compute environment.

        This parameter is required for managed compute environments. For more information, see `Compute Environments <https://docs.aws.amazon.com/batch/latest/userguide/compute_environments.html>`_ in the ** .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
        '''
        result = self._values.get("compute_resources")
        return typing.cast(typing.Optional[typing.Union[CfnComputeEnvironment.ComputeResourcesProperty, aws_cdk.core.IResolvable]], result)

    @builtins.property
    def replace_compute_environment(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        '''Specifies whether the compute environment should be replaced if an update is made that requires replacing the instances in the compute environment.

        The default value is ``true`` . To enable more properties to be updated, set this property to ``false`` . When changing the value of this property to ``false`` , no other properties should be changed at the same time. If other properties are changed at the same time, and the change needs to be rolled back but it can't, it's possible for the stack to go into the ``UPDATE_ROLLBACK_FAILED`` state. You can't update a stack that is in the ``UPDATE_ROLLBACK_FAILED`` state. However, if you can continue to roll it back, you can return the stack to its original settings and then try to update it again. For more information, see `Continue rolling back an update <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-continueupdaterollback.html>`_ in the *AWS CloudFormation User Guide* .

        The properties that can't be changed without replacing the compute environment are in the ```ComputeResources`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html>`_ property type: ```AllocationStrategy`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-allocationstrategy>`_ , ```BidPercentage`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage>`_ , ```Ec2Configuration`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2configuration>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```Ec2KeyPair`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair>`_ , ```ImageId`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid>`_ , ```InstanceRole`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole>`_ , ```InstanceTypes`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes>`_ , ```LaunchTemplate`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate>`_ , ```MaxvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus>`_ , ```MinvCpus`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus>`_ , ```PlacementGroup`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup>`_ , ```SecurityGroupIds`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids>`_ , ```Subnets`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets>`_ , `Tags <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags>`_ , ```Type`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type>`_ , and ```UpdateToLatestImageVersion`` <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-updatetolatestimageversion>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-replacecomputeenvironment
        '''
        result = self._values.get("replace_compute_environment")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

    @builtins.property
    def service_role(self) -> typing.Optional[builtins.str]:
        '''The full Amazon Resource Name (ARN) of the IAM role that allows AWS Batch to make calls to other AWS services on your behalf.

        For more information, see `AWS Batch service IAM role <https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html>`_ in the *AWS Batch User Guide* .
        .. epigraph::

           If your account already created the AWS Batch service-linked role, that role is used by default for your compute environment unless you specify a different role here. If the AWS Batch service-linked role doesn't exist in your account, and no role is specified here, the service attempts to create the AWS Batch service-linked role in your account.

        If your specified role has a path other than ``/`` , then you must specify either the full role ARN (recommended) or prefix the role name with the path. For example, if a role with the name ``bar`` has a path of ``/foo/`` then you would specify ``/foo/bar`` as the role name. For more information, see `Friendly names and paths <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-friendly-names>`_ in the *IAM User Guide* .
        .. epigraph::

           Depending on how you created your AWS Batch service role, its ARN might contain the ``service-role`` path prefix. When you only specify the name of the service role, AWS Batch assumes that your ARN doesn't use the ``service-role`` path prefix. Because of this, we recommend that you specify the full ARN of your service role when you create compute environments.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''The state of the compute environment.

        If the state is ``ENABLED`` , then the compute environment accepts jobs from a queue and can scale out automatically based on queues.

        If the state is ``ENABLED`` , then the AWS Batch scheduler can attempt to place jobs from an associated job queue on the compute resources within the environment. If the compute environment is managed, then it can scale its instances out or in automatically, based on the job queue demand.

        If the state is ``DISABLED`` , then the AWS Batch scheduler doesn't attempt to place jobs within the environment. Jobs in a ``STARTING`` or ``RUNNING`` state continue to progress normally. Managed compute environments in the ``DISABLED`` state don't scale out. However, they scale in to ``minvCpus`` value after instances become idle.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The tags applied to the compute environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def unmanagedv_cpus(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of vCPUs for an unmanaged compute environment.

        This parameter is only used for fair share scheduling to reserve vCPU capacity for new share identifiers. If this parameter isn't provided for a fair share job queue, no vCPU capacity is reserved.
        .. epigraph::

           This parameter is only supported when the ``type`` parameter is set to ``UNMANAGED`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-unmanagedvcpus
        '''
        result = self._values.get("unmanagedv_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def update_policy(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnComputeEnvironment.UpdatePolicyProperty]]:
        '''Specifies the infrastructure update policy for the compute environment.

        For more information about infrastructure updates, see `Updating compute environments <https://docs.aws.amazon.com/batch/latest/userguide/updating-compute-environments.html>`_ in the *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-updatepolicy
        '''
        result = self._values.get("update_policy")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnComputeEnvironment.UpdatePolicyProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnComputeEnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnJobDefinition(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.CfnJobDefinition",
):
    '''A CloudFormation ``AWS::Batch::JobDefinition``.

    The ``AWS::Batch::JobDefinition`` resource specifies the parameters for an AWS Batch job definition. For more information, see `Job Definitions <https://docs.aws.amazon.com/batch/latest/userguide/job_definitions.html>`_ in the ** .

    :cloudformationResource: AWS::Batch::JobDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_batch as batch
        
        # options: Any
        # parameters: Any
        # tags: Any
        
        cfn_job_definition = batch.CfnJobDefinition(self, "MyCfnJobDefinition",
            type="type",
        
            # the properties below are optional
            container_properties=batch.CfnJobDefinition.ContainerPropertiesProperty(
                image="image",
        
                # the properties below are optional
                command=["command"],
                environment=[batch.CfnJobDefinition.EnvironmentProperty(
                    name="name",
                    value="value"
                )],
                execution_role_arn="executionRoleArn",
                fargate_platform_configuration=batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                    platform_version="platformVersion"
                ),
                instance_type="instanceType",
                job_role_arn="jobRoleArn",
                linux_parameters=batch.CfnJobDefinition.LinuxParametersProperty(
                    devices=[batch.CfnJobDefinition.DeviceProperty(
                        container_path="containerPath",
                        host_path="hostPath",
                        permissions=["permissions"]
                    )],
                    init_process_enabled=False,
                    max_swap=123,
                    shared_memory_size=123,
                    swappiness=123,
                    tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                        container_path="containerPath",
                        size=123,
        
                        # the properties below are optional
                        mount_options=["mountOptions"]
                    )]
                ),
                log_configuration=batch.CfnJobDefinition.LogConfigurationProperty(
                    log_driver="logDriver",
        
                    # the properties below are optional
                    options=options,
                    secret_options=[batch.CfnJobDefinition.SecretProperty(
                        name="name",
                        value_from="valueFrom"
                    )]
                ),
                memory=123,
                mount_points=[batch.CfnJobDefinition.MountPointsProperty(
                    container_path="containerPath",
                    read_only=False,
                    source_volume="sourceVolume"
                )],
                network_configuration=batch.CfnJobDefinition.NetworkConfigurationProperty(
                    assign_public_ip="assignPublicIp"
                ),
                privileged=False,
                readonly_root_filesystem=False,
                resource_requirements=[batch.CfnJobDefinition.ResourceRequirementProperty(
                    type="type",
                    value="value"
                )],
                secrets=[batch.CfnJobDefinition.SecretProperty(
                    name="name",
                    value_from="valueFrom"
                )],
                ulimits=[batch.CfnJobDefinition.UlimitProperty(
                    hard_limit=123,
                    name="name",
                    soft_limit=123
                )],
                user="user",
                vcpus=123,
                volumes=[batch.CfnJobDefinition.VolumesProperty(
                    efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                        file_system_id="fileSystemId",
        
                        # the properties below are optional
                        authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                            access_point_id="accessPointId",
                            iam="iam"
                        ),
                        root_directory="rootDirectory",
                        transit_encryption="transitEncryption",
                        transit_encryption_port=123
                    ),
                    host=batch.CfnJobDefinition.VolumesHostProperty(
                        source_path="sourcePath"
                    ),
                    name="name"
                )]
            ),
            job_definition_name="jobDefinitionName",
            node_properties=batch.CfnJobDefinition.NodePropertiesProperty(
                main_node=123,
                node_range_properties=[batch.CfnJobDefinition.NodeRangePropertyProperty(
                    target_nodes="targetNodes",
        
                    # the properties below are optional
                    container=batch.CfnJobDefinition.ContainerPropertiesProperty(
                        image="image",
        
                        # the properties below are optional
                        command=["command"],
                        environment=[batch.CfnJobDefinition.EnvironmentProperty(
                            name="name",
                            value="value"
                        )],
                        execution_role_arn="executionRoleArn",
                        fargate_platform_configuration=batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                            platform_version="platformVersion"
                        ),
                        instance_type="instanceType",
                        job_role_arn="jobRoleArn",
                        linux_parameters=batch.CfnJobDefinition.LinuxParametersProperty(
                            devices=[batch.CfnJobDefinition.DeviceProperty(
                                container_path="containerPath",
                                host_path="hostPath",
                                permissions=["permissions"]
                            )],
                            init_process_enabled=False,
                            max_swap=123,
                            shared_memory_size=123,
                            swappiness=123,
                            tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                                container_path="containerPath",
                                size=123,
        
                                # the properties below are optional
                                mount_options=["mountOptions"]
                            )]
                        ),
                        log_configuration=batch.CfnJobDefinition.LogConfigurationProperty(
                            log_driver="logDriver",
        
                            # the properties below are optional
                            options=options,
                            secret_options=[batch.CfnJobDefinition.SecretProperty(
                                name="name",
                                value_from="valueFrom"
                            )]
                        ),
                        memory=123,
                        mount_points=[batch.CfnJobDefinition.MountPointsProperty(
                            container_path="containerPath",
                            read_only=False,
                            source_volume="sourceVolume"
                        )],
                        network_configuration=batch.CfnJobDefinition.NetworkConfigurationProperty(
                            assign_public_ip="assignPublicIp"
                        ),
                        privileged=False,
                        readonly_root_filesystem=False,
                        resource_requirements=[batch.CfnJobDefinition.ResourceRequirementProperty(
                            type="type",
                            value="value"
                        )],
                        secrets=[batch.CfnJobDefinition.SecretProperty(
                            name="name",
                            value_from="valueFrom"
                        )],
                        ulimits=[batch.CfnJobDefinition.UlimitProperty(
                            hard_limit=123,
                            name="name",
                            soft_limit=123
                        )],
                        user="user",
                        vcpus=123,
                        volumes=[batch.CfnJobDefinition.VolumesProperty(
                            efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                                file_system_id="fileSystemId",
        
                                # the properties below are optional
                                authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                                    access_point_id="accessPointId",
                                    iam="iam"
                                ),
                                root_directory="rootDirectory",
                                transit_encryption="transitEncryption",
                                transit_encryption_port=123
                            ),
                            host=batch.CfnJobDefinition.VolumesHostProperty(
                                source_path="sourcePath"
                            ),
                            name="name"
                        )]
                    )
                )],
                num_nodes=123
            ),
            parameters=parameters,
            platform_capabilities=["platformCapabilities"],
            propagate_tags=False,
            retry_strategy=batch.CfnJobDefinition.RetryStrategyProperty(
                attempts=123,
                evaluate_on_exit=[batch.CfnJobDefinition.EvaluateOnExitProperty(
                    action="action",
        
                    # the properties below are optional
                    on_exit_code="onExitCode",
                    on_reason="onReason",
                    on_status_reason="onStatusReason"
                )]
            ),
            scheduling_priority=123,
            tags=tags,
            timeout=batch.CfnJobDefinition.TimeoutProperty(
                attempt_duration_seconds=123
            )
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        type: builtins.str,
        container_properties: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]] = None,
        job_definition_name: typing.Optional[builtins.str] = None,
        node_properties: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodePropertiesProperty"]] = None,
        parameters: typing.Any = None,
        platform_capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        propagate_tags: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        retry_strategy: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.RetryStrategyProperty"]] = None,
        scheduling_priority: typing.Optional[jsii.Number] = None,
        tags: typing.Any = None,
        timeout: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TimeoutProperty"]] = None,
    ) -> None:
        '''Create a new ``AWS::Batch::JobDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param type: The type of job definition. For more information about multi-node parallel jobs, see `Creating a multi-node parallel job definition <https://docs.aws.amazon.com/batch/latest/userguide/multi-node-job-def.html>`_ in the *AWS Batch User Guide* . .. epigraph:: If the job is run on Fargate resources, then ``multinode`` isn't supported.
        :param container_properties: An object with various properties specific to container-based jobs.
        :param job_definition_name: The name of the job definition.
        :param node_properties: An object with various properties specific to multi-node parallel jobs. .. epigraph:: If the job runs on Fargate resources, then you must not specify ``nodeProperties`` ; use ``containerProperties`` instead.
        :param parameters: Default parameters or parameter substitution placeholders that are set in the job definition. Parameters are specified as a key-value pair mapping. Parameters in a ``SubmitJob`` request override any corresponding parameter defaults from the job definition. For more information about specifying parameters, see `Job definition parameters <https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html>`_ in the *AWS Batch User Guide* .
        :param platform_capabilities: The platform capabilities required by the job definition. If no value is specified, it defaults to ``EC2`` . Jobs run on Fargate resources specify ``FARGATE`` .
        :param propagate_tags: Specifies whether to propagate the tags from the job or job definition to the corresponding Amazon ECS task. If no value is specified, the tags aren't propagated. Tags can only be propagated to the tasks during task creation. For tags with the same name, job tags are given priority over job definitions tags. If the total number of combined tags from the job and job definition is over 50, the job is moved to the ``FAILED`` state.
        :param retry_strategy: The retry strategy to use for failed jobs that are submitted with this job definition.
        :param scheduling_priority: The scheduling priority of the job definition. This only affects jobs in job queues with a fair share policy. Jobs with a higher scheduling priority are scheduled before jobs with a lower scheduling priority.
        :param tags: The tags applied to the job definition.
        :param timeout: The timeout configuration for jobs that are submitted with this job definition. You can specify a timeout duration after which AWS Batch terminates your jobs if they haven't finished.
        '''
        props = CfnJobDefinitionProps(
            type=type,
            container_properties=container_properties,
            job_definition_name=job_definition_name,
            node_properties=node_properties,
            parameters=parameters,
            platform_capabilities=platform_capabilities,
            propagate_tags=propagate_tags,
            retry_strategy=retry_strategy,
            scheduling_priority=scheduling_priority,
            tags=tags,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''The tags applied to the job definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''Default parameters or parameter substitution placeholders that are set in the job definition.

        Parameters are specified as a key-value pair mapping. Parameters in a ``SubmitJob`` request override any corresponding parameter defaults from the job definition. For more information about specifying parameters, see `Job definition parameters <https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html>`_ in the *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Any) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of job definition.

        For more information about multi-node parallel jobs, see `Creating a multi-node parallel job definition <https://docs.aws.amazon.com/batch/latest/userguide/multi-node-job-def.html>`_ in the *AWS Batch User Guide* .
        .. epigraph::

           If the job is run on Fargate resources, then ``multinode`` isn't supported.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerProperties")
    def container_properties(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]]:
        '''An object with various properties specific to container-based jobs.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]], jsii.get(self, "containerProperties"))

    @container_properties.setter
    def container_properties(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]],
    ) -> None:
        jsii.set(self, "containerProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> typing.Optional[builtins.str]:
        '''The name of the job definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobDefinitionName"))

    @job_definition_name.setter
    def job_definition_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "jobDefinitionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeProperties")
    def node_properties(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodePropertiesProperty"]]:
        '''An object with various properties specific to multi-node parallel jobs.

        .. epigraph::

           If the job runs on Fargate resources, then you must not specify ``nodeProperties`` ; use ``containerProperties`` instead.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodePropertiesProperty"]], jsii.get(self, "nodeProperties"))

    @node_properties.setter
    def node_properties(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodePropertiesProperty"]],
    ) -> None:
        jsii.set(self, "nodeProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformCapabilities")
    def platform_capabilities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The platform capabilities required by the job definition.

        If no value is specified, it defaults to ``EC2`` . Jobs run on Fargate resources specify ``FARGATE`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-platformcapabilities
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "platformCapabilities"))

    @platform_capabilities.setter
    def platform_capabilities(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "platformCapabilities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagateTags")
    def propagate_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        '''Specifies whether to propagate the tags from the job or job definition to the corresponding Amazon ECS task.

        If no value is specified, the tags aren't propagated. Tags can only be propagated to the tasks during task creation. For tags with the same name, job tags are given priority over job definitions tags. If the total number of combined tags from the job and job definition is over 50, the job is moved to the ``FAILED`` state.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-propagatetags
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], jsii.get(self, "propagateTags"))

    @propagate_tags.setter
    def propagate_tags(
        self,
        value: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]],
    ) -> None:
        jsii.set(self, "propagateTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryStrategy")
    def retry_strategy(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.RetryStrategyProperty"]]:
        '''The retry strategy to use for failed jobs that are submitted with this job definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.RetryStrategyProperty"]], jsii.get(self, "retryStrategy"))

    @retry_strategy.setter
    def retry_strategy(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.RetryStrategyProperty"]],
    ) -> None:
        jsii.set(self, "retryStrategy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPriority")
    def scheduling_priority(self) -> typing.Optional[jsii.Number]:
        '''The scheduling priority of the job definition.

        This only affects jobs in job queues with a fair share policy. Jobs with a higher scheduling priority are scheduled before jobs with a lower scheduling priority.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-schedulingpriority
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "schedulingPriority"))

    @scheduling_priority.setter
    def scheduling_priority(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "schedulingPriority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TimeoutProperty"]]:
        '''The timeout configuration for jobs that are submitted with this job definition.

        You can specify a timeout duration after which AWS Batch terminates your jobs if they haven't finished.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TimeoutProperty"]], jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TimeoutProperty"]],
    ) -> None:
        jsii.set(self, "timeout", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.AuthorizationConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"access_point_id": "accessPointId", "iam": "iam"},
    )
    class AuthorizationConfigProperty:
        def __init__(
            self,
            *,
            access_point_id: typing.Optional[builtins.str] = None,
            iam: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The authorization configuration details for the Amazon EFS file system.

            :param access_point_id: The Amazon EFS access point ID to use. If an access point is specified, the root directory value specified in the ``EFSVolumeConfiguration`` must either be omitted or set to ``/`` which will enforce the path set on the EFS access point. If an access point is used, transit encryption must be enabled in the ``EFSVolumeConfiguration`` . For more information, see `Working with Amazon EFS access points <https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html>`_ in the *Amazon Elastic File System User Guide* .
            :param iam: Whether or not to use the AWS Batch job IAM role defined in a job definition when mounting the Amazon EFS file system. If enabled, transit encryption must be enabled in the ``EFSVolumeConfiguration`` . If this parameter is omitted, the default value of ``DISABLED`` is used. For more information, see `Using Amazon EFS access points <https://docs.aws.amazon.com/batch/latest/userguide/efs-volumes.html#efs-volume-accesspoints>`_ in the *AWS Batch User Guide* . EFS IAM authorization requires that ``TransitEncryption`` be ``ENABLED`` and that a ``JobRoleArn`` is specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-authorizationconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                authorization_config_property = batch.CfnJobDefinition.AuthorizationConfigProperty(
                    access_point_id="accessPointId",
                    iam="iam"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if access_point_id is not None:
                self._values["access_point_id"] = access_point_id
            if iam is not None:
                self._values["iam"] = iam

        @builtins.property
        def access_point_id(self) -> typing.Optional[builtins.str]:
            '''The Amazon EFS access point ID to use.

            If an access point is specified, the root directory value specified in the ``EFSVolumeConfiguration`` must either be omitted or set to ``/`` which will enforce the path set on the EFS access point. If an access point is used, transit encryption must be enabled in the ``EFSVolumeConfiguration`` . For more information, see `Working with Amazon EFS access points <https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html>`_ in the *Amazon Elastic File System User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-authorizationconfig.html#cfn-batch-jobdefinition-authorizationconfig-accesspointid
            '''
            result = self._values.get("access_point_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def iam(self) -> typing.Optional[builtins.str]:
            '''Whether or not to use the AWS Batch job IAM role defined in a job definition when mounting the Amazon EFS file system.

            If enabled, transit encryption must be enabled in the ``EFSVolumeConfiguration`` . If this parameter is omitted, the default value of ``DISABLED`` is used. For more information, see `Using Amazon EFS access points <https://docs.aws.amazon.com/batch/latest/userguide/efs-volumes.html#efs-volume-accesspoints>`_ in the *AWS Batch User Guide* . EFS IAM authorization requires that ``TransitEncryption`` be ``ENABLED`` and that a ``JobRoleArn`` is specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-authorizationconfig.html#cfn-batch-jobdefinition-authorizationconfig-iam
            '''
            result = self._values.get("iam")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AuthorizationConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ContainerPropertiesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "image": "image",
            "command": "command",
            "environment": "environment",
            "execution_role_arn": "executionRoleArn",
            "fargate_platform_configuration": "fargatePlatformConfiguration",
            "instance_type": "instanceType",
            "job_role_arn": "jobRoleArn",
            "linux_parameters": "linuxParameters",
            "log_configuration": "logConfiguration",
            "memory": "memory",
            "mount_points": "mountPoints",
            "network_configuration": "networkConfiguration",
            "privileged": "privileged",
            "readonly_root_filesystem": "readonlyRootFilesystem",
            "resource_requirements": "resourceRequirements",
            "secrets": "secrets",
            "ulimits": "ulimits",
            "user": "user",
            "vcpus": "vcpus",
            "volumes": "volumes",
        },
    )
    class ContainerPropertiesProperty:
        def __init__(
            self,
            *,
            image: builtins.str,
            command: typing.Optional[typing.Sequence[builtins.str]] = None,
            environment: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EnvironmentProperty"]]]] = None,
            execution_role_arn: typing.Optional[builtins.str] = None,
            fargate_platform_configuration: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.FargatePlatformConfigurationProperty"]] = None,
            instance_type: typing.Optional[builtins.str] = None,
            job_role_arn: typing.Optional[builtins.str] = None,
            linux_parameters: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.LinuxParametersProperty"]] = None,
            log_configuration: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.LogConfigurationProperty"]] = None,
            memory: typing.Optional[jsii.Number] = None,
            mount_points: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.MountPointsProperty"]]]] = None,
            network_configuration: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NetworkConfigurationProperty"]] = None,
            privileged: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            readonly_root_filesystem: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            resource_requirements: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ResourceRequirementProperty"]]]] = None,
            secrets: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.SecretProperty"]]]] = None,
            ulimits: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.UlimitProperty"]]]] = None,
            user: typing.Optional[builtins.str] = None,
            vcpus: typing.Optional[jsii.Number] = None,
            volumes: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesProperty"]]]] = None,
        ) -> None:
            '''Container properties are used in job definitions to describe the container that's launched as part of a job.

            :param image: The image used to start a container. This string is passed directly to the Docker daemon. Images in the Docker Hub registry are available by default. Other repositories are specified with ``*repository-url* / *image* : *tag*`` . Up to 255 letters (uppercase and lowercase), numbers, hyphens, underscores, colons, periods, forward slashes, and number signs are allowed. This parameter maps to ``Image`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``IMAGE`` parameter of `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . .. epigraph:: Docker image architecture must match the processor architecture of the compute resources that they're scheduled on. For example, ARM-based Docker images can only run on ARM-based compute resources. - Images in Amazon ECR Public repositories use the full ``registry/repository[:tag]`` or ``registry/repository[@digest]`` naming conventions. For example, ``public.ecr.aws/ *registry_alias* / *my-web-app* : *latest*`` . - Images in Amazon ECR repositories use the full registry and repository URI (for example, ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>`` ). - Images in official repositories on Docker Hub use a single name (for example, ``ubuntu`` or ``mongo`` ). - Images in other repositories on Docker Hub are qualified with an organization name (for example, ``amazon/amazon-ecs-agent`` ). - Images in other online repositories are qualified further by a domain name (for example, ``quay.io/assemblyline/ubuntu`` ).
            :param command: The command that's passed to the container. This parameter maps to ``Cmd`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``COMMAND`` parameter to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . For more information, see `https://docs.docker.com/engine/reference/builder/#cmd <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/builder/#cmd>`_ .
            :param environment: The environment variables to pass to a container. This parameter maps to ``Env`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--env`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . .. epigraph:: We don't recommend using plaintext environment variables for sensitive information, such as credential data. > Environment variables must not start with ``AWS_BATCH`` ; this naming convention is reserved for variables that are set by the AWS Batch service.
            :param execution_role_arn: The Amazon Resource Name (ARN) of the execution role that AWS Batch can assume. For jobs that run on Fargate resources, you must provide an execution role. For more information, see `AWS Batch execution IAM role <https://docs.aws.amazon.com/batch/latest/userguide/execution-IAM-role.html>`_ in the *AWS Batch User Guide* .
            :param fargate_platform_configuration: The platform configuration for jobs that are running on Fargate resources. Jobs that are running on EC2 resources must not specify this parameter.
            :param instance_type: The instance type to use for a multi-node parallel job. All node groups in a multi-node parallel job must use the same instance type. .. epigraph:: This parameter isn't applicable to single-node container jobs or jobs that run on Fargate resources, and shouldn't be provided.
            :param job_role_arn: The Amazon Resource Name (ARN) of the IAM role that the container can assume for AWS permissions. For more information, see `IAM roles for tasks <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
            :param linux_parameters: Linux-specific modifications that are applied to the container, such as details for device mappings.
            :param log_configuration: The log configuration specification for the container. This parameter maps to ``LogConfig`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--log-driver`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . By default, containers use the same logging driver that the Docker daemon uses. However the container might use a different logging driver than the Docker daemon by specifying a log driver with this parameter in the container definition. To use a different logging driver for a container, the log system must be configured properly on the container instance (or on a different log server for remote logging options). For more information on the options for different supported log drivers, see `Configure logging drivers <https://docs.aws.amazon.com/https://docs.docker.com/engine/admin/logging/overview/>`_ in the Docker documentation. .. epigraph:: AWS Batch currently supports a subset of the logging drivers available to the Docker daemon (shown in the ``LogConfiguration`` data type). This parameter requires version 1.18 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"`` .. epigraph:: The Amazon ECS container agent running on a container instance must register the logging drivers available on that instance with the ``ECS_AVAILABLE_LOGGING_DRIVERS`` environment variable before containers placed on that instance can use these log configuration options. For more information, see `Amazon ECS container agent configuration <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-config.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
            :param memory: This parameter is deprecated, use ``resourceRequirements`` to specify the memory requirements for the job definition. It's not supported for jobs running on Fargate resources. For jobs running on EC2 resources, it specifies the memory hard limit (in MiB) for a container. If your container attempts to exceed the specified number, it's terminated. You must specify at least 4 MiB of memory for a job using this parameter. The memory hard limit can be specified in several places. It must be specified for each node at least once.
            :param mount_points: The mount points for data volumes in your container. This parameter maps to ``Volumes`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--volume`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            :param network_configuration: The network configuration for jobs that are running on Fargate resources. Jobs that are running on EC2 resources must not specify this parameter.
            :param privileged: When this parameter is true, the container is given elevated permissions on the host container instance (similar to the ``root`` user). This parameter maps to ``Privileged`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--privileged`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . The default value is false. .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided, or specified as false.
            :param readonly_root_filesystem: When this parameter is true, the container is given read-only access to its root file system. This parameter maps to ``ReadonlyRootfs`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--read-only`` option to ``docker run`` .
            :param resource_requirements: The type and amount of resources to assign to a container. The supported resources include ``GPU`` , ``MEMORY`` , and ``VCPU`` .
            :param secrets: The secrets for the container. For more information, see `Specifying sensitive data <https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data.html>`_ in the *AWS Batch User Guide* .
            :param ulimits: A list of ``ulimits`` to set in the container. This parameter maps to ``Ulimits`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--ulimit`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.
            :param user: The user name to use inside the container. This parameter maps to ``User`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--user`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            :param vcpus: This parameter is deprecated, use ``resourceRequirements`` to specify the vCPU requirements for the job definition. It's not supported for jobs running on Fargate resources. For jobs running on EC2 resources, it specifies the number of vCPUs reserved for the job. Each vCPU is equivalent to 1,024 CPU shares. This parameter maps to ``CpuShares`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--cpu-shares`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . The number of vCPUs must be specified but can be specified in several places. You must specify it at least once for each node.
            :param volumes: A list of data volumes used in a job.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                # options: Any
                
                container_properties_property = batch.CfnJobDefinition.ContainerPropertiesProperty(
                    image="image",
                
                    # the properties below are optional
                    command=["command"],
                    environment=[batch.CfnJobDefinition.EnvironmentProperty(
                        name="name",
                        value="value"
                    )],
                    execution_role_arn="executionRoleArn",
                    fargate_platform_configuration=batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                        platform_version="platformVersion"
                    ),
                    instance_type="instanceType",
                    job_role_arn="jobRoleArn",
                    linux_parameters=batch.CfnJobDefinition.LinuxParametersProperty(
                        devices=[batch.CfnJobDefinition.DeviceProperty(
                            container_path="containerPath",
                            host_path="hostPath",
                            permissions=["permissions"]
                        )],
                        init_process_enabled=False,
                        max_swap=123,
                        shared_memory_size=123,
                        swappiness=123,
                        tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                            container_path="containerPath",
                            size=123,
                
                            # the properties below are optional
                            mount_options=["mountOptions"]
                        )]
                    ),
                    log_configuration=batch.CfnJobDefinition.LogConfigurationProperty(
                        log_driver="logDriver",
                
                        # the properties below are optional
                        options=options,
                        secret_options=[batch.CfnJobDefinition.SecretProperty(
                            name="name",
                            value_from="valueFrom"
                        )]
                    ),
                    memory=123,
                    mount_points=[batch.CfnJobDefinition.MountPointsProperty(
                        container_path="containerPath",
                        read_only=False,
                        source_volume="sourceVolume"
                    )],
                    network_configuration=batch.CfnJobDefinition.NetworkConfigurationProperty(
                        assign_public_ip="assignPublicIp"
                    ),
                    privileged=False,
                    readonly_root_filesystem=False,
                    resource_requirements=[batch.CfnJobDefinition.ResourceRequirementProperty(
                        type="type",
                        value="value"
                    )],
                    secrets=[batch.CfnJobDefinition.SecretProperty(
                        name="name",
                        value_from="valueFrom"
                    )],
                    ulimits=[batch.CfnJobDefinition.UlimitProperty(
                        hard_limit=123,
                        name="name",
                        soft_limit=123
                    )],
                    user="user",
                    vcpus=123,
                    volumes=[batch.CfnJobDefinition.VolumesProperty(
                        efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                            file_system_id="fileSystemId",
                
                            # the properties below are optional
                            authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                                access_point_id="accessPointId",
                                iam="iam"
                            ),
                            root_directory="rootDirectory",
                            transit_encryption="transitEncryption",
                            transit_encryption_port=123
                        ),
                        host=batch.CfnJobDefinition.VolumesHostProperty(
                            source_path="sourcePath"
                        ),
                        name="name"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "image": image,
            }
            if command is not None:
                self._values["command"] = command
            if environment is not None:
                self._values["environment"] = environment
            if execution_role_arn is not None:
                self._values["execution_role_arn"] = execution_role_arn
            if fargate_platform_configuration is not None:
                self._values["fargate_platform_configuration"] = fargate_platform_configuration
            if instance_type is not None:
                self._values["instance_type"] = instance_type
            if job_role_arn is not None:
                self._values["job_role_arn"] = job_role_arn
            if linux_parameters is not None:
                self._values["linux_parameters"] = linux_parameters
            if log_configuration is not None:
                self._values["log_configuration"] = log_configuration
            if memory is not None:
                self._values["memory"] = memory
            if mount_points is not None:
                self._values["mount_points"] = mount_points
            if network_configuration is not None:
                self._values["network_configuration"] = network_configuration
            if privileged is not None:
                self._values["privileged"] = privileged
            if readonly_root_filesystem is not None:
                self._values["readonly_root_filesystem"] = readonly_root_filesystem
            if resource_requirements is not None:
                self._values["resource_requirements"] = resource_requirements
            if secrets is not None:
                self._values["secrets"] = secrets
            if ulimits is not None:
                self._values["ulimits"] = ulimits
            if user is not None:
                self._values["user"] = user
            if vcpus is not None:
                self._values["vcpus"] = vcpus
            if volumes is not None:
                self._values["volumes"] = volumes

        @builtins.property
        def image(self) -> builtins.str:
            '''The image used to start a container.

            This string is passed directly to the Docker daemon. Images in the Docker Hub registry are available by default. Other repositories are specified with ``*repository-url* / *image* : *tag*`` . Up to 255 letters (uppercase and lowercase), numbers, hyphens, underscores, colons, periods, forward slashes, and number signs are allowed. This parameter maps to ``Image`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``IMAGE`` parameter of `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            .. epigraph::

               Docker image architecture must match the processor architecture of the compute resources that they're scheduled on. For example, ARM-based Docker images can only run on ARM-based compute resources.

            - Images in Amazon ECR Public repositories use the full ``registry/repository[:tag]`` or ``registry/repository[@digest]`` naming conventions. For example, ``public.ecr.aws/ *registry_alias* / *my-web-app* : *latest*`` .
            - Images in Amazon ECR repositories use the full registry and repository URI (for example, ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>`` ).
            - Images in official repositories on Docker Hub use a single name (for example, ``ubuntu`` or ``mongo`` ).
            - Images in other repositories on Docker Hub are qualified with an organization name (for example, ``amazon/amazon-ecs-agent`` ).
            - Images in other online repositories are qualified further by a domain name (for example, ``quay.io/assemblyline/ubuntu`` ).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-image
            '''
            result = self._values.get("image")
            assert result is not None, "Required property 'image' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def command(self) -> typing.Optional[typing.List[builtins.str]]:
            '''The command that's passed to the container.

            This parameter maps to ``Cmd`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``COMMAND`` parameter to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . For more information, see `https://docs.docker.com/engine/reference/builder/#cmd <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/builder/#cmd>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-command
            '''
            result = self._values.get("command")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def environment(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EnvironmentProperty"]]]]:
            '''The environment variables to pass to a container.

            This parameter maps to ``Env`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--env`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            .. epigraph::

               We don't recommend using plaintext environment variables for sensitive information, such as credential data. > Environment variables must not start with ``AWS_BATCH`` ; this naming convention is reserved for variables that are set by the AWS Batch service.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-environment
            '''
            result = self._values.get("environment")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EnvironmentProperty"]]]], result)

        @builtins.property
        def execution_role_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) of the execution role that AWS Batch can assume.

            For jobs that run on Fargate resources, you must provide an execution role. For more information, see `AWS Batch execution IAM role <https://docs.aws.amazon.com/batch/latest/userguide/execution-IAM-role.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-executionrolearn
            '''
            result = self._values.get("execution_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def fargate_platform_configuration(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.FargatePlatformConfigurationProperty"]]:
            '''The platform configuration for jobs that are running on Fargate resources.

            Jobs that are running on EC2 resources must not specify this parameter.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-fargateplatformconfiguration
            '''
            result = self._values.get("fargate_platform_configuration")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.FargatePlatformConfigurationProperty"]], result)

        @builtins.property
        def instance_type(self) -> typing.Optional[builtins.str]:
            '''The instance type to use for a multi-node parallel job.

            All node groups in a multi-node parallel job must use the same instance type.
            .. epigraph::

               This parameter isn't applicable to single-node container jobs or jobs that run on Fargate resources, and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-instancetype
            '''
            result = self._values.get("instance_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def job_role_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) of the IAM role that the container can assume for AWS permissions.

            For more information, see `IAM roles for tasks <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html>`_ in the *Amazon Elastic Container Service Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-jobrolearn
            '''
            result = self._values.get("job_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def linux_parameters(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.LinuxParametersProperty"]]:
            '''Linux-specific modifications that are applied to the container, such as details for device mappings.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-linuxparameters
            '''
            result = self._values.get("linux_parameters")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.LinuxParametersProperty"]], result)

        @builtins.property
        def log_configuration(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.LogConfigurationProperty"]]:
            '''The log configuration specification for the container.

            This parameter maps to ``LogConfig`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--log-driver`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . By default, containers use the same logging driver that the Docker daemon uses. However the container might use a different logging driver than the Docker daemon by specifying a log driver with this parameter in the container definition. To use a different logging driver for a container, the log system must be configured properly on the container instance (or on a different log server for remote logging options). For more information on the options for different supported log drivers, see `Configure logging drivers <https://docs.aws.amazon.com/https://docs.docker.com/engine/admin/logging/overview/>`_ in the Docker documentation.
            .. epigraph::

               AWS Batch currently supports a subset of the logging drivers available to the Docker daemon (shown in the ``LogConfiguration`` data type).

            This parameter requires version 1.18 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"``
            .. epigraph::

               The Amazon ECS container agent running on a container instance must register the logging drivers available on that instance with the ``ECS_AVAILABLE_LOGGING_DRIVERS`` environment variable before containers placed on that instance can use these log configuration options. For more information, see `Amazon ECS container agent configuration <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-config.html>`_ in the *Amazon Elastic Container Service Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-logconfiguration
            '''
            result = self._values.get("log_configuration")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.LogConfigurationProperty"]], result)

        @builtins.property
        def memory(self) -> typing.Optional[jsii.Number]:
            '''This parameter is deprecated, use ``resourceRequirements`` to specify the memory requirements for the job definition.

            It's not supported for jobs running on Fargate resources. For jobs running on EC2 resources, it specifies the memory hard limit (in MiB) for a container. If your container attempts to exceed the specified number, it's terminated. You must specify at least 4 MiB of memory for a job using this parameter. The memory hard limit can be specified in several places. It must be specified for each node at least once.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-memory
            '''
            result = self._values.get("memory")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def mount_points(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.MountPointsProperty"]]]]:
            '''The mount points for data volumes in your container.

            This parameter maps to ``Volumes`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--volume`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-mountpoints
            '''
            result = self._values.get("mount_points")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.MountPointsProperty"]]]], result)

        @builtins.property
        def network_configuration(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NetworkConfigurationProperty"]]:
            '''The network configuration for jobs that are running on Fargate resources.

            Jobs that are running on EC2 resources must not specify this parameter.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-networkconfiguration
            '''
            result = self._values.get("network_configuration")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NetworkConfigurationProperty"]], result)

        @builtins.property
        def privileged(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            '''When this parameter is true, the container is given elevated permissions on the host container instance (similar to the ``root`` user).

            This parameter maps to ``Privileged`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--privileged`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . The default value is false.
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided, or specified as false.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-privileged
            '''
            result = self._values.get("privileged")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

        @builtins.property
        def readonly_root_filesystem(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            '''When this parameter is true, the container is given read-only access to its root file system.

            This parameter maps to ``ReadonlyRootfs`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--read-only`` option to ``docker run`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-readonlyrootfilesystem
            '''
            result = self._values.get("readonly_root_filesystem")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

        @builtins.property
        def resource_requirements(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ResourceRequirementProperty"]]]]:
            '''The type and amount of resources to assign to a container.

            The supported resources include ``GPU`` , ``MEMORY`` , and ``VCPU`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-resourcerequirements
            '''
            result = self._values.get("resource_requirements")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ResourceRequirementProperty"]]]], result)

        @builtins.property
        def secrets(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.SecretProperty"]]]]:
            '''The secrets for the container.

            For more information, see `Specifying sensitive data <https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-secrets
            '''
            result = self._values.get("secrets")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.SecretProperty"]]]], result)

        @builtins.property
        def ulimits(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.UlimitProperty"]]]]:
            '''A list of ``ulimits`` to set in the container.

            This parameter maps to ``Ulimits`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--ulimit`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-ulimits
            '''
            result = self._values.get("ulimits")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.UlimitProperty"]]]], result)

        @builtins.property
        def user(self) -> typing.Optional[builtins.str]:
            '''The user name to use inside the container.

            This parameter maps to ``User`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--user`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-user
            '''
            result = self._values.get("user")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def vcpus(self) -> typing.Optional[jsii.Number]:
            '''This parameter is deprecated, use ``resourceRequirements`` to specify the vCPU requirements for the job definition.

            It's not supported for jobs running on Fargate resources. For jobs running on EC2 resources, it specifies the number of vCPUs reserved for the job.

            Each vCPU is equivalent to 1,024 CPU shares. This parameter maps to ``CpuShares`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--cpu-shares`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . The number of vCPUs must be specified but can be specified in several places. You must specify it at least once for each node.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-vcpus
            '''
            result = self._values.get("vcpus")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def volumes(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesProperty"]]]]:
            '''A list of data volumes used in a job.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-volumes
            '''
            result = self._values.get("volumes")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ContainerPropertiesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.DeviceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "container_path": "containerPath",
            "host_path": "hostPath",
            "permissions": "permissions",
        },
    )
    class DeviceProperty:
        def __init__(
            self,
            *,
            container_path: typing.Optional[builtins.str] = None,
            host_path: typing.Optional[builtins.str] = None,
            permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''An object representing a container instance host device.

            .. epigraph::

               This object isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :param container_path: The path inside the container that's used to expose the host device. By default, the ``hostPath`` value is used.
            :param host_path: The path for the device on the host container instance.
            :param permissions: The explicit permissions to provide to the container for the device. By default, the container has permissions for ``read`` , ``write`` , and ``mknod`` for the device.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                device_property = batch.CfnJobDefinition.DeviceProperty(
                    container_path="containerPath",
                    host_path="hostPath",
                    permissions=["permissions"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if container_path is not None:
                self._values["container_path"] = container_path
            if host_path is not None:
                self._values["host_path"] = host_path
            if permissions is not None:
                self._values["permissions"] = permissions

        @builtins.property
        def container_path(self) -> typing.Optional[builtins.str]:
            '''The path inside the container that's used to expose the host device.

            By default, the ``hostPath`` value is used.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html#cfn-batch-jobdefinition-device-containerpath
            '''
            result = self._values.get("container_path")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def host_path(self) -> typing.Optional[builtins.str]:
            '''The path for the device on the host container instance.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html#cfn-batch-jobdefinition-device-hostpath
            '''
            result = self._values.get("host_path")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def permissions(self) -> typing.Optional[typing.List[builtins.str]]:
            '''The explicit permissions to provide to the container for the device.

            By default, the container has permissions for ``read`` , ``write`` , and ``mknod`` for the device.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-device.html#cfn-batch-jobdefinition-device-permissions
            '''
            result = self._values.get("permissions")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DeviceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.EfsVolumeConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "file_system_id": "fileSystemId",
            "authorization_config": "authorizationConfig",
            "root_directory": "rootDirectory",
            "transit_encryption": "transitEncryption",
            "transit_encryption_port": "transitEncryptionPort",
        },
    )
    class EfsVolumeConfigurationProperty:
        def __init__(
            self,
            *,
            file_system_id: builtins.str,
            authorization_config: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.AuthorizationConfigProperty"]] = None,
            root_directory: typing.Optional[builtins.str] = None,
            transit_encryption: typing.Optional[builtins.str] = None,
            transit_encryption_port: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''This is used when you're using an Amazon Elastic File System file system for job storage.

            For more information, see `Amazon EFS Volumes <https://docs.aws.amazon.com/batch/latest/userguide/efs-volumes.html>`_ in the *AWS Batch User Guide* .

            :param file_system_id: The Amazon EFS file system ID to use.
            :param authorization_config: The authorization configuration details for the Amazon EFS file system.
            :param root_directory: The directory within the Amazon EFS file system to mount as the root directory inside the host. If this parameter is omitted, the root of the Amazon EFS volume is used instead. Specifying ``/`` has the same effect as omitting this parameter. The maximum length is 4,096 characters. .. epigraph:: If an EFS access point is specified in the ``authorizationConfig`` , the root directory parameter must either be omitted or set to ``/`` , which enforces the path set on the Amazon EFS access point.
            :param transit_encryption: Determines whether to enable encryption for Amazon EFS data in transit between the Amazon ECS host and the Amazon EFS server. Transit encryption must be enabled if Amazon EFS IAM authorization is used. If this parameter is omitted, the default value of ``DISABLED`` is used. For more information, see `Encrypting data in transit <https://docs.aws.amazon.com/efs/latest/ug/encryption-in-transit.html>`_ in the *Amazon Elastic File System User Guide* .
            :param transit_encryption_port: The port to use when sending encrypted data between the Amazon ECS host and the Amazon EFS server. If you don't specify a transit encryption port, it uses the port selection strategy that the Amazon EFS mount helper uses. The value must be between 0 and 65,535. For more information, see `EFS mount helper <https://docs.aws.amazon.com/efs/latest/ug/efs-mount-helper.html>`_ in the *Amazon Elastic File System User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-efsvolumeconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                efs_volume_configuration_property = batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                    file_system_id="fileSystemId",
                
                    # the properties below are optional
                    authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                        access_point_id="accessPointId",
                        iam="iam"
                    ),
                    root_directory="rootDirectory",
                    transit_encryption="transitEncryption",
                    transit_encryption_port=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "file_system_id": file_system_id,
            }
            if authorization_config is not None:
                self._values["authorization_config"] = authorization_config
            if root_directory is not None:
                self._values["root_directory"] = root_directory
            if transit_encryption is not None:
                self._values["transit_encryption"] = transit_encryption
            if transit_encryption_port is not None:
                self._values["transit_encryption_port"] = transit_encryption_port

        @builtins.property
        def file_system_id(self) -> builtins.str:
            '''The Amazon EFS file system ID to use.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-efsvolumeconfiguration.html#cfn-batch-jobdefinition-efsvolumeconfiguration-filesystemid
            '''
            result = self._values.get("file_system_id")
            assert result is not None, "Required property 'file_system_id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def authorization_config(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.AuthorizationConfigProperty"]]:
            '''The authorization configuration details for the Amazon EFS file system.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-efsvolumeconfiguration.html#cfn-batch-jobdefinition-efsvolumeconfiguration-authorizationconfig
            '''
            result = self._values.get("authorization_config")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.AuthorizationConfigProperty"]], result)

        @builtins.property
        def root_directory(self) -> typing.Optional[builtins.str]:
            '''The directory within the Amazon EFS file system to mount as the root directory inside the host.

            If this parameter is omitted, the root of the Amazon EFS volume is used instead. Specifying ``/`` has the same effect as omitting this parameter. The maximum length is 4,096 characters.
            .. epigraph::

               If an EFS access point is specified in the ``authorizationConfig`` , the root directory parameter must either be omitted or set to ``/`` , which enforces the path set on the Amazon EFS access point.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-efsvolumeconfiguration.html#cfn-batch-jobdefinition-efsvolumeconfiguration-rootdirectory
            '''
            result = self._values.get("root_directory")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def transit_encryption(self) -> typing.Optional[builtins.str]:
            '''Determines whether to enable encryption for Amazon EFS data in transit between the Amazon ECS host and the Amazon EFS server.

            Transit encryption must be enabled if Amazon EFS IAM authorization is used. If this parameter is omitted, the default value of ``DISABLED`` is used. For more information, see `Encrypting data in transit <https://docs.aws.amazon.com/efs/latest/ug/encryption-in-transit.html>`_ in the *Amazon Elastic File System User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-efsvolumeconfiguration.html#cfn-batch-jobdefinition-efsvolumeconfiguration-transitencryption
            '''
            result = self._values.get("transit_encryption")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def transit_encryption_port(self) -> typing.Optional[jsii.Number]:
            '''The port to use when sending encrypted data between the Amazon ECS host and the Amazon EFS server.

            If you don't specify a transit encryption port, it uses the port selection strategy that the Amazon EFS mount helper uses. The value must be between 0 and 65,535. For more information, see `EFS mount helper <https://docs.aws.amazon.com/efs/latest/ug/efs-mount-helper.html>`_ in the *Amazon Elastic File System User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-efsvolumeconfiguration.html#cfn-batch-jobdefinition-efsvolumeconfiguration-transitencryptionport
            '''
            result = self._values.get("transit_encryption_port")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EfsVolumeConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.EnvironmentProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "value": "value"},
    )
    class EnvironmentProperty:
        def __init__(
            self,
            *,
            name: typing.Optional[builtins.str] = None,
            value: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The Environment property type specifies environment variables to use in a job definition.

            :param name: The name of the environment variable.
            :param value: The value of the environment variable.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                environment_property = batch.CfnJobDefinition.EnvironmentProperty(
                    name="name",
                    value="value"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if name is not None:
                self._values["name"] = name
            if value is not None:
                self._values["value"] = value

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''The name of the environment variable.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def value(self) -> typing.Optional[builtins.str]:
            '''The value of the environment variable.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-value
            '''
            result = self._values.get("value")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnvironmentProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.EvaluateOnExitProperty",
        jsii_struct_bases=[],
        name_mapping={
            "action": "action",
            "on_exit_code": "onExitCode",
            "on_reason": "onReason",
            "on_status_reason": "onStatusReason",
        },
    )
    class EvaluateOnExitProperty:
        def __init__(
            self,
            *,
            action: builtins.str,
            on_exit_code: typing.Optional[builtins.str] = None,
            on_reason: typing.Optional[builtins.str] = None,
            on_status_reason: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Specifies a set of conditions to be met, and an action to take ( ``RETRY`` or ``EXIT`` ) if all conditions are met.

            :param action: Specifies the action to take if all of the specified conditions ( ``onStatusReason`` , ``onReason`` , and ``onExitCode`` ) are met. The values aren't case sensitive.
            :param on_exit_code: Contains a glob pattern to match against the decimal representation of the ``ExitCode`` returned for a job. The pattern can be up to 512 characters in length. It can contain only numbers, and can optionally end with an asterisk (*) so that only the start of the string needs to be an exact match. The string can be between 1 and 512 characters in length.
            :param on_reason: Contains a glob pattern to match against the ``Reason`` returned for a job. The pattern can be up to 512 characters in length. It can contain letters, numbers, periods (.), colons (:), and white space (including spaces and tabs). It can optionally end with an asterisk (*) so that only the start of the string needs to be an exact match. The string can be between 1 and 512 characters in length.
            :param on_status_reason: Contains a glob pattern to match against the ``StatusReason`` returned for a job. The pattern can be up to 512 characters in length. It can contain letters, numbers, periods (.), colons (:), and white space (including spaces or tabs). It can optionally end with an asterisk (*) so that only the start of the string needs to be an exact match. The string can be between 1 and 512 characters in length.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-evaluateonexit.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                evaluate_on_exit_property = batch.CfnJobDefinition.EvaluateOnExitProperty(
                    action="action",
                
                    # the properties below are optional
                    on_exit_code="onExitCode",
                    on_reason="onReason",
                    on_status_reason="onStatusReason"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "action": action,
            }
            if on_exit_code is not None:
                self._values["on_exit_code"] = on_exit_code
            if on_reason is not None:
                self._values["on_reason"] = on_reason
            if on_status_reason is not None:
                self._values["on_status_reason"] = on_status_reason

        @builtins.property
        def action(self) -> builtins.str:
            '''Specifies the action to take if all of the specified conditions ( ``onStatusReason`` , ``onReason`` , and ``onExitCode`` ) are met.

            The values aren't case sensitive.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-evaluateonexit.html#cfn-batch-jobdefinition-evaluateonexit-action
            '''
            result = self._values.get("action")
            assert result is not None, "Required property 'action' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def on_exit_code(self) -> typing.Optional[builtins.str]:
            '''Contains a glob pattern to match against the decimal representation of the ``ExitCode`` returned for a job.

            The pattern can be up to 512 characters in length. It can contain only numbers, and can optionally end with an asterisk (*) so that only the start of the string needs to be an exact match.

            The string can be between 1 and 512 characters in length.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-evaluateonexit.html#cfn-batch-jobdefinition-evaluateonexit-onexitcode
            '''
            result = self._values.get("on_exit_code")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def on_reason(self) -> typing.Optional[builtins.str]:
            '''Contains a glob pattern to match against the ``Reason`` returned for a job.

            The pattern can be up to 512 characters in length. It can contain letters, numbers, periods (.), colons (:), and white space (including spaces and tabs). It can optionally end with an asterisk (*) so that only the start of the string needs to be an exact match.

            The string can be between 1 and 512 characters in length.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-evaluateonexit.html#cfn-batch-jobdefinition-evaluateonexit-onreason
            '''
            result = self._values.get("on_reason")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def on_status_reason(self) -> typing.Optional[builtins.str]:
            '''Contains a glob pattern to match against the ``StatusReason`` returned for a job.

            The pattern can be up to 512 characters in length. It can contain letters, numbers, periods (.), colons (:), and white space (including spaces or tabs). It can optionally end with an asterisk (*) so that only the start of the string needs to be an exact match.

            The string can be between 1 and 512 characters in length.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-evaluateonexit.html#cfn-batch-jobdefinition-evaluateonexit-onstatusreason
            '''
            result = self._values.get("on_status_reason")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EvaluateOnExitProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.FargatePlatformConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"platform_version": "platformVersion"},
    )
    class FargatePlatformConfigurationProperty:
        def __init__(
            self,
            *,
            platform_version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The platform configuration for jobs that are running on Fargate resources.

            Jobs that run on EC2 resources must not specify this parameter.

            :param platform_version: The AWS Fargate platform version where the jobs are running. A platform version is specified only for jobs that are running on Fargate resources. If one isn't specified, the ``LATEST`` platform version is used by default. This uses a recent, approved version of the AWS Fargate platform for compute resources. For more information, see `AWS Fargate platform versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the *Amazon Elastic Container Service Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-fargateplatformconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                fargate_platform_configuration_property = batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                    platform_version="platformVersion"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if platform_version is not None:
                self._values["platform_version"] = platform_version

        @builtins.property
        def platform_version(self) -> typing.Optional[builtins.str]:
            '''The AWS Fargate platform version where the jobs are running.

            A platform version is specified only for jobs that are running on Fargate resources. If one isn't specified, the ``LATEST`` platform version is used by default. This uses a recent, approved version of the AWS Fargate platform for compute resources. For more information, see `AWS Fargate platform versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the *Amazon Elastic Container Service Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-fargateplatformconfiguration.html#cfn-batch-jobdefinition-containerproperties-fargateplatformconfiguration-platformversion
            '''
            result = self._values.get("platform_version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FargatePlatformConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.LinuxParametersProperty",
        jsii_struct_bases=[],
        name_mapping={
            "devices": "devices",
            "init_process_enabled": "initProcessEnabled",
            "max_swap": "maxSwap",
            "shared_memory_size": "sharedMemorySize",
            "swappiness": "swappiness",
            "tmpfs": "tmpfs",
        },
    )
    class LinuxParametersProperty:
        def __init__(
            self,
            *,
            devices: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.DeviceProperty"]]]] = None,
            init_process_enabled: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            max_swap: typing.Optional[jsii.Number] = None,
            shared_memory_size: typing.Optional[jsii.Number] = None,
            swappiness: typing.Optional[jsii.Number] = None,
            tmpfs: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TmpfsProperty"]]]] = None,
        ) -> None:
            '''Linux-specific modifications that are applied to the container, such as details for device mappings.

            :param devices: Any host devices to expose to the container. This parameter maps to ``Devices`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--device`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.
            :param init_process_enabled: If true, run an ``init`` process inside the container that forwards signals and reaps processes. This parameter maps to the ``--init`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . This parameter requires version 1.25 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"``
            :param max_swap: The total amount of swap memory (in MiB) a container can use. This parameter is translated to the ``--memory-swap`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ where the value is the sum of the container memory plus the ``maxSwap`` value. For more information, see ```--memory-swap`` details <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/resource_constraints/#--memory-swap-details>`_ in the Docker documentation. If a ``maxSwap`` value of ``0`` is specified, the container doesn't use swap. Accepted values are ``0`` or any positive integer. If the ``maxSwap`` parameter is omitted, the container doesn't use the swap configuration for the container instance it is running on. A ``maxSwap`` value must be set for the ``swappiness`` parameter to be used. .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.
            :param shared_memory_size: The value for the size (in MiB) of the ``/dev/shm`` volume. This parameter maps to the ``--shm-size`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.
            :param swappiness: This allows you to tune a container's memory swappiness behavior. A ``swappiness`` value of ``0`` causes swapping not to happen unless absolutely necessary. A ``swappiness`` value of ``100`` causes pages to be swapped very aggressively. Accepted values are whole numbers between ``0`` and ``100`` . If the ``swappiness`` parameter isn't specified, a default value of ``60`` is used. If a value isn't specified for ``maxSwap`` , then this parameter is ignored. If ``maxSwap`` is set to 0, the container doesn't use swap. This parameter maps to the ``--memory-swappiness`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . Consider the following when you use a per-container swap configuration. - Swap space must be enabled and allocated on the container instance for the containers to use. .. epigraph:: The Amazon ECS optimized AMIs don't have swap enabled by default. You must enable swap on the instance to use this feature. For more information, see `Instance store swap volumes <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-swap-volumes.html>`_ in the *Amazon EC2 User Guide for Linux Instances* or `How do I allocate memory to work as swap space in an Amazon EC2 instance by using a swap file? <https://docs.aws.amazon.com/premiumsupport/knowledge-center/ec2-memory-swap-file/>`_ - The swap space parameters are only supported for job definitions using EC2 resources. - If the ``maxSwap`` and ``swappiness`` parameters are omitted from a job definition, each container will have a default ``swappiness`` value of 60, and the total swap usage will be limited to two times the memory reservation of the container. .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.
            :param tmpfs: The container path, mount options, and size (in MiB) of the tmpfs mount. This parameter maps to the ``--tmpfs`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                linux_parameters_property = batch.CfnJobDefinition.LinuxParametersProperty(
                    devices=[batch.CfnJobDefinition.DeviceProperty(
                        container_path="containerPath",
                        host_path="hostPath",
                        permissions=["permissions"]
                    )],
                    init_process_enabled=False,
                    max_swap=123,
                    shared_memory_size=123,
                    swappiness=123,
                    tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                        container_path="containerPath",
                        size=123,
                
                        # the properties below are optional
                        mount_options=["mountOptions"]
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if devices is not None:
                self._values["devices"] = devices
            if init_process_enabled is not None:
                self._values["init_process_enabled"] = init_process_enabled
            if max_swap is not None:
                self._values["max_swap"] = max_swap
            if shared_memory_size is not None:
                self._values["shared_memory_size"] = shared_memory_size
            if swappiness is not None:
                self._values["swappiness"] = swappiness
            if tmpfs is not None:
                self._values["tmpfs"] = tmpfs

        @builtins.property
        def devices(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.DeviceProperty"]]]]:
            '''Any host devices to expose to the container.

            This parameter maps to ``Devices`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--device`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html#cfn-batch-jobdefinition-containerproperties-linuxparameters-devices
            '''
            result = self._values.get("devices")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.DeviceProperty"]]]], result)

        @builtins.property
        def init_process_enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            '''If true, run an ``init`` process inside the container that forwards signals and reaps processes.

            This parameter maps to the ``--init`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . This parameter requires version 1.25 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html#cfn-batch-jobdefinition-containerproperties-linuxparameters-initprocessenabled
            '''
            result = self._values.get("init_process_enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

        @builtins.property
        def max_swap(self) -> typing.Optional[jsii.Number]:
            '''The total amount of swap memory (in MiB) a container can use.

            This parameter is translated to the ``--memory-swap`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ where the value is the sum of the container memory plus the ``maxSwap`` value. For more information, see ```--memory-swap`` details <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/resource_constraints/#--memory-swap-details>`_ in the Docker documentation.

            If a ``maxSwap`` value of ``0`` is specified, the container doesn't use swap. Accepted values are ``0`` or any positive integer. If the ``maxSwap`` parameter is omitted, the container doesn't use the swap configuration for the container instance it is running on. A ``maxSwap`` value must be set for the ``swappiness`` parameter to be used.
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html#cfn-batch-jobdefinition-containerproperties-linuxparameters-maxswap
            '''
            result = self._values.get("max_swap")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def shared_memory_size(self) -> typing.Optional[jsii.Number]:
            '''The value for the size (in MiB) of the ``/dev/shm`` volume.

            This parameter maps to the ``--shm-size`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html#cfn-batch-jobdefinition-containerproperties-linuxparameters-sharedmemorysize
            '''
            result = self._values.get("shared_memory_size")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def swappiness(self) -> typing.Optional[jsii.Number]:
            '''This allows you to tune a container's memory swappiness behavior.

            A ``swappiness`` value of ``0`` causes swapping not to happen unless absolutely necessary. A ``swappiness`` value of ``100`` causes pages to be swapped very aggressively. Accepted values are whole numbers between ``0`` and ``100`` . If the ``swappiness`` parameter isn't specified, a default value of ``60`` is used. If a value isn't specified for ``maxSwap`` , then this parameter is ignored. If ``maxSwap`` is set to 0, the container doesn't use swap. This parameter maps to the ``--memory-swappiness`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .

            Consider the following when you use a per-container swap configuration.

            - Swap space must be enabled and allocated on the container instance for the containers to use.

            .. epigraph::

               The Amazon ECS optimized AMIs don't have swap enabled by default. You must enable swap on the instance to use this feature. For more information, see `Instance store swap volumes <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-swap-volumes.html>`_ in the *Amazon EC2 User Guide for Linux Instances* or `How do I allocate memory to work as swap space in an Amazon EC2 instance by using a swap file? <https://docs.aws.amazon.com/premiumsupport/knowledge-center/ec2-memory-swap-file/>`_

            - The swap space parameters are only supported for job definitions using EC2 resources.
            - If the ``maxSwap`` and ``swappiness`` parameters are omitted from a job definition, each container will have a default ``swappiness`` value of 60, and the total swap usage will be limited to two times the memory reservation of the container.

            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html#cfn-batch-jobdefinition-containerproperties-linuxparameters-swappiness
            '''
            result = self._values.get("swappiness")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def tmpfs(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TmpfsProperty"]]]]:
            '''The container path, mount options, and size (in MiB) of the tmpfs mount.

            This parameter maps to the ``--tmpfs`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-linuxparameters.html#cfn-batch-jobdefinition-containerproperties-linuxparameters-tmpfs
            '''
            result = self._values.get("tmpfs")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TmpfsProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LinuxParametersProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.LogConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "log_driver": "logDriver",
            "options": "options",
            "secret_options": "secretOptions",
        },
    )
    class LogConfigurationProperty:
        def __init__(
            self,
            *,
            log_driver: builtins.str,
            options: typing.Any = None,
            secret_options: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.SecretProperty"]]]] = None,
        ) -> None:
            '''Log configuration options to send to a custom log driver for the container.

            :param log_driver: The log driver to use for the container. The valid values listed for this parameter are log drivers that the Amazon ECS container agent can communicate with by default. The supported log drivers are ``awslogs`` , ``fluentd`` , ``gelf`` , ``json-file`` , ``journald`` , ``logentries`` , ``syslog`` , and ``splunk`` . .. epigraph:: Jobs that are running on Fargate resources are restricted to the ``awslogs`` and ``splunk`` log drivers. - **awslogs** - Specifies the Amazon CloudWatch Logs logging driver. For more information, see `Using the awslogs log driver <https://docs.aws.amazon.com/batch/latest/userguide/using_awslogs.html>`_ in the *AWS Batch User Guide* and `Amazon CloudWatch Logs logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/awslogs/>`_ in the Docker documentation. - **fluentd** - Specifies the Fluentd logging driver. For more information, including usage and options, see `Fluentd logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/fluentd/>`_ in the Docker documentation. - **gelf** - Specifies the Graylog Extended Format (GELF) logging driver. For more information, including usage and options, see `Graylog Extended Format logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/gelf/>`_ in the Docker documentation. - **journald** - Specifies the journald logging driver. For more information, including usage and options, see `Journald logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/journald/>`_ in the Docker documentation. - **json-file** - Specifies the JSON file logging driver. For more information, including usage and options, see `JSON File logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/json-file/>`_ in the Docker documentation. - **splunk** - Specifies the Splunk logging driver. For more information, including usage and options, see `Splunk logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/splunk/>`_ in the Docker documentation. - **syslog** - Specifies the syslog logging driver. For more information, including usage and options, see `Syslog logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/syslog/>`_ in the Docker documentation. .. epigraph:: If you have a custom driver that's not listed earlier that you want to work with the Amazon ECS container agent, you can fork the Amazon ECS container agent project that's `available on GitHub <https://docs.aws.amazon.com/https://github.com/aws/amazon-ecs-agent>`_ and customize it to work with that driver. We encourage you to submit pull requests for changes that you want to have included. However, Amazon Web Services doesn't currently support running modified copies of this software. This parameter requires version 1.18 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"``
            :param options: The configuration options to send to the log driver. This parameter requires version 1.19 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"``
            :param secret_options: The secrets to pass to the log configuration. For more information, see `Specifying sensitive data <https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-logconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                # options: Any
                
                log_configuration_property = batch.CfnJobDefinition.LogConfigurationProperty(
                    log_driver="logDriver",
                
                    # the properties below are optional
                    options=options,
                    secret_options=[batch.CfnJobDefinition.SecretProperty(
                        name="name",
                        value_from="valueFrom"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "log_driver": log_driver,
            }
            if options is not None:
                self._values["options"] = options
            if secret_options is not None:
                self._values["secret_options"] = secret_options

        @builtins.property
        def log_driver(self) -> builtins.str:
            '''The log driver to use for the container.

            The valid values listed for this parameter are log drivers that the Amazon ECS container agent can communicate with by default.

            The supported log drivers are ``awslogs`` , ``fluentd`` , ``gelf`` , ``json-file`` , ``journald`` , ``logentries`` , ``syslog`` , and ``splunk`` .
            .. epigraph::

               Jobs that are running on Fargate resources are restricted to the ``awslogs`` and ``splunk`` log drivers.

            - **awslogs** - Specifies the Amazon CloudWatch Logs logging driver. For more information, see `Using the awslogs log driver <https://docs.aws.amazon.com/batch/latest/userguide/using_awslogs.html>`_ in the *AWS Batch User Guide* and `Amazon CloudWatch Logs logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/awslogs/>`_ in the Docker documentation.
            - **fluentd** - Specifies the Fluentd logging driver. For more information, including usage and options, see `Fluentd logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/fluentd/>`_ in the Docker documentation.
            - **gelf** - Specifies the Graylog Extended Format (GELF) logging driver. For more information, including usage and options, see `Graylog Extended Format logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/gelf/>`_ in the Docker documentation.
            - **journald** - Specifies the journald logging driver. For more information, including usage and options, see `Journald logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/journald/>`_ in the Docker documentation.
            - **json-file** - Specifies the JSON file logging driver. For more information, including usage and options, see `JSON File logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/json-file/>`_ in the Docker documentation.
            - **splunk** - Specifies the Splunk logging driver. For more information, including usage and options, see `Splunk logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/splunk/>`_ in the Docker documentation.
            - **syslog** - Specifies the syslog logging driver. For more information, including usage and options, see `Syslog logging driver <https://docs.aws.amazon.com/https://docs.docker.com/config/containers/logging/syslog/>`_ in the Docker documentation.

            .. epigraph::

               If you have a custom driver that's not listed earlier that you want to work with the Amazon ECS container agent, you can fork the Amazon ECS container agent project that's `available on GitHub <https://docs.aws.amazon.com/https://github.com/aws/amazon-ecs-agent>`_ and customize it to work with that driver. We encourage you to submit pull requests for changes that you want to have included. However, Amazon Web Services doesn't currently support running modified copies of this software.

            This parameter requires version 1.18 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-logconfiguration.html#cfn-batch-jobdefinition-containerproperties-logconfiguration-logdriver
            '''
            result = self._values.get("log_driver")
            assert result is not None, "Required property 'log_driver' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def options(self) -> typing.Any:
            '''The configuration options to send to the log driver.

            This parameter requires version 1.19 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log into your container instance and run the following command: ``sudo docker version | grep "Server API version"``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-logconfiguration.html#cfn-batch-jobdefinition-containerproperties-logconfiguration-options
            '''
            result = self._values.get("options")
            return typing.cast(typing.Any, result)

        @builtins.property
        def secret_options(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.SecretProperty"]]]]:
            '''The secrets to pass to the log configuration.

            For more information, see `Specifying sensitive data <https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-logconfiguration.html#cfn-batch-jobdefinition-containerproperties-logconfiguration-secretoptions
            '''
            result = self._values.get("secret_options")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.SecretProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LogConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.MountPointsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "container_path": "containerPath",
            "read_only": "readOnly",
            "source_volume": "sourceVolume",
        },
    )
    class MountPointsProperty:
        def __init__(
            self,
            *,
            container_path: typing.Optional[builtins.str] = None,
            read_only: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            source_volume: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Details on a Docker volume mount point that's used in a job's container properties.

            This parameter maps to ``Volumes`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/api/docker_remote_api_v1.19/#create-a-container>`_ section of the Docker Remote API and the ``--volume`` option to docker run.

            :param container_path: The path on the container where the host volume is mounted.
            :param read_only: If this value is ``true`` , the container has read-only access to the volume. Otherwise, the container can write to the volume. The default value is ``false`` .
            :param source_volume: The name of the volume to mount.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                mount_points_property = batch.CfnJobDefinition.MountPointsProperty(
                    container_path="containerPath",
                    read_only=False,
                    source_volume="sourceVolume"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if container_path is not None:
                self._values["container_path"] = container_path
            if read_only is not None:
                self._values["read_only"] = read_only
            if source_volume is not None:
                self._values["source_volume"] = source_volume

        @builtins.property
        def container_path(self) -> typing.Optional[builtins.str]:
            '''The path on the container where the host volume is mounted.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-containerpath
            '''
            result = self._values.get("container_path")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def read_only(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            '''If this value is ``true`` , the container has read-only access to the volume.

            Otherwise, the container can write to the volume. The default value is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-readonly
            '''
            result = self._values.get("read_only")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

        @builtins.property
        def source_volume(self) -> typing.Optional[builtins.str]:
            '''The name of the volume to mount.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-sourcevolume
            '''
            result = self._values.get("source_volume")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MountPointsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NetworkConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"assign_public_ip": "assignPublicIp"},
    )
    class NetworkConfigurationProperty:
        def __init__(
            self,
            *,
            assign_public_ip: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The network configuration for jobs that are running on Fargate resources.

            Jobs that are running on EC2 resources must not specify this parameter.

            :param assign_public_ip: Indicates whether the job should have a public IP address. For a job that is running on Fargate resources in a private subnet to send outbound traffic to the internet (for example, to pull container images), the private subnet requires a NAT gateway be attached to route requests to the internet. For more information, see `Amazon ECS task networking <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-networking.html>`_ . The default value is "DISABLED".

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-networkconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                network_configuration_property = batch.CfnJobDefinition.NetworkConfigurationProperty(
                    assign_public_ip="assignPublicIp"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if assign_public_ip is not None:
                self._values["assign_public_ip"] = assign_public_ip

        @builtins.property
        def assign_public_ip(self) -> typing.Optional[builtins.str]:
            '''Indicates whether the job should have a public IP address.

            For a job that is running on Fargate resources in a private subnet to send outbound traffic to the internet (for example, to pull container images), the private subnet requires a NAT gateway be attached to route requests to the internet. For more information, see `Amazon ECS task networking <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-networking.html>`_ . The default value is "DISABLED".

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties-networkconfiguration.html#cfn-batch-jobdefinition-containerproperties-networkconfiguration-assignpublicip
            '''
            result = self._values.get("assign_public_ip")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NetworkConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodePropertiesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "main_node": "mainNode",
            "node_range_properties": "nodeRangeProperties",
            "num_nodes": "numNodes",
        },
    )
    class NodePropertiesProperty:
        def __init__(
            self,
            *,
            main_node: jsii.Number,
            node_range_properties: typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodeRangePropertyProperty"]]],
            num_nodes: jsii.Number,
        ) -> None:
            '''An object representing the node properties of a multi-node parallel job.

            :param main_node: Specifies the node index for the main node of a multi-node parallel job. This node index value must be fewer than the number of nodes.
            :param node_range_properties: A list of node ranges and their properties associated with a multi-node parallel job.
            :param num_nodes: The number of nodes associated with a multi-node parallel job.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                # options: Any
                
                node_properties_property = batch.CfnJobDefinition.NodePropertiesProperty(
                    main_node=123,
                    node_range_properties=[batch.CfnJobDefinition.NodeRangePropertyProperty(
                        target_nodes="targetNodes",
                
                        # the properties below are optional
                        container=batch.CfnJobDefinition.ContainerPropertiesProperty(
                            image="image",
                
                            # the properties below are optional
                            command=["command"],
                            environment=[batch.CfnJobDefinition.EnvironmentProperty(
                                name="name",
                                value="value"
                            )],
                            execution_role_arn="executionRoleArn",
                            fargate_platform_configuration=batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                                platform_version="platformVersion"
                            ),
                            instance_type="instanceType",
                            job_role_arn="jobRoleArn",
                            linux_parameters=batch.CfnJobDefinition.LinuxParametersProperty(
                                devices=[batch.CfnJobDefinition.DeviceProperty(
                                    container_path="containerPath",
                                    host_path="hostPath",
                                    permissions=["permissions"]
                                )],
                                init_process_enabled=False,
                                max_swap=123,
                                shared_memory_size=123,
                                swappiness=123,
                                tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                                    container_path="containerPath",
                                    size=123,
                
                                    # the properties below are optional
                                    mount_options=["mountOptions"]
                                )]
                            ),
                            log_configuration=batch.CfnJobDefinition.LogConfigurationProperty(
                                log_driver="logDriver",
                
                                # the properties below are optional
                                options=options,
                                secret_options=[batch.CfnJobDefinition.SecretProperty(
                                    name="name",
                                    value_from="valueFrom"
                                )]
                            ),
                            memory=123,
                            mount_points=[batch.CfnJobDefinition.MountPointsProperty(
                                container_path="containerPath",
                                read_only=False,
                                source_volume="sourceVolume"
                            )],
                            network_configuration=batch.CfnJobDefinition.NetworkConfigurationProperty(
                                assign_public_ip="assignPublicIp"
                            ),
                            privileged=False,
                            readonly_root_filesystem=False,
                            resource_requirements=[batch.CfnJobDefinition.ResourceRequirementProperty(
                                type="type",
                                value="value"
                            )],
                            secrets=[batch.CfnJobDefinition.SecretProperty(
                                name="name",
                                value_from="valueFrom"
                            )],
                            ulimits=[batch.CfnJobDefinition.UlimitProperty(
                                hard_limit=123,
                                name="name",
                                soft_limit=123
                            )],
                            user="user",
                            vcpus=123,
                            volumes=[batch.CfnJobDefinition.VolumesProperty(
                                efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                                    file_system_id="fileSystemId",
                
                                    # the properties below are optional
                                    authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                                        access_point_id="accessPointId",
                                        iam="iam"
                                    ),
                                    root_directory="rootDirectory",
                                    transit_encryption="transitEncryption",
                                    transit_encryption_port=123
                                ),
                                host=batch.CfnJobDefinition.VolumesHostProperty(
                                    source_path="sourcePath"
                                ),
                                name="name"
                            )]
                        )
                    )],
                    num_nodes=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "main_node": main_node,
                "node_range_properties": node_range_properties,
                "num_nodes": num_nodes,
            }

        @builtins.property
        def main_node(self) -> jsii.Number:
            '''Specifies the node index for the main node of a multi-node parallel job.

            This node index value must be fewer than the number of nodes.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-mainnode
            '''
            result = self._values.get("main_node")
            assert result is not None, "Required property 'main_node' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def node_range_properties(
            self,
        ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodeRangePropertyProperty"]]]:
            '''A list of node ranges and their properties associated with a multi-node parallel job.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-noderangeproperties
            '''
            result = self._values.get("node_range_properties")
            assert result is not None, "Required property 'node_range_properties' is missing"
            return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodeRangePropertyProperty"]]], result)

        @builtins.property
        def num_nodes(self) -> jsii.Number:
            '''The number of nodes associated with a multi-node parallel job.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-numnodes
            '''
            result = self._values.get("num_nodes")
            assert result is not None, "Required property 'num_nodes' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NodePropertiesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodeRangePropertyProperty",
        jsii_struct_bases=[],
        name_mapping={"target_nodes": "targetNodes", "container": "container"},
    )
    class NodeRangePropertyProperty:
        def __init__(
            self,
            *,
            target_nodes: builtins.str,
            container: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]] = None,
        ) -> None:
            '''An object representing the properties of the node range for a multi-node parallel job.

            :param target_nodes: The range of nodes, using node index values. A range of ``0:3`` indicates nodes with index values of ``0`` through ``3`` . If the starting range value is omitted ( ``:n`` ), then ``0`` is used to start the range. If the ending range value is omitted ( ``n:`` ), then the highest possible node index is used to end the range. Your accumulative node ranges must account for all nodes ( ``0:n`` ). You can nest node ranges, for example ``0:10`` and ``4:5`` , in which case the ``4:5`` range properties override the ``0:10`` properties.
            :param container: The container details for the node range.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                # options: Any
                
                node_range_property_property = batch.CfnJobDefinition.NodeRangePropertyProperty(
                    target_nodes="targetNodes",
                
                    # the properties below are optional
                    container=batch.CfnJobDefinition.ContainerPropertiesProperty(
                        image="image",
                
                        # the properties below are optional
                        command=["command"],
                        environment=[batch.CfnJobDefinition.EnvironmentProperty(
                            name="name",
                            value="value"
                        )],
                        execution_role_arn="executionRoleArn",
                        fargate_platform_configuration=batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                            platform_version="platformVersion"
                        ),
                        instance_type="instanceType",
                        job_role_arn="jobRoleArn",
                        linux_parameters=batch.CfnJobDefinition.LinuxParametersProperty(
                            devices=[batch.CfnJobDefinition.DeviceProperty(
                                container_path="containerPath",
                                host_path="hostPath",
                                permissions=["permissions"]
                            )],
                            init_process_enabled=False,
                            max_swap=123,
                            shared_memory_size=123,
                            swappiness=123,
                            tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                                container_path="containerPath",
                                size=123,
                
                                # the properties below are optional
                                mount_options=["mountOptions"]
                            )]
                        ),
                        log_configuration=batch.CfnJobDefinition.LogConfigurationProperty(
                            log_driver="logDriver",
                
                            # the properties below are optional
                            options=options,
                            secret_options=[batch.CfnJobDefinition.SecretProperty(
                                name="name",
                                value_from="valueFrom"
                            )]
                        ),
                        memory=123,
                        mount_points=[batch.CfnJobDefinition.MountPointsProperty(
                            container_path="containerPath",
                            read_only=False,
                            source_volume="sourceVolume"
                        )],
                        network_configuration=batch.CfnJobDefinition.NetworkConfigurationProperty(
                            assign_public_ip="assignPublicIp"
                        ),
                        privileged=False,
                        readonly_root_filesystem=False,
                        resource_requirements=[batch.CfnJobDefinition.ResourceRequirementProperty(
                            type="type",
                            value="value"
                        )],
                        secrets=[batch.CfnJobDefinition.SecretProperty(
                            name="name",
                            value_from="valueFrom"
                        )],
                        ulimits=[batch.CfnJobDefinition.UlimitProperty(
                            hard_limit=123,
                            name="name",
                            soft_limit=123
                        )],
                        user="user",
                        vcpus=123,
                        volumes=[batch.CfnJobDefinition.VolumesProperty(
                            efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                                file_system_id="fileSystemId",
                
                                # the properties below are optional
                                authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                                    access_point_id="accessPointId",
                                    iam="iam"
                                ),
                                root_directory="rootDirectory",
                                transit_encryption="transitEncryption",
                                transit_encryption_port=123
                            ),
                            host=batch.CfnJobDefinition.VolumesHostProperty(
                                source_path="sourcePath"
                            ),
                            name="name"
                        )]
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "target_nodes": target_nodes,
            }
            if container is not None:
                self._values["container"] = container

        @builtins.property
        def target_nodes(self) -> builtins.str:
            '''The range of nodes, using node index values.

            A range of ``0:3`` indicates nodes with index values of ``0`` through ``3`` . If the starting range value is omitted ( ``:n`` ), then ``0`` is used to start the range. If the ending range value is omitted ( ``n:`` ), then the highest possible node index is used to end the range. Your accumulative node ranges must account for all nodes ( ``0:n`` ). You can nest node ranges, for example ``0:10`` and ``4:5`` , in which case the ``4:5`` range properties override the ``0:10`` properties.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-targetnodes
            '''
            result = self._values.get("target_nodes")
            assert result is not None, "Required property 'target_nodes' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def container(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]]:
            '''The container details for the node range.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-container
            '''
            result = self._values.get("container")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NodeRangePropertyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ResourceRequirementProperty",
        jsii_struct_bases=[],
        name_mapping={"type": "type", "value": "value"},
    )
    class ResourceRequirementProperty:
        def __init__(
            self,
            *,
            type: typing.Optional[builtins.str] = None,
            value: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The type and amount of a resource to assign to a container.

            The supported resources include ``GPU`` , ``MEMORY`` , and ``VCPU`` .

            :param type: The type of resource to assign to a container. The supported resources include ``GPU`` , ``MEMORY`` , and ``VCPU`` .
            :param value: The quantity of the specified resource to reserve for the container. The values vary based on the ``type`` specified. - **type="GPU"** - The number of physical GPUs to reserve for the container. The number of GPUs reserved for all containers in a job shouldn't exceed the number of available GPUs on the compute resource that the job is launched on. .. epigraph:: GPUs are not available for jobs that are running on Fargate resources. - **type="MEMORY"** - The memory hard limit (in MiB) present to the container. This parameter is supported for jobs that are running on EC2 resources. If your container attempts to exceed the memory specified, the container is terminated. This parameter maps to ``Memory`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--memory`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . You must specify at least 4 MiB of memory for a job. This is required but can be specified in several places for multi-node parallel (MNP) jobs. It must be specified for each node at least once. This parameter maps to ``Memory`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--memory`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . .. epigraph:: If you're trying to maximize your resource utilization by providing your jobs as much memory as possible for a particular instance type, see `Memory management <https://docs.aws.amazon.com/batch/latest/userguide/memory-management.html>`_ in the *AWS Batch User Guide* . For jobs that are running on Fargate resources, then ``value`` is the hard limit (in MiB), and must match one of the supported values and the ``VCPU`` values must be one of the values supported for that memory value. - **value = 512** - ``VCPU`` = 0.25 - **value = 1024** - ``VCPU`` = 0.25 or 0.5 - **value = 2048** - ``VCPU`` = 0.25, 0.5, or 1 - **value = 3072** - ``VCPU`` = 0.5, or 1 - **value = 4096** - ``VCPU`` = 0.5, 1, or 2 - **value = 5120, 6144, or 7168** - ``VCPU`` = 1 or 2 - **value = 8192** - ``VCPU`` = 1, 2, or 4 - **value = 9216, 10240, 11264, 12288, 13312, 14336, 15360, or 16384** - ``VCPU`` = 2 or 4 - **value = 17408, 18432, 19456, 20480, 21504, 22528, 23552, 24576, 25600, 26624, 27648, 28672, 29696, or 30720** - ``VCPU`` = 4 - **type="VCPU"** - The number of vCPUs reserved for the container. This parameter maps to ``CpuShares`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--cpu-shares`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . Each vCPU is equivalent to 1,024 CPU shares. For EC2 resources, you must specify at least one vCPU. This is required but can be specified in several places; it must be specified for each node at least once. For jobs that are running on Fargate resources, then ``value`` must match one of the supported values and the ``MEMORY`` values must be one of the values supported for that ``VCPU`` value. The supported values are 0.25, 0.5, 1, 2, and 4 - **value = 0.25** - ``MEMORY`` = 512, 1024, or 2048 - **value = 0.5** - ``MEMORY`` = 1024, 2048, 3072, or 4096 - **value = 1** - ``MEMORY`` = 2048, 3072, 4096, 5120, 6144, 7168, or 8192 - **value = 2** - ``MEMORY`` = 4096, 5120, 6144, 7168, 8192, 9216, 10240, 11264, 12288, 13312, 14336, 15360, or 16384 - **value = 4** - ``MEMORY`` = 8192, 9216, 10240, 11264, 12288, 13312, 14336, 15360, 16384, 17408, 18432, 19456, 20480, 21504, 22528, 23552, 24576, 25600, 26624, 27648, 28672, 29696, or 30720

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                resource_requirement_property = batch.CfnJobDefinition.ResourceRequirementProperty(
                    type="type",
                    value="value"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if type is not None:
                self._values["type"] = type
            if value is not None:
                self._values["value"] = value

        @builtins.property
        def type(self) -> typing.Optional[builtins.str]:
            '''The type of resource to assign to a container.

            The supported resources include ``GPU`` , ``MEMORY`` , and ``VCPU`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-type
            '''
            result = self._values.get("type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def value(self) -> typing.Optional[builtins.str]:
            '''The quantity of the specified resource to reserve for the container. The values vary based on the ``type`` specified.

            - **type="GPU"** - The number of physical GPUs to reserve for the container. The number of GPUs reserved for all containers in a job shouldn't exceed the number of available GPUs on the compute resource that the job is launched on.

            .. epigraph::

               GPUs are not available for jobs that are running on Fargate resources.

            - **type="MEMORY"** - The memory hard limit (in MiB) present to the container. This parameter is supported for jobs that are running on EC2 resources. If your container attempts to exceed the memory specified, the container is terminated. This parameter maps to ``Memory`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--memory`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . You must specify at least 4 MiB of memory for a job. This is required but can be specified in several places for multi-node parallel (MNP) jobs. It must be specified for each node at least once. This parameter maps to ``Memory`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--memory`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ .

            .. epigraph::

               If you're trying to maximize your resource utilization by providing your jobs as much memory as possible for a particular instance type, see `Memory management <https://docs.aws.amazon.com/batch/latest/userguide/memory-management.html>`_ in the *AWS Batch User Guide* .

            For jobs that are running on Fargate resources, then ``value`` is the hard limit (in MiB), and must match one of the supported values and the ``VCPU`` values must be one of the values supported for that memory value.

            - **value = 512** - ``VCPU`` = 0.25
            - **value = 1024** - ``VCPU`` = 0.25 or 0.5
            - **value = 2048** - ``VCPU`` = 0.25, 0.5, or 1
            - **value = 3072** - ``VCPU`` = 0.5, or 1
            - **value = 4096** - ``VCPU`` = 0.5, 1, or 2
            - **value = 5120, 6144, or 7168** - ``VCPU`` = 1 or 2
            - **value = 8192** - ``VCPU`` = 1, 2, or 4
            - **value = 9216, 10240, 11264, 12288, 13312, 14336, 15360, or 16384** - ``VCPU`` = 2 or 4
            - **value = 17408, 18432, 19456, 20480, 21504, 22528, 23552, 24576, 25600, 26624, 27648, 28672, 29696, or 30720** - ``VCPU`` = 4
            - **type="VCPU"** - The number of vCPUs reserved for the container. This parameter maps to ``CpuShares`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/#create-a-container>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.23/>`_ and the ``--cpu-shares`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . Each vCPU is equivalent to 1,024 CPU shares. For EC2 resources, you must specify at least one vCPU. This is required but can be specified in several places; it must be specified for each node at least once.

            For jobs that are running on Fargate resources, then ``value`` must match one of the supported values and the ``MEMORY`` values must be one of the values supported for that ``VCPU`` value. The supported values are 0.25, 0.5, 1, 2, and 4

            - **value = 0.25** - ``MEMORY`` = 512, 1024, or 2048
            - **value = 0.5** - ``MEMORY`` = 1024, 2048, 3072, or 4096
            - **value = 1** - ``MEMORY`` = 2048, 3072, 4096, 5120, 6144, 7168, or 8192
            - **value = 2** - ``MEMORY`` = 4096, 5120, 6144, 7168, 8192, 9216, 10240, 11264, 12288, 13312, 14336, 15360, or 16384
            - **value = 4** - ``MEMORY`` = 8192, 9216, 10240, 11264, 12288, 13312, 14336, 15360, 16384, 17408, 18432, 19456, 20480, 21504, 22528, 23552, 24576, 25600, 26624, 27648, 28672, 29696, or 30720

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-value
            '''
            result = self._values.get("value")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceRequirementProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.RetryStrategyProperty",
        jsii_struct_bases=[],
        name_mapping={"attempts": "attempts", "evaluate_on_exit": "evaluateOnExit"},
    )
    class RetryStrategyProperty:
        def __init__(
            self,
            *,
            attempts: typing.Optional[jsii.Number] = None,
            evaluate_on_exit: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EvaluateOnExitProperty"]]]] = None,
        ) -> None:
            '''The retry strategy associated with a job.

            For more information, see `Automated job retries <https://docs.aws.amazon.com/batch/latest/userguide/job_retries.html>`_ in the *AWS Batch User Guide* .

            :param attempts: The number of times to move a job to the ``RUNNABLE`` status. You can specify between 1 and 10 attempts. If the value of ``attempts`` is greater than one, the job is retried on failure the same number of attempts as the value.
            :param evaluate_on_exit: Array of up to 5 objects that specify conditions under which the job should be retried or failed. If this parameter is specified, then the ``attempts`` parameter must also be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                retry_strategy_property = batch.CfnJobDefinition.RetryStrategyProperty(
                    attempts=123,
                    evaluate_on_exit=[batch.CfnJobDefinition.EvaluateOnExitProperty(
                        action="action",
                
                        # the properties below are optional
                        on_exit_code="onExitCode",
                        on_reason="onReason",
                        on_status_reason="onStatusReason"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if attempts is not None:
                self._values["attempts"] = attempts
            if evaluate_on_exit is not None:
                self._values["evaluate_on_exit"] = evaluate_on_exit

        @builtins.property
        def attempts(self) -> typing.Optional[jsii.Number]:
            '''The number of times to move a job to the ``RUNNABLE`` status.

            You can specify between 1 and 10 attempts. If the value of ``attempts`` is greater than one, the job is retried on failure the same number of attempts as the value.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html#cfn-batch-jobdefinition-retrystrategy-attempts
            '''
            result = self._values.get("attempts")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def evaluate_on_exit(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EvaluateOnExitProperty"]]]]:
            '''Array of up to 5 objects that specify conditions under which the job should be retried or failed.

            If this parameter is specified, then the ``attempts`` parameter must also be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html#cfn-batch-jobdefinition-retrystrategy-evaluateonexit
            '''
            result = self._values.get("evaluate_on_exit")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EvaluateOnExitProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RetryStrategyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.SecretProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "value_from": "valueFrom"},
    )
    class SecretProperty:
        def __init__(self, *, name: builtins.str, value_from: builtins.str) -> None:
            '''An object representing the secret to expose to your container.

            Secrets can be exposed to a container in the following ways:

            - To inject sensitive data into your containers as environment variables, use the ``secrets`` container definition parameter.
            - To reference sensitive information in the log configuration of a container, use the ``secretOptions`` container definition parameter.

            For more information, see `Specifying sensitive data <https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data.html>`_ in the *AWS Batch User Guide* .

            :param name: The name of the secret.
            :param value_from: The secret to expose to the container. The supported values are either the full ARN of the AWS Secrets Manager secret or the full ARN of the parameter in the AWS Systems Manager Parameter Store. .. epigraph:: If the AWS Systems Manager Parameter Store parameter exists in the same Region as the job you're launching, then you can use either the full ARN or name of the parameter. If the parameter exists in a different Region, then the full ARN must be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-secret.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                secret_property = batch.CfnJobDefinition.SecretProperty(
                    name="name",
                    value_from="valueFrom"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
                "value_from": value_from,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''The name of the secret.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-secret.html#cfn-batch-jobdefinition-secret-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value_from(self) -> builtins.str:
            '''The secret to expose to the container.

            The supported values are either the full ARN of the AWS Secrets Manager secret or the full ARN of the parameter in the AWS Systems Manager Parameter Store.
            .. epigraph::

               If the AWS Systems Manager Parameter Store parameter exists in the same Region as the job you're launching, then you can use either the full ARN or name of the parameter. If the parameter exists in a different Region, then the full ARN must be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-secret.html#cfn-batch-jobdefinition-secret-valuefrom
            '''
            result = self._values.get("value_from")
            assert result is not None, "Required property 'value_from' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SecretProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.TimeoutProperty",
        jsii_struct_bases=[],
        name_mapping={"attempt_duration_seconds": "attemptDurationSeconds"},
    )
    class TimeoutProperty:
        def __init__(
            self,
            *,
            attempt_duration_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''An object representing a job timeout configuration.

            :param attempt_duration_seconds: The time duration in seconds (measured from the job attempt's ``startedAt`` timestamp) after which AWS Batch terminates your jobs if they have not finished. The minimum value for the timeout is 60 seconds.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                timeout_property = batch.CfnJobDefinition.TimeoutProperty(
                    attempt_duration_seconds=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if attempt_duration_seconds is not None:
                self._values["attempt_duration_seconds"] = attempt_duration_seconds

        @builtins.property
        def attempt_duration_seconds(self) -> typing.Optional[jsii.Number]:
            '''The time duration in seconds (measured from the job attempt's ``startedAt`` timestamp) after which AWS Batch terminates your jobs if they have not finished.

            The minimum value for the timeout is 60 seconds.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html#cfn-batch-jobdefinition-timeout-attemptdurationseconds
            '''
            result = self._values.get("attempt_duration_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TimeoutProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.TmpfsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "container_path": "containerPath",
            "size": "size",
            "mount_options": "mountOptions",
        },
    )
    class TmpfsProperty:
        def __init__(
            self,
            *,
            container_path: builtins.str,
            size: jsii.Number,
            mount_options: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''The container path, mount options, and size of the tmpfs mount.

            .. epigraph::

               This object isn't applicable to jobs that are running on Fargate resources.

            :param container_path: The absolute file path in the container where the tmpfs volume is mounted.
            :param size: The size (in MiB) of the tmpfs volume.
            :param mount_options: The list of tmpfs volume mount options. Valid values: " ``defaults`` " | " ``ro`` " | " ``rw`` " | " ``suid`` " | " ``nosuid`` " | " ``dev`` " | " ``nodev`` " | " ``exec`` " | " ``noexec`` " | " ``sync`` " | " ``async`` " | " ``dirsync`` " | " ``remount`` " | " ``mand`` " | " ``nomand`` " | " ``atime`` " | " ``noatime`` " | " ``diratime`` " | " ``nodiratime`` " | " ``bind`` " | " ``rbind" | "unbindable" | "runbindable" | "private" | "rprivate" | "shared" | "rshared" | "slave" | "rslave" | "relatime`` " | " ``norelatime`` " | " ``strictatime`` " | " ``nostrictatime`` " | " ``mode`` " | " ``uid`` " | " ``gid`` " | " ``nr_inodes`` " | " ``nr_blocks`` " | " ``mpol`` "

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-tmpfs.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                tmpfs_property = batch.CfnJobDefinition.TmpfsProperty(
                    container_path="containerPath",
                    size=123,
                
                    # the properties below are optional
                    mount_options=["mountOptions"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "container_path": container_path,
                "size": size,
            }
            if mount_options is not None:
                self._values["mount_options"] = mount_options

        @builtins.property
        def container_path(self) -> builtins.str:
            '''The absolute file path in the container where the tmpfs volume is mounted.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-tmpfs.html#cfn-batch-jobdefinition-tmpfs-containerpath
            '''
            result = self._values.get("container_path")
            assert result is not None, "Required property 'container_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def size(self) -> jsii.Number:
            '''The size (in MiB) of the tmpfs volume.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-tmpfs.html#cfn-batch-jobdefinition-tmpfs-size
            '''
            result = self._values.get("size")
            assert result is not None, "Required property 'size' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def mount_options(self) -> typing.Optional[typing.List[builtins.str]]:
            '''The list of tmpfs volume mount options.

            Valid values: " ``defaults`` " | " ``ro`` " | " ``rw`` " | " ``suid`` " | " ``nosuid`` " | " ``dev`` " | " ``nodev`` " | " ``exec`` " | " ``noexec`` " | " ``sync`` " | " ``async`` " | " ``dirsync`` " | " ``remount`` " | " ``mand`` " | " ``nomand`` " | " ``atime`` " | " ``noatime`` " | " ``diratime`` " | " ``nodiratime`` " | " ``bind`` " | " ``rbind" | "unbindable" | "runbindable" | "private" | "rprivate" | "shared" | "rshared" | "slave" | "rslave" | "relatime`` " | " ``norelatime`` " | " ``strictatime`` " | " ``nostrictatime`` " | " ``mode`` " | " ``uid`` " | " ``gid`` " | " ``nr_inodes`` " | " ``nr_blocks`` " | " ``mpol`` "

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-tmpfs.html#cfn-batch-jobdefinition-tmpfs-mountoptions
            '''
            result = self._values.get("mount_options")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TmpfsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.UlimitProperty",
        jsii_struct_bases=[],
        name_mapping={
            "hard_limit": "hardLimit",
            "name": "name",
            "soft_limit": "softLimit",
        },
    )
    class UlimitProperty:
        def __init__(
            self,
            *,
            hard_limit: jsii.Number,
            name: builtins.str,
            soft_limit: jsii.Number,
        ) -> None:
            '''The ``ulimit`` settings to pass to the container.

            .. epigraph::

               This object isn't applicable to jobs that are running on Fargate resources.

            :param hard_limit: The hard limit for the ``ulimit`` type.
            :param name: The ``type`` of the ``ulimit`` .
            :param soft_limit: The soft limit for the ``ulimit`` type.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                ulimit_property = batch.CfnJobDefinition.UlimitProperty(
                    hard_limit=123,
                    name="name",
                    soft_limit=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "hard_limit": hard_limit,
                "name": name,
                "soft_limit": soft_limit,
            }

        @builtins.property
        def hard_limit(self) -> jsii.Number:
            '''The hard limit for the ``ulimit`` type.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-hardlimit
            '''
            result = self._values.get("hard_limit")
            assert result is not None, "Required property 'hard_limit' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def name(self) -> builtins.str:
            '''The ``type`` of the ``ulimit`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def soft_limit(self) -> jsii.Number:
            '''The soft limit for the ``ulimit`` type.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-softlimit
            '''
            result = self._values.get("soft_limit")
            assert result is not None, "Required property 'soft_limit' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "UlimitProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesHostProperty",
        jsii_struct_bases=[],
        name_mapping={"source_path": "sourcePath"},
    )
    class VolumesHostProperty:
        def __init__(
            self,
            *,
            source_path: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Determine whether your data volume persists on the host container instance and where it is stored.

            If this parameter is empty, then the Docker daemon assigns a host path for your data volume, but the data isn't guaranteed to persist after the containers associated with it stop running.

            :param source_path: The path on the host container instance that's presented to the container. If this parameter is empty, then the Docker daemon has assigned a host path for you. If this parameter contains a file location, then the data volume persists at the specified location on the host container instance until you delete it manually. If the source path location doesn't exist on the host container instance, the Docker daemon creates it. If the location does exist, the contents of the source path folder are exported. .. epigraph:: This parameter isn't applicable to jobs that run on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                volumes_host_property = batch.CfnJobDefinition.VolumesHostProperty(
                    source_path="sourcePath"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if source_path is not None:
                self._values["source_path"] = source_path

        @builtins.property
        def source_path(self) -> typing.Optional[builtins.str]:
            '''The path on the host container instance that's presented to the container.

            If this parameter is empty, then the Docker daemon has assigned a host path for you. If this parameter contains a file location, then the data volume persists at the specified location on the host container instance until you delete it manually. If the source path location doesn't exist on the host container instance, the Docker daemon creates it. If the location does exist, the contents of the source path folder are exported.
            .. epigraph::

               This parameter isn't applicable to jobs that run on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html#cfn-batch-jobdefinition-volumeshost-sourcepath
            '''
            result = self._values.get("source_path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VolumesHostProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "efs_volume_configuration": "efsVolumeConfiguration",
            "host": "host",
            "name": "name",
        },
    )
    class VolumesProperty:
        def __init__(
            self,
            *,
            efs_volume_configuration: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EfsVolumeConfigurationProperty"]] = None,
            host: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesHostProperty"]] = None,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''A list of volumes associated with the job.

            :param efs_volume_configuration: This is used when you're using an Amazon Elastic File System file system for job storage. For more information, see `Amazon EFS Volumes <https://docs.aws.amazon.com/batch/latest/userguide/efs-volumes.html>`_ in the *AWS Batch User Guide* .
            :param host: The contents of the ``host`` parameter determine whether your data volume persists on the host container instance and where it is stored. If the host parameter is empty, then the Docker daemon assigns a host path for your data volume. However, the data isn't guaranteed to persist after the containers associated with it stop running. .. epigraph:: This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.
            :param name: The name of the volume. It can be up to 255 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_). This name is referenced in the ``sourceVolume`` parameter of container definition ``mountPoints`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                volumes_property = batch.CfnJobDefinition.VolumesProperty(
                    efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                        file_system_id="fileSystemId",
                
                        # the properties below are optional
                        authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                            access_point_id="accessPointId",
                            iam="iam"
                        ),
                        root_directory="rootDirectory",
                        transit_encryption="transitEncryption",
                        transit_encryption_port=123
                    ),
                    host=batch.CfnJobDefinition.VolumesHostProperty(
                        source_path="sourcePath"
                    ),
                    name="name"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if efs_volume_configuration is not None:
                self._values["efs_volume_configuration"] = efs_volume_configuration
            if host is not None:
                self._values["host"] = host
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def efs_volume_configuration(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EfsVolumeConfigurationProperty"]]:
            '''This is used when you're using an Amazon Elastic File System file system for job storage.

            For more information, see `Amazon EFS Volumes <https://docs.aws.amazon.com/batch/latest/userguide/efs-volumes.html>`_ in the *AWS Batch User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-efsvolumeconfiguration
            '''
            result = self._values.get("efs_volume_configuration")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EfsVolumeConfigurationProperty"]], result)

        @builtins.property
        def host(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesHostProperty"]]:
            '''The contents of the ``host`` parameter determine whether your data volume persists on the host container instance and where it is stored.

            If the host parameter is empty, then the Docker daemon assigns a host path for your data volume. However, the data isn't guaranteed to persist after the containers associated with it stop running.
            .. epigraph::

               This parameter isn't applicable to jobs that are running on Fargate resources and shouldn't be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-host
            '''
            result = self._values.get("host")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesHostProperty"]], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''The name of the volume.

            It can be up to 255 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_). This name is referenced in the ``sourceVolume`` parameter of container definition ``mountPoints`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VolumesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.CfnJobDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "container_properties": "containerProperties",
        "job_definition_name": "jobDefinitionName",
        "node_properties": "nodeProperties",
        "parameters": "parameters",
        "platform_capabilities": "platformCapabilities",
        "propagate_tags": "propagateTags",
        "retry_strategy": "retryStrategy",
        "scheduling_priority": "schedulingPriority",
        "tags": "tags",
        "timeout": "timeout",
    },
)
class CfnJobDefinitionProps:
    def __init__(
        self,
        *,
        type: builtins.str,
        container_properties: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.ContainerPropertiesProperty]] = None,
        job_definition_name: typing.Optional[builtins.str] = None,
        node_properties: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.NodePropertiesProperty]] = None,
        parameters: typing.Any = None,
        platform_capabilities: typing.Optional[typing.Sequence[builtins.str]] = None,
        propagate_tags: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        retry_strategy: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.RetryStrategyProperty]] = None,
        scheduling_priority: typing.Optional[jsii.Number] = None,
        tags: typing.Any = None,
        timeout: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.TimeoutProperty]] = None,
    ) -> None:
        '''Properties for defining a ``CfnJobDefinition``.

        :param type: The type of job definition. For more information about multi-node parallel jobs, see `Creating a multi-node parallel job definition <https://docs.aws.amazon.com/batch/latest/userguide/multi-node-job-def.html>`_ in the *AWS Batch User Guide* . .. epigraph:: If the job is run on Fargate resources, then ``multinode`` isn't supported.
        :param container_properties: An object with various properties specific to container-based jobs.
        :param job_definition_name: The name of the job definition.
        :param node_properties: An object with various properties specific to multi-node parallel jobs. .. epigraph:: If the job runs on Fargate resources, then you must not specify ``nodeProperties`` ; use ``containerProperties`` instead.
        :param parameters: Default parameters or parameter substitution placeholders that are set in the job definition. Parameters are specified as a key-value pair mapping. Parameters in a ``SubmitJob`` request override any corresponding parameter defaults from the job definition. For more information about specifying parameters, see `Job definition parameters <https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html>`_ in the *AWS Batch User Guide* .
        :param platform_capabilities: The platform capabilities required by the job definition. If no value is specified, it defaults to ``EC2`` . Jobs run on Fargate resources specify ``FARGATE`` .
        :param propagate_tags: Specifies whether to propagate the tags from the job or job definition to the corresponding Amazon ECS task. If no value is specified, the tags aren't propagated. Tags can only be propagated to the tasks during task creation. For tags with the same name, job tags are given priority over job definitions tags. If the total number of combined tags from the job and job definition is over 50, the job is moved to the ``FAILED`` state.
        :param retry_strategy: The retry strategy to use for failed jobs that are submitted with this job definition.
        :param scheduling_priority: The scheduling priority of the job definition. This only affects jobs in job queues with a fair share policy. Jobs with a higher scheduling priority are scheduled before jobs with a lower scheduling priority.
        :param tags: The tags applied to the job definition.
        :param timeout: The timeout configuration for jobs that are submitted with this job definition. You can specify a timeout duration after which AWS Batch terminates your jobs if they haven't finished.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_batch as batch
            
            # options: Any
            # parameters: Any
            # tags: Any
            
            cfn_job_definition_props = batch.CfnJobDefinitionProps(
                type="type",
            
                # the properties below are optional
                container_properties=batch.CfnJobDefinition.ContainerPropertiesProperty(
                    image="image",
            
                    # the properties below are optional
                    command=["command"],
                    environment=[batch.CfnJobDefinition.EnvironmentProperty(
                        name="name",
                        value="value"
                    )],
                    execution_role_arn="executionRoleArn",
                    fargate_platform_configuration=batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                        platform_version="platformVersion"
                    ),
                    instance_type="instanceType",
                    job_role_arn="jobRoleArn",
                    linux_parameters=batch.CfnJobDefinition.LinuxParametersProperty(
                        devices=[batch.CfnJobDefinition.DeviceProperty(
                            container_path="containerPath",
                            host_path="hostPath",
                            permissions=["permissions"]
                        )],
                        init_process_enabled=False,
                        max_swap=123,
                        shared_memory_size=123,
                        swappiness=123,
                        tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                            container_path="containerPath",
                            size=123,
            
                            # the properties below are optional
                            mount_options=["mountOptions"]
                        )]
                    ),
                    log_configuration=batch.CfnJobDefinition.LogConfigurationProperty(
                        log_driver="logDriver",
            
                        # the properties below are optional
                        options=options,
                        secret_options=[batch.CfnJobDefinition.SecretProperty(
                            name="name",
                            value_from="valueFrom"
                        )]
                    ),
                    memory=123,
                    mount_points=[batch.CfnJobDefinition.MountPointsProperty(
                        container_path="containerPath",
                        read_only=False,
                        source_volume="sourceVolume"
                    )],
                    network_configuration=batch.CfnJobDefinition.NetworkConfigurationProperty(
                        assign_public_ip="assignPublicIp"
                    ),
                    privileged=False,
                    readonly_root_filesystem=False,
                    resource_requirements=[batch.CfnJobDefinition.ResourceRequirementProperty(
                        type="type",
                        value="value"
                    )],
                    secrets=[batch.CfnJobDefinition.SecretProperty(
                        name="name",
                        value_from="valueFrom"
                    )],
                    ulimits=[batch.CfnJobDefinition.UlimitProperty(
                        hard_limit=123,
                        name="name",
                        soft_limit=123
                    )],
                    user="user",
                    vcpus=123,
                    volumes=[batch.CfnJobDefinition.VolumesProperty(
                        efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                            file_system_id="fileSystemId",
            
                            # the properties below are optional
                            authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                                access_point_id="accessPointId",
                                iam="iam"
                            ),
                            root_directory="rootDirectory",
                            transit_encryption="transitEncryption",
                            transit_encryption_port=123
                        ),
                        host=batch.CfnJobDefinition.VolumesHostProperty(
                            source_path="sourcePath"
                        ),
                        name="name"
                    )]
                ),
                job_definition_name="jobDefinitionName",
                node_properties=batch.CfnJobDefinition.NodePropertiesProperty(
                    main_node=123,
                    node_range_properties=[batch.CfnJobDefinition.NodeRangePropertyProperty(
                        target_nodes="targetNodes",
            
                        # the properties below are optional
                        container=batch.CfnJobDefinition.ContainerPropertiesProperty(
                            image="image",
            
                            # the properties below are optional
                            command=["command"],
                            environment=[batch.CfnJobDefinition.EnvironmentProperty(
                                name="name",
                                value="value"
                            )],
                            execution_role_arn="executionRoleArn",
                            fargate_platform_configuration=batch.CfnJobDefinition.FargatePlatformConfigurationProperty(
                                platform_version="platformVersion"
                            ),
                            instance_type="instanceType",
                            job_role_arn="jobRoleArn",
                            linux_parameters=batch.CfnJobDefinition.LinuxParametersProperty(
                                devices=[batch.CfnJobDefinition.DeviceProperty(
                                    container_path="containerPath",
                                    host_path="hostPath",
                                    permissions=["permissions"]
                                )],
                                init_process_enabled=False,
                                max_swap=123,
                                shared_memory_size=123,
                                swappiness=123,
                                tmpfs=[batch.CfnJobDefinition.TmpfsProperty(
                                    container_path="containerPath",
                                    size=123,
            
                                    # the properties below are optional
                                    mount_options=["mountOptions"]
                                )]
                            ),
                            log_configuration=batch.CfnJobDefinition.LogConfigurationProperty(
                                log_driver="logDriver",
            
                                # the properties below are optional
                                options=options,
                                secret_options=[batch.CfnJobDefinition.SecretProperty(
                                    name="name",
                                    value_from="valueFrom"
                                )]
                            ),
                            memory=123,
                            mount_points=[batch.CfnJobDefinition.MountPointsProperty(
                                container_path="containerPath",
                                read_only=False,
                                source_volume="sourceVolume"
                            )],
                            network_configuration=batch.CfnJobDefinition.NetworkConfigurationProperty(
                                assign_public_ip="assignPublicIp"
                            ),
                            privileged=False,
                            readonly_root_filesystem=False,
                            resource_requirements=[batch.CfnJobDefinition.ResourceRequirementProperty(
                                type="type",
                                value="value"
                            )],
                            secrets=[batch.CfnJobDefinition.SecretProperty(
                                name="name",
                                value_from="valueFrom"
                            )],
                            ulimits=[batch.CfnJobDefinition.UlimitProperty(
                                hard_limit=123,
                                name="name",
                                soft_limit=123
                            )],
                            user="user",
                            vcpus=123,
                            volumes=[batch.CfnJobDefinition.VolumesProperty(
                                efs_volume_configuration=batch.CfnJobDefinition.EfsVolumeConfigurationProperty(
                                    file_system_id="fileSystemId",
            
                                    # the properties below are optional
                                    authorization_config=batch.CfnJobDefinition.AuthorizationConfigProperty(
                                        access_point_id="accessPointId",
                                        iam="iam"
                                    ),
                                    root_directory="rootDirectory",
                                    transit_encryption="transitEncryption",
                                    transit_encryption_port=123
                                ),
                                host=batch.CfnJobDefinition.VolumesHostProperty(
                                    source_path="sourcePath"
                                ),
                                name="name"
                            )]
                        )
                    )],
                    num_nodes=123
                ),
                parameters=parameters,
                platform_capabilities=["platformCapabilities"],
                propagate_tags=False,
                retry_strategy=batch.CfnJobDefinition.RetryStrategyProperty(
                    attempts=123,
                    evaluate_on_exit=[batch.CfnJobDefinition.EvaluateOnExitProperty(
                        action="action",
            
                        # the properties below are optional
                        on_exit_code="onExitCode",
                        on_reason="onReason",
                        on_status_reason="onStatusReason"
                    )]
                ),
                scheduling_priority=123,
                tags=tags,
                timeout=batch.CfnJobDefinition.TimeoutProperty(
                    attempt_duration_seconds=123
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if container_properties is not None:
            self._values["container_properties"] = container_properties
        if job_definition_name is not None:
            self._values["job_definition_name"] = job_definition_name
        if node_properties is not None:
            self._values["node_properties"] = node_properties
        if parameters is not None:
            self._values["parameters"] = parameters
        if platform_capabilities is not None:
            self._values["platform_capabilities"] = platform_capabilities
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if retry_strategy is not None:
            self._values["retry_strategy"] = retry_strategy
        if scheduling_priority is not None:
            self._values["scheduling_priority"] = scheduling_priority
        if tags is not None:
            self._values["tags"] = tags
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of job definition.

        For more information about multi-node parallel jobs, see `Creating a multi-node parallel job definition <https://docs.aws.amazon.com/batch/latest/userguide/multi-node-job-def.html>`_ in the *AWS Batch User Guide* .
        .. epigraph::

           If the job is run on Fargate resources, then ``multinode`` isn't supported.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_properties(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.ContainerPropertiesProperty]]:
        '''An object with various properties specific to container-based jobs.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
        '''
        result = self._values.get("container_properties")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.ContainerPropertiesProperty]], result)

    @builtins.property
    def job_definition_name(self) -> typing.Optional[builtins.str]:
        '''The name of the job definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
        '''
        result = self._values.get("job_definition_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_properties(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.NodePropertiesProperty]]:
        '''An object with various properties specific to multi-node parallel jobs.

        .. epigraph::

           If the job runs on Fargate resources, then you must not specify ``nodeProperties`` ; use ``containerProperties`` instead.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
        '''
        result = self._values.get("node_properties")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.NodePropertiesProperty]], result)

    @builtins.property
    def parameters(self) -> typing.Any:
        '''Default parameters or parameter substitution placeholders that are set in the job definition.

        Parameters are specified as a key-value pair mapping. Parameters in a ``SubmitJob`` request override any corresponding parameter defaults from the job definition. For more information about specifying parameters, see `Job definition parameters <https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html>`_ in the *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Any, result)

    @builtins.property
    def platform_capabilities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The platform capabilities required by the job definition.

        If no value is specified, it defaults to ``EC2`` . Jobs run on Fargate resources specify ``FARGATE`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-platformcapabilities
        '''
        result = self._values.get("platform_capabilities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        '''Specifies whether to propagate the tags from the job or job definition to the corresponding Amazon ECS task.

        If no value is specified, the tags aren't propagated. Tags can only be propagated to the tasks during task creation. For tags with the same name, job tags are given priority over job definitions tags. If the total number of combined tags from the job and job definition is over 50, the job is moved to the ``FAILED`` state.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-propagatetags
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

    @builtins.property
    def retry_strategy(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.RetryStrategyProperty]]:
        '''The retry strategy to use for failed jobs that are submitted with this job definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
        '''
        result = self._values.get("retry_strategy")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.RetryStrategyProperty]], result)

    @builtins.property
    def scheduling_priority(self) -> typing.Optional[jsii.Number]:
        '''The scheduling priority of the job definition.

        This only affects jobs in job queues with a fair share policy. Jobs with a higher scheduling priority are scheduled before jobs with a lower scheduling priority.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-schedulingpriority
        '''
        result = self._values.get("scheduling_priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''The tags applied to the job definition.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    @builtins.property
    def timeout(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.TimeoutProperty]]:
        '''The timeout configuration for jobs that are submitted with this job definition.

        You can specify a timeout duration after which AWS Batch terminates your jobs if they haven't finished.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnJobDefinition.TimeoutProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnJobDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnJobQueue(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.CfnJobQueue",
):
    '''A CloudFormation ``AWS::Batch::JobQueue``.

    The ``AWS::Batch::JobQueue`` resource specifies the parameters for an AWS Batch job queue definition. For more information, see `Job Queues <https://docs.aws.amazon.com/batch/latest/userguide/job_queues.html>`_ in the ** .

    :cloudformationResource: AWS::Batch::JobQueue
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_batch as batch
        
        cfn_job_queue = batch.CfnJobQueue(self, "MyCfnJobQueue",
            compute_environment_order=[batch.CfnJobQueue.ComputeEnvironmentOrderProperty(
                compute_environment="computeEnvironment",
                order=123
            )],
            priority=123,
        
            # the properties below are optional
            job_queue_name="jobQueueName",
            scheduling_policy_arn="schedulingPolicyArn",
            state="state",
            tags={
                "tags_key": "tags"
            }
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        compute_environment_order: typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnJobQueue.ComputeEnvironmentOrderProperty"]]],
        priority: jsii.Number,
        job_queue_name: typing.Optional[builtins.str] = None,
        scheduling_policy_arn: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Create a new ``AWS::Batch::JobQueue``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param compute_environment_order: The set of compute environments mapped to a job queue and their order relative to each other. The job scheduler uses this parameter to determine which compute environment runs a specific job. Compute environments must be in the ``VALID`` state before you can associate them with a job queue. You can associate up to three compute environments with a job queue. All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed. .. epigraph:: All compute environments that are associated with a job queue must share the same architecture. AWS Batch doesn't support mixing compute environment architecture types in a single job queue.
        :param priority: The priority of the job queue. Job queues with a higher priority (or a higher integer value for the ``priority`` parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order. For example, a job queue with a priority value of ``10`` is given scheduling preference over a job queue with a priority value of ``1`` . All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed.
        :param job_queue_name: The name of the job queue. It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).
        :param scheduling_policy_arn: The Amazon Resource Name (ARN) of the scheduling policy. The format is ``aws: *Partition* :batch: *Region* : *Account* :scheduling-policy/ *Name*`` . For example, ``aws:aws:batch:us-west-2:012345678910:scheduling-policy/MySchedulingPolicy`` .
        :param state: The state of the job queue. If the job queue state is ``ENABLED`` , it is able to accept jobs. If the job queue state is ``DISABLED`` , new jobs can't be added to the queue, but jobs already in the queue can finish.
        :param tags: The tags applied to the job queue. For more information, see `Tagging your AWS Batch resources <https://docs.aws.amazon.com/batch/latest/userguide/using-tags.html>`_ in *AWS Batch User Guide* .
        '''
        props = CfnJobQueueProps(
            compute_environment_order=compute_environment_order,
            priority=priority,
            job_queue_name=job_queue_name,
            scheduling_policy_arn=scheduling_policy_arn,
            state=state,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrJobQueueArn")
    def attr_job_queue_arn(self) -> builtins.str:
        '''Returns the job queue ARN, such as ``batch: *us-east-1* : *111122223333* :job-queue/ *JobQueueName*`` .

        :cloudformationAttribute: JobQueueArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrJobQueueArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''The tags applied to the job queue.

        For more information, see `Tagging your AWS Batch resources <https://docs.aws.amazon.com/batch/latest/userguide/using-tags.html>`_ in *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentOrder")
    def compute_environment_order(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobQueue.ComputeEnvironmentOrderProperty"]]]:
        '''The set of compute environments mapped to a job queue and their order relative to each other.

        The job scheduler uses this parameter to determine which compute environment runs a specific job. Compute environments must be in the ``VALID`` state before you can associate them with a job queue. You can associate up to three compute environments with a job queue. All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed.
        .. epigraph::

           All compute environments that are associated with a job queue must share the same architecture. AWS Batch doesn't support mixing compute environment architecture types in a single job queue.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
        '''
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobQueue.ComputeEnvironmentOrderProperty"]]], jsii.get(self, "computeEnvironmentOrder"))

    @compute_environment_order.setter
    def compute_environment_order(
        self,
        value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobQueue.ComputeEnvironmentOrderProperty"]]],
    ) -> None:
        jsii.set(self, "computeEnvironmentOrder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        '''The priority of the job queue.

        Job queues with a higher priority (or a higher integer value for the ``priority`` parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order. For example, a job queue with a priority value of ``10`` is given scheduling preference over a job queue with a priority value of ``1`` . All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
        '''
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        jsii.set(self, "priority", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> typing.Optional[builtins.str]:
        '''The name of the job queue.

        It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-jobqueuename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobQueueName"))

    @job_queue_name.setter
    def job_queue_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "jobQueueName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedulingPolicyArn")
    def scheduling_policy_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the scheduling policy.

        The format is ``aws: *Partition* :batch: *Region* : *Account* :scheduling-policy/ *Name*`` . For example, ``aws:aws:batch:us-west-2:012345678910:scheduling-policy/MySchedulingPolicy`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-schedulingpolicyarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schedulingPolicyArn"))

    @scheduling_policy_arn.setter
    def scheduling_policy_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "schedulingPolicyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[builtins.str]:
        '''The state of the job queue.

        If the job queue state is ``ENABLED`` , it is able to accept jobs. If the job queue state is ``DISABLED`` , new jobs can't be added to the queue, but jobs already in the queue can finish.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-state
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "state"))

    @state.setter
    def state(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "state", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnJobQueue.ComputeEnvironmentOrderProperty",
        jsii_struct_bases=[],
        name_mapping={"compute_environment": "computeEnvironment", "order": "order"},
    )
    class ComputeEnvironmentOrderProperty:
        def __init__(
            self,
            *,
            compute_environment: builtins.str,
            order: jsii.Number,
        ) -> None:
            '''The order in which compute environments are tried for job placement within a queue.

            Compute environments are tried in ascending order. For example, if two compute environments are associated with a job queue, the compute environment with a lower order integer value is tried for job placement first. Compute environments must be in the ``VALID`` state before you can associate them with a job queue. All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed.
            .. epigraph::

               All compute environments that are associated with a job queue must share the same architecture. AWS Batch doesn't support mixing compute environment architecture types in a single job queue.

            :param compute_environment: The Amazon Resource Name (ARN) of the compute environment.
            :param order: The order of the compute environment. Compute environments are tried in ascending order. For example, if two compute environments are associated with a job queue, the compute environment with a lower ``order`` integer value is tried for job placement first.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                compute_environment_order_property = batch.CfnJobQueue.ComputeEnvironmentOrderProperty(
                    compute_environment="computeEnvironment",
                    order=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "compute_environment": compute_environment,
                "order": order,
            }

        @builtins.property
        def compute_environment(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the compute environment.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-computeenvironment
            '''
            result = self._values.get("compute_environment")
            assert result is not None, "Required property 'compute_environment' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def order(self) -> jsii.Number:
            '''The order of the compute environment.

            Compute environments are tried in ascending order. For example, if two compute environments are associated with a job queue, the compute environment with a lower ``order`` integer value is tried for job placement first.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-order
            '''
            result = self._values.get("order")
            assert result is not None, "Required property 'order' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ComputeEnvironmentOrderProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.CfnJobQueueProps",
    jsii_struct_bases=[],
    name_mapping={
        "compute_environment_order": "computeEnvironmentOrder",
        "priority": "priority",
        "job_queue_name": "jobQueueName",
        "scheduling_policy_arn": "schedulingPolicyArn",
        "state": "state",
        "tags": "tags",
    },
)
class CfnJobQueueProps:
    def __init__(
        self,
        *,
        compute_environment_order: typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, CfnJobQueue.ComputeEnvironmentOrderProperty]]],
        priority: jsii.Number,
        job_queue_name: typing.Optional[builtins.str] = None,
        scheduling_policy_arn: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Properties for defining a ``CfnJobQueue``.

        :param compute_environment_order: The set of compute environments mapped to a job queue and their order relative to each other. The job scheduler uses this parameter to determine which compute environment runs a specific job. Compute environments must be in the ``VALID`` state before you can associate them with a job queue. You can associate up to three compute environments with a job queue. All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed. .. epigraph:: All compute environments that are associated with a job queue must share the same architecture. AWS Batch doesn't support mixing compute environment architecture types in a single job queue.
        :param priority: The priority of the job queue. Job queues with a higher priority (or a higher integer value for the ``priority`` parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order. For example, a job queue with a priority value of ``10`` is given scheduling preference over a job queue with a priority value of ``1`` . All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed.
        :param job_queue_name: The name of the job queue. It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).
        :param scheduling_policy_arn: The Amazon Resource Name (ARN) of the scheduling policy. The format is ``aws: *Partition* :batch: *Region* : *Account* :scheduling-policy/ *Name*`` . For example, ``aws:aws:batch:us-west-2:012345678910:scheduling-policy/MySchedulingPolicy`` .
        :param state: The state of the job queue. If the job queue state is ``ENABLED`` , it is able to accept jobs. If the job queue state is ``DISABLED`` , new jobs can't be added to the queue, but jobs already in the queue can finish.
        :param tags: The tags applied to the job queue. For more information, see `Tagging your AWS Batch resources <https://docs.aws.amazon.com/batch/latest/userguide/using-tags.html>`_ in *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_batch as batch
            
            cfn_job_queue_props = batch.CfnJobQueueProps(
                compute_environment_order=[batch.CfnJobQueue.ComputeEnvironmentOrderProperty(
                    compute_environment="computeEnvironment",
                    order=123
                )],
                priority=123,
            
                # the properties below are optional
                job_queue_name="jobQueueName",
                scheduling_policy_arn="schedulingPolicyArn",
                state="state",
                tags={
                    "tags_key": "tags"
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environment_order": compute_environment_order,
            "priority": priority,
        }
        if job_queue_name is not None:
            self._values["job_queue_name"] = job_queue_name
        if scheduling_policy_arn is not None:
            self._values["scheduling_policy_arn"] = scheduling_policy_arn
        if state is not None:
            self._values["state"] = state
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def compute_environment_order(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnJobQueue.ComputeEnvironmentOrderProperty]]]:
        '''The set of compute environments mapped to a job queue and their order relative to each other.

        The job scheduler uses this parameter to determine which compute environment runs a specific job. Compute environments must be in the ``VALID`` state before you can associate them with a job queue. You can associate up to three compute environments with a job queue. All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed.
        .. epigraph::

           All compute environments that are associated with a job queue must share the same architecture. AWS Batch doesn't support mixing compute environment architecture types in a single job queue.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
        '''
        result = self._values.get("compute_environment_order")
        assert result is not None, "Required property 'compute_environment_order' is missing"
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnJobQueue.ComputeEnvironmentOrderProperty]]], result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''The priority of the job queue.

        Job queues with a higher priority (or a higher integer value for the ``priority`` parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order. For example, a job queue with a priority value of ``10`` is given scheduling preference over a job queue with a priority value of ``1`` . All of the compute environments must be either EC2 ( ``EC2`` or ``SPOT`` ) or Fargate ( ``FARGATE`` or ``FARGATE_SPOT`` ); EC2 and Fargate compute environments can't be mixed.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def job_queue_name(self) -> typing.Optional[builtins.str]:
        '''The name of the job queue.

        It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-jobqueuename
        '''
        result = self._values.get("job_queue_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheduling_policy_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the scheduling policy.

        The format is ``aws: *Partition* :batch: *Region* : *Account* :scheduling-policy/ *Name*`` . For example, ``aws:aws:batch:us-west-2:012345678910:scheduling-policy/MySchedulingPolicy`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-schedulingpolicyarn
        '''
        result = self._values.get("scheduling_policy_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''The state of the job queue.

        If the job queue state is ``ENABLED`` , it is able to accept jobs. If the job queue state is ``DISABLED`` , new jobs can't be added to the queue, but jobs already in the queue can finish.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-state
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The tags applied to the job queue.

        For more information, see `Tagging your AWS Batch resources <https://docs.aws.amazon.com/batch/latest/userguide/using-tags.html>`_ in *AWS Batch User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnJobQueueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnSchedulingPolicy(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.CfnSchedulingPolicy",
):
    '''A CloudFormation ``AWS::Batch::SchedulingPolicy``.

    The ``AWS::Batch::SchedulingPolicy`` resource specifies the parameters for an AWS Batch scheduling policy. For more information, see `Scheduling Policies <https://docs.aws.amazon.com/batch/latest/userguide/scheduling_policies.html>`_ in the ** .

    :cloudformationResource: AWS::Batch::SchedulingPolicy
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_batch as batch
        
        cfn_scheduling_policy = batch.CfnSchedulingPolicy(self, "MyCfnSchedulingPolicy",
            fairshare_policy=batch.CfnSchedulingPolicy.FairsharePolicyProperty(
                compute_reservation=123,
                share_decay_seconds=123,
                share_distribution=[batch.CfnSchedulingPolicy.ShareAttributesProperty(
                    share_identifier="shareIdentifier",
                    weight_factor=123
                )]
            ),
            name="name",
            tags={
                "tags_key": "tags"
            }
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        fairshare_policy: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnSchedulingPolicy.FairsharePolicyProperty"]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Create a new ``AWS::Batch::SchedulingPolicy``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param fairshare_policy: The fair share policy of the scheduling policy.
        :param name: The name of the scheduling policy. It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).
        :param tags: The tags that you apply to the scheduling policy to help you categorize and organize your resources. Each tag consists of a key and an optional value. For more information, see `Tagging AWS Resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in *AWS General Reference* . These tags can be updated or removed using the `TagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_TagResource.html>`_ and `UntagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_UntagResource.html>`_ API operations.
        '''
        props = CfnSchedulingPolicyProps(
            fairshare_policy=fairshare_policy, name=name, tags=tags
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''Returns the scheduling policy ARN, such as ``batch: *us-east-1* : *111122223333* :scheduling-policy/ *HighPriority*`` .

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''The tags that you apply to the scheduling policy to help you categorize and organize your resources.

        Each tag consists of a key and an optional value. For more information, see `Tagging AWS Resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in *AWS General Reference* .

        These tags can be updated or removed using the `TagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_TagResource.html>`_ and `UntagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_UntagResource.html>`_ API operations.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html#cfn-batch-schedulingpolicy-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fairsharePolicy")
    def fairshare_policy(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnSchedulingPolicy.FairsharePolicyProperty"]]:
        '''The fair share policy of the scheduling policy.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html#cfn-batch-schedulingpolicy-fairsharepolicy
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnSchedulingPolicy.FairsharePolicyProperty"]], jsii.get(self, "fairsharePolicy"))

    @fairshare_policy.setter
    def fairshare_policy(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnSchedulingPolicy.FairsharePolicyProperty"]],
    ) -> None:
        jsii.set(self, "fairsharePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the scheduling policy.

        It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html#cfn-batch-schedulingpolicy-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnSchedulingPolicy.FairsharePolicyProperty",
        jsii_struct_bases=[],
        name_mapping={
            "compute_reservation": "computeReservation",
            "share_decay_seconds": "shareDecaySeconds",
            "share_distribution": "shareDistribution",
        },
    )
    class FairsharePolicyProperty:
        def __init__(
            self,
            *,
            compute_reservation: typing.Optional[jsii.Number] = None,
            share_decay_seconds: typing.Optional[jsii.Number] = None,
            share_distribution: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.Sequence[typing.Union[aws_cdk.core.IResolvable, "CfnSchedulingPolicy.ShareAttributesProperty"]]]] = None,
        ) -> None:
            '''The fair share policy for a scheduling policy.

            :param compute_reservation: A value used to reserve some of the available maximum vCPU for fair share identifiers that have not yet been used. The reserved ratio is ``( *computeReservation* /100)^ *ActiveFairShares*`` where ``*ActiveFairShares*`` is the number of active fair share identifiers. For example, a ``computeReservation`` value of 50 indicates that AWS Batch should reserve 50% of the maximum available vCPU if there is only one fair share identifier, 25% if there are two fair share identifiers, and 12.5% if there are three fair share identifiers. A ``computeReservation`` value of 25 indicates that AWS Batch should reserve 25% of the maximum available vCPU if there is only one fair share identifier, 6.25% if there are two fair share identifiers, and 1.56% if there are three fair share identifiers. The minimum value is 0 and the maximum value is 99.
            :param share_decay_seconds: The time period to use to calculate a fair share percentage for each fair share identifier in use, in seconds. A value of zero (0) indicates that only current usage should be measured. The decay allows for more recently run jobs to have more weight than jobs that ran earlier. The maximum supported value is 604800 (1 week).
            :param share_distribution: An array of ``SharedIdentifier`` objects that contain the weights for the fair share identifiers for the fair share policy. Fair share identifiers that aren't included have a default weight of ``1.0`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-schedulingpolicy-fairsharepolicy.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                fairshare_policy_property = batch.CfnSchedulingPolicy.FairsharePolicyProperty(
                    compute_reservation=123,
                    share_decay_seconds=123,
                    share_distribution=[batch.CfnSchedulingPolicy.ShareAttributesProperty(
                        share_identifier="shareIdentifier",
                        weight_factor=123
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if compute_reservation is not None:
                self._values["compute_reservation"] = compute_reservation
            if share_decay_seconds is not None:
                self._values["share_decay_seconds"] = share_decay_seconds
            if share_distribution is not None:
                self._values["share_distribution"] = share_distribution

        @builtins.property
        def compute_reservation(self) -> typing.Optional[jsii.Number]:
            '''A value used to reserve some of the available maximum vCPU for fair share identifiers that have not yet been used.

            The reserved ratio is ``( *computeReservation* /100)^ *ActiveFairShares*`` where ``*ActiveFairShares*`` is the number of active fair share identifiers.

            For example, a ``computeReservation`` value of 50 indicates that AWS Batch should reserve 50% of the maximum available vCPU if there is only one fair share identifier, 25% if there are two fair share identifiers, and 12.5% if there are three fair share identifiers. A ``computeReservation`` value of 25 indicates that AWS Batch should reserve 25% of the maximum available vCPU if there is only one fair share identifier, 6.25% if there are two fair share identifiers, and 1.56% if there are three fair share identifiers.

            The minimum value is 0 and the maximum value is 99.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-schedulingpolicy-fairsharepolicy.html#cfn-batch-schedulingpolicy-fairsharepolicy-computereservation
            '''
            result = self._values.get("compute_reservation")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def share_decay_seconds(self) -> typing.Optional[jsii.Number]:
            '''The time period to use to calculate a fair share percentage for each fair share identifier in use, in seconds.

            A value of zero (0) indicates that only current usage should be measured. The decay allows for more recently run jobs to have more weight than jobs that ran earlier. The maximum supported value is 604800 (1 week).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-schedulingpolicy-fairsharepolicy.html#cfn-batch-schedulingpolicy-fairsharepolicy-sharedecayseconds
            '''
            result = self._values.get("share_decay_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def share_distribution(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSchedulingPolicy.ShareAttributesProperty"]]]]:
            '''An array of ``SharedIdentifier`` objects that contain the weights for the fair share identifiers for the fair share policy.

            Fair share identifiers that aren't included have a default weight of ``1.0`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-schedulingpolicy-fairsharepolicy.html#cfn-batch-schedulingpolicy-fairsharepolicy-sharedistribution
            '''
            result = self._values.get("share_distribution")
            return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSchedulingPolicy.ShareAttributesProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FairsharePolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-batch.CfnSchedulingPolicy.ShareAttributesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "share_identifier": "shareIdentifier",
            "weight_factor": "weightFactor",
        },
    )
    class ShareAttributesProperty:
        def __init__(
            self,
            *,
            share_identifier: typing.Optional[builtins.str] = None,
            weight_factor: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Specifies the weights for the fair share identifiers for the fair share policy.

            Fair share identifiers that aren't included have a default weight of ``1.0`` .

            :param share_identifier: A fair share identifier or fair share identifier prefix. If the string ends with an asterisk (*), this entry specifies the weight factor to use for fair share identifiers that start with that prefix. The list of fair share identifiers in a fair share policy cannot overlap. For example, you can't have one that specifies a ``shareIdentifier`` of ``UserA*`` and another that specifies a ``shareIdentifier`` of ``UserA-1`` . There can be no more than 500 fair share identifiers active in a job queue. The string is limited to 255 alphanumeric characters, optionally followed by an asterisk (*).
            :param weight_factor: The weight factor for the fair share identifier. The default value is 1.0. A lower value has a higher priority for compute resources. For example, jobs that use a share identifier with a weight factor of 0.125 (1/8) get 8 times the compute resources of jobs that use a share identifier with a weight factor of 1. The smallest supported value is 0.0001, and the largest supported value is 999.9999.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-schedulingpolicy-shareattributes.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_batch as batch
                
                share_attributes_property = batch.CfnSchedulingPolicy.ShareAttributesProperty(
                    share_identifier="shareIdentifier",
                    weight_factor=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if share_identifier is not None:
                self._values["share_identifier"] = share_identifier
            if weight_factor is not None:
                self._values["weight_factor"] = weight_factor

        @builtins.property
        def share_identifier(self) -> typing.Optional[builtins.str]:
            '''A fair share identifier or fair share identifier prefix.

            If the string ends with an asterisk (*), this entry specifies the weight factor to use for fair share identifiers that start with that prefix. The list of fair share identifiers in a fair share policy cannot overlap. For example, you can't have one that specifies a ``shareIdentifier`` of ``UserA*`` and another that specifies a ``shareIdentifier`` of ``UserA-1`` .

            There can be no more than 500 fair share identifiers active in a job queue.

            The string is limited to 255 alphanumeric characters, optionally followed by an asterisk (*).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-schedulingpolicy-shareattributes.html#cfn-batch-schedulingpolicy-shareattributes-shareidentifier
            '''
            result = self._values.get("share_identifier")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def weight_factor(self) -> typing.Optional[jsii.Number]:
            '''The weight factor for the fair share identifier.

            The default value is 1.0. A lower value has a higher priority for compute resources. For example, jobs that use a share identifier with a weight factor of 0.125 (1/8) get 8 times the compute resources of jobs that use a share identifier with a weight factor of 1.

            The smallest supported value is 0.0001, and the largest supported value is 999.9999.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-schedulingpolicy-shareattributes.html#cfn-batch-schedulingpolicy-shareattributes-weightfactor
            '''
            result = self._values.get("weight_factor")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ShareAttributesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.CfnSchedulingPolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "fairshare_policy": "fairsharePolicy",
        "name": "name",
        "tags": "tags",
    },
)
class CfnSchedulingPolicyProps:
    def __init__(
        self,
        *,
        fairshare_policy: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnSchedulingPolicy.FairsharePolicyProperty]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Properties for defining a ``CfnSchedulingPolicy``.

        :param fairshare_policy: The fair share policy of the scheduling policy.
        :param name: The name of the scheduling policy. It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).
        :param tags: The tags that you apply to the scheduling policy to help you categorize and organize your resources. Each tag consists of a key and an optional value. For more information, see `Tagging AWS Resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in *AWS General Reference* . These tags can be updated or removed using the `TagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_TagResource.html>`_ and `UntagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_UntagResource.html>`_ API operations.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_batch as batch
            
            cfn_scheduling_policy_props = batch.CfnSchedulingPolicyProps(
                fairshare_policy=batch.CfnSchedulingPolicy.FairsharePolicyProperty(
                    compute_reservation=123,
                    share_decay_seconds=123,
                    share_distribution=[batch.CfnSchedulingPolicy.ShareAttributesProperty(
                        share_identifier="shareIdentifier",
                        weight_factor=123
                    )]
                ),
                name="name",
                tags={
                    "tags_key": "tags"
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if fairshare_policy is not None:
            self._values["fairshare_policy"] = fairshare_policy
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def fairshare_policy(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnSchedulingPolicy.FairsharePolicyProperty]]:
        '''The fair share policy of the scheduling policy.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html#cfn-batch-schedulingpolicy-fairsharepolicy
        '''
        result = self._values.get("fairshare_policy")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnSchedulingPolicy.FairsharePolicyProperty]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the scheduling policy.

        It can be up to 128 letters long. It can contain uppercase and lowercase letters, numbers, hyphens (-), and underscores (_).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html#cfn-batch-schedulingpolicy-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The tags that you apply to the scheduling policy to help you categorize and organize your resources.

        Each tag consists of a key and an optional value. For more information, see `Tagging AWS Resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`_ in *AWS General Reference* .

        These tags can be updated or removed using the `TagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_TagResource.html>`_ and `UntagResource <https://docs.aws.amazon.com/batch/latest/APIReference/API_UntagResource.html>`_ API operations.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-schedulingpolicy.html#cfn-batch-schedulingpolicy-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSchedulingPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.ComputeEnvironmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "compute_environment_name": "computeEnvironmentName",
        "compute_resources": "computeResources",
        "enabled": "enabled",
        "managed": "managed",
        "service_role": "serviceRole",
    },
)
class ComputeEnvironmentProps:
    def __init__(
        self,
        *,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional["ComputeResources"] = None,
        enabled: typing.Optional[builtins.bool] = None,
        managed: typing.Optional[builtins.bool] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''(experimental) Properties for creating a new Compute Environment.

        :param compute_environment_name: (experimental) A name for the compute environment. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - CloudFormation-generated name
        :param compute_resources: (experimental) The details of the required compute resources for the managed compute environment. If specified, and this is an unmanaged compute environment, will throw an error. By default, AWS Batch managed compute environments use a recent, approved version of the Amazon ECS-optimized AMI for compute resources. Default: - CloudFormation defaults
        :param enabled: (experimental) The state of the compute environment. If the state is set to true, then the compute environment accepts jobs from a queue and can scale out automatically based on queues. Default: true
        :param managed: (experimental) Determines if AWS should manage the allocation of compute resources for processing jobs. If set to false, then you are in charge of providing the compute resource details. Default: true
        :param service_role: (experimental) The IAM role used by Batch to make calls to other AWS services on your behalf for managing the resources that you use with the service. By default, this role is created for you using the AWS managed service policy for Batch. Default: - Role using the 'service-role/AWSBatchServiceRole' policy.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            
            my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
                compute_resources=batch.ComputeResources(
                    image=ecs.EcsOptimizedAmi(
                        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
                    ),
                    vpc=vpc
                )
            )
        '''
        if isinstance(compute_resources, dict):
            compute_resources = ComputeResources(**compute_resources)
        self._values: typing.Dict[str, typing.Any] = {}
        if compute_environment_name is not None:
            self._values["compute_environment_name"] = compute_environment_name
        if compute_resources is not None:
            self._values["compute_resources"] = compute_resources
        if enabled is not None:
            self._values["enabled"] = enabled
        if managed is not None:
            self._values["managed"] = managed
        if service_role is not None:
            self._values["service_role"] = service_role

    @builtins.property
    def compute_environment_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the compute environment.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :default: - CloudFormation-generated name

        :stability: experimental
        '''
        result = self._values.get("compute_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compute_resources(self) -> typing.Optional["ComputeResources"]:
        '''(experimental) The details of the required compute resources for the managed compute environment.

        If specified, and this is an unmanaged compute environment, will throw an error.

        By default, AWS Batch managed compute environments use a recent, approved version of the
        Amazon ECS-optimized AMI for compute resources.

        :default: - CloudFormation defaults

        :stability: experimental
        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html
        '''
        result = self._values.get("compute_resources")
        return typing.cast(typing.Optional["ComputeResources"], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The state of the compute environment.

        If the state is set to true, then the compute
        environment accepts jobs from a queue and can scale out automatically based on queues.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines if AWS should manage the allocation of compute resources for processing jobs.

        If set to false, then you are in charge of providing the compute resource details.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("managed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role used by Batch to make calls to other AWS services on your behalf for managing the resources that you use with the service.

        By default, this role is created for you using
        the AWS managed service policy for Batch.

        :default: - Role using the 'service-role/AWSBatchServiceRole' policy.

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeEnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-batch.ComputeResourceType")
class ComputeResourceType(enum.Enum):
    '''(experimental) Property to specify if the compute environment uses On-Demand, SpotFleet, Fargate, or Fargate Spot compute resources.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        vpc = ec2.Vpc(self, "VPC")
        
        spot_environment = batch.ComputeEnvironment(self, "MySpotEnvironment",
            compute_resources=batch.ComputeResources(
                type=batch.ComputeResourceType.SPOT,
                bid_percentage=75,  # Bids for resources at 75% of the on-demand price
                vpc=vpc
            )
        )
    '''

    ON_DEMAND = "ON_DEMAND"
    '''(experimental) Resources will be EC2 On-Demand resources.

    :stability: experimental
    '''
    SPOT = "SPOT"
    '''(experimental) Resources will be EC2 SpotFleet resources.

    :stability: experimental
    '''
    FARGATE = "FARGATE"
    '''(experimental) Resources will be Fargate resources.

    :stability: experimental
    '''
    FARGATE_SPOT = "FARGATE_SPOT"
    '''(experimental) Resources will be Fargate Spot resources.

    Fargate Spot uses spare capacity in the AWS cloud to run your fault-tolerant,
    time-flexible jobs at up to a 70% discount. If AWS needs the resources back,
    jobs running on Fargate Spot will be interrupted with two minutes of notification.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.ComputeResources",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "allocation_strategy": "allocationStrategy",
        "bid_percentage": "bidPercentage",
        "compute_resources_tags": "computeResourcesTags",
        "desiredv_cpus": "desiredvCpus",
        "ec2_key_pair": "ec2KeyPair",
        "image": "image",
        "instance_role": "instanceRole",
        "instance_types": "instanceTypes",
        "launch_template": "launchTemplate",
        "maxv_cpus": "maxvCpus",
        "minv_cpus": "minvCpus",
        "placement_group": "placementGroup",
        "security_groups": "securityGroups",
        "spot_fleet_role": "spotFleetRole",
        "type": "type",
        "vpc_subnets": "vpcSubnets",
    },
)
class ComputeResources:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allocation_strategy: typing.Optional[AllocationStrategy] = None,
        bid_percentage: typing.Optional[jsii.Number] = None,
        compute_resources_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        desiredv_cpus: typing.Optional[jsii.Number] = None,
        ec2_key_pair: typing.Optional[builtins.str] = None,
        image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        instance_role: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.InstanceType]] = None,
        launch_template: typing.Optional["LaunchTemplateSpecification"] = None,
        maxv_cpus: typing.Optional[jsii.Number] = None,
        minv_cpus: typing.Optional[jsii.Number] = None,
        placement_group: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        spot_fleet_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        type: typing.Optional[ComputeResourceType] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''(experimental) Properties for defining the structure of the batch compute cluster.

        :param vpc: (experimental) The VPC network that all compute resources will be connected to.
        :param allocation_strategy: (experimental) The allocation strategy to use for the compute resource in case not enough instances of the best fitting instance type can be allocated. This could be due to availability of the instance type in the region or Amazon EC2 service limits. If this is not specified, the default for the EC2 ComputeResourceType is BEST_FIT, which will use only the best fitting instance type, waiting for additional capacity if it's not available. This allocation strategy keeps costs lower but can limit scaling. If you are using Spot Fleets with BEST_FIT then the Spot Fleet IAM Role must be specified. BEST_FIT_PROGRESSIVE will select an additional instance type that is large enough to meet the requirements of the jobs in the queue, with a preference for an instance type with a lower cost. The default value for the SPOT instance type is SPOT_CAPACITY_OPTIMIZED, which is only available for for this type of compute resources and will select an additional instance type that is large enough to meet the requirements of the jobs in the queue, with a preference for an instance type that is less likely to be interrupted. Default: AllocationStrategy.BEST_FIT
        :param bid_percentage: (experimental) This property will be ignored if you set the environment type to ON_DEMAND. The maximum percentage that a Spot Instance price can be when compared with the On-Demand price for that instance type before instances are launched. For example, if your maximum percentage is 20%, then the Spot price must be below 20% of the current On-Demand price for that EC2 instance. You always pay the lowest (market) price and never more than your maximum percentage. If you leave this field empty, the default value is 100% of the On-Demand price. Default: 100
        :param compute_resources_tags: (experimental) Key-value pair tags to be applied to resources that are launched in the compute environment. For AWS Batch, these take the form of "String1": "String2", where String1 is the tag key and String2 is the tag value—for example, { "Name": "AWS Batch Instance - C4OnDemand" }. Default: - no tags will be assigned on compute resources.
        :param desiredv_cpus: (experimental) The desired number of EC2 vCPUS in the compute environment. Default: - no desired vcpu value will be used.
        :param ec2_key_pair: (experimental) The EC2 key pair that is used for instances launched in the compute environment. If no key is defined, then SSH access is not allowed to provisioned compute resources. Default: - no SSH access will be possible.
        :param image: (experimental) The Amazon Machine Image (AMI) ID used for instances launched in the compute environment. Default: - no image will be used.
        :param instance_role: (experimental) The Amazon ECS instance profile applied to Amazon EC2 instances in a compute environment. You can specify the short name or full Amazon Resource Name (ARN) of an instance profile. For example, ecsInstanceRole or arn:aws:iam::<aws_account_id>:instance-profile/ecsInstanceRole . For more information, see Amazon ECS Instance Role in the AWS Batch User Guide. Default: - a new role will be created.
        :param instance_types: (experimental) The types of EC2 instances that may be launched in the compute environment. You can specify instance families to launch any instance type within those families (for example, c4 or p3), or you can specify specific sizes within a family (such as c4.8xlarge). You can also choose optimal to pick instance types (from the C, M, and R instance families) on the fly that match the demand of your job queues. Default: optimal
        :param launch_template: (experimental) An optional launch template to associate with your compute resources. For more information, see README file. Default: - no custom launch template will be used
        :param maxv_cpus: (experimental) The maximum number of EC2 vCPUs that an environment can reach. Each vCPU is equivalent to 1,024 CPU shares. You must specify at least one vCPU. Default: 256
        :param minv_cpus: (experimental) The minimum number of EC2 vCPUs that an environment should maintain (even if the compute environment state is DISABLED). Each vCPU is equivalent to 1,024 CPU shares. By keeping this set to 0 you will not have instance time wasted when there is no work to be run. If you set this above zero you will maintain that number of vCPUs at all times. Default: 0
        :param placement_group: (experimental) The Amazon EC2 placement group to associate with your compute resources. Default: - No placement group will be used.
        :param security_groups: (experimental) The EC2 security group(s) associated with instances launched in the compute environment. Default: - AWS default security group.
        :param spot_fleet_role: (experimental) This property will be ignored if you set the environment type to ON_DEMAND. The Amazon Resource Name (ARN) of the Amazon EC2 Spot Fleet IAM role applied to a SPOT compute environment. For more information, see Amazon EC2 Spot Fleet Role in the AWS Batch User Guide. Default: - no fleet role will be used.
        :param type: (experimental) The type of compute environment: ON_DEMAND, SPOT, FARGATE, or FARGATE_SPOT. Default: ON_DEMAND
        :param vpc_subnets: (experimental) The VPC subnets into which the compute resources are launched. Default: - private subnets of the supplied VPC.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            
            my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
                compute_resources=batch.ComputeResources(
                    image=ecs.EcsOptimizedAmi(
                        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
                    ),
                    vpc=vpc
                )
            )
        '''
        if isinstance(launch_template, dict):
            launch_template = LaunchTemplateSpecification(**launch_template)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if allocation_strategy is not None:
            self._values["allocation_strategy"] = allocation_strategy
        if bid_percentage is not None:
            self._values["bid_percentage"] = bid_percentage
        if compute_resources_tags is not None:
            self._values["compute_resources_tags"] = compute_resources_tags
        if desiredv_cpus is not None:
            self._values["desiredv_cpus"] = desiredv_cpus
        if ec2_key_pair is not None:
            self._values["ec2_key_pair"] = ec2_key_pair
        if image is not None:
            self._values["image"] = image
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if launch_template is not None:
            self._values["launch_template"] = launch_template
        if maxv_cpus is not None:
            self._values["maxv_cpus"] = maxv_cpus
        if minv_cpus is not None:
            self._values["minv_cpus"] = minv_cpus
        if placement_group is not None:
            self._values["placement_group"] = placement_group
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if spot_fleet_role is not None:
            self._values["spot_fleet_role"] = spot_fleet_role
        if type is not None:
            self._values["type"] = type
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The VPC network that all compute resources will be connected to.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def allocation_strategy(self) -> typing.Optional[AllocationStrategy]:
        '''(experimental) The allocation strategy to use for the compute resource in case not enough instances of the best fitting instance type can be allocated.

        This could be due to availability of the instance type in
        the region or Amazon EC2 service limits. If this is not specified, the default for the EC2
        ComputeResourceType is BEST_FIT, which will use only the best fitting instance type, waiting for
        additional capacity if it's not available. This allocation strategy keeps costs lower but can limit
        scaling. If you are using Spot Fleets with BEST_FIT then the Spot Fleet IAM Role must be specified.
        BEST_FIT_PROGRESSIVE will select an additional instance type that is large enough to meet the
        requirements of the jobs in the queue, with a preference for an instance type with a lower cost.
        The default value for the SPOT instance type is SPOT_CAPACITY_OPTIMIZED, which is only available for
        for this type of compute resources and will select an additional instance type that is large enough
        to meet the requirements of the jobs in the queue, with a preference for an instance type that is
        less likely to be interrupted.

        :default: AllocationStrategy.BEST_FIT

        :stability: experimental
        '''
        result = self._values.get("allocation_strategy")
        return typing.cast(typing.Optional[AllocationStrategy], result)

    @builtins.property
    def bid_percentage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) This property will be ignored if you set the environment type to ON_DEMAND.

        The maximum percentage that a Spot Instance price can be when compared with the On-Demand price for
        that instance type before instances are launched. For example, if your maximum percentage is 20%,
        then the Spot price must be below 20% of the current On-Demand price for that EC2 instance. You always
        pay the lowest (market) price and never more than your maximum percentage. If you leave this field empty,
        the default value is 100% of the On-Demand price.

        :default: 100

        :stability: experimental
        '''
        result = self._values.get("bid_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def compute_resources_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Key-value pair tags to be applied to resources that are launched in the compute environment.

        For AWS Batch, these take the form of "String1": "String2", where String1 is the tag key and
        String2 is the tag value—for example, { "Name": "AWS Batch Instance - C4OnDemand" }.

        :default: - no tags will be assigned on compute resources.

        :stability: experimental
        '''
        result = self._values.get("compute_resources_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def desiredv_cpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The desired number of EC2 vCPUS in the compute environment.

        :default: - no desired vcpu value will be used.

        :stability: experimental
        '''
        result = self._values.get("desiredv_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ec2_key_pair(self) -> typing.Optional[builtins.str]:
        '''(experimental) The EC2 key pair that is used for instances launched in the compute environment.

        If no key is defined, then SSH access is not allowed to provisioned compute resources.

        :default: - no SSH access will be possible.

        :stability: experimental
        '''
        result = self._values.get("ec2_key_pair")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''(experimental) The Amazon Machine Image (AMI) ID used for instances launched in the compute environment.

        :default: - no image will be used.

        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Amazon ECS instance profile applied to Amazon EC2 instances in a compute environment.

        You can specify
        the short name or full Amazon Resource Name (ARN) of an instance profile. For example, ecsInstanceRole or
        arn:aws:iam::<aws_account_id>:instance-profile/ecsInstanceRole . For more information, see Amazon ECS
        Instance Role in the AWS Batch User Guide.

        :default: - a new role will be created.

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/instance_IAM_role.html
        '''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.InstanceType]]:
        '''(experimental) The types of EC2 instances that may be launched in the compute environment.

        You can specify instance
        families to launch any instance type within those families (for example, c4 or p3), or you can specify
        specific sizes within a family (such as c4.8xlarge). You can also choose optimal to pick instance types
        (from the C, M, and R instance families) on the fly that match the demand of your job queues.

        :default: optimal

        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.InstanceType]], result)

    @builtins.property
    def launch_template(self) -> typing.Optional["LaunchTemplateSpecification"]:
        '''(experimental) An optional launch template to associate with your compute resources.

        For more information, see README file.

        :default: - no custom launch template will be used

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/launch-templates.html
        '''
        result = self._values.get("launch_template")
        return typing.cast(typing.Optional["LaunchTemplateSpecification"], result)

    @builtins.property
    def maxv_cpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of EC2 vCPUs that an environment can reach.

        Each vCPU is equivalent to
        1,024 CPU shares. You must specify at least one vCPU.

        :default: 256

        :stability: experimental
        '''
        result = self._values.get("maxv_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minv_cpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of EC2 vCPUs that an environment should maintain (even if the compute environment state is DISABLED).

        Each vCPU is equivalent to 1,024 CPU shares. By keeping this set to 0 you will not have instance time wasted when
        there is no work to be run. If you set this above zero you will maintain that number of vCPUs at all times.

        :default: 0

        :stability: experimental
        '''
        result = self._values.get("minv_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def placement_group(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Amazon EC2 placement group to associate with your compute resources.

        :default: - No placement group will be used.

        :stability: experimental
        '''
        result = self._values.get("placement_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''(experimental) The EC2 security group(s) associated with instances launched in the compute environment.

        :default: - AWS default security group.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def spot_fleet_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) This property will be ignored if you set the environment type to ON_DEMAND.

        The Amazon Resource Name (ARN) of the Amazon EC2 Spot Fleet IAM role applied to a SPOT compute environment.
        For more information, see Amazon EC2 Spot Fleet Role in the AWS Batch User Guide.

        :default: - no fleet role will be used.

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/spot_fleet_IAM_role.html
        '''
        result = self._values.get("spot_fleet_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def type(self) -> typing.Optional[ComputeResourceType]:
        '''(experimental) The type of compute environment: ON_DEMAND, SPOT, FARGATE, or FARGATE_SPOT.

        :default: ON_DEMAND

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[ComputeResourceType], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) The VPC subnets into which the compute resources are launched.

        :default: - private subnets of the supplied VPC.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExposedSecret(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.ExposedSecret",
):
    '''(experimental) Exposed secret for log configuration.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ssm as ssm
        
        
        batch.JobDefinition(self, "job-def",
            container=batch.JobDefinitionContainer(
                image=ecs.EcrImage.from_registry("docker/whalesay"),
                log_configuration=batch.LogConfiguration(
                    log_driver=batch.LogDriver.AWSLOGS,
                    options={"awslogs-region": "us-east-1"},
                    secret_options=[
                        batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                    ]
                )
            )
        )
    '''

    def __init__(self, option_name: builtins.str, secret_arn: builtins.str) -> None:
        '''
        :param option_name: -
        :param secret_arn: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [option_name, secret_arn])

    @jsii.member(jsii_name="fromParametersStore") # type: ignore[misc]
    @builtins.classmethod
    def from_parameters_store(
        cls,
        option_name: builtins.str,
        parameter: aws_cdk.aws_ssm.IParameter,
    ) -> "ExposedSecret":
        '''(experimental) User Parameters Store Parameter.

        :param option_name: - The name of the option.
        :param parameter: - A parameter from parameters store.

        :stability: experimental
        '''
        return typing.cast("ExposedSecret", jsii.sinvoke(cls, "fromParametersStore", [option_name, parameter]))

    @jsii.member(jsii_name="fromSecretsManager") # type: ignore[misc]
    @builtins.classmethod
    def from_secrets_manager(
        cls,
        option_name: builtins.str,
        secret: aws_cdk.aws_secretsmanager.ISecret,
    ) -> "ExposedSecret":
        '''(experimental) Use Secrets Manager Secret.

        :param option_name: - The name of the option.
        :param secret: - A secret from secrets manager.

        :stability: experimental
        '''
        return typing.cast("ExposedSecret", jsii.sinvoke(cls, "fromSecretsManager", [option_name, secret]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionName")
    def option_name(self) -> builtins.str:
        '''(experimental) Name of the option.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "optionName"))

    @option_name.setter
    def option_name(self, value: builtins.str) -> None:
        jsii.set(self, "optionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''(experimental) ARN of the secret option.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))

    @secret_arn.setter
    def secret_arn(self, value: builtins.str) -> None:
        jsii.set(self, "secretArn", value)


@jsii.interface(jsii_type="@aws-cdk/aws-batch.IComputeEnvironment")
class IComputeEnvironment(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''(experimental) Properties of a compute environment.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentArn")
    def compute_environment_arn(self) -> builtins.str:
        '''(experimental) The ARN of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        '''(experimental) The name of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IComputeEnvironmentProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''(experimental) Properties of a compute environment.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch.IComputeEnvironment"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentArn")
    def compute_environment_arn(self) -> builtins.str:
        '''(experimental) The ARN of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        '''(experimental) The name of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IComputeEnvironment).__jsii_proxy_class__ = lambda : _IComputeEnvironmentProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch.IJobDefinition")
class IJobDefinition(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''(experimental) An interface representing a job definition - either a new one, created with the CDK, *using the {@link JobDefinition} class, or existing ones, referenced using the {@link JobDefinition.fromJobDefinitionArn} method.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionArn")
    def job_definition_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job definition.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> builtins.str:
        '''(experimental) The name of the batch job definition.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IJobDefinitionProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''(experimental) An interface representing a job definition - either a new one, created with the CDK, *using the {@link JobDefinition} class, or existing ones, referenced using the {@link JobDefinition.fromJobDefinitionArn} method.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch.IJobDefinition"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionArn")
    def job_definition_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job definition.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> builtins.str:
        '''(experimental) The name of the batch job definition.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJobDefinition).__jsii_proxy_class__ = lambda : _IJobDefinitionProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch.IJobQueue")
class IJobQueue(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''(experimental) Properties of a Job Queue.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueArn")
    def job_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job queue.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> builtins.str:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IJobQueueProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''(experimental) Properties of a Job Queue.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch.IJobQueue"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueArn")
    def job_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job queue.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> builtins.str:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJobQueue).__jsii_proxy_class__ = lambda : _IJobQueueProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch.IMultiNodeProps")
class IMultiNodeProps(typing_extensions.Protocol):
    '''(experimental) Properties for specifying multi-node properties for compute resources.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        '''(experimental) The number of nodes associated with a multi-node parallel job.

        :stability: experimental
        '''
        ...

    @count.setter
    def count(self, value: jsii.Number) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mainNode")
    def main_node(self) -> jsii.Number:
        '''(experimental) Specifies the node index for the main node of a multi-node parallel job.

        This node index value must be fewer than the number of nodes.

        :stability: experimental
        '''
        ...

    @main_node.setter
    def main_node(self, value: jsii.Number) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeProps")
    def range_props(self) -> typing.List["INodeRangeProps"]:
        '''(experimental) A list of node ranges and their properties associated with a multi-node parallel job.

        :stability: experimental
        '''
        ...

    @range_props.setter
    def range_props(self, value: typing.List["INodeRangeProps"]) -> None:
        ...


class _IMultiNodePropsProxy:
    '''(experimental) Properties for specifying multi-node properties for compute resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch.IMultiNodeProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        '''(experimental) The number of nodes associated with a multi-node parallel job.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        jsii.set(self, "count", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mainNode")
    def main_node(self) -> jsii.Number:
        '''(experimental) Specifies the node index for the main node of a multi-node parallel job.

        This node index value must be fewer than the number of nodes.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "mainNode"))

    @main_node.setter
    def main_node(self, value: jsii.Number) -> None:
        jsii.set(self, "mainNode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeProps")
    def range_props(self) -> typing.List["INodeRangeProps"]:
        '''(experimental) A list of node ranges and their properties associated with a multi-node parallel job.

        :stability: experimental
        '''
        return typing.cast(typing.List["INodeRangeProps"], jsii.get(self, "rangeProps"))

    @range_props.setter
    def range_props(self, value: typing.List["INodeRangeProps"]) -> None:
        jsii.set(self, "rangeProps", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMultiNodeProps).__jsii_proxy_class__ = lambda : _IMultiNodePropsProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch.INodeRangeProps")
class INodeRangeProps(typing_extensions.Protocol):
    '''(experimental) Properties for a multi-node batch job.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> "JobDefinitionContainer":
        '''(experimental) The container details for the node range.

        :stability: experimental
        '''
        ...

    @container.setter
    def container(self, value: "JobDefinitionContainer") -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromNodeIndex")
    def from_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum node index value to apply this container definition against.

        You may nest node ranges, for example 0:10 and 4:5, in which case the 4:5 range properties override the 0:10 properties.

        :default: 0

        :stability: experimental
        '''
        ...

    @from_node_index.setter
    def from_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toNodeIndex")
    def to_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum node index value to apply this container definition against. If omitted, the highest value is used relative.

        to the number of nodes associated with the job. You may nest node ranges, for example 0:10 and 4:5,
        in which case the 4:5 range properties override the 0:10 properties.

        :default: {@link IMultiNodeprops.count}

        :stability: experimental
        '''
        ...

    @to_node_index.setter
    def to_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _INodeRangePropsProxy:
    '''(experimental) Properties for a multi-node batch job.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch.INodeRangeProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> "JobDefinitionContainer":
        '''(experimental) The container details for the node range.

        :stability: experimental
        '''
        return typing.cast("JobDefinitionContainer", jsii.get(self, "container"))

    @container.setter
    def container(self, value: "JobDefinitionContainer") -> None:
        jsii.set(self, "container", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromNodeIndex")
    def from_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum node index value to apply this container definition against.

        You may nest node ranges, for example 0:10 and 4:5, in which case the 4:5 range properties override the 0:10 properties.

        :default: 0

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fromNodeIndex"))

    @from_node_index.setter
    def from_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "fromNodeIndex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toNodeIndex")
    def to_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum node index value to apply this container definition against. If omitted, the highest value is used relative.

        to the number of nodes associated with the job. You may nest node ranges, for example 0:10 and 4:5,
        in which case the 4:5 range properties override the 0:10 properties.

        :default: {@link IMultiNodeprops.count}

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "toNodeIndex"))

    @to_node_index.setter
    def to_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "toNodeIndex", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INodeRangeProps).__jsii_proxy_class__ = lambda : _INodeRangePropsProxy


@jsii.implements(IJobDefinition)
class JobDefinition(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.JobDefinition",
):
    '''(experimental) Batch Job Definition.

    Defines a batch job definition to execute a specific batch job.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ecr as ecr
        
        
        repo = ecr.Repository.from_repository_name(self, "batch-job-repo", "todo-list")
        
        batch.JobDefinition(self, "batch-job-def-from-ecr",
            container=batch.JobDefinitionContainer(
                image=ecs.EcrImage(repo, "latest")
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        container: "JobDefinitionContainer",
        job_definition_name: typing.Optional[builtins.str] = None,
        node_props: typing.Optional[IMultiNodeProps] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        platform_capabilities: typing.Optional[typing.Sequence["PlatformCapabilities"]] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param container: (experimental) An object with various properties specific to container-based jobs.
        :param job_definition_name: (experimental) The name of the job definition. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: Cloudformation-generated name
        :param node_props: (experimental) An object with various properties specific to multi-node parallel jobs. Default: - undefined
        :param parameters: (experimental) When you submit a job, you can specify parameters that should replace the placeholders or override the default job definition parameters. Parameters in job submission requests take precedence over the defaults in a job definition. This allows you to use the same job definition for multiple jobs that use the same format, and programmatically change values in the command at submission time. Default: - undefined
        :param platform_capabilities: (experimental) The platform capabilities required by the job definition. Default: - EC2
        :param retry_attempts: (experimental) The number of times to move a job to the RUNNABLE status. You may specify between 1 and 10 attempts. If the value of attempts is greater than one, the job is retried on failure the same number of attempts as the value. Default: 1
        :param timeout: (experimental) The timeout configuration for jobs that are submitted with this job definition. You can specify a timeout duration after which AWS Batch terminates your jobs if they have not finished. Default: - undefined

        :stability: experimental
        '''
        props = JobDefinitionProps(
            container=container,
            job_definition_name=job_definition_name,
            node_props=node_props,
            parameters=parameters,
            platform_capabilities=platform_capabilities,
            retry_attempts=retry_attempts,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromJobDefinitionArn") # type: ignore[misc]
    @builtins.classmethod
    def from_job_definition_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        job_definition_arn: builtins.str,
    ) -> IJobDefinition:
        '''(experimental) Imports an existing batch job definition by its amazon resource name.

        :param scope: -
        :param id: -
        :param job_definition_arn: -

        :stability: experimental
        '''
        return typing.cast(IJobDefinition, jsii.sinvoke(cls, "fromJobDefinitionArn", [scope, id, job_definition_arn]))

    @jsii.member(jsii_name="fromJobDefinitionName") # type: ignore[misc]
    @builtins.classmethod
    def from_job_definition_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        job_definition_name: builtins.str,
    ) -> IJobDefinition:
        '''(experimental) Imports an existing batch job definition by its name.

        If name is specified without a revision then the latest active revision is used.

        :param scope: -
        :param id: -
        :param job_definition_name: -

        :stability: experimental
        '''
        return typing.cast(IJobDefinition, jsii.sinvoke(cls, "fromJobDefinitionName", [scope, id, job_definition_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionArn")
    def job_definition_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job definition.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> builtins.str:
        '''(experimental) The name of the batch job definition.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.JobDefinitionContainer",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "assign_public_ip": "assignPublicIp",
        "command": "command",
        "environment": "environment",
        "execution_role": "executionRole",
        "gpu_count": "gpuCount",
        "instance_type": "instanceType",
        "job_role": "jobRole",
        "linux_params": "linuxParams",
        "log_configuration": "logConfiguration",
        "memory_limit_mib": "memoryLimitMiB",
        "mount_points": "mountPoints",
        "platform_version": "platformVersion",
        "privileged": "privileged",
        "read_only": "readOnly",
        "ulimits": "ulimits",
        "user": "user",
        "vcpus": "vcpus",
        "volumes": "volumes",
    },
)
class JobDefinitionContainer:
    def __init__(
        self,
        *,
        image: aws_cdk.aws_ecs.ContainerImage,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        execution_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        gpu_count: typing.Optional[jsii.Number] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        job_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        linux_params: typing.Optional[aws_cdk.aws_ecs.LinuxParameters] = None,
        log_configuration: typing.Optional["LogConfiguration"] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        mount_points: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.MountPoint]] = None,
        platform_version: typing.Optional[aws_cdk.aws_ecs.FargatePlatformVersion] = None,
        privileged: typing.Optional[builtins.bool] = None,
        read_only: typing.Optional[builtins.bool] = None,
        ulimits: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.Ulimit]] = None,
        user: typing.Optional[builtins.str] = None,
        vcpus: typing.Optional[jsii.Number] = None,
        volumes: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.Volume]] = None,
    ) -> None:
        '''(experimental) Properties of a job definition container.

        :param image: (experimental) The image used to start a container.
        :param assign_public_ip: (experimental) Whether or not to assign a public IP to the job. Default: - false
        :param command: (experimental) The command that is passed to the container. If you provide a shell command as a single string, you have to quote command-line arguments. Default: - CMD value built into container image.
        :param environment: (experimental) The environment variables to pass to the container. Default: none
        :param execution_role: (experimental) The IAM role that AWS Batch can assume. Required when using Fargate. Default: - None
        :param gpu_count: (experimental) The number of physical GPUs to reserve for the container. The number of GPUs reserved for all containers in a job should not exceed the number of available GPUs on the compute resource that the job is launched on. Default: - No GPU reservation.
        :param instance_type: (experimental) The instance type to use for a multi-node parallel job. Currently all node groups in a multi-node parallel job must use the same instance type. This parameter is not valid for single-node container jobs. Default: - None
        :param job_role: (experimental) The IAM role that the container can assume for AWS permissions. Default: - An IAM role will created.
        :param linux_params: (experimental) Linux-specific modifications that are applied to the container, such as details for device mappings. For now, only the ``devices`` property is supported. Default: - None will be used.
        :param log_configuration: (experimental) The log configuration specification for the container. Default: - containers use the same logging driver that the Docker daemon uses
        :param memory_limit_mib: (experimental) The hard limit (in MiB) of memory to present to the container. If your container attempts to exceed the memory specified here, the container is killed. You must specify at least 4 MiB of memory for EC2 and 512 MiB for Fargate. Default: - 4 for EC2, 512 for Fargate
        :param mount_points: (experimental) The mount points for data volumes in your container. Default: - No mount points will be used.
        :param platform_version: (experimental) Fargate platform version. Default: - LATEST platform version will be used
        :param privileged: (experimental) When this parameter is true, the container is given elevated privileges on the host container instance (similar to the root user). Default: false
        :param read_only: (experimental) When this parameter is true, the container is given read-only access to its root file system. Default: false
        :param ulimits: (experimental) A list of ulimits to set in the container. Default: - No limits.
        :param user: (experimental) The user name to use inside the container. Default: - None will be used.
        :param vcpus: (experimental) The number of vCPUs reserved for the container. Each vCPU is equivalent to 1,024 CPU shares. You must specify at least one vCPU for EC2 and 0.25 for Fargate. Default: - 1 for EC2, 0.25 for Fargate
        :param volumes: (experimental) A list of data volumes used in a job. Default: - No data volumes will be used.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ssm as ssm
            
            
            batch.JobDefinition(self, "job-def",
                container=batch.JobDefinitionContainer(
                    image=ecs.EcrImage.from_registry("docker/whalesay"),
                    log_configuration=batch.LogConfiguration(
                        log_driver=batch.LogDriver.AWSLOGS,
                        options={"awslogs-region": "us-east-1"},
                        secret_options=[
                            batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                        ]
                    )
                )
            )
        '''
        if isinstance(log_configuration, dict):
            log_configuration = LogConfiguration(**log_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
        }
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if command is not None:
            self._values["command"] = command
        if environment is not None:
            self._values["environment"] = environment
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if gpu_count is not None:
            self._values["gpu_count"] = gpu_count
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if job_role is not None:
            self._values["job_role"] = job_role
        if linux_params is not None:
            self._values["linux_params"] = linux_params
        if log_configuration is not None:
            self._values["log_configuration"] = log_configuration
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if mount_points is not None:
            self._values["mount_points"] = mount_points
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if privileged is not None:
            self._values["privileged"] = privileged
        if read_only is not None:
            self._values["read_only"] = read_only
        if ulimits is not None:
            self._values["ulimits"] = ulimits
        if user is not None:
            self._values["user"] = user
        if vcpus is not None:
            self._values["vcpus"] = vcpus
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def image(self) -> aws_cdk.aws_ecs.ContainerImage:
        '''(experimental) The image used to start a container.

        :stability: experimental
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(aws_cdk.aws_ecs.ContainerImage, result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not to assign a public IP to the job.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The command that is passed to the container.

        If you provide a shell command as a single string, you have to quote command-line arguments.

        :default: - CMD value built into container image.

        :stability: experimental
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The environment variables to pass to the container.

        :default: none

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role that AWS Batch can assume.

        Required when using Fargate.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def gpu_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of physical GPUs to reserve for the container.

        The number of GPUs reserved for all
        containers in a job should not exceed the number of available GPUs on the compute resource that the job is launched on.

        :default: - No GPU reservation.

        :stability: experimental
        '''
        result = self._values.get("gpu_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''(experimental) The instance type to use for a multi-node parallel job.

        Currently all node groups in a
        multi-node parallel job must use the same instance type. This parameter is not valid
        for single-node container jobs.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def job_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role that the container can assume for AWS permissions.

        :default: - An IAM role will created.

        :stability: experimental
        '''
        result = self._values.get("job_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def linux_params(self) -> typing.Optional[aws_cdk.aws_ecs.LinuxParameters]:
        '''(experimental) Linux-specific modifications that are applied to the container, such as details for device mappings.

        For now, only the ``devices`` property is supported.

        :default: - None will be used.

        :stability: experimental
        '''
        result = self._values.get("linux_params")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.LinuxParameters], result)

    @builtins.property
    def log_configuration(self) -> typing.Optional["LogConfiguration"]:
        '''(experimental) The log configuration specification for the container.

        :default: - containers use the same logging driver that the Docker daemon uses

        :stability: experimental
        '''
        result = self._values.get("log_configuration")
        return typing.cast(typing.Optional["LogConfiguration"], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The hard limit (in MiB) of memory to present to the container.

        If your container attempts to exceed
        the memory specified here, the container is killed. You must specify at least 4 MiB of memory for EC2 and 512 MiB for Fargate.

        :default: - 4 for EC2, 512 for Fargate

        :stability: experimental
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mount_points(self) -> typing.Optional[typing.List[aws_cdk.aws_ecs.MountPoint]]:
        '''(experimental) The mount points for data volumes in your container.

        :default: - No mount points will be used.

        :stability: experimental
        '''
        result = self._values.get("mount_points")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.MountPoint]], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs.FargatePlatformVersion]:
        '''(experimental) Fargate platform version.

        :default: - LATEST platform version will be used

        :stability: experimental
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.FargatePlatformVersion], result)

    @builtins.property
    def privileged(self) -> typing.Optional[builtins.bool]:
        '''(experimental) When this parameter is true, the container is given elevated privileges on the host container instance (similar to the root user).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("privileged")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''(experimental) When this parameter is true, the container is given read-only access to its root file system.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ulimits(self) -> typing.Optional[typing.List[aws_cdk.aws_ecs.Ulimit]]:
        '''(experimental) A list of ulimits to set in the container.

        :default: - No limits.

        :stability: experimental
        '''
        result = self._values.get("ulimits")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.Ulimit]], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''(experimental) The user name to use inside the container.

        :default: - None will be used.

        :stability: experimental
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vcpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of vCPUs reserved for the container.

        Each vCPU is equivalent to
        1,024 CPU shares. You must specify at least one vCPU for EC2 and 0.25 for Fargate.

        :default: - 1 for EC2, 0.25 for Fargate

        :stability: experimental
        '''
        result = self._values.get("vcpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[aws_cdk.aws_ecs.Volume]]:
        '''(experimental) A list of data volumes used in a job.

        :default: - No data volumes will be used.

        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.Volume]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobDefinitionContainer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.JobDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={
        "container": "container",
        "job_definition_name": "jobDefinitionName",
        "node_props": "nodeProps",
        "parameters": "parameters",
        "platform_capabilities": "platformCapabilities",
        "retry_attempts": "retryAttempts",
        "timeout": "timeout",
    },
)
class JobDefinitionProps:
    def __init__(
        self,
        *,
        container: JobDefinitionContainer,
        job_definition_name: typing.Optional[builtins.str] = None,
        node_props: typing.Optional[IMultiNodeProps] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        platform_capabilities: typing.Optional[typing.Sequence["PlatformCapabilities"]] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link JobDefinition} construct.

        :param container: (experimental) An object with various properties specific to container-based jobs.
        :param job_definition_name: (experimental) The name of the job definition. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: Cloudformation-generated name
        :param node_props: (experimental) An object with various properties specific to multi-node parallel jobs. Default: - undefined
        :param parameters: (experimental) When you submit a job, you can specify parameters that should replace the placeholders or override the default job definition parameters. Parameters in job submission requests take precedence over the defaults in a job definition. This allows you to use the same job definition for multiple jobs that use the same format, and programmatically change values in the command at submission time. Default: - undefined
        :param platform_capabilities: (experimental) The platform capabilities required by the job definition. Default: - EC2
        :param retry_attempts: (experimental) The number of times to move a job to the RUNNABLE status. You may specify between 1 and 10 attempts. If the value of attempts is greater than one, the job is retried on failure the same number of attempts as the value. Default: 1
        :param timeout: (experimental) The timeout configuration for jobs that are submitted with this job definition. You can specify a timeout duration after which AWS Batch terminates your jobs if they have not finished. Default: - undefined

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ssm as ssm
            
            
            batch.JobDefinition(self, "job-def",
                container=batch.JobDefinitionContainer(
                    image=ecs.EcrImage.from_registry("docker/whalesay"),
                    log_configuration=batch.LogConfiguration(
                        log_driver=batch.LogDriver.AWSLOGS,
                        options={"awslogs-region": "us-east-1"},
                        secret_options=[
                            batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                        ]
                    )
                )
            )
        '''
        if isinstance(container, dict):
            container = JobDefinitionContainer(**container)
        self._values: typing.Dict[str, typing.Any] = {
            "container": container,
        }
        if job_definition_name is not None:
            self._values["job_definition_name"] = job_definition_name
        if node_props is not None:
            self._values["node_props"] = node_props
        if parameters is not None:
            self._values["parameters"] = parameters
        if platform_capabilities is not None:
            self._values["platform_capabilities"] = platform_capabilities
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def container(self) -> JobDefinitionContainer:
        '''(experimental) An object with various properties specific to container-based jobs.

        :stability: experimental
        '''
        result = self._values.get("container")
        assert result is not None, "Required property 'container' is missing"
        return typing.cast(JobDefinitionContainer, result)

    @builtins.property
    def job_definition_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the job definition.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :default: Cloudformation-generated name

        :stability: experimental
        '''
        result = self._values.get("job_definition_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_props(self) -> typing.Optional[IMultiNodeProps]:
        '''(experimental) An object with various properties specific to multi-node parallel jobs.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("node_props")
        return typing.cast(typing.Optional[IMultiNodeProps], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) When you submit a job, you can specify parameters that should replace the placeholders or override the default job definition parameters.

        Parameters
        in job submission requests take precedence over the defaults in a job definition.
        This allows you to use the same job definition for multiple jobs that use the same
        format, and programmatically change values in the command at submission time.

        :default: - undefined

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def platform_capabilities(
        self,
    ) -> typing.Optional[typing.List["PlatformCapabilities"]]:
        '''(experimental) The platform capabilities required by the job definition.

        :default: - EC2

        :stability: experimental
        '''
        result = self._values.get("platform_capabilities")
        return typing.cast(typing.Optional[typing.List["PlatformCapabilities"]], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times to move a job to the RUNNABLE status.

        You may specify between 1 and
        10 attempts. If the value of attempts is greater than one, the job is retried on failure
        the same number of attempts as the value.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''(experimental) The timeout configuration for jobs that are submitted with this job definition.

        You can specify
        a timeout duration after which AWS Batch terminates your jobs if they have not finished.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IJobQueue)
class JobQueue(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.JobQueue",
):
    '''(experimental) Batch Job Queue.

    Defines a batch job queue to define how submitted batch jobs
    should be ran based on specified batch compute environments.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # shared_compute_envs: batch.ComputeEnvironment
        
        high_prio_queue = batch.JobQueue(self, "JobQueue",
            compute_environments=[batch.JobQueueComputeEnvironment(
                compute_environment=shared_compute_envs,
                order=1
            )],
            priority=2
        )
        
        low_prio_queue = batch.JobQueue(self, "JobQueue",
            compute_environments=[batch.JobQueueComputeEnvironment(
                compute_environment=shared_compute_envs,
                order=1
            )],
            priority=1
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compute_environments: typing.Sequence["JobQueueComputeEnvironment"],
        enabled: typing.Optional[builtins.bool] = None,
        job_queue_name: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param compute_environments: (experimental) The set of compute environments mapped to a job queue and their order relative to each other. The job scheduler uses this parameter to determine which compute environment should execute a given job. Compute environments must be in the VALID state before you can associate them with a job queue. You can associate up to three compute environments with a job queue.
        :param enabled: (experimental) The state of the job queue. If set to true, it is able to accept jobs. Default: true
        :param job_queue_name: (experimental) A name for the job queue. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - Cloudformation-generated name
        :param priority: (experimental) The priority of the job queue. Job queues with a higher priority (or a higher integer value for the priority parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order, for example, a job queue with a priority value of 10 is given scheduling preference over a job queue with a priority value of 1. Default: 1

        :stability: experimental
        '''
        props = JobQueueProps(
            compute_environments=compute_environments,
            enabled=enabled,
            job_queue_name=job_queue_name,
            priority=priority,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromJobQueueArn") # type: ignore[misc]
    @builtins.classmethod
    def from_job_queue_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        job_queue_arn: builtins.str,
    ) -> IJobQueue:
        '''(experimental) Fetches an existing batch job queue by its amazon resource name.

        :param scope: -
        :param id: -
        :param job_queue_arn: -

        :stability: experimental
        '''
        return typing.cast(IJobQueue, jsii.sinvoke(cls, "fromJobQueueArn", [scope, id, job_queue_arn]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueArn")
    def job_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job queue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> builtins.str:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.JobQueueComputeEnvironment",
    jsii_struct_bases=[],
    name_mapping={"compute_environment": "computeEnvironment", "order": "order"},
)
class JobQueueComputeEnvironment:
    def __init__(
        self,
        *,
        compute_environment: IComputeEnvironment,
        order: jsii.Number,
    ) -> None:
        '''(experimental) Properties for mapping a compute environment to a job queue.

        :param compute_environment: (experimental) The batch compute environment to use for processing submitted jobs to this queue.
        :param order: (experimental) The order in which this compute environment will be selected for dynamic allocation of resources to process submitted jobs.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_batch as batch
            
            # compute_environment: batch.ComputeEnvironment
            
            job_queue_compute_environment = batch.JobQueueComputeEnvironment(
                compute_environment=compute_environment,
                order=123
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environment": compute_environment,
            "order": order,
        }

    @builtins.property
    def compute_environment(self) -> IComputeEnvironment:
        '''(experimental) The batch compute environment to use for processing submitted jobs to this queue.

        :stability: experimental
        '''
        result = self._values.get("compute_environment")
        assert result is not None, "Required property 'compute_environment' is missing"
        return typing.cast(IComputeEnvironment, result)

    @builtins.property
    def order(self) -> jsii.Number:
        '''(experimental) The order in which this compute environment will be selected for dynamic allocation of resources to process submitted jobs.

        :stability: experimental
        '''
        result = self._values.get("order")
        assert result is not None, "Required property 'order' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobQueueComputeEnvironment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.JobQueueProps",
    jsii_struct_bases=[],
    name_mapping={
        "compute_environments": "computeEnvironments",
        "enabled": "enabled",
        "job_queue_name": "jobQueueName",
        "priority": "priority",
    },
)
class JobQueueProps:
    def __init__(
        self,
        *,
        compute_environments: typing.Sequence[JobQueueComputeEnvironment],
        enabled: typing.Optional[builtins.bool] = None,
        job_queue_name: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties of a batch job queue.

        :param compute_environments: (experimental) The set of compute environments mapped to a job queue and their order relative to each other. The job scheduler uses this parameter to determine which compute environment should execute a given job. Compute environments must be in the VALID state before you can associate them with a job queue. You can associate up to three compute environments with a job queue.
        :param enabled: (experimental) The state of the job queue. If set to true, it is able to accept jobs. Default: true
        :param job_queue_name: (experimental) A name for the job queue. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - Cloudformation-generated name
        :param priority: (experimental) The priority of the job queue. Job queues with a higher priority (or a higher integer value for the priority parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order, for example, a job queue with a priority value of 10 is given scheduling preference over a job queue with a priority value of 1. Default: 1

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # shared_compute_envs: batch.ComputeEnvironment
            
            high_prio_queue = batch.JobQueue(self, "JobQueue",
                compute_environments=[batch.JobQueueComputeEnvironment(
                    compute_environment=shared_compute_envs,
                    order=1
                )],
                priority=2
            )
            
            low_prio_queue = batch.JobQueue(self, "JobQueue",
                compute_environments=[batch.JobQueueComputeEnvironment(
                    compute_environment=shared_compute_envs,
                    order=1
                )],
                priority=1
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environments": compute_environments,
        }
        if enabled is not None:
            self._values["enabled"] = enabled
        if job_queue_name is not None:
            self._values["job_queue_name"] = job_queue_name
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def compute_environments(self) -> typing.List[JobQueueComputeEnvironment]:
        '''(experimental) The set of compute environments mapped to a job queue and their order relative to each other.

        The job scheduler uses this parameter to
        determine which compute environment should execute a given job. Compute environments must be in the VALID state before you can associate them
        with a job queue. You can associate up to three compute environments with a job queue.

        :stability: experimental
        '''
        result = self._values.get("compute_environments")
        assert result is not None, "Required property 'compute_environments' is missing"
        return typing.cast(typing.List[JobQueueComputeEnvironment], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The state of the job queue.

        If set to true, it is able to accept jobs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def job_queue_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :default: - Cloudformation-generated name

        :stability: experimental
        '''
        result = self._values.get("job_queue_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The priority of the job queue.

        Job queues with a higher priority (or a higher integer value for the priority parameter) are evaluated first
        when associated with the same compute environment. Priority is determined in descending order, for example, a job queue with a priority value
        of 10 is given scheduling preference over a job queue with a priority value of 1.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobQueueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.LaunchTemplateSpecification",
    jsii_struct_bases=[],
    name_mapping={"launch_template_name": "launchTemplateName", "version": "version"},
)
class LaunchTemplateSpecification:
    def __init__(
        self,
        *,
        launch_template_name: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Launch template property specification.

        :param launch_template_name: (experimental) The Launch template name.
        :param version: (experimental) The launch template version to be used (optional). Default: - the default version of the launch template

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            # my_launch_template: ec2.CfnLaunchTemplate
            
            
            my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
                compute_resources=batch.ComputeResources(
                    launch_template=batch.LaunchTemplateSpecification(
                        launch_template_name=my_launch_template.launch_template_name
                    ),
                    vpc=vpc
                ),
                compute_environment_name="MyStorageCapableComputeEnvironment"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "launch_template_name": launch_template_name,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def launch_template_name(self) -> builtins.str:
        '''(experimental) The Launch template name.

        :stability: experimental
        '''
        result = self._values.get("launch_template_name")
        assert result is not None, "Required property 'launch_template_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The launch template version to be used (optional).

        :default: - the default version of the launch template

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LaunchTemplateSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch.LogConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "log_driver": "logDriver",
        "options": "options",
        "secret_options": "secretOptions",
    },
)
class LogConfiguration:
    def __init__(
        self,
        *,
        log_driver: "LogDriver",
        options: typing.Any = None,
        secret_options: typing.Optional[typing.Sequence[ExposedSecret]] = None,
    ) -> None:
        '''(experimental) Log configuration options to send to a custom log driver for the container.

        :param log_driver: (experimental) The log driver to use for the container.
        :param options: (experimental) The configuration options to send to the log driver. Default: - No configuration options are sent
        :param secret_options: (experimental) The secrets to pass to the log configuration as options. For more information, see https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data-secrets.html#secrets-logconfig Default: - No secrets are passed

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ssm as ssm
            
            
            batch.JobDefinition(self, "job-def",
                container=batch.JobDefinitionContainer(
                    image=ecs.EcrImage.from_registry("docker/whalesay"),
                    log_configuration=batch.LogConfiguration(
                        log_driver=batch.LogDriver.AWSLOGS,
                        options={"awslogs-region": "us-east-1"},
                        secret_options=[
                            batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                        ]
                    )
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_driver": log_driver,
        }
        if options is not None:
            self._values["options"] = options
        if secret_options is not None:
            self._values["secret_options"] = secret_options

    @builtins.property
    def log_driver(self) -> "LogDriver":
        '''(experimental) The log driver to use for the container.

        :stability: experimental
        '''
        result = self._values.get("log_driver")
        assert result is not None, "Required property 'log_driver' is missing"
        return typing.cast("LogDriver", result)

    @builtins.property
    def options(self) -> typing.Any:
        '''(experimental) The configuration options to send to the log driver.

        :default: - No configuration options are sent

        :stability: experimental
        '''
        result = self._values.get("options")
        return typing.cast(typing.Any, result)

    @builtins.property
    def secret_options(self) -> typing.Optional[typing.List[ExposedSecret]]:
        '''(experimental) The secrets to pass to the log configuration as options.

        For more information, see https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data-secrets.html#secrets-logconfig

        :default: - No secrets are passed

        :stability: experimental
        '''
        result = self._values.get("secret_options")
        return typing.cast(typing.Optional[typing.List[ExposedSecret]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-batch.LogDriver")
class LogDriver(enum.Enum):
    '''(experimental) The log driver to use for the container.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ssm as ssm
        
        
        batch.JobDefinition(self, "job-def",
            container=batch.JobDefinitionContainer(
                image=ecs.EcrImage.from_registry("docker/whalesay"),
                log_configuration=batch.LogConfiguration(
                    log_driver=batch.LogDriver.AWSLOGS,
                    options={"awslogs-region": "us-east-1"},
                    secret_options=[
                        batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                    ]
                )
            )
        )
    '''

    AWSLOGS = "AWSLOGS"
    '''(experimental) Specifies the Amazon CloudWatch Logs logging driver.

    :stability: experimental
    '''
    FLUENTD = "FLUENTD"
    '''(experimental) Specifies the Fluentd logging driver.

    :stability: experimental
    '''
    GELF = "GELF"
    '''(experimental) Specifies the Graylog Extended Format (GELF) logging driver.

    :stability: experimental
    '''
    JOURNALD = "JOURNALD"
    '''(experimental) Specifies the journald logging driver.

    :stability: experimental
    '''
    LOGENTRIES = "LOGENTRIES"
    '''(experimental) Specifies the logentries logging driver.

    :stability: experimental
    '''
    JSON_FILE = "JSON_FILE"
    '''(experimental) Specifies the JSON file logging driver.

    :stability: experimental
    '''
    SPLUNK = "SPLUNK"
    '''(experimental) Specifies the Splunk logging driver.

    :stability: experimental
    '''
    SYSLOG = "SYSLOG"
    '''(experimental) Specifies the syslog logging driver.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-batch.PlatformCapabilities")
class PlatformCapabilities(enum.Enum):
    '''(experimental) Platform capabilities.

    :stability: experimental
    '''

    EC2 = "EC2"
    '''(experimental) Specifies EC2 environment.

    :stability: experimental
    '''
    FARGATE = "FARGATE"
    '''(experimental) Specifies Fargate environment.

    :stability: experimental
    '''


@jsii.implements(IComputeEnvironment)
class ComputeEnvironment(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch.ComputeEnvironment",
):
    '''(experimental) Batch Compute Environment.

    Defines a batch compute environment to run batch jobs on.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # vpc: ec2.Vpc
        
        my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
            compute_resources=batch.ComputeResources(
                image=ecs.EcsOptimizedAmi(
                    generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
                ),
                vpc=vpc
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional[ComputeResources] = None,
        enabled: typing.Optional[builtins.bool] = None,
        managed: typing.Optional[builtins.bool] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param compute_environment_name: (experimental) A name for the compute environment. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - CloudFormation-generated name
        :param compute_resources: (experimental) The details of the required compute resources for the managed compute environment. If specified, and this is an unmanaged compute environment, will throw an error. By default, AWS Batch managed compute environments use a recent, approved version of the Amazon ECS-optimized AMI for compute resources. Default: - CloudFormation defaults
        :param enabled: (experimental) The state of the compute environment. If the state is set to true, then the compute environment accepts jobs from a queue and can scale out automatically based on queues. Default: true
        :param managed: (experimental) Determines if AWS should manage the allocation of compute resources for processing jobs. If set to false, then you are in charge of providing the compute resource details. Default: true
        :param service_role: (experimental) The IAM role used by Batch to make calls to other AWS services on your behalf for managing the resources that you use with the service. By default, this role is created for you using the AWS managed service policy for Batch. Default: - Role using the 'service-role/AWSBatchServiceRole' policy.

        :stability: experimental
        '''
        props = ComputeEnvironmentProps(
            compute_environment_name=compute_environment_name,
            compute_resources=compute_resources,
            enabled=enabled,
            managed=managed,
            service_role=service_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromComputeEnvironmentArn") # type: ignore[misc]
    @builtins.classmethod
    def from_compute_environment_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        compute_environment_arn: builtins.str,
    ) -> IComputeEnvironment:
        '''(experimental) Fetches an existing batch compute environment by its amazon resource name.

        :param scope: -
        :param id: -
        :param compute_environment_arn: -

        :stability: experimental
        '''
        return typing.cast(IComputeEnvironment, jsii.sinvoke(cls, "fromComputeEnvironmentArn", [scope, id, compute_environment_arn]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentArn")
    def compute_environment_arn(self) -> builtins.str:
        '''(experimental) The ARN of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        '''(experimental) The name of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))


__all__ = [
    "AllocationStrategy",
    "CfnComputeEnvironment",
    "CfnComputeEnvironmentProps",
    "CfnJobDefinition",
    "CfnJobDefinitionProps",
    "CfnJobQueue",
    "CfnJobQueueProps",
    "CfnSchedulingPolicy",
    "CfnSchedulingPolicyProps",
    "ComputeEnvironment",
    "ComputeEnvironmentProps",
    "ComputeResourceType",
    "ComputeResources",
    "ExposedSecret",
    "IComputeEnvironment",
    "IJobDefinition",
    "IJobQueue",
    "IMultiNodeProps",
    "INodeRangeProps",
    "JobDefinition",
    "JobDefinitionContainer",
    "JobDefinitionProps",
    "JobQueue",
    "JobQueueComputeEnvironment",
    "JobQueueProps",
    "LaunchTemplateSpecification",
    "LogConfiguration",
    "LogDriver",
    "PlatformCapabilities",
]

publication.publish()
