import os
import json
import pathlib
import time
from packaging import version
from kabaret import flow
from kabaret.flow_entities.store import EntityStore

from libreflow import _version as libreflow_version
from libreflow.pianoplayer import _version as project_version

from libreflow.utils.kabaret.flow_entities.entities import GlobalEntityCollection
from libreflow.utils.flow import ActionValueStore, GenericActionView
from libreflow.baseflow import (
    ProjectSettings as BaseProjectSettings,
    MultisiteConfig,
    SynchronizeFiles,
    KitsuConfig,
    LoginPage,
    LogOut
)
from libreflow.baseflow.users import Users, UserProfile, UserEnvironment
from libreflow.baseflow.site import GotoCurrentSiteQueue
from libreflow.baseflow.film import FilmCollection
from libreflow.baseflow.task_manager import TaskManager
from libreflow.baseflow.runners import (
    Blender,
    AfterEffects,
    AfterEffectsRender,
    RV,
    MarkSequenceRunner,
    SessionWorker,
    DefaultEditor,
    DefaultRunners
)

from .entity_manager import EntityManager
from .film import Film, Sequence, Shot
from .users import User
from .site import WorkingSite
from .file import (
    CreateFileAction,
    CreateFolderAction
)
from .packaging import PackageSettings
from .shotgrid import ShotGridConfig


class ProjectSettings(BaseProjectSettings):

    task_manager      = flow.Child(TaskManager)

    libreflow_version = flow.Param('0.0.0').ui(editable=False)
    project_version   = flow.Param('0.0.0').ui(editable=False)

    actions = flow.Child(GenericActionView)

    with flow.group('Default ShotGrid Login'):
        sg_login = flow.Param("").ui(label="Login")
        sg_password = flow.Param("").ui(label="Password", editor='password')


class Synchronization(flow.Object):

    ICON = ('icons.libreflow', 'sync')
    
    _project = flow.Parent()
    synchronize_files = flow.Child(SynchronizeFiles)
    jobs = flow.Child(GotoCurrentSiteQueue)

    def summary(self):
        nb_waiting_jobs = self.root().project().get_current_site().count_jobs(
            status='WAITING'
        )
        
        if nb_waiting_jobs > 0:
            return (
                "<font color=#D5000D><b>"
                f"{nb_waiting_jobs} job(s) waiting"
                "</b></font>"
            )


class Admin(flow.Object):

    ICON = ('icons.gui', 'user-admin')

    _project = flow.Parent()

    project_settings = flow.Child(ProjectSettings)
    users = flow.Child(Users).ui(show_filter=True)
    user_environment = flow.Child(UserEnvironment).ui(expanded=False)
    multisites = flow.Child(MultisiteConfig).ui(label='Sites')
    kitsu = flow.Child(KitsuConfig).ui(label='Kitsu settings')
    shotgrid = flow.Child(ShotGridConfig).ui(label='ShotGrid settings')
    default_applications = flow.Child(DefaultRunners).ui(expanded=False)
    login_page = flow.Child(LoginPage).ui(hidden=True)
    packaging = flow.Child(PackageSettings)

    entity_manager = flow.Child(EntityManager)


class Project(flow.Object):
    '''
    This class defines the project root.
    '''
    
    log_out_action  = flow.Child(LogOut).ui(label='Log out')
    user            = flow.Child(UserProfile)
    synchronization = flow.Child(Synchronization).ui(expanded=True)
    films           = flow.Child(FilmCollection).ui(expanded=True, action_submenus=True, items_action_submenus=True)
    admin           = flow.Child(Admin)

    _RUNNERS_FACTORY = None

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if slot_name == 'libreflow.baseflow.film.Film':
            return Film
        elif slot_name == 'libreflow.baseflow.shot.Sequence':
            return Sequence
        elif slot_name == 'libreflow.baseflow.shot.Shot':
            return Shot
        elif slot_name == 'libreflow.baseflow.file.CreateFileAction':
            return CreateFileAction
        elif slot_name == 'libreflow.baseflow.file.CreateFolderAction':
            return CreateFolderAction
        elif slot_name == 'libreflow.baseflow.users.User':
            return User
        elif slot_name == 'libreflow.baseflow.site.WorkingSite':
            return WorkingSite
    
    def get_contextual_view(self, context_name):
        if context_name == 'settings':
            return self.admin.project_settings.settings
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                path_format='{film}/{sequence}/{shot}/{task}/{file_mapped_name}/{revision}/{file_base_name}'
            )

    def get_root(self, alternative=None):
        '''
        alternative can be used if root_dir.get() returns None
        '''
        root_dir = self.admin.multisites.root_dir.get()
        
        if root_dir is None and alternative is not None:
            root_dir = alternative
        
        return root_dir
    
    def get_temp_folder(self):
        return self.admin.multisites.temp_dir.get()
    
    def project_settings_folder(self):
        return pathlib.Path(pathlib.Path.home(), '.libreflow', self.name())

    def set_user_name(self, username):
        project_settings_folder = self.project_settings_folder()

        if not os.path.exists(project_settings_folder):
            os.makedirs(project_settings_folder)

        user_file = os.path.join(project_settings_folder, 'current_user.json')

        with open(user_file, 'w+') as f:
            user_config = dict(username=username)
            json.dump(user_config, f)
        
        self.user.current_user_id.touch()
    
    def get_user_name(self):
        '''
        Returns the name of the current user.
        '''
        return self.user.current_user_id.get()

    def get_user(self, name=None):
        '''
        Returns the user of this project with the given name.
        '''
        if name is None:
            name = self.get_user_name()
        
        if not self.admin.users.has_mapped_name(name):
            return None
        
        return self.admin.users[name]
    
    def get_default_file_presets(self):
        return self.admin.project_settings.default_files

    def user_settings_folder(self):
        return pathlib.Path(self.project_settings_folder(), self.get_user_name())
    
    def get_current_site(self):
        '''
        Returns the current working site.
        '''
        return self.get_working_sites()[
            self.admin.multisites.current_site_name.get()
        ]
    
    def get_exchange_site(self):
        '''
        Returns the current exchange site.
        '''
        return self.get_exchange_sites()[
            self.admin.multisites.exchange_site_name.get()
        ]

    def get_working_sites(self):
        return self.admin.multisites.working_sites

    def get_exchange_sites(self):
        return self.admin.multisites.exchange_sites

    def get_entity_manager(self):
        return self.admin.entity_manager

    def get_entity_store(self):
        return self.admin.entity_manager.store
    
    def get_task_manager(self):
        return self.admin.project_settings.task_manager
    
    def get_sync_manager(self):
        return self.synchronization.synchronize_files
    
    def kitsu_config(self):
        return self.admin.kitsu
    
    def kitsu_api(self):
        return self.admin.kitsu.gazu_api
    
    def kitsu_bindings(self):
        return self.admin.kitsu.bindings
    
    def get_factory(self):
        self.ensure_runners_loaded()
        return self._RUNNERS_FACTORY
    
    def ensure_runners_loaded(self):
        session = self.root().session()
        subprocess_manager = session.get_actor('SubprocessManager')

        if self._RUNNERS_FACTORY is None:
            self._RUNNERS_FACTORY = subprocess_manager.create_new_factory(
                'Libreflow.pianoplayer Tools'
            )
            self._register_runners()

        subprocess_manager.ensure_factory(self._RUNNERS_FACTORY)
    
    def update_kitsu_host(self, server_url):
        kitsu_api = self.kitsu_api()
        kitsu_api.set_server_url(server_url)
        kitsu_api.set_host(server_url + '/api')

        return kitsu_api.host_is_valid()
    
    def show_login_page(self):
        kitsu_api = self.kitsu_api()
        valid_host = kitsu_api.host_is_valid()

        if not valid_host:
            logged_in = False
        else:
            logged_in = kitsu_api.current_user_logged_in()

        if not logged_in:
            try:
                f = open('%s/kitsu_config.json' % self.user_settings_folder(), 'r')
            except IOError:
                logged_in = False
            else:
                kitsu_config = json.load(f)
                kitsu_api.set_host(kitsu_config['kitsu_host'])
                kitsu_api.set_tokens(kitsu_config['tokens'])

                logged_in = kitsu_api.current_user_logged_in()

        return not kitsu_api.host_is_valid() or not logged_in
    
    def log_in(self, kitsu_login, kitsu_password):
        kitsu_api = self.kitsu_api()

        self.update_kitsu_host(self.admin.kitsu.server_url.get())
        kitsu_user_data = kitsu_api.log_in(kitsu_login, kitsu_password)

        if kitsu_user_data is None:
            return 1
        
        kitsu_id = kitsu_user_data['user']['id']

        # Set current user
        # user_name = self.admin.users.get_user_name(kitsu_login)
        user = self.admin.users.get_user_by_uid(kitsu_id)

        if user is None:
            # Create user profile if not registered
            user = self.admin.users.add_user(kitsu_id, kitsu_login)

            if user is None:
                return 2

            # user_name = user.name()
        
        self.set_user_name(user.name())

        # Create user folder at first login
        user_settings_folder = self.user_settings_folder()
        if not os.path.exists(user_settings_folder):
            os.makedirs(user_settings_folder)

        # Save authentification tokens
        tokens = kitsu_api.get_tokens()
        kitsu_config = {}
        kitsu_config['tokens'] = tokens
        kitsu_config['kitsu_host'] = kitsu_api.get_host()

        if user_settings_folder is not None:
            with open('%s/kitsu_config.json' % user_settings_folder, 'w+') as f:
                json.dump(kitsu_config, f)

        return 0
    
    def log_out(self):
        self.kitsu_api().log_out()
    
    def get_shotgrid_config(self):
        return self.admin.shotgrid
    
    def update_user_environment(self):
        self.admin.user_environment.update()
    
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
            if v[0] == 'libreflow.pianoplayer':
                user._last_project_used_version.set(v[1])
            elif v[0] == 'libreflow':
                user._last_libreflow_used_version.set(v[1])

    def get_required_versions(self):
        '''
        Returns a list of dependencies
        [dependecyName, currentVersion, requiredVersion, updateNeeded(0:no|1:yes minor|2: yes major)],[]
        '''
        versions = []

        libreflow_cur_version = version.parse(
            libreflow_version.get_versions()['version']
        )
        libreflow_req_version = version.parse(
            self.admin.project_settings.libreflow_version.get()
        )
        
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

        versions.append([
            'libreflow',
            str(libreflow_cur_version),
            str(libreflow_req_version),
            libreflow_needs_update]
        )
        
        project_cur_version = version.parse(
            project_version.get_versions()['version']
        )
        project_req_version = version.parse(
            self.admin.project_settings.project_version.get()
        )

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

       
        versions.append([
            'libreflow.pianoplayer',
            str(project_cur_version),
            str(project_req_version),
            project_needs_update
        ])
    
        for v in versions:
            print(v)
        return versions
    
    def get_project_thumbnail(self):
        image = self.admin.project_settings.project_thumbnail.get()
        return image
    
    def get_action_value_store(self):
        return self.get_entity_manager().action_value_store
    
    def settings(self):
        return self.admin.project_settings
    
    def touch(self):
        super(Project, self).touch()
        self.ensure_runners_loaded()
        self.update_user_environment()
    
    def _register_runners(self):
        self._RUNNERS_FACTORY.ensure_runner_type(Blender)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffects)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffectsRender)
        self._RUNNERS_FACTORY.ensure_runner_type(RV)
        self._RUNNERS_FACTORY.ensure_runner_type(MarkSequenceRunner)
        self._RUNNERS_FACTORY.ensure_runner_type(SessionWorker)
        self._RUNNERS_FACTORY.ensure_runner_type(DefaultEditor)
    
    def _fill_ui(self, ui):
        if self._RUNNERS_FACTORY is None:
            self.ensure_runners_loaded()
        
        self.touch()

        if self.show_login_page():
            ui['custom_page'] = 'libreflow.baseflow.LoginPageWidget'
