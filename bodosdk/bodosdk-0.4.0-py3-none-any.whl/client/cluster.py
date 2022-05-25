from typing import Dict, List, Union
from uuid import UUID

from bodosdk.api.cluster import ClusterApi
from bodosdk.models.cluster import ClusterDefinition, ClusterMetadata, ClusterResponse, ClusterTaskInfo, \
    InstanceCategory, BodoImage, ScaleCluster
from bodosdk.models.job import JobClusterDefinition


class ClusterClient:
    def __init__(self, api: ClusterApi):
        self._api = api

    def get_available_instance_types(self, region: str) -> Dict[str, InstanceCategory]:
        """
        Returns mapping of categorized instance types

        :param region: region for which we check instance types
        :type region: str
        :return: mapping where key is category name
        :rtype: Dict[str, InstanceCategory]
        """
        return self._api.get_available_instances(region)

    def get_available_images(self, region: str) -> Dict[str, BodoImage]:
        """
        Returns mapping of bodo version and image name

        :param region: region for which we check images
        :type region: str
        :return: mapping where key is bodo version and value is object with name and version
        :rtype: Dict[str, BodoImage]
        """
        return self._api.get_available_images(region)

    def get_definition_from_uuid(self, uuid) -> JobClusterDefinition:
        """
        Returns a JobClusterDefinition object that the client can use while defining a JobDefinition
        If a client wants to spin up a new cluster with identical configurations as the one they already have running,
        with `uuid`, call this function to get a JobClusterDefinition they can use to send jobs to the newly defined cluster.

        :param uuid: cluster uuid in the bodo platform dashboard
        :type uuid: str
        :return: JobClusterDefinition with metadata: instance type, image id, accelrated networking and workers
        :rtype: JobClusterDefinition
        
        """
        return JobClusterDefinition(**self._api.get_cluster(uuid).dict())

    def list(self) -> List[ClusterMetadata]:
        """
        Return metadata about all the clusters which are currently defined by the client. 
        The metadata include name of the cluster, uuid, status and description if any.

        :rtype: List of ClusterMetadata
        
        """
        return self._api.get_all_clusters()

    def get(self, uuid) -> ClusterResponse:
        """
        Given a uuid for a specific cluster, returns a ClusterResponse object to list out the details about the cluster
        """
        return self._api.get_cluster(uuid)

    def create(self, cluster_definition: ClusterDefinition) -> ClusterResponse:
        """
        Creates a new cluster for the client to use. Takes in a ClusterDefinition object as an input and 
        creates a cluster based on the data specified in the objects. Returns a ClusterResponse object in
        case of a success with metadata about the cluster created.

        :param: Details about the new cluster to be created
        :type: ClusterDefinition
        :return: response after creating a cluster 
        :rtype: ClusterResponse
        """
        return self._api.create_cluster(cluster_definition)

    def list_tasks(self, uuid) -> List[ClusterTaskInfo]:
        """
        Given a uuid of a cluster, returns a list of all tasks running in the cluster. The returned list contains an
        object with details about the uuid, status, type and logs of the task. 

        :param: uuid of the cluster to get tasks at
        :type: int
        :return: List of information about tasks running in the cluster. Each element of the list is an object with 
                    fields: uuid, status, taskType and logs
        :rtype: List[ClusterTaskInfo]
        """
        return self._api.get_tasks_in_cluster(uuid)

    def remove(self, uuid: Union[str, UUID], force_remove: bool = False, mark_as_terminated: bool = False):
        """
        Removes the cluster with the given uuid. Also takes in 2 options: to force delete the cluster and to mark it as permanently
        terminated. 
        """
        return self._api.remove_cluster(uuid, force_remove, mark_as_terminated)

    def scale(self, scale_cluster: ScaleCluster) -> ClusterResponse:
        """
        Changes the number of workers in the cluster with `uuid` to the specified new scale.
        The input `new_scale` is of type ScaleCluster which has an entry for the new number of workers in the cluster
        returns a cluster response object.

        :input: uuid and new scale 
        :type: str and ScaleCluster object
        :return: the updates metadata about the cluster after the api call
        :rtype: ClusterResponse
        """
        return self._api.scale_cluster(scale_cluster)

    def pause(self, uuid) -> ClusterResponse:
        """
        Stops cluster, cluster may be resumed later on.

        :input: uuid
        :type: uuid
        :return: the updates metadata about the cluster after the api call
        :rtype: ClusterResponse
        """
        return self._api.pause(uuid)

    def resume(self, uuid) -> ClusterResponse:
        """
        Resume paused cluster

        :input: uuid
        :type: uuid
        :return: the updates metadata about the cluster after the api call
        :rtype: ClusterResponse
        """
        return self._api.resume(uuid)
