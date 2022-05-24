from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error
from .uiform import SailUiForm

ADMIN_URI_PATH: str = "/suite/rest/a/applications/latest/app/admin"


class Admin:
    def __init__(self, interactor: _Interactor):
        self.interactor = interactor

    @raises_locust_error
    def visit(self) -> 'SailUiForm':
        """
        Navigates to /admin

        Returns: The SAIL UI Form

        Example:

            >>> self.appian.admin.visit()

        """
        # Navigate to Admin Console
        headers = self.interactor.setup_sail_headers()
        headers['X-Client-Mode'] = 'ADMIN'
        label = "Admin.MainMenu"
        response = self.interactor.get_page(ADMIN_URI_PATH, headers=headers, label=label)
        response.raise_for_status()
        return SailUiForm(self.interactor, response.json(), ADMIN_URI_PATH, breadcrumb=f'{label}.SailUi')
