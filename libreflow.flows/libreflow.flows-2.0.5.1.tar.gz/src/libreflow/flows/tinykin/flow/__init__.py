import time
import timeago
import datetime
from packaging import version
from kabaret import flow
from kabaret.subprocess_manager.runners import Explorer

from libreflow import _version as libreflow_version
from libreflow.flows import _version as libreflowthesiren_version

from ..resources import file_templates
from ..resources.icons import flow as icons_flow

from libreflow.baseflow import (
    Project         as BaseProject,
    ProjectSettings as BaseProjectSettings,
    Admin           as BaseAdmin
)
from libreflow.baseflow.film import Sequences
from libreflow.baseflow.runners import (
    Blender,
    AfterEffects,
    AfterEffectsRender,
    MarkSequenceRunner,
    RV,
    SessionWorker,
    DefaultEditor
)

from .file import (
    CreateFileAction, CreateFolderAction,
    Revision,
    FileSystemMap,
    PublishFileAction,
    TrackedFile,
    TrackedFolder,
    DefaultFileViewItem
)
from .lib import AssetLib
from .film import Films
from .users import User, CheckUsersAction


class ProjectSettings(BaseProjectSettings):

    publish_ok_files = flow.Param('').ui(editable=False)
    libreflow_version = flow.Param('0.0.0').ui(editable=False)
    project_version = flow.Param('0.0.0').ui(editable=False)


class Project(BaseProject, flow.InjectionProvider):

    films = flow.Child(Films).ui(expanded=True)
    asset_lib = flow.Child(AssetLib).ui(label='Asset Library')
    admin = flow.Child(BaseAdmin)

    _check_users = flow.Child(CheckUsersAction)

    sequences = flow.Child(Sequences).ui(hidden=True)

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if slot_name == 'libreflow.baseflow.file.FileSystemMap':
            return FileSystemMap
        # elif slot_name == 'libreflow.baseflow.file.CreateFolderAction':
        #     return CreateFolderAction
        elif slot_name == 'libreflow.baseflow.file.Revision':
            return Revision
        elif slot_name == 'libreflow.baseflow.file.TrackedFile':
            return TrackedFile
        elif slot_name == 'libreflow.baseflow.file.TrackedFolder':
            return TrackedFolder
        elif slot_name == 'libreflow.baseflow.file.DefaultFileViewItem':
            return DefaultFileViewItem
        elif slot_name == 'libreflow.baseflow.ProjectSettings':
            return ProjectSettings
        elif slot_name == 'libreflow.baseflow.file.PublishFileAction':
            return PublishFileAction
        elif slot_name == 'libreflow.baseflow.users.User':
            return User

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

    def _register_runners(self):
        self._RUNNERS_FACTORY.ensure_runner_type(Blender)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffects)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffectsRender)
        self._RUNNERS_FACTORY.ensure_runner_type(MarkSequenceRunner)
        self._RUNNERS_FACTORY.ensure_runner_type(Explorer)
        self._RUNNERS_FACTORY.ensure_runner_type(RV)
        self._RUNNERS_FACTORY.ensure_runner_type(SessionWorker)
        self._RUNNERS_FACTORY.ensure_runner_type(DefaultEditor)
