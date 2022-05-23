import os

from kabaret import flow
from libreflow.baseflow.file import TrackedFile
from libreflow.baseflow.runners import CHOICES_ICONS as FILE_ICONS

from ...resources.icons import flow as _


class PackageFilePreset(flow.Object):

    start_oid         = flow.Param('')
    oid_filter        = flow.Param('')
    revision_name     = flow.Param()
    relative_path     = flow.Param()


class PackageFilePresets(flow.Map):

    @classmethod
    def mapped_type(cls):
        return PackageFilePreset
    
    def add_preset(self, start_oid, oid_filter, revision_name=None, relative_path=None):
        name = f'p{len(self):03}'
        p = self.add(name)
        p.start_oid.set(start_oid)
        p.oid_filter.set(oid_filter)
        p.revision_name.set(revision_name)
        p.relative_path.set(relative_path.replace('\\', '/') if relative_path else None)
    
    def columns(self):
        return ['Start OID', 'OID filter', 'Revision', 'Relative path']
    
    def _fill_row_cells(self, row, item):
        row['Start OID'] = item.start_oid.get()
        row['OID filter'] = item.oid_filter.get()
        row['Revision'] = item.revision_name.get()
        row['Relative path'] = item.relative_path.get()


class CreatePackageFilePreset(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    start_oid     = flow.SessionParam('./files')
    oid_filter    = flow.SessionParam('')
    revision      = flow.SessionParam('').ui(
        label='Revision',
        placeholder='Leave empty to pick latest revision',
    )
    relative_path = flow.SessionParam('').ui(
        label='Revision',
        tooltip='File relative path within the package',
        placeholder='Leave empty to pack files without intermediary directories'
    )

    _package = flow.Parent()

    def get_buttons(self):
        return ['Create', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._package.add_file_preset(
            self.start_oid.get(),
            self.oid_filter.get(),
            self.revision.get() or None,
            self.relative_path.get() or None
        )
        self._package.file_presets.touch()


class PackageTemplate(flow.Object):
    
    ICON = ('icons.gui', 'package')

    file_presets = flow.Child(PackageFilePresets)

    create_preset = flow.Child(CreatePackageFilePreset)
    
    def add_file_preset(self, parent_oid, name_filter, revision_name=None, relative_path=None):
        self.file_presets.add_preset(parent_oid, name_filter, revision_name, relative_path)

    def get_default_files(self, relative_to_oid=None):
        files_data = []

        for preset in self.file_presets.mapped_items():
            for f, r in self._list_file_objects(
                preset.start_oid.get(),
                preset.oid_filter.get(),
                preset.revision_name.get(),
                relative_to_oid
            ):
                files_data.append((f, r, preset.relative_path.get()))

        return files_data
    
    def _list_file_objects(self, parent_oid, name_filter, revision_name=None, relative_to_oid=None):
        file_object = None
        revision_object = None
        file_oid = parent_oid + '/' + name_filter

        if relative_to_oid is not None and file_oid.startswith('.'):
            try:
                file_oid = self.root().session().cmds.Flow.resolve_path(
                    relative_to_oid + '/' + file_oid
                )
            except flow.exceptions.MissingRelationError:
                file_oid = None

        if file_oid is not None and self.root().session().cmds.Flow.exists(file_oid):
            o = self.root().get_object(file_oid)

            if isinstance(o, TrackedFile):
                file_object = o

                if revision_name is not None:
                    revision_object = o.get_revision(revision_name)
                else:
                    revision_object = o.get_head_revision()
                
                if revision_object is not None:
                    yield file_object, revision_object


class CreatePackageTemplateAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    package_name = flow.SessionParam('').ui(label='Name')

    _packages = flow.Parent()

    def get_buttons(self):
        return ['Create', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        package = self._packages.add(self.package_name.get())
        self._packages.touch()


class PackageTemplates(flow.Map):

    create_template = flow.Child(CreatePackageTemplateAction).ui(label='Create template')

    @classmethod
    def mapped_type(cls):
        return PackageTemplate
    
    def columns(self):
        return ['Name']
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()


class PackageSettings(flow.Object):

    ICON = ('icons.gui', 'package')

    package_templates = flow.Child(PackageTemplates)

    def get_template(self, name):
        try:
            template = self.package_templates[name]
        except flow.exceptions.MappedNameError:
            template = None
        
        return template
    
    def get_default_files(self, package_template_name, relative_to_oid=None):
        package_template = self.get_template(package_template_name)

        if package_template is None:
            return []
        else:
            return package_template.get_default_files(relative_to_oid)


class RevertSessionValue(flow.Action):

    ICON = ('icons.libreflow', 'refresh')

    _value = flow.Parent()
    _item  = flow.Parent(3)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        self._value.set(self._item.get_default_value(self._value.name()))


class SessionValueWithRevertAction(flow.values.SessionValue):

    revert = flow.Child(RevertSessionValue)


class EditPackageItemAction(flow.Action):

    ICON = ('icons.libreflow', 'edit-blank')

    relative_path = flow.SessionParam(None, SessionValueWithRevertAction)

    _item = flow.Parent()

    def get_buttons(self):
        self.relative_path.set(self._item.relative_path.get())
        return ['Confirm changes', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._item._relative_path.set(self.relative_path.get() or None)
        self._item.touch()


class ToggleItemEnabled(flow.Action):

    _item = flow.Parent()
    _package = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        self._item.enabled.set(
            not self._item.enabled.get()
        )
        self._item.touch()


class PackageItem(flow.Object):

    file_name = flow.Computed()
    source_path = flow.Computed()
    revision_name = flow.Computed()
    relative_path = flow.Computed()
    enabled = flow.SessionParam(True).ui(editor='bool')

    edit = flow.Child(EditPackageItemAction)
    toggle_enable = flow.Child(ToggleItemEnabled)

    _file_name = flow.Param()
    _source_path = flow.Param()
    _revision_name = flow.Param()
    _relative_path = flow.Param()

    _package = flow.Parent()
    
    def pack(self, target_folder):
        path = self.source_path.get()
        relative_path = self.relative_path.get()

        if relative_path is not None:
            target_folder = os.path.join(target_folder, relative_path)
            os.makedirs(target_folder, exist_ok=True)
        
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(
                target_folder, self.file_name.get()
            ))
        else:
            shutil.copy2(self.source_path.get(), target_folder)
    
    def compute_child_value(self, child_value):
        if child_value is self.file_name:
            self.file_name.set(
                self._file_name.get() or self.get_default_value('file_name')
            )
        elif child_value is self.source_path:
            self.source_path.set(
                self._source_path.get() or self.get_default_value('source_path')
            )
        elif child_value is self.revision_name:
            self.revision_name.set(
                self._revision_name.get() or self.get_default_value('revision_name')
            )
        elif child_value is self.relative_path:
            self.relative_path.set(
                self._relative_path.get() or self.get_default_value('relative_path')
            )
    
    def get_default_value(self, value_name):
        return self._package.get_item_data(self.name())[value_name]
    
    def get_icon(self):
        return FILE_ICONS.get(
            os.path.splitext(self.file_name.get())[1][1:],
            ('icons.gui', 'folder-white-shape')
        )


class RefreshPackageContent(flow.Action):

    ICON = ('icons.libreflow', 'refresh')

    _view = flow.Parent()

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        self._view.refresh()


class DropFiles(flow.ConnectAction):

    _package = flow.Parent()

    def run(self, objects, urls):
        for o in objects:
            if isinstance(o, TrackedFile):
                r = o.get_head_revision()
                if r is not None:
                    self._package.add_from_object(o, r)
        for u in urls:
            if u.startswith('file:///'):
                if platform.system() == 'Windows':
                    u = u.replace('file:///', '')
                else:
                    u = u.replace('file://', '')
            
            self._package.add_from_url(u)
        
        self._package.touch()


class PackageView(flow.DynamicMap):

    refresh_action = flow.Child(RefreshPackageContent).ui(label='Refresh')
    drop_files = flow.Child(DropFiles)

    _action = flow.Parent()

    def __init__(self, parent, name):
        super(PackageView, self).__init__(parent, name)
        self._item_names_cache = None
        self._items_cache = None

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(PackageItem)
    
    def columns(self):
        return ['Enabled', 'File', 'Revision']
    
    def mapped_names(self, page_num=0, page_size=None):
        if self._items_cache is None:
            self._item_names_cache = []
            self._items_cache = {}
            
            default_files = self.root().project().admin.packaging.get_default_files(
                self.get_package_template(),
                self.get_start_oid()
            )
            i = 0

            for file, revision, relative_path in default_files:
                self.add_from_object(file, revision, relative_path, f'f{i:03}')
                i += 1
        
        return self._item_names_cache
    
    def refresh(self):
        self._items_cache = None
        self.touch()
    
    def get_package_template(self):
        return self._action.get_package_template()
    
    def get_start_oid(self):
        return self._action.get_start_oid()
    
    def get_item_data(self, name):
        self.mapped_names()
        return self._items_cache[name]
    
    def add_from_object(self, file_object, revision_object, relative_path=None, name=None):
        return self._add_item(
            self._get_data_from_object(file_object, revision_object, relative_path), name
        )
    
    def add_from_url(self, url, relative_path=None, name=None):
        return self._add_item(
            self._get_data_from_url(url, relative_path),name
        )
    
    def _add_item(self, data, name=None):
        self.mapped_names()
        if name is None:
            name = f'f{len(self):03}'
        
        self._item_names_cache.append(name)
        self._items_cache[name] = data

        return self.get_mapped(name)
    
    def _get_data_from_object(self, file_object, revision_object, relative_path):
        return {
            'file_name': file_object.display_name.get(),
            'revision_name': revision_object.name(),
            'source_path': revision_object.get_path().replace('\\', '/'),
            'relative_path': relative_path,
        }
    
    def _get_data_from_url(self, url, relative_path):
        return {
            'file_name': os.path.basename(url),
            'revision_name': None,
            'source_path': url.replace('\\', '/'),
            'relative_path': relative_path,
        }
    
    def _fill_row_cells(self, row, item):
        self.mapped_names()
        path = item.file_name.get()
        relative_path = item.relative_path.get()
        if relative_path is not None:
            path = os.path.join(relative_path, path).replace('\\', '/')
        row['Enabled'] = ''
        row['File'] = path
        row['Revision'] = item.revision_name.get() or 'untracked'

    def _fill_row_style(self, style, item, row):
        self.mapped_names()
        style['icon'] = ('icons.gui', 'check' if item.enabled.get() else 'check-box-empty')
        style['File_icon'] = item.get_icon()
        style['activate_oid'] = item.toggle_enable.oid()
