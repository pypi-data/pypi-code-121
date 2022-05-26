from kabaret import flow
from libreflow.baseflow import (
    Project as BaseProject,
    ProjectSettings as BaseProjectSettings,
    LogOut,
    UserProfile,
    Admin as BaseAdmin,
    Synchronization
)
from libreflow.baseflow.film import FilmCollection
from libreflow.baseflow.task_manager import TaskManager

from .entity_manager import EntityManager
from .user import User
from .film import Film
from .shot import Sequence, Shot
from .task import Task


class ProjectSettings(BaseProjectSettings):

    task_manager = flow.Child(TaskManager)


class Admin(BaseAdmin):

    entity_manager = flow.Child(EntityManager)

    store = flow.Child(flow.Object).ui(hidden=True)
    dependency_templates = flow.Child(flow.Object).ui(hidden=True)


class Project(BaseProject, flow.InjectionProvider):
    
    log_out_action  = flow.Child(LogOut).ui(label='Log out')

    user            = flow.Child(UserProfile)
    synchronization = flow.Child(Synchronization).ui(expanded=True)
    films           = flow.Child(FilmCollection).ui(expanded=True)
    admin           = flow.Child(Admin)

    asset_lib = flow.Child(flow.Object).ui(hidden=True)
    sequences = flow.Child(flow.Object).ui(hidden=True)

    _RUNNERS_FACTORY = None

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if slot_name == 'libreflow.baseflow.film.Film':
            return Film
        elif slot_name == 'libreflow.baseflow.shot.Sequence':
            return Sequence
        elif slot_name == 'libreflow.baseflow.shot.Shot':
            return Shot
        elif slot_name == 'libreflow.baseflow.users.User':
            return User
        elif slot_name == 'libreflow.baseflow.ProjectSettings':
            return ProjectSettings
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                path_format='{film}/{sequence}/{shot}/{task}/{file_mapped_name}/{revision}/{file_base_name}'
            )

    def update_user_last_visit(self):
        user_login = self.get_user_name()
        requiredVersion = self.get_required_versions()

        if not user_login or not requiredVersion:
            return

        users = self.admin.users

        if user_login not in users.mapped_names():
            return
        user = users[user_login]

        user._last_visit.set(time.time())
        for v in requiredVersion:
            if v[0] == 'libreflow.flows':
                user._last_project_used_version.set(v[1])
            elif v[0] == 'libreflow':
                user._last_libreflow_used_version.set(v[1])

    def get_required_versions(self):
        '''
        return a list of dependencies
        [dependecyName, currentVersion, requiredVersion, updateNeeded(0:no|1:yes minor|2: yes major)],[]
        '''
        versions = []

        libreflow_cur_version = version.parse(libreflow_version.get_versions()['version'])
        libreflow_req_version = version.parse(self.admin.project_settings.libreflow_version.get())
        
        if libreflow_cur_version < libreflow_req_version \
                and ((libreflow_cur_version.major < libreflow_req_version.major) or \
                    (libreflow_cur_version.minor < libreflow_req_version.minor)):
            # VERY IMPORTANT UPDATE
            libreflow_needs_update = 2
        elif libreflow_cur_version < libreflow_req_version:
            # MINOR UPDATE
            libreflow_needs_update = 1
        else:
            # NO UDPATE
            libreflow_needs_update = 0

        versions.append(['libreflow', str(libreflow_cur_version), str(libreflow_req_version), libreflow_needs_update])
        
        project_cur_version = version.parse(libreflowthesiren_version.get_versions()['version'])
        project_req_version = version.parse(self.admin.project_settings.project_version.get())

        if project_cur_version < project_req_version \
                and ((project_cur_version.major < project_req_version.major) or \
                    (project_cur_version.minor < project_req_version.minor)):
            # VERY IMPORTANT UPDATE
            project_needs_update = 2
        elif project_cur_version < project_req_version:
            # MINOR UPDATE
            project_needs_update = 1
        else:
            # NO UDPATE
            project_needs_update = 0

       
        versions.append(['libreflow.flows', str(project_cur_version), str(project_req_version), project_needs_update])
    
        for v in versions:
            print(v)
        return versions
    
    def get_default_file_presets(self):
        return self.admin.project_settings.default_files
    
    def get_entity_manager(self):
        return self.admin.entity_manager
    
    def get_task_manager(self):
        return self.admin.project_settings.task_manager

    def get_entity_store(self):
        return self.get_entity_manager().store
    
    def get_action_value_store(self):
        return self.get_entity_manager().action_value_store
