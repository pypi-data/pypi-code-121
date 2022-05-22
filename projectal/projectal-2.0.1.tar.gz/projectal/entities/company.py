from projectal.entity import Entity
from projectal.linkers import *
from projectal import api


class Company(Entity, StaffLinker, CompanyLinker, DepartmentLinker, LocationLinker,
              ProjectLinker, ContactLinker):
    """
    Implementation of the [Company](https://projectal.com/docs/latest/#tag/Company) API.
    """
    _path = 'company'
    _name = 'COMPANY'

    @classmethod
    def tree(cls, uuId=None, level=False, include_department=False):
        """
        Return company list in organisation chart format.

        `uuId`: Of a company. If no company is requested, the full
        organizational chart is returned (default: `None`)

        `level`: If `True`, only returns the top level of the
        hierarchy (default: `False`).

        `include_department`: If `True`, lists all departments within
        each company and their sub-companies (default: `False`).

        """
        url = '/api/company/tree?'
        params = []
        params.append('uuId={}'.format(uuId)) if uuId else None
        params.append('level=true') if level else None
        params.append('includeDepartment=true') if include_department else None
        url += '&'.join(params)

        return api.get(url)


    @classmethod
    def get_primary_company(cls):
        """Return the Primary company"""
        payload = {
            "name": "Find primary company uuId",
            "type": "msql", "start": 0, "limit": 1,
            "select": [
                ["COMPANY.uuId"]
            ],
            "filter": [["COMPANY.type", 'eq', 'Primary']]
        }
        response = api.query(payload)
        uuId = response[0][0]
        return cls.get(uuId)
