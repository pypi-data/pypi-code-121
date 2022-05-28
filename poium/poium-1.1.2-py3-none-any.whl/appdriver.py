from poium.config import Browser


class AppDriver:

    @staticmethod
    def install_app(app_path):
        """
        Install the application found at `app_path` on the device.
        """
        Browser.driver.install_app(app_path)

    @staticmethod
    def is_app_installed(bundle_id) -> bool:
        """
        Checks whether the application specified by `bundle_id` is installed on the device.
        """
        return Browser.driver.is_app_installed(bundle_id)
