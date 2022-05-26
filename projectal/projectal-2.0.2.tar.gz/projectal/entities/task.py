import projectal
from projectal.entity import Entity
from projectal.linkers import *
from projectal import api


class Task(Entity, FileLinker, RebateLinker, ResourceLinker, SkillLinker,
           StaffLinker, StageLinker):
    """
    Implementation of the [Task](https://projectal.com/docs/latest/#tag/Task) API.
    """
    _path = 'task'
    _name = 'TASK'

    @classmethod
    def create(cls, holder, entities):
        """Create a Task

        `holder`: An instance or the `uuId` of the owner

        `entities`: `dict` containing the fields of the entity to be created,
        or a list of such `dict`s to create in bulk.
        """
        holder = holder['uuId'] if isinstance(holder, dict) else holder
        params = "?holder=" + holder
        return super().create(entities, params)

    def update_order(self, order_at_uuId, order_as=True):
        url = "/api/task/update?order-at={}&order-as={}".format(
            order_at_uuId, 'true' if order_as else 'false')
        return api.put(url, [{'uuId': self['uuId']}])

    def link_predecessor_task(self, predecessor_task):
        return self.__plan(self, predecessor_task, 'add')

    def relink_predecessor_task(self, predecessor_task):
        return self.__plan(self, predecessor_task, 'update')

    def unlink_predecessor_task(self, predecessor_task):
        return self.__plan(self, predecessor_task, 'delete')

    @classmethod
    def __plan(cls, from_task, to_task, operation):
        url = '/api/task/plan/task/{}'.format(operation)
        payload = {
            'uuId': from_task['uuId'],
            'taskList': [to_task]
        }
        api.post(url, payload=payload)
        return True

    def parents(self):
        """
        Return an ordered list of `uuId`s of this task's parents, up to
        (but not including) the root of the project.
        """
        payload = {
            "name": "Task Parents",
            "type": "msql",
            "start": 0,
            "limit": -1,
            "holder": "{}".format(self['uuId']),
            "select": [
                [
                    "TASK(one).PARENT_ALL_TASK.name"
                ],
                [
                    "TASK(one).PARENT_ALL_TASK.uuId"
                ]
            ],
        }
        list = api.query(payload)
        # Results come back in reverse order. Flip them around
        list.reverse()
        return list

    def project_uuId(self):
        """Return the `uuId` of the Project that holds this Task."""
        payload = {
            "name": "Project that holds this task",
            "type": "msql", "start": 0, "limit": 1,
            "holder": "{}".format(self['uuId']),
            "select": [
                ["TASK.PROJECT.uuId"]
            ],
        }
        projects = api.query(payload)
        for t in projects:
            return t[0]
        return None

    @classmethod
    def add_task_template(cls, project, template):
        """Insert TaskTemplate `template` into Project `project`"""
        url = '/api/task/task_template/add?override=false&group=false'
        payload = {
            'uuId': project['uuId'],
            'templateList': [template]
        }
        api.post(url, payload)
