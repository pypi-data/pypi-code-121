from otrs_somconnexio.user_management_client.client import UserManagementClient


class CustomerUser:
    def __init__(self, id, client=UserManagementClient):
        self.id = id
        self.client = client(self.id)

    def change_language(self, lang):
        self.client.set_preference(
            'UserLanguage',
            lang
        )

    def set_mm_account_id(self, mm_account_id):
        """
        Set "MMAccountId" parameter in the OTRS preferences from this CustomerUser
        """
        self.client.set_preference(
            'MMAccountId',
            mm_account_id
        )

    def get_mm_account_id(self):
        """
        Set "MMAccountId" parameter in the OTRS preferences from this CustomerUser
        Returns a str with the ID or None if the parameter has not been set
        """
        preferences = self.client.get_preferences()

        return preferences.get('MMAccountId')

    def get_data(self):
        return self.client.get_data()
