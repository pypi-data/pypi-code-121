from kabaret import flow
from libreflow.baseflow.site import WorkingSite as BaseWorkingSite
from libreflow.baseflow.site import ConfigureWorkingSite as BaseConfigureWorkingSite
from libreflow.utils.flow import SiteActionView

class ConfigureWorkingSite(BaseConfigureWorkingSite):
    use_sg_default = flow.BoolParam(True).ui(label="Use ShotGrid Default Account")

    with flow.group('ShotGrid Login'):
        sg_login = flow.Param("").ui(label="Login")
        sg_password = flow.Param("").ui(label="Password", editor='password')
    
    def _fill_action_fields(self):
        self.use_sg_default.set(self._site.use_sg_default.get())
        self.sg_login.set(self._site.sg_login.get())
        self.sg_password.set(self._site.sg_password.get())
        super(ConfigureWorkingSite, self)._fill_action_fields()
    
    def _configure_site(self, site):
        site.use_sg_default.set(self.use_sg_default.get())
        site.sg_login.set(self.sg_login.get())
        site.sg_password.set(self.sg_password.get())
        super(ConfigureWorkingSite, self)._configure_site(site)
    
    def run(self, button):
        if self.use_sg_default.get():
            self.sg_login.set("")
            self.sg_password.set("")
        super(ConfigureWorkingSite, self).run(button)

class SGEditable(flow.values.StringValue):
    _site = flow.Parent()

    def _fill_ui(self, ui):
        ui['editable'] = self._site.sg_editable.get()

class WorkingSite(BaseWorkingSite):

    configuration = flow.Child(ConfigureWorkingSite)

    use_sg_default = flow.BoolParam().ui(label="Use ShotGrid Default Account", editable=False)

    with flow.group('ShotGrid Login'):
        sg_editable = flow.BoolParam().ui(hidden=True, label="Is Editable").watched()
        sg_login = flow.Param("", SGEditable).ui(hidden=True)
        sg_password = flow.Param("", SGEditable).ui(editor='password', hidden=True)
        sg_displaylogin = flow.Computed().ui(label="Login")
        sg_displaypassword = flow.Computed().ui(label="Password", editor='password')

    actions = flow.Child(SiteActionView)

    package_source_dir = flow.Param()
    package_target_dir = flow.Param()
    package_layout_dir = flow.Param()
    package_clean_dir  = flow.Param()
    package_color_dir  = flow.Param()
    package_line_dir   = flow.Param()
    export_target_dir  = flow.Param()
    target_sites       = flow.OrderedStringSetParam()

    def compute_child_value(self, child_value):
        if child_value is self.sg_displaylogin:
            if self.use_sg_default.get() == True:
                self.sg_login.set(self.root().project().admin.project_settings.sg_login.get())
            self.sg_displaylogin.set(self.sg_login.get())
        elif child_value is self.sg_displaypassword:
            if self.use_sg_default.get() == True:
                self.sg_password.set(self.root().project().admin.project_settings.sg_password.get())
            self.sg_displaypassword.set(self.sg_password.get())
        super(WorkingSite, self).compute_child_value(child_value)