from __future__ import annotations

import ssl
from abc import abstractmethod
from collections.abc import Callable

import attr
import requests
import urllib3

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.models.vsphere_tagging import CategorySpec, TagSpec


class VSphereApiException(BaseVCenterException):
    """Base vSphere API Exception."""


class VSphereApiConnectionException(BaseVCenterException):
    """Failed to create API client due to some specific reason."""


class VSphereApiInvalidCredentials(VSphereApiConnectionException):
    def __init__(self):
        super().__init__("Connection failed. Please, check credentials.")


class VSphereApiServiceUnavailable(VSphereApiConnectionException):
    def __init__(self):
        super().__init__("vSphere Automation API service unavailable.")


class TagApiException(VSphereApiException):
    """Base Tag API Exception."""


class UserCannotBeAuthenticated(TagApiException):
    def __init__(self):
        super().__init__("User can not be authenticated...")


class EntityAlreadyExists(TagApiException):
    """Indicates that an attempt was made to create an entity that already exists."""


class TagAlreadyExists(EntityAlreadyExists):
    def __init__(self, name: str, category_id: str):
        self.name = name
        self.category_id = category_id
        super().__init__(f"Tag '{name}' already exists in Category ID '{category_id}'.")


class CategoryAlreadyExists(EntityAlreadyExists):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Category '{name}' already exists.")


class NotEnoughPrivileges(TagApiException):
    """Not enough privileges to perform an operation."""


class NotEnoughPrivilegesCreateCategory(NotEnoughPrivileges):
    def __init__(self):
        super().__init__("Not enough privileges to create the category.")


class NotEnoughPrivilegesReadCategory(NotEnoughPrivileges):
    def __init__(self):
        super().__init__("Not enough privileges to read the category.")


class NotEnoughPrivilegesDeleteCategory(NotEnoughPrivileges):
    def __init__(self):
        super().__init__("Not enough privileges to delete the category.")


class NotEnoughPrivilegesCreateTag(NotEnoughPrivileges):
    def __init__(self):
        super().__init__("Not enough privileges to create the tag.")


class NotEnoughPrivilegesReadTag(NotEnoughPrivileges):
    def __init__(self):
        super().__init__("Not enough privileges to read the Tag.")


class NotEnoughPrivilegesDeleteTag(NotEnoughPrivileges):
    def __init__(self):
        super().__init__("Not enough privileges to delete the Tag.")


class NotEnoughPrivilegesListObjectTags(NotEnoughPrivileges):
    def __init__(self, obj_id: str, obj_type: str):
        self.obj_id = obj_id
        self.obj_type = obj_type
        msg = (
            f"Cannot list tags of the object '{obj_type}' with id '{obj_id}'. "
            f"Not enough privileges."
        )
        super().__init__(msg)


class NotEnoughPrivilegesAttachTagsToObject(NotEnoughPrivileges):
    def __init__(self, obj_id: str, obj_type: str):
        self.obj_id = obj_id
        self.obj_type = obj_type
        super().__init__(
            f"Cannot attach tags to the object '{obj_type}' with id '{obj_id}'. "
            f"Not enough privileges."
        )


class EntityDoesntExists(TagApiException):
    """The entity doesn't exist."""


class CategoryIdDoesntExists(EntityDoesntExists):
    def __init__(self, category_id: str):
        self.category_id = category_id
        super().__init__(f"Category with ID '{category_id}' doesn't exist.")


class CategoryNameDoesntExists(EntityDoesntExists):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Category with name '{name}' doesn't exists.")


class TagIdDoesntExists(EntityDoesntExists):
    def __init__(self, tag_id: str):
        super().__init__(f"Tag with ID '{tag_id}' doesn't exist.")


class TagNameDoesntExists(EntityDoesntExists):
    def __init__(self, name: str, category_id: str):
        m = f"Tag with name '{name}' doesn't exists in the category id '{category_id}'"
        super().__init__(m)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class BaseAPIClient:
    address: str
    username: str
    password: str
    session: requests.Session = requests.Session()
    scheme: str = "https"
    port: int = 443
    verify_ssl: bool = ssl.CERT_NONE

    def __attrs_post_init__(self):
        self.session.verify = self.verify_ssl
        self.session.headers.update({"Content-Type": "application/json"})
        if self.username and self.password:
            self.session.auth = (self.username, self.password)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @abstractmethod
    def _base_url(self):
        pass

    def _do_request(
        self,
        method: Callable,
        path: str,
        raise_for_status: bool = True,
        http_error_map: dict[int, Exception | type[Exception]] | None = None,
        **kwargs: dict,
    ) -> requests.Response:
        if http_error_map is None:
            http_error_map = {}

        url = f"{self._base_url()}/{path}"
        res = method(url=url, **kwargs)
        try:
            raise_for_status and res.raise_for_status()
        except requests.exceptions.HTTPError as caught_err:
            http_code = caught_err.response.status_code
            err = http_error_map.get(http_code, VSphereApiException)
            raise err from caught_err
        return res

    def _do_get(
        self,
        path: str,
        raise_for_status: bool = True,
        http_error_map: dict[int, Exception | type[Exception]] | None = None,
        **kwargs: dict,
    ) -> requests.Response:
        """Basic GET request client method."""
        return self._do_request(
            self.session.get, path, raise_for_status, http_error_map, **kwargs
        )

    def _do_post(
        self,
        path: str,
        raise_for_status: bool = True,
        http_error_map: dict[int, Exception | type[Exception]] | None = None,
        **kwargs: dict,
    ) -> requests.Response:
        """Basic POST request client method."""
        return self._do_request(
            self.session.post, path, raise_for_status, http_error_map, **kwargs
        )

    def _do_put(
        self,
        path: str,
        raise_for_status: bool = True,
        http_error_map: dict[int, Exception] | None = None,
        **kwargs: dict,
    ) -> requests.Response:
        """Basic PUT request client method."""
        return self._do_request(
            self.session.put, path, raise_for_status, http_error_map, **kwargs
        )

    def _do_delete(
        self,
        path: str,
        raise_for_status: bool = True,
        http_error_map: dict[int, Exception | type[Exception]] | None = None,
        **kwargs: dict,
    ) -> requests.Response:
        """Basic DELETE request client method."""
        return self._do_request(
            self.session.delete, path, raise_for_status, http_error_map, **kwargs
        )


class VSphereAutomationAPI(BaseAPIClient):
    class Decorators:
        @classmethod
        def get_data(cls, decorated):
            def inner(*args, **kwargs):
                return decorated(*args, **kwargs).json()["value"]

            return inner

    def _base_url(self):
        return f"{self.scheme}://{self.address}:{self.port}/rest/com/vmware/cis"

    def connect(self) -> None:
        error_map = {
            401: VSphereApiInvalidCredentials,
            503: VSphereApiServiceUnavailable,
        }
        self._do_post(path="session", http_error_map=error_map)

    @Decorators.get_data
    def create_category(self, name: str):
        """Create category.

        Note: you need the create category privilege.
        """
        error_map = {
            400: CategoryAlreadyExists(name),
            403: NotEnoughPrivilegesCreateCategory,
        }
        category_spec = {"create_spec": CategorySpec(name=name).to_dict()}
        return self._do_post(
            path="tagging/category", http_error_map=error_map, json=category_spec
        )

    @Decorators.get_data
    def get_category_list(self):
        """Get list of all existed category.

        Note: The list will only contain those categories
              for which you have read privileges.
        """
        return self._do_get(path="tagging/category")

    @Decorators.get_data
    def get_category_info(self, category_id: str):
        """Fetches the category information for the given category identifier.

        Note: you need the read privilege on the category.
        """
        error_map = {
            403: NotEnoughPrivilegesReadCategory,
            404: CategoryIdDoesntExists(category_id),
        }
        return self._do_get(
            path=f"tagging/category/id:{category_id}", http_error_map=error_map
        )

    def delete_category(self, category_id: str) -> None:
        """Deletes an existing category.

        Note: you need the delete privilege on the category.
        """
        error_map = {
            401: UserCannotBeAuthenticated,
            403: NotEnoughPrivilegesDeleteCategory,
            404: CategoryIdDoesntExists(category_id),
        }
        self._do_delete(
            path=f"tagging/category/id:{category_id}", http_error_map=error_map
        )

    @Decorators.get_data
    def create_tag(self, name: str, category_id: str):
        """Creates a tag.

        Note: you need the create tag privilege on the input category.
        """
        error_map = {
            400: TagAlreadyExists(name, category_id),
            403: NotEnoughPrivilegesCreateTag,
            404: CategoryIdDoesntExists(category_id),
        }
        tag_spec = {
            "create_spec": TagSpec(name=name, category_id=category_id).to_dict()
        }
        return self._do_post(
            path="tagging/tag", json=tag_spec, http_error_map=error_map
        )

    @Decorators.get_data
    def get_all_category_tags(self, category_id: str):
        """Get all tags ids for the given category.

        Note: you need the read privilege on the given category
              and the individual tags in that category.
        """
        error_map = {
            403: NotEnoughPrivilegesReadCategory,
            404: CategoryIdDoesntExists(category_id),
        }
        return self._do_post(
            path=f"tagging/tag/id:{category_id}?~action=list-tags-for-category",
            http_error_map=error_map,
        )

    @Decorators.get_data
    def get_tag_info(self, tag_id: str):
        """Get tag information for the given tag identifier.

        Note: you need the read privilege on the tag in order to view the tag info.
        """
        error_map = {
            403: NotEnoughPrivilegesReadTag,
            404: TagIdDoesntExists(tag_id),
        }
        return self._do_get(path=f"tagging/tag/id:{tag_id}", http_error_map=error_map)

    def attach_multiple_tags_to_object(
        self, obj_id: str, obj_type: str, tag_ids: list[str]
    ) -> None:
        """Attaches the given tags to the input object.

        Note: you need the read privilege on the object and
              the attach tag privilege on each tag.
        """
        create_association = {
            "object_id": {"id": obj_id, "type": obj_type},
            "tag_ids": tag_ids,
        }
        error_map = {
            401: UserCannotBeAuthenticated,
            403: NotEnoughPrivilegesAttachTagsToObject(obj_id, obj_type),
        }
        self._do_post(
            path="tagging/tag-association?~action=attach-multiple-tags-to-object",
            json=create_association,
            http_error_map=error_map,
        )

    @Decorators.get_data
    def list_attached_tags(self, obj_id: str, obj_type: str):
        """Get the list of tags attached to the given object.

        Note: you need the read privilege on the input object.
              The list will only contain those tags
              for which you have the read privileges.
        """
        error_map = {
            401: UserCannotBeAuthenticated,
            403: NotEnoughPrivilegesListObjectTags(obj_id, obj_type),
        }
        get_association = {"object_id": {"id": obj_id, "type": obj_type}}
        return self._do_post(
            path="tagging/tag-association?~action=list-attached-tags",
            json=get_association,
            http_error_map=error_map,
        )

    @Decorators.get_data
    def list_attached_objects(self, tag_id: str):
        """Get the list of attached objects for the given tag.

        Note: you need the read privilege on the input tag.
              Only those objects for which you have the read privilege will be returned.
        """
        error_map = {
            401: UserCannotBeAuthenticated,
            403: NotEnoughPrivilegesReadTag,
            404: TagIdDoesntExists(tag_id),
        }
        return self._do_post(
            path=f"tagging/tag-association/id:{tag_id}?~action=list-attached-objects",
            http_error_map=error_map,
        )

    def delete_tag(self, tag_id: str) -> None:
        """Deletes an existing tag.

        Note: you need the delete privilege on the tag.
        """
        error_map = {
            401: UserCannotBeAuthenticated,
            403: NotEnoughPrivilegesDeleteTag,
            404: TagIdDoesntExists(tag_id),
        }
        self._do_delete(path=f"tagging/tag/id:{tag_id}", http_error_map=error_map)
