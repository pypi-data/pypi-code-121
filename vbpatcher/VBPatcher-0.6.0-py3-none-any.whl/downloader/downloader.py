import msvcrt as m
import os
import sys
from os import PathLike
from urllib.error import HTTPError
from zipfile import ZipFile

import requests
import tqdm
import VBPatcher.appglobals.appglobals
from requests import Response
from VBPatcher.applogger.applogger import logger


class _Downloader:
    """Wrapper containing patch-file update functionality.

	- Class Methods:
		- :func:`dl_stable(self, url) -> BufferedWriter`
			- Download latest BepInEx stable release.

		- :func:`dl_dev(self, url) -> BufferedWriter`
			- Download latest BepInEx development build.

		- :func:`unzip_patch(self, filename, stable) -> None`
			- Unzip downloaded patch files before deleting patch `.zip` archive.

		- :func:`UpdatePatcher(self) -> None`
			- Process to retrieve latest available patch files using class methods.
	"""

    def _dl_stable(self, url):
        """Download zip containing latest BepInEx stable release.

		---

		:param url: URL from which to download zip archive.
		:type url: :class:`str`
		:return: zip archive containing patch files.
		:rtype: :class:`BufferedWriter`
		"""

        logger.info('Downloading latest BepInEx stable release...')

        try:
            rq: Response = requests.get(url, allow_redirects=True, stream=True)
            rq.raise_for_status()  # Check for HTTP errors

            file_size: int = int(rq.headers.get('Content-Length'))
            chunk_size: int = 1024  # 1 MB
            num_bars: int = file_size // chunk_size

            with open(
              f'./patch-files/stable/BepInEx_stable_{VBPatcher.appglobals.appglobals.b_stable}.zip',
              'wb') as patch_stable:
                for chunk in tqdm.tqdm(rq.iter_content(chunk_size=chunk_size),
                        total=num_bars,
                        unit='KB',
                        desc='Downloading Stable Release',
                        file=sys.stdout):
                    patch_stable.write(chunk)

            logger.info(
             f'Completed BepInEx latest stable-release download!\n>> Downloaded from url:\n>> {url}\n'
            )
            print(
             f'\nCompleted BepInEx latest stable-release download!\n>> Downloaded from url:\n>> {url}\n'
            )
            return patch_stable

        except [Exception, HTTPError] as err:
            logger.error(
             f'Encountered error while downloading latest stable release zip archive...\n>> Exception:\n{err}\n'
            )
            print(
             f'Encountered error while downloading latest stable release zip archive...\n>> Exception:\n{err}\n'
            )

    def _dl_dev(self, url):
        """Download zip archive containing latest BepInEx development build.

		---

		:param url: URL from which to download zip archive.
		:type url: :class:`str`
		:return: zip archive containing patch files.
		:rtype: :class:`BufferedWriter`
		"""
        logger.info('Downloading latest BepInEx development-build...')

        try:
            rq: Response = requests.get(url, allow_redirects=True, stream=True)
            rq.raise_for_status()  # Check for HTTP errors

            file_size: int = int(rq.headers.get('Content-Length'))
            chunk_size: int = 1024  # 1 MB
            num_bars: int = file_size // chunk_size

            with open(
              f'./patch-files/development/BepInEx_dev_{VBPatcher.appglobals.appglobals.b_dev}.zip',
              'wb') as patch_dev:
                for chunk in tqdm.tqdm(rq.iter_content(chunk_size=chunk_size),
                        total=num_bars,
                        unit='KB',
                        desc='Downloading Dev-Build',
                        file=sys.stdout):
                    patch_dev.write(chunk)

                logger.info(
                 f'Completed BepInEx latest development-build download!\n>> Downloaded from url:\n>> {url}\n'
                )
                print(
                 f'\nCompleted BepInEx latest development-build download!\n>> Downloaded from url:\n>> {url}\n'
                )
            return patch_dev

        except [Exception, HTTPError] as err:
            logger.error(
             f'Encountered error while downloading latest development-build zip archive...\n>> Exception:\n{err}\n'
            )
            print(
             f'Encountered error while downloading latest development-build zip archive...\n>> Exception:\n{err}'
            )

    def _unzip_patch(self, filename: PathLike | str, mode: int) -> None:
        """Unzip downloaded patch files and cleanup leftover files.

		---

		:param filename: filename of zip archive.
		:type filename: :class:`str` | :class:`PathLike`
		:param mode: set to 1 to unzip stable release archive, or 2 to unzip dev-build archive.
		:type stable: :class:`bool`
		:return: downloaded/extracted patch files.
		:rtype: None
		"""
        logger.info('Unzipping patch files...')
        print('Unzipping patch files...')

        try:
            if mode == 1:  # Unzip stable-release patch files
                with ZipFile(filename) as archive:
                    archive.extractall(path='./patch-files/stable')
                # Remove unnecessary files
                os.unlink('./patch-files/stable/doorstop_config.ini')
                os.unlink(f'./patch-files/stable/BepInEx_stable_{VBPatcher.appglobals.appglobals.b_stable}.zip')
            elif mode == 2: # Unzip dev-build patch files
                with ZipFile(filename) as archive:
                    archive.extractall(path='./patch-files/development')
                # Remove unnecessary files
                os.unlink('./patch-files/development/doorstop_config.ini')
                os.unlink(f'./patch-files/development/BepInEx_dev_{VBPatcher.appglobals.appglobals.b_dev}.zip')

            logger.info(
             'Successfully unzipped archive!\n>> Deleted extra files...\n>> Patch ready for deployment!\n'
            )
            print(
             '\nSuccessfully unzipped archive!\n>> Deleted extra files...\n>> Patch ready for deployment!\n'
            )

        except Exception as err:
            logger.error(
                f'Encountered error while attempting to unzip archive...\n>> Exception: {err}\n'
            )
            print(
                f'\nEncountered error while attempting to unzip archive...\n>> Exception: {err}\n'
            )

    def UpdatePatcher(self) -> None:
        """Retrieve latest available patch files.

		---

		:return: download most recent release/build patch files.
		:rtype: None
		"""
        # Retrieve latest stable release patch files from http://api.github.com/repos/BepInEx/BepInEx/releases/latest
        if self._dl_stable(VBPatcher.appglobals.appglobals.url_stable):
            self._unzip_patch(
             f'./patch-files/stable/BepInEx_stable_{VBPatcher.appglobals.appglobals.b_stable}.zip',
             1)

        # Retrieve development build patch files from https://builds.bepinex.dev/projects/bepinex_be
        if self._dl_dev(VBPatcher.appglobals.appglobals.url_dev):
            self._unzip_patch(
             f'./patch-files/development/BepInEx_dev_{VBPatcher.appglobals.appglobals.b_dev}.zip',
             2)

        print('\n>> Press anything to continue...\n')
        m.getch()  # Wait for user to press any key to continue
