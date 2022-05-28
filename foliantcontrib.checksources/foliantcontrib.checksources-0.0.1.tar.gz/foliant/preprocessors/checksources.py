"""
Preprocessor for Foliant documentation authoring tool.

Check chapters for untracked and missing files
"""
import os

from foliant.preprocessors.utils.preprocessor_ext import BasePreprocessorExt


class Preprocessor(BasePreprocessorExt):
    defaults = {
        'not_in_chapters': [],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('checksources')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')
        self.src_dir = self.project_path / self.config['src_dir']

    def apply(self):
        self.logger.info('Applying preprocessor')
        self.logger.debug(f'Not warn for files: {self.options["not_in_chapters"]}')

        def _recursive_process_chapters(chapters_subset):
            if isinstance(chapters_subset, dict):
                new_chapters_subset = {}
                for key, value in chapters_subset.items():
                    new_chapters_subset[key] = _recursive_process_chapters(value)

            elif isinstance(chapters_subset, list):
                new_chapters_subset = []
                for item in chapters_subset:
                    new_chapters_subset.append(_recursive_process_chapters(item))

            elif isinstance(chapters_subset, str):
                if chapters_subset.endswith('.md'):
                    chapter_file_path = (self.src_dir / chapters_subset).resolve()
                    if os.path.exists(chapter_file_path):
                        self.logger.debug(f'Adding file to the list of mentioned in chapters: {chapter_file_path}')
                    else:
                        self.logger.debug('Not exist, throw warning')
                        self._warning(f'{os.path.relpath(chapter_file_path)} does not exist')

                    chapters_files_paths.append(chapter_file_path)

                new_chapters_subset = chapters_subset

            else:
                new_chapters_subset = chapters_subset

            return new_chapters_subset

        chapters_files_paths = []

        _recursive_process_chapters(self.config.get('chapters', []))

        self.logger.debug(f'List of files mentioned in chapters: {chapters_files_paths}')

        def _fill_not_in_chapters():

            for not_in_chapters in self.options['not_in_chapters']:
                not_in_chapters_paths.append((self.src_dir / not_in_chapters).resolve())

        not_in_chapters_paths = []

        _fill_not_in_chapters()

        self.logger.debug(f'List of files mentioned in not_in_chapters: {not_in_chapters_paths}')

        for markdown_file_path in self.src_dir.rglob('*.md'):
            markdown_file_path = markdown_file_path.resolve()

            self.logger.debug(f'Checking if the file is mentioned in chapters: {markdown_file_path}')

            if markdown_file_path in chapters_files_paths or markdown_file_path in not_in_chapters_paths:
                self.logger.debug('Mentioned, keeping')

            else:
                self.logger.debug('Not mentioned, throw warning')
                self._warning(f'{os.path.relpath(markdown_file_path)} does not mentioned in chapters')

        self.logger.info('Preprocessor applied')
