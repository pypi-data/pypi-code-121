from .cch_dialog import CchDialog
from pywinauto.timings import TimeoutError as PwaTimeoutError
from ta_cch_axcess import logger


class TaxReturn(CchDialog):
    def __init__(self, cch, year, client_id):
        super(TaxReturn, self).__init__(cch, title_re=f"{year}\w:{client_id}.*", visible_only=False)

    def close(self):
        self.window.close()
        close_return_popup = self.window.child_window(title="Close Return", control_type="Window")
        try:
            close_return_popup.wait("exists")
            close_return_popup.child_window(title="Yes", control_type="Button").click()
        except PwaTimeoutError:
            logger.warning(close_return_popup.child_window(auto_id="MessageLbl").window_text())
        close_return_popup.wait_not("exists")
