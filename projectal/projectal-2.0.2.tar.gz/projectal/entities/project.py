from projectal.entity import Entity
from projectal.linkers import *
from projectal import api


class Project(Entity, CustomerLinker, FileLinker, LocationLinker, RebateLinker,
              StageLinker, StageListLinker):
    """
    Implementation of the [Project](https://projectal.com/docs/latest/#tag/Project) API.
    """
    _path = 'project'
    _name = 'PROJECT'

    @classmethod
    def stage_order(cls, uuId, stages):
        """Reorder the Project's Stage links in a customer order."""
        url = '/api/project/stage_list/order?holder={}'.format(uuId)
        api.post(url, stages)
        return True

    @classmethod
    def autoschedule(cls, project, mode='ASAP'):
        """
        Autoschedule the project.

        `project`: A Project entity

        `mode`: `ASAP` or `ALAP`
        """
        url = '/api/project/schedule?mode={}'.format(mode)
        api.post(url, [project])
        return True

    def tasks(self):
        """Get a list of uuIds of all tasks in this Project."""
        payload = {
            "name": "Task in project",
            "type": "msql",
            "start": 0,
            "limit": -1,
            "holder": "{}".format(self['uuId']),
            "select": [
                [
                    "PROJECT.TASK.uuId"
                ]
            ],
        }
        return [t[0] for t in api.query(payload)]
