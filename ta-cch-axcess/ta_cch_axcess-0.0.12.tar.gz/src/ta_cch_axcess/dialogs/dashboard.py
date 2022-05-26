from .cch_dialog import CchDialog


class Dashboard(CchDialog):
    def __init__(self, app):
        super(Dashboard, self).__init__(app, title="Dashboard", visible_only=False)

    def select_application_link(self, name):
        self.window.set_focus()
        self.window.child_window(class_name="TextBlock", title="Application Links").click_input()
        self.window.child_window(class_name="cch-db-applnk-lnk ng-binding", title=name).wait("exists", timeout=15)
        self.window.child_window(class_name="cch-db-applnk-lnk ng-binding", title=name).click_input()
