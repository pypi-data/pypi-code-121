from pathlib import Path

import nbformat
from jupyter_server.services.contents.largefilemanager import LargeFileManager
from tornado.web import HTTPError

from .config import get_storage_for_notebook
from .parsing import decompose_notebook, recompose_notebook


class NewpyterContentsManager(LargeFileManager):
    """
    Contents manager that can handle `newpyter` notebooks.
    Aside from representing newpyter notebooks as text (and back),
    they are responsible for conversion and listing/editing/renamings of files
    """

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.log.info(f'Newpyter activated')

    def get(self, path, content=True, type=None, format=None):
        if path.endswith('.newpy') and type in (None, 'notebook'):
            try:
                return self._newpy_notebook_model(path, content=content)
            except BaseException as e:
                raise HTTPError(500, f'Could not load notebook: \n{e}')
        else:
            return LargeFileManager.get(self, path=path, content=content, type=type, format=format)

    def _newpy_notebook_model(self, path, content=True):
        """Build a notebook model

        if content is requested, the notebook content will be populated
        as a JSON structure (not double-serialized)
        """
        model = self._base_model(path)
        model['type'] = 'notebook'
        os_path = self._get_os_path(path)

        if content:
            with open(os_path, encoding='utf-8') as f:
                nb = recompose_notebook(f.read(), notebook_path=os_path)

            # just mark all cells as trusted
            self.notary.mark_cells(nb, trusted=True)
            model['content'] = nb
            model['format'] = 'json'
            self.validate_notebook_model(model)
        return model

    def save(self, model, path=""):
        """Save the file model and return the model with no content."""
        if not (path.endswith('.newpy') and model['type'] == 'notebook'):
            return LargeFileManager.save(self, model=model, path=path)

        try:
            os_path = self._get_os_path(path)

            self.log.debug("Saving newpyter notebook %s", os_path)

            decomposed = decompose_notebook(
                notebook=nbformat.from_dict(model['content']),
                storage=get_storage_for_notebook(notebook_filename=Path(os_path)),
            )

            with self.atomic_writing(os_path, encoding='utf-8') as f:
                f.write(decomposed)

            model = self.get(path, content=False)
            # ignore post hooks for newpyter notebooks
            # self.run_post_save_hook(model=model, os_path=os_path)
            return model

        except Exception as e:
            self.log.error(u"Error while saving file: %s %s", path, e, exc_info=True)
            raise HTTPError(500, u"Unexpected error while saving file: %s %s" % (path, e))

    def rename_file(self, old_path, new_path) -> None:
        self.log.error(f'Move called: {old_path} {new_path}')

        if Path(old_path).suffix == '.newpy' and Path(new_path).suffix == '.ipynb':
            return self.convert_from_newpy_to_ipynb_or_reverse(old_path, new_path)

        if Path(new_path).suffix == '.newpy' and Path(old_path).suffix == '.ipynb':
            return self.convert_from_newpy_to_ipynb_or_reverse(old_path, new_path)

        return super().rename_file(old_path, new_path)

    def convert_from_newpy_to_ipynb_or_reverse(self, old_path, new_path) -> None:
        self.log.info(f'Conversion from {old_path} to {new_path}')
        if Path(self._get_os_path(new_path)).exists():
            raise HTTPError(409, u'File already exists: %s' % new_path)
        if not Path(self._get_os_path(old_path)).exists():
            raise HTTPError(404, u'File does not exist: %s' % old_path)

        model = self.get(old_path)
        self.save(model, path=new_path)
        self.delete(old_path)
