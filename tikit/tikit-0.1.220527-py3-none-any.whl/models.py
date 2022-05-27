# -*- coding: utf-8 -*-
from tikit.tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

IMAGE_TYPES = ["SYSTEM", "CCR", "TCR"]


class ResourceConfigInfo:
    """资源配置

    """

    def __init__(self, charge_type, instance_type=None, instance_num=None, cpu=None, memory=None, gpu_type=None,
                 gpu=None):
        r"""
        :param instance_type: 算力规格ID
        :type instance_type: str
        :param instance_num: 计算节点数
        :type instance_num: int
        :param cpu: cpu核数，1000=1核
        :type cpu: int
        :param memory: 内存，单位为MB
        :type memory: int
        :param gpu_type: gpu卡类型
        :type gpu_type: str
        :param gpu: gpu数
        :type gpu: int
        """
        self.ChargeType = charge_type
        self.InstanceNum = instance_num
        self.Cpu = cpu
        self.Memory = memory
        self.GpuType = gpu_type
        self.Gpu = gpu
        self.InstanceType = instance_type

    @staticmethod
    def new_postpaid(instance_type, instance_num):
        """获取后付费模式下的资源配置

        :param instance_type:   实例类型。通过 describe_postpaid_training_price() 查看实例列表
        :type instance_type:    str
        :param instance_num:    实例数量
        :type instance_num:     int
        :return:
        :rtype:
        """
        return ResourceConfigInfo(charge_type="POSTPAID_BY_HOUR", instance_type=instance_type,
                                  instance_num=instance_num)

    @staticmethod
    def new_prepaid(cpu, memory, gpu=0, gpu_type=None, instance_num=1):
        """获取预付费模式下的资源配置

        :param cpu:     CPU个数，单位是核
        :type cpu:      float
        :param memory:  内存大小，单位是GB
        :type memory:   float
        :param gpu_type: gpu类型
        :type gpu_type: str
        :param gpu:     gpu个数
        :type gpu:      float
        :param instance_num:    实例数量
        :type instance_num:     int
        :return:
        :rtype:
        """
        cpu = int(cpu * 1000)
        memory = int(memory * 1024)
        gpu = int(gpu * 100)
        return ResourceConfigInfo(charge_type="PREPAID", cpu=cpu, memory=memory, gpu=gpu,
                                  gpu_type=gpu_type, instance_num=instance_num)


class FrameworkInfo:

    def __init__(self, name, training_mode, framework_version=None, image_type=None, image_url=None,
                 registry_region=None, registry_id=None):
        self.Name = name
        self.TrainingMode = training_mode

        self.FrameworkVersion = framework_version

        self.ImageType = image_type
        self.ImageUrl = image_url
        self.RegistryRegion = registry_region
        self.RegistryId = registry_id

    @staticmethod
    def new_custom(training_mode, image_type, image_url, registry_region=None, registry_id=None):
        """自定义训练框架的配置

        :param training_mode:   训练模式。 通过describe_training_frameworks()查看列表
        :type training_mode:    str
        :param image_type:      腾讯云容器镜像服务的镜像类型，如"CCR"
        :type image_type:       str
        :param image_url:       腾讯云容器镜像服务的镜像地址
        :type image_url:        str
        :param registry_region: 腾讯云容器镜像服务的镜像仓库的域
        :type registry_region:  str
        :param registry_id:     腾讯云容器镜像服务的镜像仓库ID
        :type registry_id:      str
        :return:
        :rtype:
        """
        return FrameworkInfo(name="CUSTOM",
                             training_mode=training_mode,
                             image_type=image_type,
                             image_url=image_url,
                             registry_region=registry_region,
                             registry_id=registry_id)

    @staticmethod
    def new_system_framework(framework_name, framework_version, training_mode):
        """系统内置的训练框架

        :param framework_name:      框架名称。 通过describe_training_frameworks()查看列表
        :type framework_name:       str
        :param framework_version:   框架版本。 通过describe_training_frameworks()查看列表
        :type framework_version:    str
        :param training_mode:       训练模式。 通过describe_training_frameworks()查看列表
        :type training_mode:        str
        :return:
        :rtype:
        """
        return FrameworkInfo(name=framework_name,
                             framework_version=framework_version,
                             training_mode=training_mode)


class TrainingDataConfig:
    def __init__(self):
        self.DataSource = None
        self.DataConfigDict = None  # Deprecated
        self.TargetPath = None
        self.CosStr = None
        self.DatasetId = None
        self.CfsId = None
        self.CfsPath = None
        self.HdfsId = None
        self.HdfsPath = None

    @staticmethod
    def new_mount_cos(cos_str, target_path):
        """一个cos类型的训练数据

        :param cos_str:      cos存储，格式： <bucket>/<cos path>/
        :type cos_str: str
        :param  target_path:  目标挂载路径
        :type target_path: str
        :return:
        :rtype:
        """
        ret = TrainingDataConfig()
        ret.TargetPath = target_path
        ret.DataSource = "COS"
        ret.CosStr = cos_str
        return ret

    @staticmethod
    def new_dataset_mount(dataset_id, target_path):
        """一个dataset类型的训练数据

        :param dataset_id:  数据集ID
        :type dataset_id: str
        :param  target_path:  目标挂载路径
        :type target_path: str
        :return:
        :rtype:
        """
        ret = TrainingDataConfig()
        ret.TargetPath = target_path
        ret.DataSource = "DATASET"
        ret.DatasetId = dataset_id
        return ret

    @staticmethod
    def new_mount_cfs(cfs_id, source_path, target_path):
        """新建一个dataset类型的训练数据集配置

        :param cfs_id:      CFS的ID
        :type cfs_id: str
        :param  source_path: CFS的路径
        :type source_path: str
        :param  target_path: 目标挂载路径
        :type target_path: str
        :return:
        :rtype:
        """
        ret = TrainingDataConfig()
        ret.TargetPath = target_path
        ret.DataSource = "CFS"
        ret.CfsId = cfs_id
        ret.CfsPath = source_path
        return ret

    @staticmethod
    def new_mount_hdfs(hdfs_id, source_path, target_path):
        """新建一个dataset类型的训练数据集配置

        :param hdfs_id:      EMR上HDFS的ID
        :type hdfs_id: str
        :param  source_path: HDFS的路径
        :type source_path: str
        :param  target_path: 目标挂载路径
        :type target_path: str
        :return:
        :rtype:
        """
        ret = TrainingDataConfig()
        ret.TargetPath = target_path
        ret.DataSource = "HDFS"
        ret.HdfsId = hdfs_id
        ret.HdfsPath = source_path
        return ret

    @staticmethod
    def new_dataset(id_target_dict):
        """ Deprecated !
        新建一个dataset类型的训练数据集配置

        :param id_target_dict:  数据集信息。 dataset id -> 下载的目标路径
        :type id_target_dict:   dict
        :return:
        :rtype:
        """
        ret = TrainingDataConfig()
        ret.DataSource = "DATASET"
        ret.DataConfigDict = id_target_dict
        return ret

    @staticmethod
    def new_cos_data(cos_str_target_dict):
        """Deprecated !
        新建一个cos类型的训练数据集配置

        :param cos_str_target_dict:     数据集信息。  <bucket>/<cos path>/ -> 下载的目标路径
        :type cos_str_target_dict:      dict
        :return:
        :rtype:
        """
        ret = TrainingDataConfig()
        ret.DataSource = "COS"
        ret.DataConfigDict = cos_str_target_dict
        return ret


class ReasoningEnvironment:
    def __init__(self, source, image_key=None, image_type=None, image_url=None, registry_region=None, registry_id=None):
        self.Source = source
        self.ImageKey = image_key
        self.ImageType = image_type
        self.ImageUrl = image_url
        self.RegistryRegion = registry_region
        self.RegistryId = registry_id

    @staticmethod
    def new_system_environment(image_key):
        """平台内置的运行环境

        :param image_key:   镜像标识。通过 describe_system_reasoning_images() 查看列表
        :type image_key:    str
        :return:
        :rtype:
        """
        return ReasoningEnvironment("SYSTEM", image_key)

    @staticmethod
    def new_custom_environment(image_type, image_url, registry_region=None, registry_id=None):
        """自定义的推理运行环境

        :param image_type:      腾讯云容器镜像服务的镜像类型，如"CCR"
        :type image_type:       str
        :param image_url:       腾讯云容器镜像服务的镜像地址
        :type image_url:        str
        :param registry_region: 腾讯云容器镜像服务的镜像仓库的域
        :type registry_region:  str
        :param registry_id:     腾讯云容器镜像服务的镜像仓库ID
        :type registry_id:      str
        :return:
        :rtype:
        """
        if image_type not in IMAGE_TYPES:
            raise TencentCloudSDKException(message='image_type not must in {}'.format(IMAGE_TYPES))
        return ReasoningEnvironment("CUSTOM",
                                    image_type=image_type,
                                    image_url=image_url,
                                    registry_region=registry_region,
                                    registry_id=registry_id)
