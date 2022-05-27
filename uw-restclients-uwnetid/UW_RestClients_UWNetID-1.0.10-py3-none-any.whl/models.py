# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from restclients_core import models
from dateutil.parser import parse


class UwEmailForwarding(models.Model):
    fwd = models.CharField(max_length=64, null=True)
    permitted = models.NullBooleanField()
    status = models.CharField(max_length=16)

    def is_active(self):
        return self.status == "Active"

    def is_uwgmail(self):
        return self.fwd is not None and "@gamail.uw.edu" in self.fwd

    def is_uwlive(self):
        return self.fwd is not None and "@ol.uw.edu" in self.fwd

    def json_data(self):
        return {'fwd': self.fwd,
                'status': self.status,
                'is_active': self.is_active(),
                'permitted': self.permitted,
                'is_uwgmail': self.is_uwgmail(),
                'is_uwlive': self.is_uwlive()
                }

    def __str__(self):
        return "{status: {0}, permitted: {1}, fwd: {2}}".format(
            self.status, self.permitted, self.fwd)


class Subscription(models.Model):
    SUBS_OFFICE_356_PILOT = 59
    SUBS_CODE_KERBEROS = 60
    SUBS_CODE_2FA = 64
    SUBS_CODE_ZOOM_LICENSE_ACCESS = 75
    SUBS_CODE_ZOOM_BASIC_ACCESS = 76
    SUBS_CODE_CANVAS_STUDENT = 77
    SUBS_CODE_CANVAS_AFFILIATE = 78
    SUBS_CODE_CANVAS_SPONSORED = 79
    SUBS_CODE_HUSKY_ONNET_EXTENSION = 89
    SUBS_CODE_U_FORWARDING = 105
    SUBS_CODE_GOOGLE_APPS = 144
    SUBS_CODE_GOOGLE_APPS_TEST = 145
    SUBS_CODE_OFFICE_365 = 233
    SUBS_CODE_OFFICE_365_TEST = 234
    SUBS_CODE_PROJECT_SERVER_ONLINE_USER_ACCESS = 237
    SUBS_CODE_PROJECT_SERVER_ONLINE_USER_ACCESS_TEST = 238
    SUBS_CODE_FUTURE_OFFICE_365 = 250
    SUBS_CODE_OFFICE_365_ADDEE = 251

    STATUS_ACTIVE = 20
    STATUS_EXPIRED = 21
    STATUS_DISUSERED = 22
    STATUS_PENDING = 23
    STATUS_INACTIVE = 24
    STATUS_CANCELLING = 25
    STATUS_SUSPENDED = 29
    STATUS_UNPERMITTED = 101

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_DISUSERED, "Disusered"),
        (STATUS_PENDING, "Pending"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_CANCELLING, "Cancelling"),
        (STATUS_SUSPENDED, "Suspended"),
        (STATUS_UNPERMITTED, "Unpermitted"),
    )

    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)
    subscription_code = models.SmallIntegerField()
    subscription_name = models.CharField(max_length=64)
    permitted = models.BooleanField(default=False)
    status_code = models.SmallIntegerField(choices=STATUS_CHOICES)
    status_name = models.CharField(max_length=12)
    data_value = models.CharField(max_length=32, null=True)
    data_field = models.CharField(max_length=256, null=True)

    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)
        self.actions = []
        self.permits = []

    def is_status_inactive(self):
        return self.status_code == Subscription.STATUS_INACTIVE

    def is_status_active(self):
        return self.status_code == Subscription.STATUS_ACTIVE

    def from_json(self, uwnetid, data):
        self.uwnetid = uwnetid
        self.subscription_code = int(data['subscriptionCode'])
        self.subscription_name = data['subscriptionName']
        self.permitted = data['permitted']
        self.status_code = int(data['statusCode'])
        self.status_name = data['statusName']

        if 'dataField' in data:
            self.data_field = data['dataField']

        if 'dataValue' in data:
            self.data_value = data['dataValue']

        for action_data in data.get('actions', []):
            action = SubscriptionAction(
                action=action_data)
            self.actions.append(action)

        if 'permits' in data:
            for permit_data in data.get('permits', []):
                permit = SubscriptionPermit(
                    mode=permit_data['mode'],
                    category_code=permit_data['categoryCode'],
                    category_name=permit_data['categoryName'],
                    status_code=permit_data['statusCode'],
                    status_name=permit_data['statusName'])

                if 'dataValue' in permit_data:
                    permit.data_value = permit_data['dataValue']

                self.permits.append(permit)

        return self

    def json_data(self):
        data = {
            'uwNetID': self.uwnetid,
            'subscriptionCode': self.subscription_code,
            'subscriptionName': self.subscription_name,
            'permitted': self.permitted,
            'statusCode': self.status_code,
            'statusName': self.status_name,
            'actions': [],
            'permits': []
        }

        if self.data_field:
            data['dataField'] = self.data_field

        if self.data_value:
            data['dataValue'] = self.data_value

        for action in self.actions:
            data['actions'].append(action.json_data())

        for permit in self.permits:
            data['permits'].append(permit.json_data())

        return data

    def __str__(self):
        return json.dumps(self.json_data())


class SubscriptionPostResponse(models.Model):
    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)
    time_stamp = models.DateTimeField()
    action = models.CharField(max_length=12)
    result = models.CharField(max_length=16)
    http_status = models.SmallIntegerField()
    more_info = models.CharField(max_length=512)

    def from_json(self, data):
        try:
            self.uwnetid = data['query']['action']
            self.time_stamp = data['timeStamp']
            self.action = data['query']['action']
            self.result = data['result']
            self.http_status = int(data['httpStatus'])
            self.more_info = data['moreInfo']
            self.query = data['query']
        except KeyError:
            raise Exception(
                "Malformed Sub POST Response: {}".format(data))

        return self


class SubscriptionPermit(models.Model):
    UNDERGRAD_C_CODE = 1
    GRAD_C_CODE = 2
    STAFF_C_CODE = 4
    FACULTY_C_CODE = 5
    DEPARTMENT_C_CODE = 11
    COURSE_C_CODE = 12
    CLINICIAN_C_CODE = 13
    STUDENT_EMPLOYEE_C_CODE = 14
    AFFILIATE_EMPLOYEE_C_CODE = 15
    ALUMNI_C_CODE = 16
    CLINICIAN_NETID_C_CODE = 17
    EO_TECHFEE_STUD_C_CODE = 18
    EO_NON_TECHFEE_STUD_C_CODE = 19
    APPLICANT_C_CODE = 20
    RETIREE_C_CODE = 34
    SYSTEM_ADMIN_C_CODE = 46
    MEDICAL_RESIDENT_C_CODE = 145
    CURRENT_STATUS_CODE = 1
    FORMER_STATUS_CODE = 3
    IMPLICIT_MODE = "implicit"

    mode = models.CharField(max_length=16)
    category_code = models.SmallIntegerField()
    category_name = models.CharField(max_length=32)
    status_code = models.SmallIntegerField()
    status_name = models.CharField(max_length=16)
    data_value = models.CharField(max_length=256, null=True)

    def is_mode_implicit(self):
        return self.mode == SubscriptionPermit.IMPLICIT_MODE

    def is_category_alumni(self):
        return self.category_code == SubscriptionPermit.ALUMNI_C_CODE

    def is_category_staff(self):
        return self.category_code == SubscriptionPermit.STAFF_C_CODE

    def is_category_faculty(self):
        return self.category_code == SubscriptionPermit.FACULTY_C_CODE

    def is_category_department(self):
        return self.category_code == SubscriptionPermit.DEPARTMENT_C_CODE

    def is_category_course(self):
        return self.category_code == SubscriptionPermit.COURSE_C_CODE

    def is_category_student_employee(self):
        return (
            self.category_code == SubscriptionPermit.STUDENT_EMPLOYEE_C_CODE)

    def is_category_affiliate_employee(self):
        return (
            self.category_code == SubscriptionPermit.AFFILIATE_EMPLOYEE_C_CODE)

    def is_category_clinician(self):
        return self.category_code == SubscriptionPermit.CLINICIAN_C_CODE

    def is_category_clinician_netid_only(self):
        return self.category_code == SubscriptionPermit.CLINICIAN_NETID_C_CODE

    def is_category_grad(self):
        return self.category_code == SubscriptionPermit.GRAD_C_CODE

    def is_category_undergrad(self):
        return self.category_code == SubscriptionPermit.UNDERGRAD_C_CODE

    def is_category_retiree(self):
        return self.category_code == SubscriptionPermit.RETIREE_C_CODE

    def is_category_system_administrator(self):
        return self.category_code == SubscriptionPermit.SYSTEM_ADMIN_C_CODE

    def is_status_current(self):
        return self.status_code == SubscriptionPermit.CURRENT_STATUS_CODE

    def is_status_former(self):
        return self.status_code == SubscriptionPermit.FORMER_STATUS_CODE

    def json_data(self):
        data = {
            'type': 'permit',
            'mode': self.mode,
            'categoryCode': self.category_code,
            'categoryName': self.category_name,
            'statusCode': self.status_code,
            'statusName': self.status_name,
        }

        if self.data_value:
            data['dataValue'] = self.data_value

        return data


class SubscriptionAction(models.Model):
    SHOW = "show"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    SUSPEND = "suspend"
    REACTIVATE = "reactivate"
    MODIFY = "modify"
    SETNAME = "setname"
    DISUSER = "disuser"
    REUSE = "reuse"

    ACTION_TYPES = (
        (SHOW, "Show"),
        (ACTIVATE, "Activate"),
        (DEACTIVATE, "Deactivate"),
        (SUSPEND, "Suspend"),
        (REACTIVATE, "Reactivate"),
        (MODIFY, "Modify"),
        (SETNAME, "Setname"),
        (DISUSER, "Disuser"),
        (REUSE, "Reuse"),
    )

    action = models.CharField(max_length=12,
                              choices=ACTION_TYPES,
                              default=SHOW)

    def json_data(self):
        return self.action


class Category(models.Model):
    ALTID_SHARED_DEPARTMENTAL = 11
    ALTID_SHARED_COURSE = 12
    ALTID_SHARED_SAO = 21
    ALTID_SHARED_CLINICAL_1 = 22
    ALTID_SHARED_CLINICAL_2 = 23
    ALTID_SHARED_FORWARDING = 24
    ALTID_ADMIN_ADMINISTRATOR_EADM_WADM = 46
    ALTID_SHARED_APPLICATION = 52
    ALTID_SUPPORT_DEPARTMENTAL = 69
    GOOGLE_SUITE_ENDORSEE = 234
    OFFICE_365_ENDORSEE = 235
    CANVAS_PROVISIONEE = 236
    ZOOM_LICENSED_PROVISIONEE = 237
    ZOOM_BASIC_PROVISIONEE = 238
    HUSKY_ONNET_EXT_PROVISIONEE = 239

    STATUS_ACTIVE = 1
    STATUS_GRACE = 2
    STATUS_FORMER = 3

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_GRACE, "Grace"),
        (STATUS_FORMER, "Former"),
    )

    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)
    category_code = models.SmallIntegerField(null=True)
    category_name = models.CharField(max_length=64, null=True)
    expiration = models.DateField(null=True)
    notify_code = models.SmallIntegerField(null=True)
    notify_date = models.DateField(null=True)
    source_code = models.SmallIntegerField(null=True)
    source_name = models.CharField(max_length=32, null=True)
    status_code = models.SmallIntegerField(choices=STATUS_CHOICES)
    status_name = models.CharField(max_length=12, null=True)

    def from_json(self, uwnetid, data):
        self.uwnetid = uwnetid
        self.category_code = int(data['categoryCode'])
        self.category_name = data['categoryName']
        self.expiration = parse(data['expiration']) if (
            'expiration') in data else None
        self.notify_code = int(data['notifyCode']) if (
            'notifyCode' in data) else None
        self.notify_date = parse(data['notifyDate']) if (
            'notifyDate') in data else None
        self.source_code = int(data['sourceCode'])
        self.source_name = data['sourceName']
        self.status_code = int(data['statusCode'])
        self.status_name = data['statusName']
        return self

    def json_data(self):
        data = {
            'uwNetID': self.uwnetid,
            'categoryCode': self.category_code,
            'categoryName': self.category_name,
            'expiration': self.expiration,
            'notifyCode': self.notify_code,
            'notifyDate': self.notify_date,
            'sourceCode': self.source_code,
            'sourceName': self.source_name,
            'statusCode': self.status_code,
            'statusName': self.status_name
        }

        return data

    def __str__(self):
        return json.dumps(self.json_data())


def convert_seconds_to_days(interval):
    return interval/60/60/24


def convert_days_to_seconds(interval):
    return interval*60*60*24


class UwPassword(models.Model):
    ADMIN = "Admin"
    PERSON = "Person"
    OTHER = "Other"

    ABANDONED = "Abandoned"
    ACTIVE = "Active"
    DISENFRANCHISED = "Disenfranchised"
    INACTIVE = "Inactive"
    WANTED = "Wanted"

    KERB_STATUS_ACTIVE = "Active"
    KERB_STATUS_DISABLED = "Disabled"
    KERB_STATUS_EXPIRED = "Expired"
    KERB_STATUS_INACTIVE = "Inactive"
    KERB_STATUS_PENDING = "Pending"
    KERB_STATUS_OTHER = "Other"
    KERB_STATUS_SUSPENDED = "Suspended"

    DEFAULT_MED_INTERVAL = convert_days_to_seconds(120)   # 120 days

    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)
    kerb_status = models.CharField(max_length=32)

    last_change = models.DateTimeField(null=True)     # timestamps

    # the expiration interval in seconds
    interval = models.IntegerField(null=True)

    last_change_med = models.DateTimeField(null=True)    # timestamps
    expires_med = models.DateTimeField(null=True)    # timestamps

    # the expiration interval in seconds
    interval_med = models.IntegerField(null=True)
    minimum_length = models.SmallIntegerField()
    time_stamp = models.DateTimeField()

    def is_status_admin(self):
        return UwPassword.ADMIN in self.netid_status

    def is_status_person(self):
        return UwPassword.PERSON in self.netid_status

    def is_status_active(self):
        return UwPassword.ACTIVE in self.netid_status

    def is_active_person(self):
        return self.is_status_active() and self.is_status_person()

    def is_kerb_status_active(self):
        return UwPassword.KERB_STATUS_ACTIVE == self.kerb_status

    def is_kerb_status_disabled(self):
        return UwPassword.KERB_STATUS_DISABLED == self.kerb_status

    def is_kerb_status_expired(self):
        return UwPassword.KERB_STATUS_EXPIRED == self.kerb_status

    def is_kerb_status_inactive(self):
        return UwPassword.KERB_STATUS_INACTIVE == self.kerb_status

    def is_kerb_status_other(self):
        return UwPassword.KERB_STATUS_OTHER == self.kerb_status

    def is_kerb_status_pending(self):
        return UwPassword.KERB_STATUS_PENDING == self.kerb_status

    def is_kerb_status_suspended(self):
        return UwPassword.KERB_STATUS_SUSPENDED == self.kerb_status

    def json_data(self):
        data = {
            'uwnetid': self.uwnetid,
            'kerb_status': self.kerb_status,
            'last_change': self.last_change,
            'interval': self.interval,
            'last_change_med': self.last_change_med,
            'expires_med': self.expires_med,
            'interval_med': self.interval_med,
            'minimum_length': self.minimum_length,
            'time_stamp': self.time_stamp,
        }

        try:
            data['interval'] = self.interval
        except AttributeError:
            pass

        try:
            data['interval_med'] = self.interval_med
        except AttributeError:
            pass

        try:
            data['netid_status'] = self.netid_status
        except AttributeError:
            pass

        return data

    def __init__(self, *args, **kwargs):
        super(UwPassword, self).__init__(*args, **kwargs)
        self.netid_status = []

    class Meta:
        db_table = "restclients_uwnetid_password"


class Supported(models.Model):
    name = models.SlugField(max_length=64,
                            db_index=True,
                            unique=True)
    role = models.SlugField(max_length=16, null=True)
    netid_type = models.SlugField(max_length=16, null=True)
    status = models.SlugField(max_length=16, null=True)

    def is_shared_netid(self):
        return self.netid_type == 'shared'

    def is_owner(self):
        return self.role == 'owner' or self.role == 'owner-admin'

    def is_admin(self):
        return self.role == 'administrator' or self.role == 'owner-admin'

    def from_json(self, data):
        self.name = data['name']
        self.role = data.get('role')
        self.netid_type = data.get('netidType')
        self.status = data.get('status')
        return self

    def json_data(self):
        return {
            'name': self.name,
            'role': self.role,
            'netidType': self.netid_type,
            'status': self.status
        }

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        db_table = "restclients_uwnetid_supported"


class Admin(models.Model):
    name = models.SlugField(max_length=64,
                            db_index=True,
                            unique=True)
    role = models.SlugField(max_length=16, null=True)

    def is_owner(self):
        return self.role == 'owner' or self.role == 'owner-admin'

    def is_admin(self):
        return self.role == 'administrator' or self.role == 'owner-admin'

    def from_json(self, data):
        self.name = data['name']
        self.role = data.get('role')
        return self

    def json_data(self):
        return {
            'name': self.name,
            'role': self.role
        }

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        db_table = "restclients_uwnetid_admin"
