import os
import re

from pypers.utils.utils import ls_dir
from pypers.utils import utils
from pypers.core.step import FunctionStep
from pypers.steps.base import merge_spec_dict
from pypers.core.interfaces import db
from pypers.core.interfaces.db.cache import clear_cache


class FetchStep(FunctionStep):
    base_spec = {
        "args": {
            "inputs": [],
            "params": [
                {
                    "name": "limit",
                    "type": "int",
                    "descr": "the upper limit of the archives to fetch. "
                             "default 0 (all)",
                    "value": 0
                },
                {
                    "name": "file_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                },
                {
                    "name": "cmd_retry_limit",
                    "type": "int",
                    "descr": "the limit to retry a command until the pipeline "
                             "step fails",
                    "value": 5
                },
                {
                    "name": "http_get_retries",
                    "type": "int",
                    "descr": "the limit to retry an http get until the "
                             "step fails",
                    "value": 7
                },
                {
                    "name": "http_get_delay",
                    "type": "int",
                    "descr": "initial delay between retries in seconds",
                    "value": 4
                },
                {
                    "name": "http_get_backoff",
                    "type": "int",
                    "descr": "backoff multiplier "
                             "e.g. value of 2 will double the delay each retry",
                    "value": 2
                }
            ],
            "outputs": [
                {
                    "name": "output_files",
                    "type": "file",
                    "descr": "the download files from the feed"
                }
            ]
        }
    }

    from_type = None

    def __init__(self, *args, **kwargs):
        merge_spec_dict(self.spec, self.base_spec)
        super(FetchStep, self).__init__(*args, **kwargs)
        self.logger = self.log

    def _get_done_archives(self):
        done_file = db.get_done_file_manager().get_done(self.collection)
        done_file = sorted(done_file, key=lambda i: i['process_date'], reverse=True)
        return [line['archive_name'] for line in done_file]

    def _check_input(self):
        self.fetch_from = self.meta['pipeline']['input']
        if not self.from_type:
            if not self.fetch_from or not self.fetch_from.get('from_dir'):
                raise Exception('Please set the input of the pipeline '
                                '[from_dir]')
        elif not self.fetch_from or not (
                self.fetch_from.get('from_dir') or
                self.fetch_from.get(self.from_type)):
            raise Exception('Please set the input of the pipeline '
                            '[from_dir|%s]' % self.from_type)

    def _process_from_local_folder(self):
        # getting files from local dir
        if self.fetch_from.get('from_dir'):
            self.logger.info(
                'getting %s files that match the regex [%s] from %s' % (
                    'all' if self.limit == 0 else self.limit,
                    self.file_regex,
                    self.fetch_from['from_dir']))
            self.output_files = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_regex, limit=self.limit,
                skip=self.done_archives)
            return True
        return False

    def _send_notification_corrupt_archive(self, raw_corrupted_archives):
        corrupted_archives = []
        for archive in raw_corrupted_archives:
            corrupted_archives.append(archive.replace(self.output_dir, ''))
        db_data = db.get_db().get_run_id_config(self.run_id, self.collection)
        notify_params = db_data.get('pipeline_configuration', {}).get(
            'config', {}).get(
            'steps', {}).get(
            'notify', {})
        recipients = notify_params.get('recipients', [])
        replay_to = notify_params.get('reply_to', None)
        subject = "Corrupted archives for %s %s in WIPO's Global %s Database" % (
            self.collection.upper()[0:2], self.collection.upper()[2:4],
            self.pipeline_type)
        if replay_to:
            recipients.append(replay_to)
            # sending email from localhost
            html = utils.template_render(
                'notify_archive_corrupted.html',
                archives=corrupted_archives)
            utils.send_mail(
                replay_to, recipients, subject, html=html)

        raise Exception("stop")

    def process(self):
        clear_cache(self.meta['pipeline'].get('output_dir', None))
        self.done_archives = self._get_done_archives()
        self._check_input()
        if self._process_from_local_folder():
            return
        self.rgx = re.compile(self.file_regex, re.IGNORECASE)
        self.specific_process()
        # archive validation
        valid_output = []
        invalid_output = []
        for output in self.output_files:
            if not utils.validate_archive(output, self.logger):
                self.logger.error("%s archive is not valid" % output)
                invalid_output.append(output)
            else:
                valid_output.append(output)
        if invalid_output:
            self._send_notification_corrupt_archive(invalid_output)
        self.output_files = valid_output


