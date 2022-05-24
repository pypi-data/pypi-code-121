#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Internationalization"""

import logging
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Text, Union

import yaml
from yaml.representer import Representer
from skill_sdk.i18n import PROGRAM, PROGRAM_NOT_FOUND, get_locale_dir

logger = logging.getLogger(__name__)


def extract_translations(
    modules: List[Text], locale_dir: Text = None
) -> Optional[Path]:
    """
    Extract translatable strings from Python modules and write translations to `messages.pot`

    :param modules: List of Python modules to scan
    :param locale_dir:
    :return:
    """
    command = "extract"
    path = get_locale_dir(locale_dir)
    if not path.exists():
        path.mkdir(parents=True)

    output = path / "messages.pot"
    try:
        result = subprocess.check_output(
            [
                PROGRAM,
                command,
                f"--input-dirs={','.join(modules)}",
                f"--output={str(output)}",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
        logger.debug(result)

        logger.info("Translation template written to %s", repr(output))
        return output

    except FileNotFoundError:
        logger.error(PROGRAM_NOT_FOUND, command)

    except subprocess.CalledProcessError as ex:
        logger.error("Failed to extract translations: %s", repr(ex.stdout))

    return None


def init_locales(
    template: Path, locales: List[Text], locale_dir: Text = None, force: bool = False
) -> bool:
    """
    Create empty .po file in locale_dir

    :param template:    Template (.pot) file to create translation
    :param locales:     List of translations to initialize, eg. ['en', 'de', 'fr']
    :param locale_dir:  Locale folder
    :param force:       If `True`, try to unlink the [locale].po file first

    :return:            `True` if all locales have been initialized, `False` if error occurred
    """
    command = "init"
    for locale in locales:
        output = get_locale_dir(locale_dir) / f"{locale}.po"

        logger.info("Creating %s ...", repr(output))
        try:
            if output.exists() and force:
                output.unlink()

            subprocess.check_call(
                [
                    PROGRAM,
                    command,
                    f"--locale={locale}",
                    f"--input-file={template}",
                    f"--output-file={str(output)}",
                ]
            )

        except FileNotFoundError:
            logger.error(PROGRAM_NOT_FOUND, command)
            return False

        except subprocess.CalledProcessError as ex:
            logger.error("Failed to create %s: %s", repr(output), repr(ex))
            return False

    return True


def _translate(lines: Iterator, messages: Dict[Text, Union[Text, List[Text]]]) -> List:
    """
    Update lines from .po file with translated messages dict

    :param lines:
    :param messages:
    :return:
    """
    translated = []
    for line in lines:
        if line.strip().startswith("msgid"):
            translated.append(line)
            msgid = line.strip().split(" ")[-1].strip("'\"")
            msgstr = messages.get(msgid)
            if isinstance(msgstr, (list, tuple)):
                msgstr = next(iter(msgstr), None)
            if isinstance(msgstr, str):
                msgstr = msgstr.replace('"', '\\"')  # Escape double quotes
                msgstr = msgstr.strip()  # Strip blanks and new lines
                msgstr = msgstr.replace("\n", '"\n"')  # Add quotes to new lines
            try:
                line = f'msgstr "{msgstr}"' if msgstr else next(lines)
                next(lines)
            except StopIteration:
                pass
        translated.append(line)
    return translated


def translate_locale(
    locale: Text, messages: Dict[Text, Union[Text, List[Text]]], locale_dir: Text = None
) -> Optional[List]:
    """
    Read data from .po file and update it with translated messages

    :param locale:
    :param messages:
    :param locale_dir:
    :return:
    """
    po_file = get_locale_dir(locale_dir) / f"{locale}.po"
    try:
        logger.info("Translating %s ...", po_file.name)
        with po_file.open() as f:
            lines = iter(f.readlines())
            return _translate(lines, messages)
    except (AttributeError, KeyError, FileNotFoundError) as ex:
        logger.error("Failed to translate %s: %s", po_file.name, repr(ex))
        return None


def update_translation(
    locale: Text, messages: Dict[Text, Union[Text, List[Text]]], locale_dir: Text = None
) -> Optional[Path]:
    """
    Update .po file with translated messages

    :param locale:
    :param messages:
    :param locale_dir:
    :return:
    """
    po_file = get_locale_dir(locale_dir) / f"{locale}.po"
    translated = translate_locale(locale, messages, locale_dir)
    if translated:
        with po_file.open("w+") as f:
            logger.info("Updating %s ...", po_file.name)
            f.writelines(translated)
            return po_file
    else:
        logger.info("Nothing to translate in %s", po_file.name)
        return None


def _download_full_catalog(
    download_url: Text, scope: Text, token: Text = None, tenant: Text = None
) -> Dict:
    """
    Download a complete translation catalog from text service

    :param download_url:
    :param token:
    :param tenant:
    :return:
    """

    from skill_sdk.services.text import TextService

    logger.info(f"Downloading translations from {download_url}...")

    headers = {"X-Application-Authentication": f"Bearer {token}"} if token else {}
    headers.update({"X-Tenant": tenant}) if tenant else None

    service = TextService(download_url, scope, headers=headers, add_auth_header=False)
    return service.admin_get_full_catalog()


def download_translations(
    download_url: Text,
    scope: Text,
    token: Text = None,
    tenant: Text = None,
    force: bool = False,
):
    """
    Load translations from text service and save to locale/{language}.yaml

    :param download_url:    Text services URL to download translations
    :param scope:           Translation catalogue scope (skill name)
    :param token:           Bearer authentication token (X-Application-Authentication)
    :param tenant:          Tenant for authentication   (X-Tenant)
    :param force:           Overwrite existing translations if exist
    :return:
    """

    catalog = _download_full_catalog(download_url, scope, token, tenant)

    if catalog:

        yaml.add_representer(defaultdict, Representer.represent_dict)
        for locale in catalog:
            yaml_file = (get_locale_dir() / locale).with_suffix(".yaml")
            if yaml_file.exists() and not force:
                logger.error(
                    '"%s exists and no "--force" specified. Skipping...', yaml_file
                )
            else:
                logger.info("Saving %s to %s", repr(locale), yaml_file)
                with yaml_file.open("w+") as f:
                    yaml.dump(catalog[locale], f, allow_unicode=True)
