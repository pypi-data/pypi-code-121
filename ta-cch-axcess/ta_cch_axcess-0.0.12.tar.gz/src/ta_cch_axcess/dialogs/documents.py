from .cch_dialog import CchDialog
from ta_cch_axcess import logger
import re


class Documents(CchDialog):
    def __init__(self, cch_app):
        super(Documents, self).__init__(cch_app, title="Document", found_index=0, visible_only=False)

    def open_document_search(self):
        self.window.set_focus()
        self.window.maximize()
        self.window.child_window(class_name="RichTextBox", auto_id="txtSearch").click_input()
        self.window.child_window(class_name="RichTextBox", auto_id="txtSearch").type_keys("^a{BACKSPACE}")
        self.window.child_window(class_name="RichTextBox", auto_id="txtSearch").type_keys("Document")
        self.window.child_window(auto_id="imgSearch", class_name="Button").click_input()
        logger.info("Waiting for the search to complete...")
        self.window.child_window(auto_id="txtblockProgress", class_name="TextBlock", title="Search Completed.").wait(
            "enabled", timeout=40, retry_interval=1
        )
        logger.info("Complete!")

    def get_files_by_client_id(self, client_id):
        logger.info(f"Getting files of client id: {client_id}")

        self.window.child_window(title="Incoming files", class_name="TabItem").click_input()

        files_table = self.window.child_window(
            best_match="Records", class_name="ViewableRecordCollection"
        ).wrapper_object()

        cells = files_table.descendants(title="CCH.Document.UI.DocumentCentral.UIClasses.PendingApprovalEntityInfo")

        row_counter = 0
        found_row = False

        for cell in cells:
            childrens = cell.children(class_name="Cell")
            records = cell.children(class_name="ViewableRecordCollection")
            for children in childrens:
                if client_id in children.legacy_properties()["Name"]:
                    found_row = True
                if found_row and (
                    ("Files" in children.legacy_properties()["Name"])
                    or ("File" in children.legacy_properties()["Name"])
                ):
                    files_number = re.sub(r"[File|Files]", "", children.legacy_properties()["Name"]).strip()

            if found_row:
                break

            row_counter = row_counter + 1

        if row_counter == 1:
            files_number = "1"

        for record in records:
            if "Records" in record.legacy_properties()["Name"]:
                results = record.children(class_name="Record")
                for result in results:
                    if "FileSearchResultList" in result.legacy_properties()["Name"]:
                        datagrids = result.children(class_name="ViewableRecordCollection")
                        for datagrid in datagrids:
                            if "Records" in datagrid.legacy_properties()["Name"]:
                                list_data = datagrid.children(class_name="Record")
                                self.cell_to_click = list_data[int(files_number) - 1].children(class_name="Cell")

        self.window.child_window(
            title="CCH.Document.UI.DocumentCentral.UIClasses.PendingApprovalEntityInfo",
            class_name="Record",
            found_index=0,
        ).click_input()
        for x in range(row_counter):
            self.window.type_keys("{DOWN}")
        self.window.type_keys("{RIGHT}")
        keys_to_press = ""

        for x in range(int(files_number) - 1):
            keys_to_press = keys_to_press + "{DOWN}"

        self.window.type_keys("{DOWN}")
        self.window.type_keys("{VK_SHIFT down}{VK_CONTROL down}")
        self.window.type_keys(keys_to_press)
        self.window.type_keys("{VK_SHIFT up}{VK_CONTROL up}")

    def download_files(self, folder_name):
        self.cell_to_click[0].right_click_input()

        self.window.child_window(auto_id="mnuDownloadExistingCopy").wait("exists", timeout=15)
        self.window.child_window(auto_id="mnuDownloadExistingCopy").click_input()
        try:
            self.window.child_window(title=folder_name).wait("exists", timeout=15)
            self.window.child_window(title=folder_name).click_input()
        except Exception:
            self.window.child_window(title=folder_name + " (pinned)").wait("exists", timeout=15)
            self.window.child_window(title=folder_name + " (pinned)").click_input()

        self.window.child_window(auto_id="1").click_input()

    def press_process_files(self):
        self.window.child_window(auto_id="btnProcessPendingFiles", class_name="Button").wait("ready", timeout=15)
        self.window.child_window(auto_id="btnProcessPendingFiles").click_input()

    def reset_grid(self):
        self.window.child_window(auto_id="btnReset", class_name="Button").click_input()
