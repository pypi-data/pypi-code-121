import os
import shutil
from datetime import datetime
from kabaret import flow


MAX_DELIVERY_COUNT = 1e3


class _SafeDict(dict):
    '''
    From https://stackoverflow.com/a/17215533
    '''
    def __missing__(self, key):
        return '{' + key + '}'


class AddPresetAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    label       = flow.SessionParam('')
    file_name   = flow.SessionParam('')
    department  = flow.SessionParam('')
    relative_path = flow.SessionParam('')
    optional    = flow.SessionParam().ui(editor='bool')

    _map = flow.Parent()

    def get_buttons(self):
        return ('Add', 'Cancel')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        p = self._map.add(f'p{len(self._map):04}')
        p.label.set(self.label.get())
        p.file_name.set(self.file_name.get())
        p.relative_path.set(self.relative_path.get() or None)
        p.department.set(self.department.get())
        p.optional.set(self.optional.get())
        self._map.touch()


class RemovePresetAction(flow.Action):

    ICON = ('icons.gui', 'remove-symbol')

    _item = flow.Parent()
    _map  = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def run(self, button):
        map = self._map
        map.remove(self._item.name())
        map.touch()


class ExportFilePreset(flow.Object):

    label      = flow.Param()
    department = flow.Param()
    file_name  = flow.Param()
    relative_path = flow.Param()
    optional   = flow.BoolParam()

    remove     = flow.Child(RemovePresetAction)

    _film      = flow.Parent(4)

    def find_revision(self, sequence_name, shot_name):
        file_name = self.file_name.get().replace('.', '_')
        file_oid = f'{self._film.oid()}/sequences/{sequence_name}/shots/{shot_name}/tasks/{self.department.get()}/files/{file_name}'
        revision_data = {
            'oid': None,
            'path': None,
            'site': None,
        }
        status = 'not_found'

        try:
            f = self.root().get_object(file_oid)
        except (ValueError, flow.exceptions.MappedNameError):
            pass
        else:
            r = f.get_head_revision()

            if r is not None:
                revision_data['oid'] = r.oid()
                revision_data['path'] = r.get_path()
                revision_data['site'] = r.site.get()

                if r.get_sync_status() != 'Available':
                    if r.get_sync_status(exchange=True) == 'Available':
                        status = 'needs_dl'
                    elif r.get_sync_status() == 'Requested':
                        status = 'requested'
                    else:
                        status = 'needs_sync'
                else:
                    status = 'available'

        revision_data['status'] = status
        
        return revision_data


class ExportFilePresets(flow.Map):

    add_preset = flow.Child(AddPresetAction)

    _action = flow.Parent(2)

    @classmethod
    def mapped_type(cls):
        return ExportFilePreset

    def touch(self):
        self._action._shots_data = None
        super(ExportFilePresets, self).touch()


class ExportSettings(flow.Object):

    file_presets = flow.Child(ExportFilePresets)
    shot_filter  = flow.DictParam({})


class RequestFilesAction(flow.Action):
    """
    Export files of shots filtered by their Kitsu statutes.
    """

    ICON = ('icons.gui', 'share-symbol')

    settings = flow.Child(ExportSettings)

    _film        = flow.Parent()

    def __init__(self, parent, name):
        super(RequestFilesAction, self).__init__(parent, name)
        self._shots_data = None

    def file_names_and_labels(self):
        """
        Returns the names of the files to export
        """
        return [
            (p.name(), p.label.get())
            for p in self.settings.file_presets.mapped_items()
        ]
    
    def shot_ids(self, force_update=False):
        return list(self.shots_data(force_update).keys())

    def shots_data(self, force_update=False):
        """
        Returns a dict describing the shot files to export.

        The returned dict has the following layout:
        {
            <shot_id>: {
                sequence_name,
                shot_name,
                files: {
                    <preset_id>: {
                        label: <label>,
                        file_name: <file_name>,
                        revision: <revision>,
                        optional: <optional>
                    }
                },
                status,
                selected
            }
        }
        """
        if self._shots_data is None or force_update:
            self._shots_data = self._compute_shots_data()
        
        return self._shots_data
    
    def shot_data(self, id):
        return self.shots_data()[id]

    def request_shot_files(self):
        s = self.root().project().get_current_site()
        target_folder = s.export_target_dir.get()
        shots = self.shots_data().copy()

        for shot in shots.values():
            if not shot['selected'] or shot['status'] == 'missing_files':
                continue
            
            shot_target_folder = os.path.join(
                target_folder,
                f"TS_{shot['sequence_name']}_{shot['shot_name']}"
            )
            if os.path.exists(shot_target_folder):
                shutil.rmtree(shot_target_folder)

            for preset_name, file_data in shot['files'].copy().items():
                self._process_file(shot['sequence_name'], shot['shot_name'], preset_name, file_data, shot_target_folder)

            if shot['status'] == 'needs_dl':
                self.remove_shot(shot)
            else:
                self._update_shot_status(shot['sequence_name'], shot['shot_name'])

    def remove_shot(self, shot):
        self.shots_data()
        self._shots_data.pop(f"{shot['sequence_name']}_{shot['shot_name']}")

    def _update_file(self, sequence_name, shot_name, preset_name, file_data):
        self.shots_data()
        self._shots_data[f'{sequence_name}_{shot_name}']['files'][preset_name] = file_data

    def _compute_shots_data(self):
        shots_data = {}
        shot_filter = self.settings.shot_filter.get() or None
        kitsu = self.root().project().kitsu_api()

        kitsu_shots = sorted(kitsu.get_shots(shot_filter))

        for sequence_name, shot_name in kitsu_shots:
            files = self._find_shot_files(sequence_name, shot_name)
            status = self._get_shot_status(files)

            if status == 'available':
                # Skip shots whose mandatory files are already available
                continue

            shots_data[f'{sequence_name}_{shot_name}'] = {
                'name': f'TS_{sequence_name}_{shot_name}',
                'sequence_name': sequence_name,
                'shot_name': shot_name,
                'files': files,
                'status': status,
                'selected': False,
            }
        
        return shots_data

    def update_selected(self, shot_id, selected):
        self._shots_data[shot_id]['selected'] = selected

    def _get_shot_status(self, files):
        status = 'available'
        needs_dl = False # At least one file not available on site
        needs_sync = False # At least one file not available on server
        requested = False # At least one file already requested
        missing_files = False # At least one file not existing

        for file_data in files.values():
            if not file_data['optional'] and file_data['status'] == 'not_found':
                missing_files = True
                break
            elif file_data['status'] == 'needs_dl':
                needs_dl = True
            elif file_data['status'] == 'needs_sync':
                needs_sync = True
            elif file_data['status'] == 'requested':
                requested = True
        
        if missing_files:
            status = 'missing_files'
        elif needs_sync:
            status = 'needs_sync'
        elif needs_dl:
            status = 'needs_dl'
        elif requested:
            status = 'requested'
        
        return status

    def _find_shot_files(self, sequence_name, shot_name):
        sources = {}

        for preset in self.settings.file_presets.mapped_items():
            revision_data = preset.find_revision(sequence_name, shot_name)
            sources[preset.name()] = {
                'label': preset.label.get(),
                'name': preset.file_name.get(),
                'revision_oid': revision_data['oid'],
                'revision_path': revision_data['path'],
                'status': revision_data['status'],
                'source_site': revision_data['site'],
                'relative_path': preset.relative_path.get(),
                'optional': preset.optional.get()
            }
        
        return sources

    def _process_file(self, sequence_name, shot_name, preset_name, file_data, target_folder):
        synced = self._sync_file(sequence_name, shot_name, preset_name, file_data)

        if synced:
            self._copy_file(file_data['revision_path'], target_folder, file_data['relative_path'])

    def _sync_file(self, sequence_name, shot_name, preset_name, file_data):
        status = file_data['status']

        if status == 'not_found':
            return False

        current_site = self.root().project().get_current_site()
        user_name = self.root().project().get_user_name()
        oid = file_data['revision_oid']
        path = file_data['revision_path']

        if status == 'needs_sync':
            print(f"Export :: Request {oid}")

            site_name = file_data['source_site']
            source_site = self.root().project().get_working_sites()[site_name]

            # Ask source site for upload
            source_site.get_queue().submit_job(
                job_type='Upload',
                init_status='WAITING',
                emitter_oid=oid,
                user=user_name,
                studio=source_site.name(),
            )
            r = self.root().get_object(oid)
            r.set_sync_status('Requested')
            self._update_file_status(sequence_name, shot_name, preset_name, 'requested')
            
            return False
        else:
            print(f"Export :: Download {oid}")

            # Download revision
            job = current_site.get_queue().submit_job(
                job_type='Download',
                init_status='WAITING',
                emitter_oid=oid,
                user=self.root().project().get_user_name(),
                studio=current_site.name(),
            )
            self.root().project().get_sync_manager().process(job)
        
        return True

    def _update_shot_status(self, sequence_name, shot_name):
        self.shots_data()
        shot_key = f'{sequence_name}_{shot_name}'
        files = self._shots_data[shot_key]['files']
        status = self._get_shot_status(files)
        self._shots_data[shot_key]['status'] = status

    def _update_file_status(self, sequence_name, shot_name, preset_name, status):
        self.shots_data()
        self._shots_data[f'{sequence_name}_{shot_name}']['files'][preset_name]['status'] = status

    def _copy_file(self, src_path, target_folder, rel_path=None):
        dst_path = target_folder
        if rel_path is not None:
            dst_path = os.path.join(dst_path, rel_path)

        print(f"Export :: Copy {src_path} -> {dst_path}")

        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            if rel_path is None:
                dst_path = os.path.join(target_folder, os.path.basename(src_path))
            if os.path.exists(dst_path):
                os.remove(dst_path)
            
            shutil.copy2(src_path, dst_path)

    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.pianoplayer.ui.export.ExportFilesWidget'
