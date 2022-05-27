""" The chan save module preserves 4chan media.

Available commands:
None, will trigger on 4chan links by users.

Usage example:
[user]: https://4chan.org/i/1231231.jpg

Would results in:
"Bot: Image saved at [website-url]"
"""
import hashlib
import logging
import os
import re
from typing import List

from nio import RoomMessage, MatrixRoom

from chaanbot.database import Database
from chaanbot.matrix import Matrix

logger = logging.getLogger("chan_save")


class ChanSave:
    url_regexes = [re.compile(r"4chan.org"), re.compile(r"i.4cdn.org", re.IGNORECASE)]
    file_extensions_to_save = ["jpg", "png", "bmp", "gif", "jpeg", "webm", "pdf"]
    always_run = True

    def __init__(self, config, matrix: Matrix, database: Database, requests):
        self.matrix = matrix
        self.requests = requests
        save_dirpath = config.get("chan_save", "save_dirpath", fallback=None)
        url_to_access_saved_files = config.get("chan_save", "url_to_access_saved_files", fallback=None)

        if save_dirpath:
            self.save_dirpath = save_dirpath if save_dirpath.endswith("/") else save_dirpath + "/"
            if not os.access(self.save_dirpath, os.W_OK):
                logger.warning("No write access for save_dirpath: {} Module disabled.".format(self.save_dirpath))
                self.disabled = True
                return
            logger.debug("Will save 4chan media at {}".format(self.save_dirpath))
        else:
            logger.info("No location provided for chan_save, module disabled")
            self.disabled = True
            return

        if url_to_access_saved_files:
            self.url_to_access_saved_files = url_to_access_saved_files if url_to_access_saved_files.endswith(
                "/") else url_to_access_saved_files + "/"
            logger.debug("Saved media will be accessible at {}".format(self.url_to_access_saved_files))

    async def run(self, room: MatrixRoom, event: RoomMessage, message) -> bool:
        links = self._get_links(message)
        for link in links:
            if link and self._should_run(link):
                logger.debug("Should run chan_save, checking if which (if any) file to save")
                file_extension = self._get_file_extension(link)
                if file_extension:
                    filename, filepath = self._get_filename_and_filepath(link, file_extension)
                    if not os.path.exists(filepath):
                        self._save_media(link, filepath)
                        if hasattr(self, "url_to_access_saved_files"):
                            await self.matrix.send_text_to_room(
                                "File saved to {}{} .".format(self.url_to_access_saved_files, filename), room.room_id)
                    else:
                        logger.debug("File from url {} already saved at {}".format(link, filepath))

        return False  # ChanSave does not use commands and should not return that it has handled one

    def _get_links(self, message) -> List[str]:
        http_message = re.sub(r"www\.", message, re.IGNORECASE) \
            if re.match(r"www\.", message, re.IGNORECASE) and not (
                re.match("http:", message, re.IGNORECASE) or re.match("https:", message, re.IGNORECASE)) \
            else message

        links = re.findall(r"http[^(\s)]+", http_message, re.IGNORECASE)  # Match from http to next space to get links
        return links

    def _should_run(self, link) -> bool:
        return not hasattr(self, "disabled") and list(
            filter(lambda regex_url: regex_url.search(link), self.url_regexes))

    def _get_file_extension(self, link):
        for extension in self.file_extensions_to_save:
            if link.lower().endswith(".{}".format(extension.lower())):
                return extension

    def _get_filename_and_filepath(self, link, file_extension) -> (str, str):
        filename = "{}.{}".format(hashlib.sha1(link.encode()).hexdigest(), file_extension)
        filepath = "{}{}".format(self.save_dirpath, filename)
        return filename, filepath

    def _save_media(self, link, filepath):
        request = self.requests.get(link, allow_redirects=True)
        with open(filepath, 'wb') as file:
            file.write(request.content)
