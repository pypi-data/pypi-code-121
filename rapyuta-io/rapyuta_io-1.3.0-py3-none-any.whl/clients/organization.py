from __future__ import absolute_import
import enum
from rapyuta_io.utils.object_converter import ObjBase, nested_field


class Organization(ObjBase):
    """
    Organization is the representation of a group of users on the Platform. Every user must be part of at least one
    organization.

    :ivar guid: guid of the Organization
    :vartype guid: str
    :ivar name: Name of the Organization
    :vartype name: str
    :ivar country_id: County ID of the Organization
    :vartype country_id: int
    :ivar country: Country details of the Organization
    :vartype country:   :py:class:`~rapyuta_io.clients.organization.Country`
    :ivar province: Province of the Organization
    :vartype province: str
    :ivar postal_code: Postal Code of the Organization
    :vartype postal_code: str
    :ivar url: URL of the Organization
    :vartype url: str
    :ivar plan_id: Plan ID of the Organization
    :vartype plan_id: int
    :ivar state: The state of the Organization on the Platform
    :vartype state: :py:class:`~rapyuta_io.clients.organization.OrganizationState`
    :ivar creator: GUID of the User that created the Organization
    :vartype creator: str
    :ivar short_guid: short guid of the Organization
    :vartype short_guid: str
    """

    def __init__(self):
        self.guid = None
        self.name = None
        self.country_id = None
        self.country = None
        self.province = None
        self.postal_code = None
        self.url = None
        self.plan_id = None
        self.state = None
        self.creator = None
        self.short_guid = None

    def get_deserialize_map(self):
        return {
            'guid': 'guid',
            'name': 'name',
            'country_id': 'countryID',
            'country': nested_field('country', Country),
            'province': 'province',
            'postal_code': 'postalCode',
            'url': 'url',
            'plan_id': 'planID',
            'state': 'state',
            'creator': 'creator',
            'short_guid': 'shortGUID'
        }

    def get_serialize_map(self):
        return {
            'guid': 'guid',
        }



class OrganizationState(str, enum.Enum):
    """
    Enumeration variables for OrganizationState.

    OrganizationState can be any of the following types \n

    OrganizationState.ACTIVATED ('ACTIVATED') \n
    OrganizationState.SUSPENDED ('SUSPENDED') \n
    OrganizationState.MARKEDSUSPENSION ('MARKEDSUSPENSION') \n

    """
    ACTIVATED = 'ACTIVATED'
    SUSPENDED = 'SUSPENDED'
    MARKEDSUSPENSION = 'MARKEDSUSPENSION'


class Country(ObjBase):
    """
    Country is the representation of country details of an Organization on the platform.

    :ivar id: id of the Country
    :vartype id: int
    :ivar created_at: creation time of the Country details on the platform
    :vartype created_at: str
    :ivar updated_at: updation time of the Country details on the platform
    :vartype updated_at: str
    :ivar deleted_at: deletion time of the Country details on the platform
    :vartype deleted_at: str
    :ivar name: name of the Country
    :vartype name: str
    :ivar code: code of the Country
    :vartype code: str
    """
    def __init__(self):
        self.id = None
        self.created_at = None
        self.updated_at = None
        self.deleted_at = None
        self.name = None
        self.code = None

    def get_deserialize_map(self):
        return {
            'id': 'ID',
            'created_at': 'CreatedAt',
            'updated_at': 'UpdatedAt',
            'deleted_at': 'DeletedAt',
            'name': 'name',
            'code': 'code',
        }

    def get_serialize_map(self):
        pass
