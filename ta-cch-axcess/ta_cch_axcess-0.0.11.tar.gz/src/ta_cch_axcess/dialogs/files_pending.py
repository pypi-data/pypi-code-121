from .cch_dialog import CchDialog
from ta_cch_axcess import logger


class FilesPending(CchDialog):
    def __init__(self, cch_app):
        super(FilesPending, self).__init__(
            cch_app, title_re="Files Pending Approval", found_index=0, visible_only=False
        )

    def process_files_in_document(self, tax_year, client_id):
        logger.info(f"Proccesing files of client id: {client_id}")

        self.window.child_window(auto_id="btnBrowseFolder").wait("exists", timeout=30)
        self.window.child_window(auto_id="btnBrowseFolder").click_input()
        self.window_popup = self.app.window(title_re="Choose a folder")
        self.window_popup.child_window(title=tax_year, class_name="TextBlock").double_click_input()
        self.window.child_window(auto_id="cmbClass").click_input()
        self.window.child_window(title="Tax", class_name="ListBoxItem", found_index=0).wait("exists", timeout=10)
        self.window.child_window(title="Tax", class_name="ListBoxItem", found_index=0).click_input()
        self.window.child_window(auto_id="cmbSubclass").click_input()
        self.window.child_window(title="Support Documents (PBC)", class_name="ListBoxItem", found_index=0).wait(
            "exists", timeout=10
        )
        self.window.child_window(title="Support Documents (PBC)", class_name="ListBoxItem", found_index=0).click_input()
        checkbox_all = self.window.child_window(auto_id="pfxChkBoxSelectAll", class_name="CheckBox").wrapper_object()

        checkbox_all_state = checkbox_all.get_toggle_state()

        if checkbox_all_state == 0:
            self.window.child_window(auto_id="pfxChkBoxSelectAll", class_name="CheckBox").toggle()

        self.window.child_window(auto_id="btnApplyToSelectedFiles").click_input()
        self.window.child_window(auto_id="btnApprove").wait("ready", timeout=5)
        self.window.child_window(auto_id="btnApprove").click_input()
        self.window_popup_approve = self.app.window(title="Approve Files")
        self.window_popup_approve.wait("exists", timeout=60 * 10)
        self.window_popup_approve.child_window(auto_id="PART_ThirdButton").click_input()
        self.window.child_window(auto_id="btnCancel").click_input()
        self.window_popup_approve.child_window(auto_id="PART_SecondButton").click_input()
