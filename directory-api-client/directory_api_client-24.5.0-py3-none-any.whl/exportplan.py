from directory_client_core.authentication import SessionSSOAuthenticator

from directory_api_client.base import AbstractAPIClient

url_exportplan = '/exportplan/company-export-plan/{pk}/'

url_model_object_create = 'exportplan/export-plan-model-object-list-create/'
url_model_object_update_delete = 'exportplan/export-plan-model-object-update-delete/{pk}/'
url_model_object_details = 'exportplan/export-plan-model-object-detail/{pk}/{model_name}/'

url_exportplan_pdf_upload = 'exportplan/pdf-upload/'

# New Multi export-plan api methods will replace old ones above
url_exportplan_detail_list = '/exportplan/detail-list/'
url_exportplan_create = 'exportplan/create/'


class ExportPlanAPIClient(AbstractAPIClient):
    authenticator = SessionSSOAuthenticator

    def update(self, sso_session_id, id, data):
        return self.patch(url=url_exportplan.format(pk=id), data=data, authenticator=self.authenticator(sso_session_id))

    def detail(self, sso_session_id, id):
        return self.get(
            url=url_exportplan.format(pk=id),
            authenticator=self.authenticator(sso_session_id),
        )

    def create(self, sso_session_id, data):
        return self.post(url=url_exportplan_create, data=data, authenticator=self.authenticator(sso_session_id))

    def delete_export_plan(self, sso_session_id, id):
        return self.delete(url=url_exportplan.format(pk=id), authenticator=self.authenticator(sso_session_id))

    def model_object_update(self, sso_session_id, id, data, model_name):
        data['model_name'] = model_name
        return self.patch(
            url=url_model_object_update_delete.format(pk=id),
            data=data,
            authenticator=self.authenticator(sso_session_id),
        )

    def model_object_delete(self, sso_session_id, id, model_name):
        data = {'model_name': model_name}
        return self.delete(
            url=url_model_object_update_delete.format(pk=id),
            data=data,
            authenticator=self.authenticator(sso_session_id),
        )

    def model_object_detail(self, sso_session_id, id, model_name):
        return self.get(
            url=url_model_object_details.format(pk=id, model_name=model_name),
            authenticator=self.authenticator(sso_session_id),
        )

    def model_object_create(self, sso_session_id, data, model_name):
        data['model_name'] = model_name
        return self.post(url=url_model_object_create, data=data, authenticator=self.authenticator(sso_session_id))

    def pdf_upload(self, sso_session_id, data):
        files = {}
        if 'pdf_file' in data:
            files['pdf_file'] = data.pop('pdf_file')
        return self.post(
            url=url_exportplan_pdf_upload,
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def detail_list(self, sso_session_id):
        return self.get(url=url_exportplan_detail_list, authenticator=self.authenticator(sso_session_id))
