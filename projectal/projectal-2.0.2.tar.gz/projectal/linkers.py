"""
All linkers inherit from `BaseLinker`.

Linkers provide the interface to add/update/delete links between entities.
Only certain entities can link to certain other entities. When using this
library, your tooling should show you which link methods are available
to the Entity subclass you are using.

Note that some links require additional data in the link. You must ensure
the destination object has this data before adding or updating the link
(example below). See the API documentation for exact link details.
Missing data will raise a `projectal.errors.ProjectalException` with
information about what is missing.


An instance of an entity class that inherits from a linker is able to link
to an instance of the target entity class directly.

```
# Get task and staff
task = projectal.Task.get('1b21e445-f29a...')
staff = projectal.Staff.get('1b21e445-f29a...')

# Task-to-Staff links require a 'resourceLink'
staff['resourceLink'] = {'utilization': 0.6}

# Task inherits from StaffLinker, so staff linking available
task.link_staff(staff)
```

"""

from projectal import api


class BaseLinker(dict):
    """
    This base class provides methods for adding, updating, and deleting
    links between entities.

    Used internally by the library.
    """

    # TODO: The linker currently only lets you link 1-to-1. In the future,
    # we should detect and support linking in bulk.

    @classmethod
    def _add_link(cls, from_entity, to_entity_name, to_entity_list, list_name=None):
        cls._link(from_entity, to_entity_name, to_entity_list, 'add', list_name=list_name)

    @classmethod
    def _update_link(cls, from_entity, to_entity_name, to_entity_list):
        cls._link(from_entity, to_entity_name, to_entity_list, 'update')

    @classmethod
    def _delete_link(cls, from_entity, to_entity_name, to_entity_list, list_name=None):
        cls._link(from_entity, to_entity_name, to_entity_list, 'delete', list_name=list_name)

    @classmethod
    def _link(cls, from_entity, to_entity_name, to_entity_list, operation, list_name=None):
        """
        `from_uuId`: Source entity uuId

        `to_entity_name`: Destination entity name (e.g. 'staff')

        `to_entity_list`: List of uuIds (and optional data) we are linking to

        `operation`: `add`, `update`, `delete`

        `list_name`: Some list names differ from the standard pattern, so we
         pass in the name we would like to use instead.
        """
        to_key = list_name or to_entity_name.lower() + 'List'
        payload = {
            'uuId': from_entity['uuId'],
            to_key: to_entity_list
        }
        url = '/api/{}/link/{}/{}'.format(cls._path, to_entity_name, operation)
        api.post(url, payload=payload)

        # Workaround for dict link instead of list
        if list_name == 'stage' and operation == 'add':
            from_entity['stage'] = {}

        # Modify the entity object's cache of links to match the changes we pushed
        # to the server.
        if isinstance(from_entity.get(to_key, []), list):
            if operation == 'add':
                # Sometimes the backend doesn't return a list when it has none. Create it.
                if to_key not in from_entity:
                    from_entity[to_key] = []

                for to_entity in to_entity_list:
                    from_entity[to_key].append(to_entity)
            else:
                for to_entity in to_entity_list:
                    # Find it in original list
                    for i, old in enumerate(from_entity[to_key]):
                        if old['uuId'] == to_entity['uuId']:
                            if operation == 'update':
                                from_entity[to_key][i] = to_entity
                            elif operation == 'delete':
                                del from_entity[to_key][i]
        if isinstance(from_entity.get(to_key, None), dict):
            if operation in ['add', 'update']:
                from_entity[to_key] = to_entity_list
            elif operation == 'delete':
                from_entity[to_key] = None

        # Update the "old" record of the link on the entity to avoid
        # flagging it for changes (link lists are not meant to be user editable).
        from_entity._Entity__old[to_key] = from_entity[to_key]


class AccessPolicyLinker(BaseLinker):
    """Subclass can link to Access Policies"""
    def link_access_policy(self, access_policy):
        self._add_link(self, 'access_policy', [access_policy], list_name='accessPolicyList')

    def unlink_access_policy(self, access_policy):
        self._delete_link(self, 'access_policy', [access_policy], list_name='accessPolicyList')


class CompanyLinker(BaseLinker):
    """Subclass can link to Companies"""
    def link_company(self, company):
        self._add_link(self, 'company', [company])

    def unlink_company(self, company):
        self._delete_link(self, 'company', [company])


class ContactLinker(BaseLinker):
    """Subclass can link to Contacts"""
    def link_contact(self, contact):
        self._add_link(self, 'contact', [contact])

    def unlink_contact(self, contact):
        self._delete_link(self, 'contact', [contact])


class CustomerLinker(BaseLinker):
    """Subclass can link to Customers"""
    def link_customer(self, customer):
        self._add_link(self, 'customer', [customer])

    def unlink_customer(self, customer):
        self._delete_link(self, 'customer', [customer])


class DepartmentLinker(BaseLinker):
    """Subclass can link to Departments"""
    def link_department(self, department):
        self._add_link(self, 'department', [department])

    def unlink_department(self, department):
        self._delete_link(self, 'department', [department])


class FileLinker(BaseLinker):
    """Subclass can link to Files"""
    def link_file(self, file):
        self._add_link(self, 'file', [file], list_name='storageFileList')

    def unlink_file(self, file):
        self._delete_link(self, 'file', [file], list_name='storageFileList')


class FolderLinker(BaseLinker):
    """Subclass can link to Folders"""
    def link_folder(self, folder):
        self._add_link(self, 'folder', [folder], list_name='folders')

    def unlink_folder(self, folder):
        self._delete_link(self, 'folder', [folder], list_name='folders')


class LocationLinker(BaseLinker):
    """Subclass can link to Locations"""
    def link_location(self, location):
        self._add_link(self, 'location', [location])

    def unlink_location(self, location):
        self._delete_link(self, 'location', [location])


class PermissionLinker(BaseLinker):
    """Subclass can link to Permissions"""
    def link_permission(self, permission):
        return self._add_link(self, 'permission', [permission])

    def unlink_permission(self, permission):
        return self._delete_link(self, 'permission', [permission])


class ProjectLinker(BaseLinker):
    """Subclass can link to Projects"""
    def link_project(self, project):
        self._add_link(self, 'project', [project])

    def unlink_project(self, project):
        self._delete_link(self, 'project', [project])


class RebateLinker(BaseLinker):
    """Subclass can link to Rebates"""
    def link_rebate(self, rebate):
        self._add_link(self, 'rebate', [rebate])

    def unlink_rebate(self, rebate):
        self._delete_link(self, 'rebate', [rebate])


class ResourceLinker(BaseLinker):
    """Subclass can link to Resources"""
    def link_resource(self, resource):
        self._add_link(self, 'resource', [resource])

    def relink_resource(self, resource):
        self._update_link(self, 'resource', [resource])

    def unlink_resource(self, resource):
        self._delete_link(self, 'resource', [resource])


class SkillLinker(BaseLinker):
    """Subclass can link to Skills"""
    def link_skill(self, skill):
        self._add_link(self, 'skill', [skill])

    def relink_skill(self, skill):
        self._update_link(self, 'skill', [skill])

    def unlink_skill(self, skill):
        self._delete_link(self, 'skill', [skill])


class StaffLinker(BaseLinker):
    """Subclass can link to Staff"""
    def link_staff(self, staff):
        self._add_link(self, 'staff', [staff])

    def relink_staff(self, staff):
        self._update_link(self, 'staff', [staff])

    def unlink_staff(self, staff):
        self._delete_link(self, 'staff', [staff])


class StageLinker(BaseLinker):
    """Subclass can link to Stages"""
    def link_stage(self, stage):
        self._add_link(self, 'stage', stage, list_name='stage')

    def unlink_stage(self, stage):
        self._delete_link(self, 'stage', stage, list_name='stage')


class StageListLinker(BaseLinker):
    """Subclass can link to Stage List"""
    def link_stage_list(self, stages):
        stages = [s for s in stages]
        self._add_link(self, 'stage_list', stages, list_name='stageList')

    def unlink_stage_list(self, stages):
        stages = [{'uuId': s['uuId']} for s in stages]
        self._delete_link(self, 'stage_list', stages, list_name='stageList')
