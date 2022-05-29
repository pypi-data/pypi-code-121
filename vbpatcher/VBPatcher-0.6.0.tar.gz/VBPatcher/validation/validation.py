import os
from zipfile import is_zipfile

import PyLoadBar
import VBPatcher.appglobals.appglobals
import VBPatcher.downloader.downloader
from VBPatcher.applogger.applogger import logger
from VBPatcher.subprocessing.subprocessing import _exitPatcher

DL = VBPatcher.downloader.downloader._Downloader()
bar = PyLoadBar.PyLoadBar()


class _Validate:
    """Validate location and deployability of necessary patch files.

    - Class methods:
        - :func:`_verify_stable(self, url) -> bool`
            - Verify presence of BepInEx stable release patch files.

        - :func:`_verify_dev(self, url) -> bool:`
            - Verify presence of BepInEx dev build patch files.

        - :func:`_start_checks(self) -> None`
            - Verify presence of all BepInEx patch files.
    """

    def _validate_stable(self, url) -> bool:
        """Validate presence of BepInEx stable release patch files.

        ---

        :param url: url to download BepInEx stable release from if not found.
        :type url: :class:`Any`
        :return: validation of patch files.
        :rtype: :class:`bool`
        """
        logger.info(
            f'Validating BepInEx stable-build {VBPatcher.appglobals.appglobals.b_stable} patch...'
        )

        patch_contents: list = [
            ['.gitkeep', 'changelog.txt', 'winhttp.dll'], [],
            [
                '0Harmony.dll', '0Harmony.xml', '0Harmony20.dll',
                'BepInEx.dll', 'BepInEx.Harmony.dll', 'BepInEx.Harmony.xml',
                'BepInEx.Preloader.dll', 'BepInEx.Preloader.xml',
                'BepInEx.xml', 'HarmonyXInterop.dll', 'Mono.Cecil.dll',
                'Mono.Cecil.Mdb.dll', 'Mono.Cecil.Pdb.dll',
                'Mono.Cecil.Rocks.dll', 'MonoMod.RuntimeDetour.dll',
                'MonoMod.RuntimeDetour.xml', 'MonoMod.Utils.dll',
                'MonoMod.Utils.xml'
            ]
        ]

        stable_match: bool = False

        verified: list = []

        try:
            verified.extend(
                file
                for (root, dirs,
                     file) in os.walk('./patch-files/stable', topdown=True))

            if verified == patch_contents:
                stable_match = True
                logger.info(
                    f'BepInEx stable-build {VBPatcher.appglobals.appglobals.b_stable} patch ready for deployment!\n'
                )
            else:
                logger.info(
                    f'Unable to locate BepInEx stable-build {VBPatcher.appglobals.appglobals.b_stable} patch...\n>> Attempting to download...'
                )
                DL._dl_stable(url)  # Download *.zip archive from url
                if is_zipfile(  # Check if downloaded archive is a zip file
                        f'./patch-files/stable/BepInEx_stable_{VBPatcher.appglobals.appglobals.b_stable}.zip'
                ):
                    DL._unzip_patch(  # Unzip archive
                        f'./patch-files/stable/BepInEx_stable_{VBPatcher.appglobals.appglobals.b_stable}.zip',
                        1)
                    stable_match = True
                    logger.info(
                        f'Download successful!\n>> BepInEx stable-build {VBPatcher.appglobals.appglobals.b_stable} patch ready for deployment!\n'
                    )
                else:
                    stable_match = False
                    logger.error(
                        'Download failed!\n>> BepInEx dev-build patch unable to be deployed!\n'
                    )

        except Exception as err:
            stable_match = False
            logger.error(
                f'Encountered error during BepInEx stable-build {VBPatcher.appglobals.appglobals.b_stable} patch validation...\n>> Exception:\n{err}\n'
            )
        finally:
            return stable_match

    def _validate_dev(self, url) -> bool:
        """Validate presence of BepInEx development build patch files.

        ---

        :param url: url to download BepInEx development build from if not found.
        :type url: :class:`PathLike` | :class:`str`
        :return: validation of patch files.
        :rtype: :class:`bool`
        """
        logger.info(
            f'Validating BepInEx dev-build {VBPatcher.appglobals.appglobals.b_dev} patch...'
        )

        patch_contents: list = [
            ['.gitkeep', 'changelog.txt', 'winhttp.dll'], [],
            [
                '0Harmony.dll', 'BepInEx.Core.dll', 'BepInEx.Core.xml',
                'BepInEx.Preloader.Core.dll', 'BepInEx.Preloader.Core.xml',
                'BepInEx.Preloader.Unity.dll', 'BepInEx.Preloader.Unity.xml',
                'BepInEx.Unity.dll', 'BepInEx.Unity.xml', 'Mono.Cecil.dll',
                'Mono.Cecil.Mdb.dll', 'Mono.Cecil.Pdb.dll',
                'Mono.Cecil.Rocks.dll', 'MonoMod.RuntimeDetour.dll',
                'MonoMod.Utils.dll', 'SemanticVersioning.dll'
            ]
        ]

        dev_match: bool = False

        verified: list = []

        try:
            verified.extend(file for (
                root, dirs,
                file) in os.walk('./patch-files/development/', topdown=True))

            if verified == patch_contents:
                dev_match = True
                logger.info(
                    f'BepInEx dev-build {VBPatcher.appglobals.appglobals.b_dev} patch ready for deployment!\n'
                )

            else:
                logger.info(
                    f'Unable to locate BepInEx dev-build {VBPatcher.appglobals.appglobals.b_dev} patch...\n>> Attempting to download...'
                )
                DL._dl_dev(url)  # Download *.zip file from url
                if is_zipfile(  # Check if downloaded archive is a zip file
                        f'./patch-files/development/BepInEx_dev_{VBPatcher.appglobals.appglobals.b_dev}.zip'
                ):
                    DL._unzip_patch(  # Unzip archive
                        f'./patch-files/development/BepInEx_dev_{VBPatcher.appglobals.appglobals.b_dev}.zip',
                        2)

                    dev_match = True
                    logger.info(
                        f'Download successful!\n>> BepInEx dev-build {VBPatcher.appglobals.appglobals.b_dev} patch ready for deployment!\n'
                    )

                else:
                    dev_match = False
                    logger.error(
                        'Download failed!\n>> BepInEx dev-build patch unable to be deployed!\n'
                    )

        except Exception as err:
            dev_match = False
            logger.error(
                f'Encountered error during BepInEx dev-build {VBPatcher.appglobals.appglobals.b_dev} patch validation...\n>> Exception:\n{err}\n'
            )
        finally:
            return dev_match

    def _start_checks(self) -> None:
        """Verify necessary patcher components upon start.

        - If any patch files are missing, attempt to download them.

        ---

        :return: continue to application if verification is successful, otherwise exits program.
        :rtype: None
        """
        logger.info('Initializing VBPatcher start checks...\n')
        print('Initializing VBPatcher start checks...\n')

        if self._validate_stable(VBPatcher.appglobals.appglobals.url_stable
                                 ) and self._validate_dev(
                                     VBPatcher.appglobals.appglobals.url_dev):
            logger.info('VBPatcher start checks completed successfully!\n')
            print('VBPatcher start checks completed successfully!\n')
        else:
            logger.error(
                'VBPatcher start checks failed!\n>> One or more patch files were not able to be verified...\n'
            )
            bar.load(
                'ERROR: One or more patch files were not able to be verified and cannot be deployed...\nCheck log for more details',
                'Exiting Patcher',
                enable_display=False)
            return _exitPatcher()
