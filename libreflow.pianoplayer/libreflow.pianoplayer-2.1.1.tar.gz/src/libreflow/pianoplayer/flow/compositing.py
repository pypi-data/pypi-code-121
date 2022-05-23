import os
import re
import time
import glob
from collections import defaultdict
from kabaret import flow
from kabaret.app import resources
from libreflow.baseflow.file import GenericRunAction
from libreflow.baseflow.runners import CHOICES_ICONS as FILE_ICONS
from libreflow.resources.icons import libreflow as _

from ..resources.scripts import aftereffects as _


class CompSceneDependency(flow.Object):
    
    department = flow.Computed()
    file_name = flow.Computed()
    path = flow.Computed()

    _map = flow.Parent()

    def extension(self):
        ext = os.path.splitext(self.file_name.get())[1]
        if ext:
            ext = ext[1:]
        return ext

    def compute_child_value(self, child_value):
        if child_value is self.department:
            self.department.set(self._map.get_department(self.name()))
        elif child_value is self.file_name:
            self.file_name.set(self._map.get_file_name(self.name()))
        elif child_value is self.path:
            self.path.set(self._map.get_path(self.name()))


class RefreshDependencies(flow.Action):

    ICON = ('icons.libreflow', 'refresh')

    _map = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._map.touch()


class CompSceneDependencies(flow.DynamicMap):

    ICON = ('icons.libreflow', 'dependencies')
    STYLE_BY_STATUS = {
        'available': ('icons.gui', 'available')
    }

    refresh = flow.Child(RefreshDependencies)

    _sequence = flow.Parent(6)
    _shot = flow.Parent(4)

    @classmethod
    def mapped_type(cls):
        return CompSceneDependency

    def __init__(self, parent, name):
        super(CompSceneDependencies, self).__init__(parent, name)
        self._dependencies_data = None

    def mapped_names(self, page_num=0, page_size=None):
        if self._dependencies_data is None:
            self._dependencies_data = {}

            for department, file_name, path, optional in self._get_dependencies():
                if path is None and optional:
                    continue

                mapped_name = '%s_%s' % (department, file_name.replace('.', '_'))
                self._dependencies_data[mapped_name] = {
                    'department': department,
                    'file_name': file_name,
                    'path': path
                }
        
        return self._dependencies_data.keys()

    def columns(self):
        return ['Status', 'Dependency']

    def get_dependency_path(self, department, file_name):
        mapped_name = '%s_%s' % (department, file_name.replace('.', '_'))
        path = None
        try:
            dep = self.get_mapped(mapped_name)
        except flow.exceptions.MappedNameError:
            pass
        else:
            path = dep.path.get()

        return path
    
    def get_department(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data[mapped_name]['department']

    def get_file_name(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data[mapped_name]['file_name']

    def get_path(self, mapped_name):
        self.mapped_names()
        return self._dependencies_data[mapped_name]['path']

    def touch(self):
        self._dependencies_data = None
        super(CompSceneDependencies, self).touch()
    
    def _get_dependencies(self):
        deps = [
            (('misc', 'background.psd'), False, {}),
            (('misc', 'animatic.mp4'), False, {}),
            (('misc', 'video_ref.mp4'), True, {}),
            ([
                ('misc', 'audio.wav'),
                ('misc', 'audio'),
            ], False, {}),
            (('clean', 'layers'), False, {'Reception_clean': 'OMIT'}),
        ]
        return [self._get_dependency_data(d) for d in deps]

    def _get_dependency_data(self, dependency):
        path = None
        target, optional, ignore_statutes = dependency
        department = file_name = None

        if type(target) is tuple:
            department, file_name = target
            path = self._get_target_path(department, file_name)
        elif type(target) is list:
            # Get the first existing dependency
            for d, f in target:
                department, file_name = d, f
                path = self._get_target_path(department, file_name)
                if path is not None:
                    break
        
        if not optional:
            kitsu = self.root().project().kitsu_api()

            for task, status in ignore_statutes.items():
                if kitsu.get_shot_task_status_name(self._sequence.name(), self._shot.name(), task) == status:
                    optional = True
                    break
        
        return department, file_name, path, optional

    def _get_target_path(self, department, file_name):
        file_name = file_name.replace('.', '_')
        oid = f'{self._shot.oid()}/tasks/{department}/files/{file_name}'
        path = None

        try:
            f = self.root().get_object(oid)
        except (ValueError, flow.exceptions.MappedNameError):
            pass
        else:
            r = f.get_head_revision()
            if r is not None and r.exists():
                path = r.get_path().replace('\\', '/')

        return path

    def _fill_row_cells(self, row, item):
        row['Status'] = ''
        row['Dependency'] = '%s/%s' % (
            item.department.get() or 'undefined',
            item.file_name.get() or 'undefined'
        )

    def _fill_row_style(self, style, item, row):
        if item.path.get() is None:
            style['Status_icon'] = ('icons.gui', 'warning')
        else:
            style['Status_icon'] = ('icons.gui', 'available')
        
        style['Dependency_icon'] = FILE_ICONS.get(
            item.extension(), ('icons.gui', 'folder-white-shape')
        )


class InitCompScene(GenericRunAction):

    ICON = ('icons.libreflow', 'afterfx')

    DEFAULT_KITSU_STATUTES = [
        {'task': 'Reception', 'status': 'Done'},
        {'task': 'Reception_clean', 'status': 'Done', 'ignore_statutes': ['OMIT']}
    ]

    dependencies = flow.Child(CompSceneDependencies).ui(expanded=True)
    layer_groups_regex    = flow.Param('(.*)_(col|color|line)$').ui(hidden=True)
    target_sg_status      = flow.DictParam(dict(task='Comp', status='rs')).ui(hidden=True)
    target_kitsu_statutes = flow.Param(DEFAULT_KITSU_STATUTES).ui(hidden=True) # [{task -> str, status -> str, ignore_statutes -> list}]

    _shot     = flow.Parent(3)
    _sequence = flow.Parent(5)
    _film     = flow.Parent(7)

    def __init__(self, parent, name):
        super(InitCompScene, self).__init__(parent, name)
        self._comp_scene_path = None

    def runner_name_and_tags(self):
        return 'AfterEffects', []

    @classmethod
    def supported_extensions(cls):
        return ['aep']

    def target_file_extension(self):
        return 'aep'

    def needs_dialog(self):
        return True

    def get_buttons(self):
        file_map = self._shot.tasks.compositing.files
        msg = '<h2>Initialise compositing shot</h2>'

        if file_map.has_file('compositing', 'aep'):
            f = file_map['compositing_aep']
            if f.has_working_copy(from_current_user=True):
                msg += '<h3><font color=#D5000D>You already have a working copy on this shot. \
                        Initialising it will overwrite your changes.</font></h3>'
        
        sg = self.root().project().get_shotgrid_config()
        duration = sg.get_shot_duration(self._shot.shotgrid_id.get())

        if duration is None:
            msg += '<h3><font color=#D5000D> The duration of this site is undefined. \
                    This scene will be created with a duration of 1 frame.</font></h3>'
        
        self.message.set(msg)

        return ['Initialise', 'Cancel']

    def extra_argv(self):
        script_path = resources.get('scripts.aftereffects', 'init_comp_scene.jsx').replace('\\', '/')
        width, height = 4096, 1743
        
        sg = self.root().project().get_shotgrid_config()
        duration = sg.get_shot_duration(self._shot.shotgrid_id.get()) or 1
        comp_name = f'{self._film.name()}_{self._sequence.name()}_{self._shot.name()}'

        # Build AfterEffects JSX script

        # We need to use single quoted strings in the script
        # https://docs.python.org/3/library/subprocess.html#converting-an-argument-sequence-to-a-string-on-windows
        script_str = f"//@include '{script_path}'\n\nsetupScene('{self._comp_scene_path}', '{comp_name}', {width}, {height}, {duration})\n"

        labels_and_paths = self._get_layers_labels_and_paths()
        animatic_path = self._get_animatic_path()
        video_ref_path = self._get_video_ref_path()
        audio_paths = self._get_audio_paths()
        background_path = self._get_background_path()

        if labels_and_paths is not None:
            script_str += f"importLayers({str(labels_and_paths[0])}, {str(labels_and_paths[1])}, {width}, {height}, {duration}, '{comp_name}');\n"
        if background_path is not None:
            script_str += f"importBackground('{background_path}', {width}, {height}, {duration}, '{comp_name}');\n"
        if animatic_path is not None:
            script_str += f"importAnimatic('{animatic_path}', '{comp_name}');\n"
        if video_ref_path is not None:
            script_str += f"importVideoRef('{video_ref_path}', '{comp_name}');\n"
        for audio_path in audio_paths:
            script_str += f"importAudio('{audio_path}', '{comp_name}');\n"
        
        script_str += "saveScene();\n"
        args = ['-s', script_str, '-noui']

        return args

    def run(self, button):
        if button == 'Cancel':
            return
        
        comp_scene = self._ensure_comp_scene()

        # Initialise compositing scene working copy
        wc = comp_scene.create_working_copy()
        comp_scene.set_current_user_on_revision(wc.name())
        self._comp_scene_path = wc.get_path().replace('\\', '/')

        ret = super(InitCompScene, self).run(button)
        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(ret['runner_id'])
        print(f'Init compositing :: Initialising shot {self._film.name()}_{self._sequence.name()}_{self._shot.name()}...')

        while runner_info['is_running']:
            time.sleep(1)
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(ret['runner_id'])
        
        print(f'Init compositing :: Shot {self._film.name()}_{self._sequence.name()}_{self._shot.name()} initialised !')
        
        # Create a revision
        comp_scene.publish(comment='Initialised with scene builder', keep_editing=True)

        # Update ShotGrid status
        target_status = self.target_sg_status.get()
        sg = self.root().project().get_shotgrid_config()
        sg.set_shot_task_status(self._shot.shotgrid_id.get(), target_status['task'], target_status['status'])

        # Update Kitsu statutes
        kitsu = self.root().project().kitsu_api()
        for target_status in self.target_kitsu_statutes.get():
            current_status = kitsu.get_shot_task_status_name(self._sequence.name(), self._shot.name(), target_status['task'])
            
            if current_status not in target_status.get('ignore_statutes', []):
                kitsu.set_shot_task_status(self._sequence.name(), self._shot.name(), target_status['task'], target_status['status'])

        return ret

    def _ensure_comp_scene(self):
        file_map = self._shot.tasks.compositing.files

        if file_map.has_file('compositing', 'aep'):
            aep_file = file_map['compositing_aep']
        else:
            aep_file = file_map.add_file('compositing', 'aep', tracked=True)
        
        return aep_file

    def _get_layers_labels_and_paths(self):
        layers_path = self.dependencies.get_dependency_path('clean', 'layers')
        labels_and_paths = None

        if layers_path is not None:
            i = 0
            regex = self.layer_groups_regex.get()
            paths = defaultdict(list)

            for layers_dir in os.listdir(layers_path):
                m = re.match(regex, layers_dir)
                if m is not None:
                    layers_label = m.group(1)
                else:
                    layers_label = f'layers_{i:04}'
                    i += 1
                
                paths[layers_label].append(
                    os.path.join(layers_path, layers_dir).replace('\\', '/')
                )
            
            labels_and_paths = list(paths.keys()), list(paths.values())
        
        return labels_and_paths

    def _get_background_path(self):
        return self.dependencies.get_dependency_path('misc', 'background.psd')

    def _get_animatic_path(self):
        return self.dependencies.get_dependency_path('misc', 'animatic.mp4')

    def _get_video_ref_path(self):
        return self.dependencies.get_dependency_path('misc', 'video_ref.mp4')

    def _get_audio_paths(self):
        audio_path = self.dependencies.get_dependency_path('misc', 'audio.wav')
        
        if audio_path is not None:
            return [audio_path]
        
        audio_folder = self.dependencies.get_dependency_path('misc', 'audio')
        paths = []

        if audio_folder is not None:
            paths = [
                os.path.join(audio_folder, name).replace('\\', '/')
                for name in glob.glob(f'{audio_folder}/*.wav')
            ]
        
        return sorted(paths)
