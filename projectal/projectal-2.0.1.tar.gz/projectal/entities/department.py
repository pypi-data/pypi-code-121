from projectal.entity import Entity
from projectal.linkers import *
from projectal import api


class Department(Entity, StaffLinker, DepartmentLinker):
    """
    Implementation of the [Department](https://projectal.com/docs/latest/#tag/Department) API.
    """
    _path = 'department'
    _name = 'DEPARTMENT'

    @staticmethod
    def tree(uuId=None, level=None, active_staff=True, inactive_staff=True):
        """
        Return department list in tree format

        `uuId`: Of a department. If no department is requested, the full
        department chart is returned (default: `None`)

        `level`: If `True`, only returns the top level of the
        hierarchy (default: `False`).

        `active_staff`: If `True`, includes the list of staff in each
        department who are considered 'active' (i.e, today is within
        their start and end dates) (default: `True`)

        'inactive_staff`: If `True`, includes the list of staff in each
        department who are considered 'inactive' (i.e, today is outside
        their start and end dates) (default: `True`)
        """
        url = '/api/department/tree?'
        params = []
        params.append('uuId={}'.format(uuId)) if uuId else None
        params.append('level=true') if level else None
        params.append('activeStaff={}'.format('true' if active_staff else 'false'))
        params.append('inactiveStaff={}'.format('true' if inactive_staff else 'false'))
        url += '&'.join(params)

        return api.get(url)

