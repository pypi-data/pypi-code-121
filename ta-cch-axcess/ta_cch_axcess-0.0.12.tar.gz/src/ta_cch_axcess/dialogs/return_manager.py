from .cch_dialog import CchDialog


class ReturnManager(CchDialog):
    def __init__(self, cch):
        super(ReturnManager, self).__init__(cch, title="Return Manager", visible_only=False)

    def search_by_client_id_or_name(self, search_term):
        search_input = self.window.child_window(auto_id="clientSearchTextBox")
        search_input.wait("exists")
        search_input.set_text(search_term)
        search_input.type_keys("{ENTER}")
        # self.window.child_window(
        # 	auto_id='PART_SearchIconButton',
        # 	found_index=0
        # ).click()

    def get_table(self):
        return self.window.child_window(auto_id="_pageDataGrid").child_window(
            title="Records", class_name="ViewableRecordCollection", control_type="DataGrid"
        )
