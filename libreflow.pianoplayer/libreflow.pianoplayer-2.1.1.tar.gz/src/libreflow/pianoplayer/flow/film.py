import os
import re
import fileseq
from collections import defaultdict
from kabaret import flow
from kabaret.flow_entities.entities import Entity, Property
from libreflow.utils.kabaret.flow_entities.entities import EntityView
from libreflow.baseflow.maputils import SimpleCreateAction
from libreflow.baseflow.film import Film as BaseFilm
from libreflow.baseflow.shot import Sequence as BaseSequence, Shot as BaseShot, ShotCollection
from libreflow.baseflow.task import TaskCollection
from libreflow.baseflow.file import CreateDefaultFilesAction, GenericRunAction
from libreflow.baseflow.users import ToggleBookmarkAction

from .packaging import PackAction, CreateLayoutPackagesAction, CreateCleanPackagesAction
from .unpacking import UnpackCleanPackagesAction, UnpackLayoutPackagesAction
from .export import RequestFilesAction
from .compositing import InitCompScene
from .shotgrid import ShotGridEntity

from libreflow.resources.icons import libreflow as _, applications as _
from ..resources.icons import gui as _


MAX_DELIVERY_COUNT = 1e3


class CreateDepartmentDefaultFilesAction(CreateDefaultFilesAction):

    _department = flow.Parent()

    def get_target_groups(self):
        return [self._department.name()]

    def get_file_map(self):
        return self._department.files


class AbstractRVOption(GenericRunAction):
    """
    Abstract run action which instantiate an RV runner,
    with its default version.
    """
    def runner_name_and_tags(self):
        return 'RV', []
    
    def get_version(self, button):
        return None


class CompareWithAnimaticAction(AbstractRVOption):
    """
    Compares a shot compositing preview with its animatic,
    if both files.
    """
    ICON = ('icons.libreflow', 'compare-previews')

    _comp_preview_path  = flow.Computed(cached=True)
    _animatic_path = flow.Computed(cached=True)

    _shot = flow.Parent()

    def needs_dialog(self):
        self._comp_preview_path.touch()
        self._animatic_path.touch()

        return (
            self._comp_preview_path.get() is None
            or self._animatic_path.get() is None
        )
    
    def get_buttons(self):
        if self._comp_preview_path.get() is None:
            self.message.set('<h2>This shot has no compositing preview.</h2>')
        elif self._animatic_path.get() is None:
            self.message.set('<h2>This shot has no animatic.</h2>')
        
        return ['Close']

    def compute_child_value(self, child_value):
        if child_value is self._animatic_path:
            self._animatic_path.set(
                self._get_last_revision_path('misc', 'animatic.mp4')
            )
        elif child_value is self._comp_preview_path:
            self._comp_preview_path.set(
                self._get_last_revision_path('compositing', 'compositing_movie.mov')
            )
    
    def extra_argv(self):
        return [
            '-wipe', '-autoRetime', '0',
            self._comp_preview_path.get(),
            self._animatic_path.get()
        ]

    def run(self, button):
        if button == 'Close':
            return
        else:
            super(CompareWithAnimaticAction, self).run(button)

    def _get_last_revision_path(self, task_name, file_name):
        path = None

        if self._shot.tasks.has_mapped_name(task_name):
            task = self._shot.tasks[task_name]
            name, ext = file_name.rsplit('.', 1)

            if task.files.has_file(name, ext):
                f = task.files[f'{name}_{ext}']
                r = f.get_head_revision()

                if r is not None:
                    path = r.get_path()

        return path


class OpenAnimationLayers(AbstractRVOption):
    """
    Opens a shot's set of animation layers.
    """
    ICON = ('icons.gui', 'anim-layers')

    _layers_paths = flow.Computed(cached=True)

    _shot = flow.Parent()

    def needs_dialog(self):
        self._layers_paths.touch()
        return not bool(self._layers_paths.get())
    
    def get_buttons(self):
        if not self._layers_paths.get():
            self.message.set('<h2>This shot has no animation layers.</h2>')
        
        return ['Close']

    def extra_argv(self):
        paths = []
        for col_path, line_path in self._layers_paths.get():
            if line_path is not None:
                paths.append(line_path)
            if col_path is not None:
                paths.append(col_path)
        
        return ['-bg', 'checker', '-over'] + paths

    def compute_child_value(self, child_value):
        if child_value is self._layers_paths:
            self._layers_paths.set(self._get_layers_paths())
    
    def run(self, button):
        if button == 'Close':
            return
        else:
            super(OpenAnimationLayers, self).run(button)
    
    def _get_layers_paths(self):
        paths = {}

        if self._shot.tasks.has_mapped_name('clean'):
            clean = self._shot.tasks['clean']

            if clean.files.has_folder('layers'):
                f = clean.files['layers']
                r = f.get_head_revision()

                if r is not None:
                    layers_folder = r.get_path()

                    paths = defaultdict(lambda: [None, None])
                    for dir_name in os.listdir(layers_folder):
                        dir_path = os.path.join(layers_folder, dir_name)
                        m = re.match('(.*)_(col|color)$', dir_name, re.IGNORECASE)
                        index = 0
                        if m is None:
                            m = re.match('(.*)_(line)$', dir_name, re.IGNORECASE)
                            index = 1
                            if m is None:
                                continue
                        
                        sequences = fileseq.findSequencesOnDisk(dir_path)
                        if sequences:
                            seq_format = sequences[0].format(template='{basename}{padding}{extension}')
                            paths[m.group(1)][index] = os.path.join(dir_path, seq_format)

        return sorted(paths.values())


class Shot(BaseShot, ShotGridEntity):

    tasks = flow.Child(TaskCollection).ui(expanded=True)

    compare_comp_antc = flow.Child(CompareWithAnimaticAction).ui(
        label='Compare with animatic'
    )
    open_anim_layers  = flow.Child(OpenAnimationLayers).ui(
        label='Open animation layers'
    )

    def ensure_tasks(self):
        """
        Creates the tasks of this shot based on the task
        templates of the project, skipping any existing task.
        """
        mgr = self.root().project().get_task_manager()

        for dt in mgr.default_tasks.mapped_items():
            if not self.tasks.has_mapped_name(dt.name()) and not dt.optional.get():
                t = self.tasks.add(dt.name())
                t.enabled.set(dt.enabled.get())
        
        self.tasks.touch()


class Shots(ShotCollection):

    def add(self, name, object_type=None):
        """
        Adds a shot to the global shot collection, and creates
        its tasks.
        """
        s = super(Shots, self).add(name, object_type)
        s.ensure_tasks()


class CreateSGShots(flow.Action):

    ICON = ('icons.flow', 'shotgrid')

    skip_existing = flow.SessionParam(False).ui(editor='bool')

    _sequence = flow.Parent()

    def get_buttons(self):
        return ['Create shots', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        skip_existing = self.skip_existing.get()
        shots_data = self.root().project().get_shotgrid_config().get_shots_data(
            self._sequence.shotgrid_id.get()
        )
        for data in shots_data:
            name = data['name'].lower()

            if not self._sequence.shots.has_mapped_name(name):
                s = self._sequence.shots.add(name)
            elif not skip_existing:
                s = self._sequence.shots[name]
            else:
                continue
            
            print(f'Create shot {self._sequence.name()} {data["name"]}')
            s.shotgrid_id.set(data['shotgrid_id'])
        
        self._sequence.shots.touch()


class Sequence(BaseSequence, ShotGridEntity):

    shots = flow.Child(Shots).ui(expanded=True)

    with flow.group('ShotGrid'):
        create_shots = flow.Child(CreateSGShots)


class CreateSGSequences(flow.Action):

    ICON = ('icons.flow', 'shotgrid')

    skip_existing = flow.SessionParam(False).ui(editor='bool')
    create_shots = flow.SessionParam(False).ui(editor='bool')

    _film = flow.Parent()

    def get_buttons(self):
        return ['Create sequences', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        sequences_data = self.root().project().get_shotgrid_config().get_sequences_data()
        create_shots = self.create_shots.get()
        skip_existing = self.skip_existing.get()

        for data in sequences_data:
            name = data['name'].lower()

            if not self._film.sequences.has_mapped_name(name):
                s = self._film.sequences.add(name)
            elif not skip_existing:
                s = self._film.sequences[name]
            else:
                continue
            
            print(f'Create sequence {data["name"]}')
            s.shotgrid_id.set(data['shotgrid_id'])

            if create_shots:
                s.create_shots.skip_existing.set(skip_existing)
                s.create_shots.run('Create shots')
        
        self._film.sequences.touch()


class PackageTypeChoiceValue(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'
    CHOICES = ['Layout', 'Clean']

    _action = flow.Parent()

    def choices(self):
        return self.CHOICES
    
    def revert_to_default(self):
        values = self.root().project().get_action_value_store().get_action_values(
            self._action.name(), {self.name(): self.get()}
        )
        value = values[self.name()]

        if value in self.choices():
            self.set(value)


class CreatePackagesAction(flow.Action):

    ICON = ('icons.gui', 'package')

    package_type = flow.SessionParam('Layout', PackageTypeChoiceValue)

    _film = flow.Parent()

    def get_buttons(self):
        self.package_type.revert_to_default()
        return ['Select', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        if self.package_type.get() == 'Layout':
            ret = self.get_result(
                next_action=self._film.create_layout_packages.oid()
            )
        else:
            ret = self.get_result(
                next_action=self._film.create_clean_packages.oid()
            )
        
        return ret


class UnpackPackagesAction(flow.Action):

    ICON = ('icons.gui', 'package')

    package_type = flow.SessionParam('Layout', PackageTypeChoiceValue)

    _film = flow.Parent()

    def get_buttons(self):
        self.package_type.revert_to_default()
        return ['Select', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        if self.package_type.get() == 'Layout':
            ret = self.get_result(
                next_action=self._film.unpack_layout_packages.oid()
            )
        else:
            ret = self.get_result(
                next_action=self._film.unpack_clean_packages.oid()
            )
        
        return ret


class RequestAnimLayersAction(RequestFilesAction):

    ICON = ('icons.gui', 'anim-layers')


class Film(BaseFilm):

    with flow.group('Packages'):
        create_packages        = flow.Child(CreatePackagesAction).ui(label='Create')
        create_layout_packages = flow.Child(CreateLayoutPackagesAction)
        create_clean_packages  = flow.Child(CreateCleanPackagesAction)
        unpack_packages        = flow.Child(UnpackPackagesAction).ui(label='Unpack')
        unpack_layout_packages = flow.Child(UnpackLayoutPackagesAction)
        unpack_clean_packages  = flow.Child(UnpackCleanPackagesAction)
    with flow.group('Request'):
        request_layers         = flow.Child(RequestAnimLayersAction).ui(label='Layers')
    with flow.group('ShotGrid'):
        create_sequences       = flow.Child(CreateSGSequences)
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(film=self.name())

    def _fill_ui(self, ui):
        if self.root().project().show_login_page():
            ui['custom_page'] = 'libreflow.baseflow.LoginPageWidget'
