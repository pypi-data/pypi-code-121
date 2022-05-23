from kabaret import flow
from kabaret.app.actors.flow.generic_home_flow import ProjectsMap
from kabaret.app.actors.flow.generic_home_flow import AbstractHomeRoot


class ClassicHome(flow.Object):
    """
    Access the classic home with right click on the oid on top of the page
    Useful to add projects or change status
    """

    projects = flow.Child(ProjectsMap).ui(
        auto_fit=False, columns_width=(50, 20), expanded=True
    )


class Home(flow.SessionObject):
    """
    This Home is completely overrided by the custom_page
    designed in the custom_home.ui
    """

    ClassicHome = flow.Child(ClassicHome)

    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.pianoplayer.custom_home.ui.ProjectHomePageWidget'

    def get_projects(self):
        return self.root().flow_actor.get_projects_info()


class CustomHomeRoot(AbstractHomeRoot):

    Home = flow.Child(Home)