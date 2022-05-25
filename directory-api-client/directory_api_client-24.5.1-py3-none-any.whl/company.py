from directory_client_core.authentication import SessionSSOAuthenticator

from directory_api_client.base import AbstractAPIClient

url_profile = '/supplier/company/'
url_case_study_detail = '/supplier/company/case-study/{id}/'
url_case_study_published_detail = '/public/case-study/{id}/'
url_case_study_create = '/supplier/company/case-study/'
url_validate_company_number = '/validate/company-number/'
url_verify_with_code = '/supplier/company/verify/'
url_verify_with_companies_house = '/supplier/company/verify/companies-house/'
url_verify_with_identity_request = 'supplier/company/verify/identity/'
url_published_profile_detail = '/public/company/{number}/'
url_search_find_a_supplier = '/company/search/'
url_search_investment_support_directory = '/investment-support-directory/search/'
url_transfer_invite_create = '/supplier/company/transfer-ownership-invite/'
url_collaborator_list = '/supplier/company/collaborators/'
url_collaborator_add = '/supplier/company/add-collaborator/'
url_collaborator_remove = '/supplier/company/remove-collaborators/'
url_collaborator_invite = '/supplier/company/collaborator-invite/'
url_collaborator_invite_detail = '/supplier/company/collaborator-invite/{invite_key}/'
url_collaborator_role_change = '/supplier/company/change-collaborator-role/{sso_id}/'
url_collaboration_request = '/supplier/company/collaborator-request/'
url_collaboration_request_detail = '/supplier/company/collaborator-request/{request_key}/'
url_company_delete_by_sso_id = '/supplier/company/{sso_id}/{request_key}/'


class CompanyAPIClient(AbstractAPIClient):

    authenticator = SessionSSOAuthenticator

    def profile_update(self, sso_session_id, data):
        files = {}
        if 'logo' in data:
            files['logo'] = data.pop('logo')
        return self.patch(
            url=url_profile,
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def profile_retrieve(self, sso_session_id):
        return self.get(url=url_profile, authenticator=self.authenticator(sso_session_id))

    def published_profile_retrieve(self, number):
        return self.get(
            url=url_published_profile_detail.format(number=number),
            use_fallback_cache=True,
        )

    def validate_company_number(self, number):
        return self.get(url=url_validate_company_number, params={'number': number})

    def case_study_create(self, data, sso_session_id):
        files = {}
        for field in ['image_one', 'image_two', 'image_three', 'video_one']:
            if data.get(field):
                files[field] = data.pop(field)
        return self.post(
            url=url_case_study_create,
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def case_study_update(self, data, sso_session_id, case_study_id):
        files = {}
        for field in ['image_one', 'image_two', 'image_three', 'video_one']:
            if data.get(field):
                files[field] = data.pop(field)
        return self.patch(
            url=url_case_study_detail.format(id=case_study_id),
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def case_study_delete(self, sso_session_id, case_study_id):
        return self.delete(
            url=url_case_study_detail.format(id=case_study_id), authenticator=self.authenticator(sso_session_id)
        )

    def case_study_retrieve(self, sso_session_id, case_study_id):
        return self.get(
            url=url_case_study_detail.format(id=case_study_id),
            authenticator=self.authenticator(sso_session_id),
            use_fallback_cache=True,
        )

    def published_case_study_retrieve(self, case_study_id):
        return self.get(url=url_case_study_published_detail.format(id=case_study_id), use_fallback_cache=True)

    def verify_with_code(self, sso_session_id, code):
        return self.post(
            url=url_verify_with_code,
            data={'code': code},
            authenticator=self.authenticator(sso_session_id),
        )

    def verify_with_companies_house(self, sso_session_id, access_token):
        return self.post(
            url=url_verify_with_companies_house,
            data={'access_token': access_token},
            authenticator=self.authenticator(sso_session_id),
        )

    def verify_identity_request(self, sso_session_id):
        return self.post(
            url=url_verify_with_identity_request,
            authenticator=self.authenticator(sso_session_id),
        )

    def search_find_a_supplier(self, **kwargs):
        return self.get(url=url_search_find_a_supplier, params=kwargs, use_fallback_cache=True)

    def search_investment_search_directory(self, **kwargs):
        return self.get(url=url_search_investment_support_directory, params=kwargs, use_fallback_cache=True)

    def collaborator_create(self, sso_session_id, data):
        """Create a supplier and adds it to a company"""
        return self.post(url=url_collaborator_add, data=data, authenticator=self.authenticator(sso_session_id))

    def collaborator_list(self, sso_session_id):
        """List the collaborators attached to a the current user's company"""
        return self.get(url=url_collaborator_list, authenticator=self.authenticator(sso_session_id))

    def collaborator_disconnect(self, sso_session_id, sso_id):
        """Disconnect the specified user from their company"""
        return self.post(
            url=url_collaborator_remove,
            data={'sso_ids': [sso_id]},
            authenticator=self.authenticator(sso_session_id),
        )

    def collaborator_invite_create(self, sso_session_id, data):
        """Invite a email address to become a collaborator of the current user's company"""
        return self.post(url=url_collaborator_invite, data=data, authenticator=self.authenticator(sso_session_id))

    def collaborator_invite_retrieve(self, invite_key):
        """Retrieve the details of a collaboration invite"""
        return self.get(
            url=url_collaborator_invite_detail.format(invite_key=invite_key),
            use_fallback_cache=True,
        )

    def collaborator_invite_list(self, sso_session_id):
        """List all collaboration invites for the current user's company"""
        return self.get(url=url_collaborator_invite, authenticator=self.authenticator(sso_session_id))

    def collaborator_invite_accept(self, sso_session_id, invite_key):
        """Accept a collaboration invite. Become attached the the company"""
        # Adding name to populate supplier can remove once we remove from supplier
        return self.patch(
            url=url_collaborator_invite_detail.format(invite_key=invite_key),
            data={'accepted': True},
            authenticator=self.authenticator(sso_session_id),
        )

    def collaborator_invite_delete(self, sso_session_id, invite_key):
        """Delete a collaboration invite."""
        return self.delete(
            url=url_collaborator_invite_detail.format(invite_key=invite_key),
            authenticator=self.authenticator(sso_session_id),
        )

    def collaborator_role_update(self, sso_session_id, sso_id, role):
        url = url_collaborator_role_change.format(sso_id=sso_id)
        return self.patch(url=url, data={'role': role}, authenticator=self.authenticator(sso_session_id))

    def collaboration_request_create(self, sso_session_id, role):
        """Create a collaboration requests for the current user's company"""
        return self.post(
            url=url_collaboration_request,
            data={'role': role},
            authenticator=self.authenticator(sso_session_id),
        )

    def collaboration_request_list(self, sso_session_id):
        """List all collaboration requests for the current user's company"""
        return self.get(url=url_collaboration_request, authenticator=self.authenticator(sso_session_id))

    def collaboration_request_accept(self, sso_session_id, request_key):
        """Accept a collaboration request. Upgrade role"""
        return self.patch(
            url=url_collaboration_request_detail.format(request_key=request_key),
            data={'accepted': True},
            authenticator=self.authenticator(sso_session_id),
        )

    def collaboration_request_delete(self, sso_session_id, request_key):
        """Delete a collaboration request."""
        return self.delete(
            url=url_collaboration_request_detail.format(request_key=request_key),
            authenticator=self.authenticator(sso_session_id),
        )

    def delete_company_by_sso_id(self, sso_id, request_key):
        return self.delete(
            url=url_company_delete_by_sso_id.format(sso_id=sso_id, request_key=request_key),
            authenticator=self.authenticator(sso_id),
        )
