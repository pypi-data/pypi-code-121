from pywinauto import Application
from ta_captcha_solver.ta_captcha_solver import ImageCaptcha
from ta_cch_axcess.cch_error import CCHException
from ta_cch_axcess.dialogs import Dashboard
from pathlib import Path
import os
from ta_cch_axcess import logger
from tempfile import TemporaryDirectory
from pywinauto.timings import TimeoutError as pywinautoTimeoutError

from RPA.Robocorp.Vault import Vault
from ta_bitwarden_cli.ta_bitwarden_cli import Bitwarden


def get_bitwarden_cli():
    logger.info("requesting credentials...")
    bitwarden_credentials = Vault().get_secret("bitwarden_credentials")
    bit_warden = Bitwarden(bitwarden_credentials)
    bit_warden.bitwarden_login()
    return bit_warden


# CCH_PATH = r"C:\Program Files (x86)\WK\ProSystem fx Suite\Smart Client\SaaS\CCH.CommonUIFramework.Shell.exe"
class CCH(Application):
    def __init__(self, cch_path, cch_creds_group, captcha_creds_group):
        """
        :param credentials:
        :param api_key:
        :param cch_path: path to CCH executable
        :param otp_refresh_func: function to get fresh otp value
        """
        super().__init__(backend="uia", allow_magic_lookup=True)
        self.bitwarden = get_bitwarden_cli()
        self.cch_creds_group = cch_creds_group
        self.captcha_creds_group = captcha_creds_group
        credentials = self._get_creds()
        self.cch_path = str(cch_path)
        try:
            self.connect(title="Dashboard", timeout=20)
        except Exception as e:
            logger.info(f"{type(e)} - No pre-exist CCH instance found - starting new")
            logger.info(f'starting CCH with "{cch_path}"')
            os.startfile(cch_path)
            self._login(credentials)

    def _login(self, credentials):
        login = credentials["cch"]["login"]
        password = credentials["cch"]["password"]
        api_key = credentials["captcha"]["API Key"]

        logger.info("Waiting to connect to CCH Login Window")
        self.connect(title="CCH Axcess Login", timeout=60 * 5, found_index=0)
        self["CCH Axcess Login"].set_focus()
        self.login_window = self.LoginDialog
        self.login_window.wait("exists")

        logger.info("Typing in username field...")

        self.username_edit = self.login_window.child_window(auto_id="usernametxt")
        self.username_edit.wait("exists", timeout=30)
        self.username_edit.set_focus()
        self.username_edit.click_input()
        self.username_edit.wait("ready", timeout=30)
        self.username_edit.set_text(login)

        logger.info("Typing in password field...")
        self.password_edit = self.login_window.child_window(auto_id="password")
        self.password_edit.wait("exists", timeout=30)
        self.password_edit.set_focus()
        self.password_edit.click_input()
        self.password_edit.wait("ready", timeout=30)

        self.temp_dir = TemporaryDirectory()
        for _attempt in range(3):
            try:
                self.password_edit.set_text(password)
                captcha_img = self.login_window.child_window(best_match="image")
                img = captcha_img.capture_as_image()
                captcha_img_path = str(Path(self.temp_dir.name) / "captcha_screenshot.png")
                img.save(captcha_img_path)
                self.solve_captcha(api_key, captcha_img_path)
                self.password_edit.wait_not("exists", timeout=5)
                break
            except pywinautoTimeoutError as e:
                logger.warning(e)
                if _attempt >= 2:
                    raise e
            except CCHException as e:
                logger.warning(e)
                if _attempt >= 2:
                    raise e

        try:
            logger.info("Selecting MFA option...")
            self.mfa_option = self.login_window.child_window(auto_id="MfaMode", found_index=1).wait("exists", timeout=5)

            self.mfa_option.set_focus()
            self.mfa_option.click_input()

            self.sendcode_option = self.login_window.child_window(auto_id="btnSendCodeText").wait("exists", timeout=30)

            self.sendcode_option.set_focus()
            self.sendcode_option.click_input()
            self.login_window.child_window(auto_id="btnSubmitForVerification").wait("exists", timeout=5)

            self.mfa_edit = self.login_window.child_window(auto_id="VerificationCode")
            self.mfa_edit.wait("exists", timeout=5)
            self.mfa_edit.set_focus()
            self.mfa_edit.click_input()
            self.mfa_edit.wait("ready")
            self.solve_MFA_code()
        except pywinautoTimeoutError as e:
            logger.warning(f"{e} - No MFA presented")

        self.dashboard = Dashboard(self)

    def _login_warning(self):
        login_warning_element = self.login_window.child_window(class_name="errorPanel loginErrorBox")
        if login_warning_element.exists():
            msg = login_warning_element.window_text()
            logger.warning(msg)
            return msg

    def _get_creds(self):
        logger.info("Getting CCH credentials")
        creds = self.bitwarden.get_credentials({"cch": self.cch_creds_group, "captcha": self.captcha_creds_group})
        return creds

    def _get_otp(self):
        creds = self._get_creds()
        return creds["cch"]["otp"]

    def solve_captcha(self, api_key, captcha_image):
        image_captcha = ImageCaptcha(captcha_guru_api_key=api_key, image_source=captcha_image)
        image_captcha.solve()
        captcha_edit = self.login_window.child_window(auto_id="captchaText")
        captcha_edit.set_focus()
        captcha_edit.click_input()
        captcha_edit.wait("ready", timeout=30)
        captcha_edit.set_text(image_captcha.token)
        login_button = self.login_window.child_window(class_name="btn btn-primary loginButton")
        login_button.click_input()
        logger.info(f"Attempted solution {image_captcha.token}")
        try:
            login_button.wait_not("exists", timeout=5)
        except pywinautoTimeoutError:
            warning_message = self._login_warning()
            if warning_message:
                raise CCHException(warning_message)

    def solve_MFA_code(self):
        logger.info("Enter MFA code...")
        otp = self._get_otp()
        self.mfa_edit.set_text(otp)
        self.login_window.child_window(auto_id="btnSubmitForVerification").click_input()


if __name__ == "__main__":
    from src.ta_cch_axcess.dialogs import ReturnManager

    os.environ["RPA_SECRET_MANAGER"] = "RPA.Robocorp.Vault.FileSecrets"
    os.environ["RPA_SECRET_FILE"] = r"D:\Users\thoughtful_auto2\Documents\secrets.json"
    logger.info(os.environ["RPA_SECRET_MANAGER"])
    logger.info(os.environ["RPA_SECRET_FILE"])
    cch = CCH(
        r"C:\Program Files (x86)\WK\ProSystem fx Suite\Smart Client\SaaS\CCH.CommonUIFramework.Shell.exe",
        "CCH Access",
        "Support @ TA captcha.guru",
    )
    db = Dashboard(cch)
    db.select_application_link("Return Manager")
    rm = ReturnManager(cch)
    rm.search_by_client_id_or_name("123")
    table = rm.get_table()
    rows = table.descendants(control_type="DataItem")
