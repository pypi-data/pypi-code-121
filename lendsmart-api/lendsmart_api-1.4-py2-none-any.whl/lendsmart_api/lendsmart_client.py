from __future__ import absolute_import

import json
import logging
from datetime import datetime
import time
import pkg_resources
import requests

from lendsmart_api.errors import ApiError, UnexpectedResponseError
from lendsmart_api.objects import PredictionWorkflow, LendingTerm, PredictionInference, PredictionSegment, Document, Base, AccountSign, DocumentPointer,Task,LetterOfExplanation, Openids
from lendsmart_api.objects import Openids, Advisors, Namespace, Account, Notifier, FinicityReports
from lendsmart_api.objects.filtering import Filter

from .common import load_and_validate_keys, SSH_KEY_TYPES
from .paginated_list import PaginatedList
from lendsmart_api.constants import *
from ramda import *

package_version = pkg_resources.require("lendsmart_api")[0].version

logger = logging.getLogger(__name__)

"""
Group is used provide API client access to all the groups.
"""


class Group:
    def __init__(self, client):
        self.client = client
        self.namespace = ''

    def is_not_found(self, response):
        status_code = path_or('', ['reason'], response)
        if self.client.ignore_not_found and equals(status_code, 'Not Found'):
            return True
        return False


"""
PredictionGroup is used for maintains all prediction works
This Group is used to create PredictionSegment, PredictionWorkflow, PredictionInference records from Lambda
Also update status in PredictionWorkflows
"""


class PredictionGroup(Group):
    def segment_create(self, label=None):
        """
        Creates a new PredictionSegments, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new PredictionSegments

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/prediction_segments', data=label)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating Prediction Segment '
                                          'Client!', json=result)

        c = PredictionSegment(self.client, result['id'], result)
        return c

    def inference_create(self, label=None):
        """
        Creates a new PredictionInference, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new PredictionInference

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/prediction_inferences', data=label)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating Prediction Inference '
                                          'Client!', json=result)

        c = PredictionInference(self.client, result['id'], result)
        return c

    def workflows(self, *filters):
        """
        Requests and returns a list of PredictionWorkflow on your
        account.
        """
        return self.client._get_and_filter(PredictionWorkflow, *filters)

    def workflow_create(self, data=None):
        """
        Creates a new PredictionWorkflow, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new PredictionWorkflow

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/prediction_workflows', data=data)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating Longivew '
                                          'Client!', json=result)

        c = PredictionWorkflow(self.client, result['id'], result)
        return c

    def workflow_describe(self, label=None):
        """
        Get a PredictionWorkflow

        :returns: The PredictionWorkflow.
        :rtype: PredictionWorkflow
        """
        result = self.client.get(
            '/prediction_workflows/describe/{}'.format(label))
        #c = PredictionWorkflowList(self.client, result)
        if self.is_not_found(result):
            return {}

        if not 'items' in result:
            raise UnexpectedResponseError('Unexpected response when getting PredictionWorkflow'
                                          'Client!', json=result)

        return result

    def workflow_update_status(self, did=None, updated_at=None, param=None):
        """
        Update a status in PredictionWorkflow

        :returns: The PredictionWorkflow.
        :rtype: PredictionWorkflow
        """
        current_time = time.time()
        result = self.client.put(
            '/prediction_workflows/{}/status?updated_at={}'.format(did, updated_at), data=param)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating PredictionWorkflow'
                                          'Client!', json=result)
        c = PredictionWorkflow(self.client, result['id'], result)
        return c

class LendingTerms(Group):
    def lending_terms(self, *filters):
        """
        Requests and returns a list of Lending Term on your
        account.
        """
        return self.client._get_and_filter(LendingTerm, *filters)

    def lending_term_get(self, label=None):
        """
        Get a LendingTerm

        :returns: The LendingTerm.
        :rtype: LendingTerm
        """
        result = self.client.get('/lending_terms/{}'.format(label))
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting LendingTerm'
                                          'Client!', json=result)
        return result

    def lending_term_get_loan_id(self, label=None):
        """
        Get a LendingTerm

        :returns: The LendingTerm.
        :rtype: LendingTerm
        """
        result = self.client.get('/lending_terms/describe/{}'.format(label))

        if self.is_not_found(result):
            return {}

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting LendingTerm'
                                          'Client!', json=result)

        return result

    def lending_term_update(self, id, param=None):
        """
        Update a Signature in API

        :returns: The Updated Signature.
        :rtype: Signature
        """
        result = self.client.put('/lending_terms/{}'.format(id), data=param)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting LendingTerm'
                                          'Client!', json=result)

        return result

"""
    Documents is used to trigger Document related requests to API
    This class is used to do following operations in Api
    1. DocumentCreate
    2. DocumentGet
    3. DocumentStatusUpdate
    4. DocumentPointersCreate
"""


class Documents(Group):
    def documents(self, *filters):
        """
        Requests and returns a list of Document on your
        account.
        """
        return self.client._get_and_filter(Document, *filters)

    def document_get(self, label=None):
        """
        Get a Document

        :returns: The Document.
        :rtype: Document
        """
        result = self.client.get('/documents/{}'.format(label))
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting Document'
                                          'Client!', json=result)
        c = Document(self.client, result['id'], result)
        return c

    def document_create(self, data=None):
        """
        Creates a new Document, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new Document

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/documents', data=data)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating Longivew '
                                          'Client!', json=result)

        c = Document(self.client, result['id'], result)
        return c

    def document_update_status(self, did=None, updated_at=None, param=None):
        """
        Update a Document status

        :returns: The Document.
        :rtype: Document
        """
        current_time = time.time()
        result = self.client.put(
            '/documents/{}/status?updated_at={}'.format(did, updated_at), data=param)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating Document'
                                          'Client!', json=result)
        c = Document(self.client, result['id'], result)
        return c

    def document_pointer_create(self, data=None):
        """
        Creates a new DocumentPointer, with given inputs.

        :param label: The label for the new client. If None, a default label based
            on the new client's ID will be used.

        :returns: A new DocumentPointer

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/'+ self.client.get_namespace() +'/document_pointers', data=data)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating DocumentPointer'
                                          'Client!', json=result)

        c = DocumentPointer(self.client, result['id'], result)
        return c


"""
    AccountSignGroup is used to trigger Signature related requests to API
    This class is used to do following operations in Api
    1. SignatureUpdate
    2. SignatureGet
"""

class NotifiersGroup(Group):
    def notifiers(self, *filters):
        """
        Requests and returns a list of Notifiers on your
        account.
        """
        return self.client._get_and_filter(Notifier, *filters)


    def notifier_create(self, label, data=None):
        """
        Creates a new Notifier, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new Notifier

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        notifier_url = '/'+ self.client.get_namespace() +'{}/{}'.format(LENDSMART_NOTIFIER_ROOT, label)
        result = self.client.post(notifier_url, data=data)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating notifier '
                                          'Client!', json=result)


        return result


class AccountSignGroup(Group):
    def account_sign_update(self, id, param=None):
        """
        Update a Signature in API

        :returns: The Updated Signature.
        :rtype: Signature
        """
        result = self.client.put('/account_signs/{}'.format(id), data=param)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting AccountSign'
                                          'Client!', json=result)

    def signature_get(self, label=None):
        """
        Get a Signature

        :returns: The Signature.
        :rtype: Signature
        """
        result = self.client.get('/account_signs/{}'.format(label))
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting Signature'
                                          'Client!', json=result)
        c = AccountSign(self.client, result['id'], result)
        return result


class FreddieMacGroup(Group):
    def authenticate_freddiemac(self):
        """
        Authenticates Freddiemac in Lendsmart API
        """
        result = self.client.get(FREDDIEMAC_AUTHNETICATE_ROOT)
        if equals(path_or('', ['status'], result), 'Failure'):
            raise UnexpectedResponseError('Unexpected response when authentiation freddiemac'
                                          'Client!', json=result)
        return result

    def run_lpa(self, loan_id, data=None):
        """
        Run Loan Product Advisor For Freddiemac
        """
        result = self.client.post(FREDDIEMAC_RUN_LPA_ROOT + loan_id, data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when submitting loan to freddiemac'
                                          'Client!', json=result)
        return result

    def poll_request_id(self, request_id,data=None):
        """
        Run Poll request using request id for freddiemac
        """
        result = self.client.post(FREDDIEMAC_RUN_LPA_ROOT + '/polls/' + request_id, data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when polling request id from freddiemac'
                                          'Client!', json=result)
        return result


class TaskGroup(Group):
    def create_task(self, data=None):
        """
        Create a task
        """
        result = self.client.post('/'+ self.client.get_namespace() + LENDSMART_TASK_CREATE_ROOT, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating task'
                                          'Client!', json=result)

        # c = Task(self.client, result['id'], result)
        return result

    def update_task_by_namespace(self, data=None):
        """
        Updates the particular task
        """
        result = self.client.put('/'+ self.client.get_namespace() + LENDSMART_TASK_CREATE_ROOT + '/' + path_or('', ['id'], data), data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating task'
                                          'Client!', json=result)
        return result

    def update_task(self, data=None):
        """
        Updates the particular task
        """
        result = self.client.put(LENDSMART_TASK_CREATE_ROOT + '/' + path_or('', ['id'], data), data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating task'
                                          'Client!', json=result)
        return result

    def update_provider_task(self, id, data=None):
        """
        Updates the particular task
        """
        result = self.client.put(LENDSMART_TASK_CREATE_ROOT + '/provider/' + id, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating task'
                                          'Client!', json=result)
        return result

    def get_task_by_task_id(self, task_id):
        """
        Gives the task by task id
        """
        result = self.client.get(LENDSMART_TASK_CREATE_ROOT + task_id)
        if is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing task'
                                          'Client!', json=result)
        return result

    def get_task_by_provider_id(self, provider_id):
        """
        Gives the task by provider id
        """
        result = self.client.get(LENDSMART_TASK_CREATE_ROOT + '/provider/' + provider_id)
        if self.is_not_found(result):
            return {}

        if not 'id' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing task'
                                          'Client!', json=result)
        return result

    def get_task_by_role_id(self, role_id):
        """
        Gives the task by role id
        """
        result = self.client.get(LENDSMART_TASK_CREATE_ROOT + '/describe/' + role_id)
        if self.is_not_found(result):
            return {}

        if not 'items' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing task'
                                          'Client!', json=result)


        return result

class OpenidsGroup(Group):
    def create_openid(self, data=None):
        """
        Create a openid
        """
        result = self.client.post(LENDSMART_OPENID_CREATE_ROOT, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating openid'
                                          'Client!', json=result)

        return result

    def update_openid(self, data=None):
        """
        Updates the particular openid
        """
        result = self.client.put(LENDSMART_OPENID_CREATE_ROOT + path_or('', ['id'], data), data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating openid'
                                          'Client!', json=result)
        return result

    def get_openid_by_role_id(self, role_id, provider):
        """
        Gives the openid by role id
        """
        result = self.client.get(LENDSMART_OPENID_CREATE_ROOT + '/describe/' + role_id+ '/'+provider)

        if self.is_not_found(result):
            return {}

        if not 'items' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing openid'
                                          'Client!', json=result)


        return result

    def get_openid_by_account_id(self, account_id):
        """
        Gives the openid by account_id
        """
        result = self.client.get(LENDSMART_OPENID_CREATE_ROOT + '/accounts/' + account_id)
        if self.is_not_found(result):
            return {}

        if not 'items' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing openid'
                                          'Client!', json=result)

        return result

    def get_openid_by_customer_id(self, customer_id):
        """
        Gives the openid by customer id
        """
        result = self.client.get(LENDSMART_OPENID_CREATE_ROOT + '/' + customer_id)
        if self.is_not_found(result):
            return {}

        if not 'id' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing openid'
                                          'Client!', json=result)
        return result



class NamespaceGroup(Group):
    def create_namespace(self, data=None):
        """
        Create a namespace
        """
        result = self.client.post(LENDSMART_NAMESPACE_ROOT, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating namespace'
                                          'Client!', json=result)

        c = Namespace(self.client, result['id'], result)
        return c

    def update_namespace(self, data=None):
        """
        Updates the particular namespace
        """
        result = self.client.put(LENDSMART_NAMESPACE_ROOT + path_or('', ['id'], data), data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating namespace'
                                          'Client!', json=result)
        return result

    def get_namespace_by_id(self, namespace_id):
        """
        Gives the namespace by id
        """
        result = self.client.get(LENDSMART_NAMESPACE_ROOT + namespace_id)
        if is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing namespace'
                                          'Client!', json=result)
        return result

class LoanappGroup(Group):
    def create_loanapp(self, data=None):
        """
        Create a loanapp
        """
        result = self.client.post(LENDSMART_LOANAPP_ROOT, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating loanapp'
                                          'Client!', json=result)

        return result

    def update_loanapp(self, data=None):
        """
        Updates the particular loanapp
        """
        result = self.client.put(LENDSMART_LOANAPP_ROOT + '/' + path_or('', ['id'], data), data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating loanapp'
                                          'Client!', json=result)
        return result

    def get_loanapp_by_id(self, loanapp_id):
        """
        Gives the loanapp by id
        """
        result = self.client.get(LENDSMART_LOANAPP_ROOT + '/' + loanapp_id)
        if is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing loanapp'
                                          'Client!', json=result)
        return result
    def get_all_short_loanapp(self, data=None):
        """
        fetch the loanapps with filters
        """
        url = '/{}{}/{}/{}'.format(self.client.get_namespace(),LENDSMART_LOANAPP_ROOT,'all','short')
        result=self.client.post(url,data=data)
        if is_empty(result):
            raise UnexpectedResponseError('Unexpected response when getting loanapp', json=result)

        return result

class LoanappRoleGroup(Group):
    def create_loanapprole(self, data=None):
        """
        create the loanapp role for a loan application
          Args:
               data: dict request payload which has what is the role of the applicant for the loan"""
        result=self.client.post(LENDSMART_LOANAPP_ROLE, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating loanapp role'
                                          'Client!', json=result)
        return result



class LoanstatusGroup(Group):
    def describe_loan_status(self, loanapp_id):
        """
        Describing a loanstatus
        """
        url = '{}/{}/{}'.format(LENDSMART_LOANSTATUS_ROOT,'describe',loanapp_id)
        result = self.client.get(url)
        if self.is_not_found(result):
            return {}

        if not 'items' in result:
            raise UnexpectedResponseError('Unexpected response when describe loanstatus'
                                           'Client!', json=result)
        return result

    def update_loan_status(self, namespace, data=None):
        """
        Updates the particular loanstatus
        """
        result = self.client.put( '/' + namespace + LENDSMART_LOANSTATUS_ROOT+ '/' + path_or('', ['id'], data), data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating loanstatus'
                                           'Client!', json=result)
        return result

    def get_loan_status_by_id(self, loan_status_id):
        """
        Gives the loanstatus by id
        """
        result = self.client.get(LENDSMART_LOANAPP_ROOT + '/' + loan_status_id)
        if is_empty(result):
            raise UnexpectedResponseError('Unexpected response when get loanstatus'
                                           'Client!', json=result)
        return result


class LetterOfExplanationGroup(Group):
    def create_loe(self, data=None):
        """
        Creates a loe
        """
        result = self.client.post(LENDSMART_LETTER_OF_EXPLANATION_ROOT, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating letter of explanantion'
                                          'Client!', json=result)
        loe = LetterOfExplanation(self.client, result['id'], result)
        return loe

    def update_loe(self, data=None):
        """
        Updates the given loe
        """
        result = self.client.put(LENDSMART_LETTER_OF_EXPLANATION_ROOT, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating letter of explanantion'
                                          'Client!', json=result)
        return result

    def get_loe_by_loanid(self, loan_id):
        """
        Gives the Loe by loan id
        """
        result = self.client.get(LENDSMART_LETTER_OF_EXPLANATION_ROOT + '/describe/' + loan_id)
        if self.is_not_found(result):
            return {}

        if not 'items' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when getting letter of explanantion'
                                          'Client!', json=result)

        return result

"""
    LoanDocumetGroup is used to trigger loan_documents related requests to API
    This class is used to do following operations in Api
    1. LoanDocumetsUpdate
"""

class LoanDocumetGroup(Group):
    def update(self, id, param=None):
        """
        Update a LoanDocuments in API

        :returns: The Updated LoanDocuments.
        :rtype: LoanDocuments
        """
        result = self.client.put('/loan_documents/{}'.format(id), data=param)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating LoanDocuments'
                                          'Client!', json=result)


class EventBridgeGroup(Group):
    def create(self, namespace, data=None):
        result = self.client.post('/{}'.format(namespace)+LENDSMART_EVENT_BRIDGE_CREATE_ROOT , data=data)
        if not 'event' in result:
            raise UnexpectedResponseError('Unexpected response when creating advisor profile'
                                          'Client!', json=result)
        return result

class AdvisorProfileGroup(Group):
    def create(self, data=None):
        result = self.client.post(LENDSMART_ADVISOR_PROFILE_CREATE_ROOT, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating advisor profile'
                                          'Client!', json=result)
        return result

    def update(self, data=None):
        result = self.client.put(LENDSMART_ADVISOR_PROFILE_CREATE_ROOT+'/'+data['id'],data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating letter of explanantion'
                                        'Client!', json=result)
        return result
    def get_advisor_profile_by_email(self, email):
        result = self.client.get(LENDSMART_ADVISOR_PROFILE_CREATE_ROOT+'/email/'+email)

        if self.is_not_found(result):
            return {}

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting advisor profile by email id'
                                        'Client!', json=result)
        return result

    def get_advisor_profile_by_user_name(self, name):
        """
        Gives the advisor by name
        """
        result = self.client.get(LENDSMART_ADVISOR_PROFILE_CREATE_ROOT + '/name/' + name)
        if self.is_not_found(result):
            return {}

        if not 'id' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when describing advisor'
                                          'Client!', json=result)

        return result

class TeamMemberGroup(Group):
    def get_team_member_by_id(self, team_member_id):
        result = self.client.get(LENDSMART_TEAM_MEMBER_ROOT +'/'+ team_member_id)
        if self.is_not_found(result):
            return {}

        if not 'id' in result or is_empty(result):
            raise UnexpectedResponseError('Unexpected response when creating team member'
                                          'Client!', json=result)
        return result

    def update_team_member(self, data=None):
        print("data",data)
        result = self.client.put(LENDSMART_TEAM_MEMBER_ROOT +'/'+data['id'], data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating team member'
                                          'Client!', json=result)
        return result

    def create_team_member(self, data=None):
        result = self.client.post(LENDSMART_TEAM_MEMBER_ROOT,data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating team member'
                                          'Client!', json=result)
        return result

class AccountsGroup(Group):
    def accounts(self, *filters):
        """
        Requests and returns a list of Account on your
        account.
        """
        return self.client._get_and_filter(Account, *filters)

    def account_get(self, label=None):
        """
        Get a Account

        :returns: The Account.
        :rtype: Account
        """
        result = self.client.get('/accounts/{}'.format(label))
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting Account'
                                          'Client!', json=result)
        c = Account(self.client, result['id'], result)
        return result

class OriginationLoanPerimissionGroup(Group):
    def create_originating_loan_permission(self, data):
        result = self.client.post(LENDSMART_ORIGINATION_LOAN_PERMISSIONS, data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when get origination loan permission'
                                          'Client!', json=result)
        return result

    def update_loan_permission(self, data):
        result = self.client.put(LENDSMART_ORIGINATION_LOAN_PERMISSIONS+'/'+data['id'], data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating origination loan permission'
                                          'Client!', json=result)
        return result
    def get_originating_loan_permission_by_advisor_id(self,advisor_id):
        result = self.client.get(LENDSMART_ORIGINATION_LOAN_PERMISSIONS+'/advisor/'+advisor_id)

        if self.is_not_found(result):
            return {}

        if not 'kind' in result:
            raise UnexpectedResponseError('Unexpected response when updating origination loan permission'
                                          'Client!', json=result)

        return result

"""
BusinssGroup is used to handler business record api calls
"""
class BusinssGroup(Group):
    def describe_business(self, owner_id):
        result = self.client.get(LENDSMART_BUSINESS_ROOT+'/describe/'+owner_id)

        if self.is_not_found(result):
            return {}

        if not 'items' in result:
            raise UnexpectedResponseError('Unexpected response when get business record'
                                          'Client!', json=result)

        return result

    def update_business(self, data):
        result = self.client.put(LENDSMART_BUSINESS_ROOT+'/'+path_or('', ['id'], data), data=data)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating business'
                                          'Client!', json=result)
        return result

class Finicity(Group):
    def Finicity(self, *filters):
        """
        This is finicity 1.5 version
        Requests and returns a list of FinicityVOA on your
        account.
        """
        return self.client._get_and_filter(FinicityReports, *filters)

    def generate_voie(self, data):
        """
        This is finicity 1.5 version
        Get a FinicityVOIE

        :returns: The FinicityVOIE.
        :rtype: FinicityVOIE
        """
        result = self.client.post(LENDSMART_FINICITY_VOIE_ROOT, data=data)
        
        return result

    def generate_voa(self, data):
        """
        This is finicity 1.5 version
        Get a FinicityVOA

        :returns: The FinicityVOA.
        :rtype: FinicityVOA
        """
        result = self.client.post(LENDSMART_FINICITY_VOA_ROOT, data=data)
        
        return result
class EmploymentGroup(Group):
    def get_employment_by_id(self, id):
        '''
        This will return the employment details by loanapp or loanapp_role id
        '''
        result = self.client.get(LENDSMART_EMPLOYMENT_ROOT+'/describe/'+id)
        if not 'items' in result:
            raise UnexpectedResponseError('Unexpected response when get business record'
                                          'Client!', json=result)

        return result


class LendsmartClient:
    def __init__(self, service_account, base_url, user_agent=None):
        """
        The main interface to the Lendsmart API.

        :param service_account: The service_account is used for communication with the
                      API.  Can be either a Lambda servie account or other.
        :type service_account: ServiceAccount
        :param base_url: The base URL for API requests.  Generally, you shouldn't
                         change this.
        :type base_url: str
        :param user_agent: What to append to the User Agent of all requests made
                           by this client.  Setting this allows Lendsmart's internal
                           monitoring applications to track the usage of your
                           application.  Setting this is not necessary, but some
                           applications may desire this behavior.
        :type user_agent: str
        """
        self.base_url = base_url
        self._add_user_agent = user_agent
        self.service_account = service_account
        self.session = requests.Session()
        self.tenant_namespace = ''

        #: Access information related to the Prediction service - see
        #: :any:`PredictionGroup` for more information
        self.prediction = PredictionGroup(self)
        self.document = Documents(self)
        self.signature = AccountSignGroup(self)
        self.loan_documents = LoanDocumetGroup(self)
        self.lending_terms = LendingTerms(self)
        self.letter_of_explanations = LetterOfExplanationGroup(self)
        self.freddiemac = FreddieMacGroup(self)
        self.task = TaskGroup(self)
        self.origination_loan_permission = OriginationLoanPerimissionGroup(self)
        self.team_members = TeamMemberGroup(self)
        self.advisor_profile = AdvisorProfileGroup(self)
        self.event_bridge = EventBridgeGroup(self)
        self.openids = OpenidsGroup(self)
        self.namespace = NamespaceGroup(self)
        self.loanapp = LoanappGroup(self)
        self.loanapp_role=LoanappRoleGroup(self)
        self.business = BusinssGroup(self)
        self.notifier = NotifiersGroup(self)
        self.loan_status = LoanstatusGroup(self)
        self.account = AccountsGroup(self)
        self.finicity = Finicity(self)
        self.employment= EmploymentGroup(self)
        self.ignore_not_found = False

    def set_namespace(self, namespace):
        self.tenant_namespace = namespace

    def set_ignore_not_found_error(self):
        self.ignore_not_found = True

    def get_namespace(self):
        return self.tenant_namespace

    @property
    def _user_agent(self):
        return '{}python-lendsmart_api/{} {}'.format(
            '{} '.format(self._add_user_agent) if self._add_user_agent else '',
            package_version,
            requests.utils.default_user_agent()
        )

    def load(self, target_type, target_id, target_parent_id=None):
        """
        Constructs and immediately loads the object, circumventing the
        lazy-loading scheme by immediately making an API request.  Does not
        load related objects.

        For example, if you wanted to load an :any:`Instance` object with ID 123,
        you could do this::

           loaded_lendsmart = client.load(Instance, 123)

        Similarly, if you instead wanted to load a :any:`NodeBalancerConfig`,
        you could do so like this::

           loaded_nodebalancer_config = client.load(NodeBalancerConfig, 456, 432)

        :param target_type: The type of object to create.
        :type target_type: type
        :param target_id: The ID of the object to create.
        :type target_id: int or str
        :param target_parent_id: The parent ID of the object to create, if
                                 applicable.
        :type target_parent_id: int, str, or None

        :returns: The resulting object, fully loaded.
        :rtype: target_type
        :raise ApiError: if the requested object could not be loaded.
        """
        result = target_type.make_instance(
            target_id, self, parent_id=target_parent_id)
        result._api_get()

        return result

    def _api_call(self, endpoint, model=None, method=None, data=None, filters=None):
        """
        Makes a call to the lendsmart api.  Data should only be given if the method is
        POST or PUT, and should be a dictionary
        """
        if not self.service_account:
            raise RuntimeError("You do not have an API service account!")

        if not method:
            raise ValueError("Method is required for API calls!")

        if model:
            endpoint = endpoint.format(**vars(model))
        url = '{}{}'.format(self.base_url, endpoint)
        headers = {
            'Authorization': "Bearer {}".format(self.service_account.bearer_token()),
            'Content-Type': 'application/json',
            'User-Agent': self._user_agent,
            'X-AUTH-LENDSMART-SERVICE-ACCOUNT-NAME': self.service_account.CONST_SERVICE_ACCOUNT_NAME,
        }

        if filters:
            headers['X-Filter'] = json.dumps(filters)

        body = None
        if data is not None:
            body = json.dumps(data)

        response = method(url, headers=headers, data=body)
        warning = response.headers.get('Warning', None)
        if warning:
            logger.warning('Received warning from server: {}'.format(warning))

        if 399 < response.status_code < 600:
            j = None
            error_msg = '{}: '.format(response.status_code)
            try:
                j = response.json()
                if 'message' in j.keys():
                    error_msg += '{}; {} '.format(j['reason'], j['message'])
                if self.ignore_not_found and response.status_code == 404:
                    return j

            except:
                pass
            raise ApiError(error_msg, status=response.status_code, json=j)

        if response.status_code != 204:
            j = response.json()
        else:
            j = None  # handle no response body

        return j

    def _get_objects(self, endpoint, cls, model=None, parent_id=None, filters=None):
        response_json = self.get(endpoint, model=model, filters=filters)

        if not "data" in response_json:
            raise UnexpectedResponseError(
                "Problem with response!", json=response_json)

        if 'pages' in response_json:
            formatted_endpoint = endpoint
            if model:
                formatted_endpoint = formatted_endpoint.format(**vars(model))
            return PaginatedList.make_paginated_list(response_json, self, cls,
                                                     parent_id=parent_id, page_url=formatted_endpoint[1:],
                                                     filters=filters)
        return PaginatedList.make_list(response_json["data"], self, cls,
                                       parent_id=parent_id)

    def get(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.get, **kwargs)

    def post(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.post, **kwargs)

    def put(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.put, **kwargs)

    def delete(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.delete, **kwargs)

    def documents(self, *filters):
        """
        Retrieves a list of available Documents
        Document available to the acting user.

        :returns: A list of available Documents.
        :rtype: PaginatedList of Document
        """
        return self._get_and_filter(Document, *filters)

    def document_create(self, disk, label=None, description=None):
        """
        Creates a new Document

        :returns: The new Document.
        :rtype: Document
        """

        if label is not None:
            params = {
                "object_meta": {
                    "name": label["name"],
                    "account": label["account"]
                },
                "document_name": label["document_name"],
                "location": label["location"],
                "represents_schema": label["represents_schema"],
                "status": {
                    "phase": "Pending",
                    "message": "",
                    "reason": "",
                    "conditions": []
                }
            }

        if description is not None:
            params["description"] = description

        result = self.post('/documents', data=params)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating an '
                                          'Document {}'.format(disk))

        return Document(self, result['id'], result)
