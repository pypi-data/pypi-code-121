from typing import Dict, List

from bodosdk.api.base import BackendApi
from bodosdk.exc import ResourceNotFound, ServiceUnavailable, UnknownError, ValidationError
from bodosdk.models.cluster import ClusterDefinition, ClusterTaskInfo, InstanceType, InstanceCategory, BodoImage, \
    ClusterResponse, ScaleCluster


class ClusterApi(BackendApi):

    def __init__(self, *args, **kwargs):
        super(ClusterApi, self).__init__(*args, **kwargs)
        self._resource_url = f"cluster"

    def get_available_instances(self, region) -> Dict[str, InstanceCategory]:
        resp = self._requests.get(f"{self.get_resource_url()}/availableInstances/{region}",
                                  headers=self.get_auth_header())

        result = {}
        for row in resp.json():
            cat = InstanceCategory(
                name=row.get('label'),
                instance_types={}
            )
            for opt in row.get('options', []):
                instance_type = InstanceType(**opt.get('label'))
                cat.instance_types[instance_type.name] = instance_type
            result[cat.name] = cat
        return result

    def get_available_images(self, region) -> Dict[str, BodoImage]:
        resp = self._requests.get(f"{self.get_resource_url()}/availableImages/{region}/worker",
                                  headers=self.get_auth_header())
        result = {}
        for row in resp.json():
            for opt in row.get('options'):
                img = BodoImage(
                    image_id=opt['label']['imageId'],
                    bodo_version=opt['label']['bodo_version']
                )
                result[img.bodo_version] = img
        return result

    def get_cluster(self, uuid) -> ClusterResponse:
        response = self._requests.get(f"{self.get_resource_url('v2')}/{uuid}", headers=self.get_auth_header())
        if str(response.status_code).startswith('2'):
            return ClusterResponse(**response.json())
        if response.status_code == 404:
            raise ResourceNotFound
        if response.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError(response.content)

    def get_all_clusters(self) -> List[ClusterResponse]:
        response = self._requests.get(f"{self.get_resource_url()}", headers=self.get_auth_header())
        all_clusters: List[ClusterResponse] = []
        if str(response.status_code).startswith('2'):
            for entry in response.json():
                cluster_info = ClusterResponse(**entry)
                all_clusters.append(cluster_info)
            return all_clusters
        if response.status_code == 404:
            raise ResourceNotFound
        if response.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError(response.content)

    def create_cluster(self, cluster_definition: ClusterDefinition) -> ClusterResponse:
        headers = {
            'Content-type': 'application/json'
        }
        headers.update(self.get_auth_header())
        resp = self._requests.post(self.get_resource_url(), data=cluster_definition.json(by_alias=True),
                                   headers=headers)
        if str(resp.status_code).startswith('2'):
            return ClusterResponse(**resp.json())
        if resp.status_code == 404:
            raise ResourceNotFound("Probably wrong workspace keys")
        if resp.status_code in (400, 422):
            raise ValidationError(resp.json())
        if resp.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError

    def get_tasks_in_cluster(self, uuid):
        response = self._requests.get(f"{self.get_resource_url()}/{uuid}/tasks", headers=self.get_auth_header())
        all_tasks: List[ClusterTaskInfo] = []
        for entry in response.json():
            all_tasks.append(ClusterTaskInfo(**entry))
        return all_tasks

    def remove_cluster(self, uuid, force_remove, mark_as_terminated):
        params = {
            "force": str(force_remove).lower(),
            "mark_as_terminated": str(mark_as_terminated).lower()
        }
        response = self._requests.delete(f"{self.get_resource_url()}/{uuid}", params=params,
                                         headers=self.get_auth_header())
        if str(response.status_code).startswith('2'):
            return
        if response.status_code == 404:
            raise ResourceNotFound
        if response.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError(response.content)

    def scale_cluster(self, scale_cluster: ScaleCluster):
        headers = {
            'Content-type': 'application/json'
        }
        headers.update(self.get_auth_header())
        resp = self._requests.patch(f"{self.get_resource_url()}/{scale_cluster.uuid}",
                                    data=scale_cluster.json(by_alias=True, exclude={'uuid': True}),
                                    headers=headers)

        if str(resp.status_code).startswith('2'):
            return ClusterResponse(**resp.json())
        if resp.status_code == 404:
            raise ResourceNotFound()
        if resp.status_code in (400, 422):
            raise ValidationError(resp.json())
        if resp.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError

    def pause(self, uuid):
        headers = {
            'Content-type': 'application/json'
        }
        headers.update(self.get_auth_header())
        resp = self._requests.put(f"{self.get_resource_url()}/{uuid}/pause", headers=headers)
        if str(resp.status_code).startswith('2'):
            return ClusterResponse(**resp.json())
        if resp.status_code == 404:
            raise ResourceNotFound()
        if resp.status_code in (400, 422):
            raise ValidationError(resp.json())
        if resp.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError

    def resume(self, uuid):
        headers = {
            'Content-type': 'application/json'
        }
        headers.update(self.get_auth_header())
        resp = self._requests.put(f"{self.get_resource_url()}/{uuid}/resume", headers=headers)
        if str(resp.status_code).startswith('2'):
            return ClusterResponse(**resp.json())
        if resp.status_code == 404:
            raise ResourceNotFound()
        if resp.status_code in (400, 422):
            raise ValidationError(resp.json())
        if resp.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError
