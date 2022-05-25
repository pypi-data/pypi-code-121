from ta_cch_axcess import logger


class CCHDialogNames:
    DASHBOARD = "Dashboard"
    RETURN_MANAGER = "Return Manager"
    DOCUMENTS = "Documents"


class CchDialog:
    def __init__(self, cch_app, **search_criteria):
        """
        :param cch_app: instance of CCH application
        :param search_criteria: kw args for app.window() pywinauto method
        """
        logger.info(f"getting CMS dialog title {search_criteria}")
        self.app = cch_app
        self.window = self.app.window(**search_criteria)
        self.window.wait("exists", timeout=30)
        logger.info(f"Connected {self.window}")
        super(CchDialog, self).__init__()
