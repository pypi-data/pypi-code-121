from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error
from .uiform import SailUiForm

DESIGN_URI_PATH: str = "/suite/rest/a/applications/latest/app/design"


class Design:
    def __init__(self, interactor: _Interactor):
        self.interactor = interactor

    @raises_locust_error
    def visit(self) -> 'SailUiForm':
        """
        Navigates to /design

        Returns: The SAIL UI Form

        Example:

            >>> self.appian.design.visit()

        """
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'DESIGN'
        label = "Design.ApplicationList"
        response = self.interactor.get_page(DESIGN_URI_PATH, headers=headers, label=label)
        response.raise_for_status()
        return SailUiForm(self.interactor, response.json(), DESIGN_URI_PATH, breadcrumb=f'{label}.SailUi')

    @raises_locust_error
    def visit_object(self, opaque_id: str) -> 'SailUiForm':
        """
        Navigates to a specific object within the /design environment

        Returns: The SAIL UI Form

        Example:

             >>> self.appian.design.visit_object("lABD1iTIu_lxy_3T_90Is2fs63uh52xESYi6-fun7FBWshlrBQ0EptlFUdGyIRzSSluPyVdvOhvGgL6aBlnjlkWfQlALYR2aRZ_AIliJ4lc3g")

        """
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'DESIGN'
        uri = DESIGN_URI_PATH + '/' + opaque_id
        label = "Design.SelectedObject." + opaque_id[0:10]
        response = self.interactor.get_page(uri, headers=headers, label=label)
        response.raise_for_status()
        return SailUiForm(self.interactor, response.json(), uri, breadcrumb=f'{label}.SailUi')

    @raises_locust_error
    def visit_app(self, app_id: str) -> 'SailUiForm':
        """
        Navigates to a specific object within the /design environment

        Returns: The SAIL UI Form

        Example:

            >>> self.appian.design.visit_app("AADZeglVgAAgfpsAAJsAAAAAAdA")

        """
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'DESIGN'
        uri = f"{DESIGN_URI_PATH}/app/{app_id}"
        label = f"Design.SelectedApplication.{app_id}"
        response = self.interactor.get_page(uri, headers=headers, label=label)
        response.raise_for_status()
        return SailUiForm(self.interactor, response.json(), uri, breadcrumb=f'{label}.SailUi')

    def create_application(self, application_name: str) -> 'SailUiForm':
        """
        Creates an application and returns a form within representing the app contents

        Returns: The SAIL UI Form

        """
        design_form: SailUiForm = self.visit()
        app_form: SailUiForm = self._create_object(design_form, link_name='New Application', object_name=application_name)
        app_form.breadcrumb = f"Design.SelectedApplicationByName.{application_name}"
        return app_form

    def create_record_type(self, app_form: SailUiForm,
                           record_type_name: str) -> 'SailUiForm':
        """
        Takes an application form and creates a record type with the given name

        Returns: The SAIL UI Form after the record type is created

        """
        return self._create_object(app_form, link_name='Record Type', object_name=record_type_name)

    def create_report(self, app_form: SailUiForm,
                      report_name: str) -> 'SailUiForm':
        """
        Takes an application form and creates a record type with the given name

        Returns: The SAIL UI Form after the record type is created

        """
        return self._create_object(app_form, link_name='Report', object_name=report_name)

    def _create_object(self, ui_form: SailUiForm, link_name: str, object_name: str) -> 'SailUiForm':
        return ui_form.click(link_name)\
            .fill_text_field('Name', object_name)\
            .click('Create')\
            .assert_no_validations_present()\
            .click('Save')
