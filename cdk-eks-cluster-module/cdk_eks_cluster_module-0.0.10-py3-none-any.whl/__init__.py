'''
# cdk-eks-cluster-module

cdk-eks-cluster-module  is a [CDK]((github.com/aws-cdk/cdk)) that helps you configure complete EKS clusters that are fully bootstrapped with the operational software that is needed to deploy and operate workloads. You can describe the configuration for the desired state of your EKS cluster, such as the control plane, worker nodes, and Kubernetes add-ons, as code.

## :sparkles: Features

* :white_check_mark: AWS EKS Cluster Addons
* :white_check_mark: Support for Multiple NodeGroups with labels and taints
* :white_check_mark: Support for Multiple fargate profiles with labels and namespace
* :white_check_mark: AWS EKS Identity Provider Configuration
* :white_check_mark: Support for custom AMI, custom launch template, and custom user data including custom user data template
* :white_check_mark: commonComponents interface allow to install custom repo/local helm chart
* :white_check_mark: Install aws-ebs-csi-driver,aws-efs-csi-driver,node-problem-detector helm charts to help manage storage, and nodes.

## :clapper: Quick Start

The quick start shows you how to create an **AWS-EKS** using this module.

### Prerequisites

* A working [`aws`](https://aws.amazon.com/cli/) CLI installation with access to an account and administrator privileges
* You'll need a recent [NodeJS](https://nodejs.org) installation
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to interact with your fresh cluster

To get going you'll need a CDK project. For details please refer to the [detailed guide for CDK](https://docs.aws.amazon.com/cdk/latest/guide/hello_world.html).

Create an empty directory on your system.

```bash
mkdir aws-quick-start-eks && cd aws-quick-start-eks
```

Bootstrap your CDK project, we will use TypeScript, but you can switch to any other supported language.

```bash
npx cdk init sample-eks  --language typescript
npx cdk bootstrap
```

Install using NPM:

```
npm install @smallcase/cdk-eks-cluster-module
```

Using yarn

```
yarn add @smallcase/cdk-eks-cluster-module
```

Using eks cluster can be deployed using the following sample code snippet:

```python
import {
  EKSCluster,
  VpcCniAddonVersion,
} from '@smallcase/cdk-eks-cluster-module';

const key = new kms.Key(this, 'EKS-KMS', {
      enabled: true,
      alias: 'EKS-KMS',
    });
key.addToResourcePolicy(new iam.PolicyStatement({
      sid: 'encrypt root volumes of nodeGroup using kms',
      actions: [
        'kms:Encrypt',
        'kms:Decrypt',
        'kms:ReEncrypt*',
        'kms:GenerateDataKey*',
        'kms:CreateGrant',
        'kms:DescribeKey',
      ],
      resources: ['*'],
      principals: [new iam.AnyPrincipal()],
      conditions: {
        StringEquals: {
          'kms:CallerAccount': '<YOUR-AWS-ID>',
          'kms:ViaService': 'ec2.<REGION>.amazonaws.com',
        },
      },
    }));

  const securityGroup = new ec2.SecurityGroup(
      this,
      'EKS-WORKER-SG',
      {
        vpc: vpc,
        description: 'Kubernetes Worker SecurityGroup',
      },
    );

  const testNodeTemplete = new ec2.LaunchTemplate(this, 'testNodeTemplete', {
      instanceType: new ec2.InstanceType('m5a.large'),
      blockDevices: [
        {
          deviceName: '/dev/xvda',
          volume: ec2.BlockDeviceVolume.ebs(40,
            {
              deleteOnTermination: true,
              encrypted: true,
              volumeType: ec2.EbsDeviceVolumeType.GP3,
              kmsKey: key,
            },
          ),
          mappingEnabled: true,
        },
      ],
    });
let ekscluster = new EKSCluster(this, 'EKS-CLUSTER', {
      availabilityZones: Stack.of(this).availabilityZones,
      clusterVPC: vpc,
      kmsKey: key,
      region: Stack.of(this).region,
      workerSecurityGroup: securityGroup,
      addonProps: {
        vpnCniAddonVersion: VpcCniAddonVersion.V1_11_0,
      },
      clusterConfig: {
        clusterName: 'EKS-CLUSTER',
        clusterVersion: eks.KubernetesVersion.V1_22,
        // this will create cluster autoscaler service account with iam role
        addAutoscalerIam: true,
        albControllerVersion: eks.AlbControllerVersion.V2_2_4,
        defaultCapacity: 3,
        subnets: {
          privateSubnetGroupName: 'Private',
        },
        nodeGroups: [
          {
            name: 'test-node',
            instanceTypes: [],
            minSize: 3,
            maxSize: 6,
            launchTemplateSpec: {
              version: testNodeTemplete.versionNumber,
              id: testNodeTemplete.launchTemplateId!,
            },
            subnetGroupName: 'Private',
            labels: {
              role: 'test-eks-cluster',
            },
            taints: {
              role: 'test-eks-cluster',
            },
            tags: {
              'k8s.io/cluster-autoscaler/enabled': 'TRUE',
              'k8s.io/cluster-autoscaler/EKS-CLUSTER':
                'owned',
            },
          },
        ]
        commonComponents: {
          'aws-efs-csi-driver': {
            iamPolicyPath: ['../../assets/policy/aws-efs-csi-driver-policy.json'],
            // above mention iam policy will be used for this service account
            serviceAccounts: ['efs-csi-controller-sa', 'efs-csi-node-sa'],
            helm: {
              chartName: 'aws-efs-csi-driver',
              chartVersion: '2.2.0',
              helmRepository: 'https://kubernetes-sigs.github.io/aws-efs-csi-driver/',
              namespace: 'kube-system',
            },
          },
        },
        teamMembers: [
          "your-aws-user",
        ],
        teamExistingRolePermission: { //optional
          '<YOUR_ROLE_ARN>': 'system:masters',
        },
      }
  })
```

## [API.md](./API.md)
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
import aws_cdk.aws_eks
import aws_cdk.aws_kms
import constructs


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.AddonProps",
    jsii_struct_bases=[],
    name_mapping={"vpn_cni_addon_version": "vpnCniAddonVersion"},
)
class AddonProps:
    def __init__(
        self,
        *,
        vpn_cni_addon_version: typing.Optional["VpcCniAddonVersion"] = None,
    ) -> None:
        '''
        :param vpn_cni_addon_version: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if vpn_cni_addon_version is not None:
            self._values["vpn_cni_addon_version"] = vpn_cni_addon_version

    @builtins.property
    def vpn_cni_addon_version(self) -> typing.Optional["VpcCniAddonVersion"]:
        result = self._values.get("vpn_cni_addon_version")
        return typing.cast(typing.Optional["VpcCniAddonVersion"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddonProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.ArgoCD",
    jsii_struct_bases=[],
    name_mapping={
        "assume_role_arn": "assumeRoleArn",
        "cluster_role_name": "clusterRoleName",
    },
)
class ArgoCD:
    def __init__(
        self,
        *,
        assume_role_arn: builtins.str,
        cluster_role_name: builtins.str,
    ) -> None:
        '''
        :param assume_role_arn: 
        :param cluster_role_name: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "assume_role_arn": assume_role_arn,
            "cluster_role_name": cluster_role_name,
        }

    @builtins.property
    def assume_role_arn(self) -> builtins.str:
        result = self._values.get("assume_role_arn")
        assert result is not None, "Required property 'assume_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_role_name(self) -> builtins.str:
        result = self._values.get("cluster_role_name")
        assert result is not None, "Required property 'cluster_role_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArgoCD(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.ClusterConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "cluster_version": "clusterVersion",
        "default_capacity": "defaultCapacity",
        "node_groups": "nodeGroups",
        "subnets": "subnets",
        "tags": "tags",
        "team_members": "teamMembers",
        "add_autoscaler_iam": "addAutoscalerIam",
        "alb_controller_version": "albControllerVersion",
        "argo_cd": "argoCD",
        "common_components": "commonComponents",
        "farget_profiles": "fargetProfiles",
        "namespaces": "namespaces",
        "public_allow_access": "publicAllowAccess",
        "team_existing_role_permission": "teamExistingRolePermission",
    },
)
class ClusterConfig:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        cluster_version: aws_cdk.aws_eks.KubernetesVersion,
        default_capacity: jsii.Number,
        node_groups: typing.Sequence["NodeGroupConfig"],
        subnets: "InternalMap",
        tags: "InternalMap",
        team_members: typing.Sequence[builtins.str],
        add_autoscaler_iam: typing.Optional[builtins.bool] = None,
        alb_controller_version: typing.Optional[aws_cdk.aws_eks.AlbControllerVersion] = None,
        argo_cd: typing.Optional[ArgoCD] = None,
        common_components: typing.Optional[typing.Mapping[builtins.str, "ICommonComponentsProps"]] = None,
        farget_profiles: typing.Optional[typing.Sequence["FargetProfile"]] = None,
        namespaces: typing.Optional[typing.Mapping[builtins.str, "NamespaceSpec"]] = None,
        public_allow_access: typing.Optional[typing.Sequence[builtins.str]] = None,
        team_existing_role_permission: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param cluster_name: 
        :param cluster_version: 
        :param default_capacity: 
        :param node_groups: 
        :param subnets: 
        :param tags: 
        :param team_members: 
        :param add_autoscaler_iam: 
        :param alb_controller_version: 
        :param argo_cd: 
        :param common_components: 
        :param farget_profiles: 
        :param namespaces: 
        :param public_allow_access: 
        :param team_existing_role_permission: 
        '''
        if isinstance(subnets, dict):
            subnets = InternalMap(**subnets)
        if isinstance(tags, dict):
            tags = InternalMap(**tags)
        if isinstance(argo_cd, dict):
            argo_cd = ArgoCD(**argo_cd)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
            "cluster_version": cluster_version,
            "default_capacity": default_capacity,
            "node_groups": node_groups,
            "subnets": subnets,
            "tags": tags,
            "team_members": team_members,
        }
        if add_autoscaler_iam is not None:
            self._values["add_autoscaler_iam"] = add_autoscaler_iam
        if alb_controller_version is not None:
            self._values["alb_controller_version"] = alb_controller_version
        if argo_cd is not None:
            self._values["argo_cd"] = argo_cd
        if common_components is not None:
            self._values["common_components"] = common_components
        if farget_profiles is not None:
            self._values["farget_profiles"] = farget_profiles
        if namespaces is not None:
            self._values["namespaces"] = namespaces
        if public_allow_access is not None:
            self._values["public_allow_access"] = public_allow_access
        if team_existing_role_permission is not None:
            self._values["team_existing_role_permission"] = team_existing_role_permission

    @builtins.property
    def cluster_name(self) -> builtins.str:
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_version(self) -> aws_cdk.aws_eks.KubernetesVersion:
        result = self._values.get("cluster_version")
        assert result is not None, "Required property 'cluster_version' is missing"
        return typing.cast(aws_cdk.aws_eks.KubernetesVersion, result)

    @builtins.property
    def default_capacity(self) -> jsii.Number:
        result = self._values.get("default_capacity")
        assert result is not None, "Required property 'default_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def node_groups(self) -> typing.List["NodeGroupConfig"]:
        result = self._values.get("node_groups")
        assert result is not None, "Required property 'node_groups' is missing"
        return typing.cast(typing.List["NodeGroupConfig"], result)

    @builtins.property
    def subnets(self) -> "InternalMap":
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast("InternalMap", result)

    @builtins.property
    def tags(self) -> "InternalMap":
        result = self._values.get("tags")
        assert result is not None, "Required property 'tags' is missing"
        return typing.cast("InternalMap", result)

    @builtins.property
    def team_members(self) -> typing.List[builtins.str]:
        result = self._values.get("team_members")
        assert result is not None, "Required property 'team_members' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def add_autoscaler_iam(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("add_autoscaler_iam")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def alb_controller_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_eks.AlbControllerVersion]:
        result = self._values.get("alb_controller_version")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.AlbControllerVersion], result)

    @builtins.property
    def argo_cd(self) -> typing.Optional[ArgoCD]:
        result = self._values.get("argo_cd")
        return typing.cast(typing.Optional[ArgoCD], result)

    @builtins.property
    def common_components(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "ICommonComponentsProps"]]:
        result = self._values.get("common_components")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "ICommonComponentsProps"]], result)

    @builtins.property
    def farget_profiles(self) -> typing.Optional[typing.List["FargetProfile"]]:
        result = self._values.get("farget_profiles")
        return typing.cast(typing.Optional[typing.List["FargetProfile"]], result)

    @builtins.property
    def namespaces(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "NamespaceSpec"]]:
        result = self._values.get("namespaces")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "NamespaceSpec"]], result)

    @builtins.property
    def public_allow_access(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("public_allow_access")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def team_existing_role_permission(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("team_existing_role_permission")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CommonHelmCharts(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@smallcase/cdk-eks-cluster-module.CommonHelmCharts",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_eks.ICluster,
        helm_props: "StandardHelmProps",
        iam_policy_path: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param helm_props: 
        :param iam_policy_path: 
        :param service_accounts: 
        '''
        props = CommonHelmChartsProps(
            cluster=cluster,
            helm_props=helm_props,
            iam_policy_path=iam_policy_path,
            service_accounts=service_accounts,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.CommonHelmChartsProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "helm_props": "helmProps",
        "iam_policy_path": "iamPolicyPath",
        "service_accounts": "serviceAccounts",
    },
)
class CommonHelmChartsProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_eks.ICluster,
        helm_props: "StandardHelmProps",
        iam_policy_path: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cluster: 
        :param helm_props: 
        :param iam_policy_path: 
        :param service_accounts: 
        '''
        if isinstance(helm_props, dict):
            helm_props = StandardHelmProps(**helm_props)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "helm_props": helm_props,
        }
        if iam_policy_path is not None:
            self._values["iam_policy_path"] = iam_policy_path
        if service_accounts is not None:
            self._values["service_accounts"] = service_accounts

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.ICluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.ICluster, result)

    @builtins.property
    def helm_props(self) -> "StandardHelmProps":
        result = self._values.get("helm_props")
        assert result is not None, "Required property 'helm_props' is missing"
        return typing.cast("StandardHelmProps", result)

    @builtins.property
    def iam_policy_path(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("iam_policy_path")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("service_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonHelmChartsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EKSCluster(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@smallcase/cdk-eks-cluster-module.EKSCluster",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        availability_zones: typing.Sequence[builtins.str],
        cluster_config: ClusterConfig,
        kms_key: aws_cdk.aws_kms.Key,
        region: builtins.str,
        worker_security_group: aws_cdk.aws_ec2.SecurityGroup,
        addon_props: typing.Optional[AddonProps] = None,
        cluster_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param availability_zones: 
        :param cluster_config: 
        :param kms_key: 
        :param region: 
        :param worker_security_group: 
        :param addon_props: 
        :param cluster_vpc: 
        '''
        props = EKSClusterProps(
            availability_zones=availability_zones,
            cluster_config=cluster_config,
            kms_key=kms_key,
            region=region,
            worker_security_group=worker_security_group,
            addon_props=addon_props,
            cluster_vpc=cluster_vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addServiceAccountWithIamRole")
    def add_service_account_with_iam_role(
        self,
        service_account_name: builtins.str,
        service_account_namespace: builtins.str,
        policy: typing.Any,
    ) -> None:
        '''
        :param service_account_name: -
        :param service_account_namespace: -
        :param policy: -
        '''
        return typing.cast(None, jsii.invoke(self, "addServiceAccountWithIamRole", [service_account_name, service_account_namespace, policy]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalFargetProfile")
    def additional_farget_profile(self) -> typing.List[aws_cdk.aws_eks.FargateProfile]:
        return typing.cast(typing.List[aws_cdk.aws_eks.FargateProfile], jsii.get(self, "additionalFargetProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalNodegroups")
    def additional_nodegroups(self) -> typing.List[aws_cdk.aws_eks.Nodegroup]:
        return typing.cast(typing.List[aws_cdk.aws_eks.Nodegroup], jsii.get(self, "additionalNodegroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        return typing.cast(aws_cdk.aws_eks.Cluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fargetProfiles")
    def farget_profiles(self) -> typing.List["FargetProfile"]:
        return typing.cast(typing.List["FargetProfile"], jsii.get(self, "fargetProfiles"))


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.EKSClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zones": "availabilityZones",
        "cluster_config": "clusterConfig",
        "kms_key": "kmsKey",
        "region": "region",
        "worker_security_group": "workerSecurityGroup",
        "addon_props": "addonProps",
        "cluster_vpc": "clusterVPC",
    },
)
class EKSClusterProps:
    def __init__(
        self,
        *,
        availability_zones: typing.Sequence[builtins.str],
        cluster_config: ClusterConfig,
        kms_key: aws_cdk.aws_kms.Key,
        region: builtins.str,
        worker_security_group: aws_cdk.aws_ec2.SecurityGroup,
        addon_props: typing.Optional[AddonProps] = None,
        cluster_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param availability_zones: 
        :param cluster_config: 
        :param kms_key: 
        :param region: 
        :param worker_security_group: 
        :param addon_props: 
        :param cluster_vpc: 
        '''
        if isinstance(cluster_config, dict):
            cluster_config = ClusterConfig(**cluster_config)
        if isinstance(addon_props, dict):
            addon_props = AddonProps(**addon_props)
        self._values: typing.Dict[str, typing.Any] = {
            "availability_zones": availability_zones,
            "cluster_config": cluster_config,
            "kms_key": kms_key,
            "region": region,
            "worker_security_group": worker_security_group,
        }
        if addon_props is not None:
            self._values["addon_props"] = addon_props
        if cluster_vpc is not None:
            self._values["cluster_vpc"] = cluster_vpc

    @builtins.property
    def availability_zones(self) -> typing.List[builtins.str]:
        result = self._values.get("availability_zones")
        assert result is not None, "Required property 'availability_zones' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def cluster_config(self) -> ClusterConfig:
        result = self._values.get("cluster_config")
        assert result is not None, "Required property 'cluster_config' is missing"
        return typing.cast(ClusterConfig, result)

    @builtins.property
    def kms_key(self) -> aws_cdk.aws_kms.Key:
        result = self._values.get("kms_key")
        assert result is not None, "Required property 'kms_key' is missing"
        return typing.cast(aws_cdk.aws_kms.Key, result)

    @builtins.property
    def region(self) -> builtins.str:
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def worker_security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        result = self._values.get("worker_security_group")
        assert result is not None, "Required property 'worker_security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.SecurityGroup, result)

    @builtins.property
    def addon_props(self) -> typing.Optional[AddonProps]:
        result = self._values.get("addon_props")
        return typing.cast(typing.Optional[AddonProps], result)

    @builtins.property
    def cluster_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("cluster_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EKSClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.FargetProfile",
    jsii_struct_bases=[],
    name_mapping={
        "namespaces": "namespaces",
        "profile_name": "profileName",
        "labels": "labels",
    },
)
class FargetProfile:
    def __init__(
        self,
        *,
        namespaces: typing.Sequence[builtins.str],
        profile_name: builtins.str,
        labels: typing.Optional["InternalMap"] = None,
    ) -> None:
        '''
        :param namespaces: 
        :param profile_name: 
        :param labels: 
        '''
        if isinstance(labels, dict):
            labels = InternalMap(**labels)
        self._values: typing.Dict[str, typing.Any] = {
            "namespaces": namespaces,
            "profile_name": profile_name,
        }
        if labels is not None:
            self._values["labels"] = labels

    @builtins.property
    def namespaces(self) -> typing.List[builtins.str]:
        result = self._values.get("namespaces")
        assert result is not None, "Required property 'namespaces' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def profile_name(self) -> builtins.str:
        result = self._values.get("profile_name")
        assert result is not None, "Required property 'profile_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def labels(self) -> typing.Optional["InternalMap"]:
        result = self._values.get("labels")
        return typing.cast(typing.Optional["InternalMap"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargetProfile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@smallcase/cdk-eks-cluster-module.ICommonComponentsProps")
class ICommonComponentsProps(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="helm")
    def helm(self) -> "StandardHelmProps":
        ...

    @helm.setter
    def helm(self, value: "StandardHelmProps") -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamPolicyPath")
    def iam_policy_path(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @iam_policy_path.setter
    def iam_policy_path(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccounts")
    def service_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @service_accounts.setter
    def service_accounts(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...


class _ICommonComponentsPropsProxy:
    __jsii_type__: typing.ClassVar[str] = "@smallcase/cdk-eks-cluster-module.ICommonComponentsProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="helm")
    def helm(self) -> "StandardHelmProps":
        return typing.cast("StandardHelmProps", jsii.get(self, "helm"))

    @helm.setter
    def helm(self, value: "StandardHelmProps") -> None:
        jsii.set(self, "helm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamPolicyPath")
    def iam_policy_path(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "iamPolicyPath"))

    @iam_policy_path.setter
    def iam_policy_path(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "iamPolicyPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccounts")
    def service_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "serviceAccounts"))

    @service_accounts.setter
    def service_accounts(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "serviceAccounts", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICommonComponentsProps).__jsii_proxy_class__ = lambda : _ICommonComponentsPropsProxy


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.InternalMap",
    jsii_struct_bases=[],
    name_mapping={},
)
class InternalMap:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InternalMap(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.NamespaceSpec",
    jsii_struct_bases=[],
    name_mapping={"annotations": "annotations", "labels": "labels"},
)
class NamespaceSpec:
    def __init__(
        self,
        *,
        annotations: typing.Optional[InternalMap] = None,
        labels: typing.Optional[InternalMap] = None,
    ) -> None:
        '''
        :param annotations: 
        :param labels: 
        '''
        if isinstance(annotations, dict):
            annotations = InternalMap(**annotations)
        if isinstance(labels, dict):
            labels = InternalMap(**labels)
        self._values: typing.Dict[str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if labels is not None:
            self._values["labels"] = labels

    @builtins.property
    def annotations(self) -> typing.Optional[InternalMap]:
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[InternalMap], result)

    @builtins.property
    def labels(self) -> typing.Optional[InternalMap]:
        result = self._values.get("labels")
        return typing.cast(typing.Optional[InternalMap], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NamespaceSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.NodeGroupConfig",
    jsii_struct_bases=[],
    name_mapping={
        "instance_types": "instanceTypes",
        "labels": "labels",
        "max_size": "maxSize",
        "min_size": "minSize",
        "name": "name",
        "subnet_group_name": "subnetGroupName",
        "taints": "taints",
        "capacity_type": "capacityType",
        "desired_size": "desiredSize",
        "disk_size": "diskSize",
        "launch_template_spec": "launchTemplateSpec",
        "node_ami_version": "nodeAMIVersion",
        "ssh_key_name": "sshKeyName",
        "subnet_az": "subnetAz",
        "tags": "tags",
    },
)
class NodeGroupConfig:
    def __init__(
        self,
        *,
        instance_types: typing.Sequence[aws_cdk.aws_ec2.InstanceType],
        labels: InternalMap,
        max_size: jsii.Number,
        min_size: jsii.Number,
        name: builtins.str,
        subnet_group_name: builtins.str,
        taints: InternalMap,
        capacity_type: typing.Optional[aws_cdk.aws_eks.CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        launch_template_spec: typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec] = None,
        node_ami_version: typing.Optional[builtins.str] = None,
        ssh_key_name: typing.Optional[builtins.str] = None,
        subnet_az: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[InternalMap] = None,
    ) -> None:
        '''
        :param instance_types: 
        :param labels: 
        :param max_size: 
        :param min_size: 
        :param name: 
        :param subnet_group_name: 
        :param taints: 
        :param capacity_type: 
        :param desired_size: 
        :param disk_size: 
        :param launch_template_spec: 
        :param node_ami_version: 
        :param ssh_key_name: 
        :param subnet_az: 
        :param tags: 
        '''
        if isinstance(labels, dict):
            labels = InternalMap(**labels)
        if isinstance(taints, dict):
            taints = InternalMap(**taints)
        if isinstance(launch_template_spec, dict):
            launch_template_spec = aws_cdk.aws_eks.LaunchTemplateSpec(**launch_template_spec)
        if isinstance(tags, dict):
            tags = InternalMap(**tags)
        self._values: typing.Dict[str, typing.Any] = {
            "instance_types": instance_types,
            "labels": labels,
            "max_size": max_size,
            "min_size": min_size,
            "name": name,
            "subnet_group_name": subnet_group_name,
            "taints": taints,
        }
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if desired_size is not None:
            self._values["desired_size"] = desired_size
        if disk_size is not None:
            self._values["disk_size"] = disk_size
        if launch_template_spec is not None:
            self._values["launch_template_spec"] = launch_template_spec
        if node_ami_version is not None:
            self._values["node_ami_version"] = node_ami_version
        if ssh_key_name is not None:
            self._values["ssh_key_name"] = ssh_key_name
        if subnet_az is not None:
            self._values["subnet_az"] = subnet_az
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def instance_types(self) -> typing.List[aws_cdk.aws_ec2.InstanceType]:
        result = self._values.get("instance_types")
        assert result is not None, "Required property 'instance_types' is missing"
        return typing.cast(typing.List[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def labels(self) -> InternalMap:
        result = self._values.get("labels")
        assert result is not None, "Required property 'labels' is missing"
        return typing.cast(InternalMap, result)

    @builtins.property
    def max_size(self) -> jsii.Number:
        result = self._values.get("max_size")
        assert result is not None, "Required property 'max_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_size(self) -> jsii.Number:
        result = self._values.get("min_size")
        assert result is not None, "Required property 'min_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_group_name(self) -> builtins.str:
        result = self._values.get("subnet_group_name")
        assert result is not None, "Required property 'subnet_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def taints(self) -> InternalMap:
        result = self._values.get("taints")
        assert result is not None, "Required property 'taints' is missing"
        return typing.cast(InternalMap, result)

    @builtins.property
    def capacity_type(self) -> typing.Optional[aws_cdk.aws_eks.CapacityType]:
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.CapacityType], result)

    @builtins.property
    def desired_size(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("desired_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_size(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def launch_template_spec(
        self,
    ) -> typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec]:
        result = self._values.get("launch_template_spec")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec], result)

    @builtins.property
    def node_ami_version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("node_ami_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_key_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ssh_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_az(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("subnet_az")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[InternalMap]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[InternalMap], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodeGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.StandardHelmProps",
    jsii_struct_bases=[],
    name_mapping={
        "chart_name": "chartName",
        "chart_release_name": "chartReleaseName",
        "chart_version": "chartVersion",
        "create_namespace": "createNamespace",
        "helm_repository": "helmRepository",
        "helm_values": "helmValues",
        "local_helm_chart": "localHelmChart",
        "namespace": "namespace",
    },
)
class StandardHelmProps:
    def __init__(
        self,
        *,
        chart_name: builtins.str,
        chart_release_name: typing.Optional[builtins.str] = None,
        chart_version: typing.Optional[builtins.str] = None,
        create_namespace: typing.Optional[builtins.bool] = None,
        helm_repository: typing.Optional[builtins.str] = None,
        helm_values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        local_helm_chart: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param chart_name: 
        :param chart_release_name: 
        :param chart_version: 
        :param create_namespace: 
        :param helm_repository: 
        :param helm_values: 
        :param local_helm_chart: 
        :param namespace: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "chart_name": chart_name,
        }
        if chart_release_name is not None:
            self._values["chart_release_name"] = chart_release_name
        if chart_version is not None:
            self._values["chart_version"] = chart_version
        if create_namespace is not None:
            self._values["create_namespace"] = create_namespace
        if helm_repository is not None:
            self._values["helm_repository"] = helm_repository
        if helm_values is not None:
            self._values["helm_values"] = helm_values
        if local_helm_chart is not None:
            self._values["local_helm_chart"] = local_helm_chart
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def chart_name(self) -> builtins.str:
        result = self._values.get("chart_name")
        assert result is not None, "Required property 'chart_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def chart_release_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("chart_release_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def chart_version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("chart_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_namespace(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("create_namespace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def helm_repository(self) -> typing.Optional[builtins.str]:
        result = self._values.get("helm_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def helm_values(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        result = self._values.get("helm_values")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def local_helm_chart(self) -> typing.Optional[builtins.str]:
        result = self._values.get("local_helm_chart")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StandardHelmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@smallcase/cdk-eks-cluster-module.VpcCniAddonProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "addon_version": "addonVersion",
        "namespace": "namespace",
        "resolve_conflicts": "resolveConflicts",
    },
)
class VpcCniAddonProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        addon_version: typing.Optional["VpcCniAddonVersion"] = None,
        namespace: typing.Optional[builtins.str] = None,
        resolve_conflicts: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param cluster: 
        :param addon_version: 
        :param namespace: 
        :param resolve_conflicts: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
        }
        if addon_version is not None:
            self._values["addon_version"] = addon_version
        if namespace is not None:
            self._values["namespace"] = namespace
        if resolve_conflicts is not None:
            self._values["resolve_conflicts"] = resolve_conflicts

    @builtins.property
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_eks.Cluster, result)

    @builtins.property
    def addon_version(self) -> typing.Optional["VpcCniAddonVersion"]:
        result = self._values.get("addon_version")
        return typing.cast(typing.Optional["VpcCniAddonVersion"], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resolve_conflicts(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("resolve_conflicts")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcCniAddonProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpcCniAddonVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@smallcase/cdk-eks-cluster-module.VpcCniAddonVersion",
):
    def __init__(self, version: builtins.str) -> None:
        '''
        :param version: -
        '''
        jsii.create(self.__class__, self, [version])

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, version: builtins.str) -> "VpcCniAddonVersion":
        '''Custom add-on version.

        :param version: custom add-on version.
        '''
        return typing.cast("VpcCniAddonVersion", jsii.sinvoke(cls, "of", [version]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_10_1")
    def V1_10_1(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.10.1.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_10_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_10_2")
    def V1_10_2(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.10.2.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_10_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_10_3")
    def V1_10_3(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.10.3.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_10_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_11_0")
    def V1_11_0(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.11.0.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_11_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_6_3")
    def V1_6_3(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.6.3.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_6_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_7_10")
    def V1_7_10(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.7.10.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_7_10"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_7_5")
    def V1_7_5(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.7.5.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_7_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_7_6")
    def V1_7_6(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.7.6.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_7_6"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_7_9")
    def V1_7_9(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.7.9.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_7_9"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_8_0")
    def V1_8_0(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.8.0.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_8_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_9_0")
    def V1_9_0(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.9.0.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_9_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_9_1")
    def V1_9_1(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.9.1.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_9_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_9_3")
    def V1_9_3(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.9.3.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_9_3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))


class VpcEniAddon(
    aws_cdk.aws_eks.CfnAddon,
    metaclass=jsii.JSIIMeta,
    jsii_type="@smallcase/cdk-eks-cluster-module.VpcEniAddon",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_eks.Cluster,
        addon_version: typing.Optional[VpcCniAddonVersion] = None,
        namespace: typing.Optional[builtins.str] = None,
        resolve_conflicts: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param addon_version: 
        :param namespace: 
        :param resolve_conflicts: 
        '''
        props = VpcCniAddonProps(
            cluster=cluster,
            addon_version=addon_version,
            namespace=namespace,
            resolve_conflicts=resolve_conflicts,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "AddonProps",
    "ArgoCD",
    "ClusterConfig",
    "CommonHelmCharts",
    "CommonHelmChartsProps",
    "EKSCluster",
    "EKSClusterProps",
    "FargetProfile",
    "ICommonComponentsProps",
    "InternalMap",
    "NamespaceSpec",
    "NodeGroupConfig",
    "StandardHelmProps",
    "VpcCniAddonProps",
    "VpcCniAddonVersion",
    "VpcEniAddon",
]

publication.publish()
