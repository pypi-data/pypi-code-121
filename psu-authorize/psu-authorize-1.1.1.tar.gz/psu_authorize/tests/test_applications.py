import unittest
from psu_authorize.classes.Application import Application


class TestApplications(unittest.TestCase):
    """
    Test the functions used by the PSU module
    """

    def test_application_constructor(self):
        """
        Test the Application constructor
        """
        ferpa_data = {"id": 1, "app_code": "FERPA", "app_title": "FERPA Consent"}
        ferpa_app = Application(ferpa_data)

        self.assertTrue(ferpa_app.id == 1)
        self.assertTrue(ferpa_app.code == "FERPA")
        self.assertTrue(ferpa_app.title == "FERPA Consent")

    def test_global_app_constructor(self):
        """
        Test the Application constructor for GLOBAL app
        """
        global_app = Application.global_app()

        self.assertTrue(global_app.id == 0)
        self.assertTrue(global_app.code == "GLOBAL")
        self.assertTrue("Global" in global_app.title)


if __name__ == "__main__":
    unittest.main()
