import logging

import math
from unittest import TestCase

from dnastack import CollectionServiceClient
from dnastack.configuration.models import ServiceEndpoint
from dnastack.feature_flags import in_global_debug_mode
from dnastack.common.environments import flag
from dnastack.common.logger import get_logger

try:
    import psutil
    _psutil_installed = True
except ImportError:
    _psutil_installed = False


class TestStress(TestCase):
    _logger = get_logger('lib/stress_test', logging.DEBUG if in_global_debug_mode else logging.INFO)
    _proc_info = psutil.Process() if _psutil_installed else None

    def setUp(self) -> None:
        if not flag('E2E_STRESS_TEST_ENABLED'):
            self.skipTest('Disabled. Set E2E_STRESS_TEST_ENABLED=true to enable.')

        if not _psutil_installed:
            self.fail('psutil is required for this test.')

    def test_issue_180415300(self):
        """Tracker Issue #180415300

        Expected: Query should take a long time, with millions of rows in the results.

        Actual: Query finishes surprisingly quickly, with about 13K results.

        .. note:: This test is specifically designed for a certain deployment.
        """
        client = CollectionServiceClient.make(ServiceEndpoint(adapter_type='collections',
                                                              url='https://explorer.beta.dnastack.com/api/',
                                                              mode='explorer'))

        sub_client = client.data_connect('sars-cov-2-ncbi-sequence-read-archive')

        initial_memory_usage = self._get_current_memory_usage()

        # Attempt to iterate through 1.5M rows without keeping any row.
        row_count = 0
        for row in sub_client.query('SELECT * FROM publisher_data.ncbi_sra.variants LIMIT 1500000'):
            row_count += 1
            if row_count % 100000 == 0:
                current_memory_usage = self._get_current_memory_usage()
                self._logger.debug(f'Receiving {row_count} rows (mem diff: {self._format_readable_byte_size(current_memory_usage - initial_memory_usage)})...')
            self.assertGreater(len(row.keys()), 0)
        self._logger.info(f'Received {row_count} rows (mem diff: {self._format_readable_byte_size(self._get_current_memory_usage() - initial_memory_usage)})...')
        self.assertGreaterEqual(1500000, row_count)

    def _get_current_memory_usage(self):
        return self._proc_info.memory_info().rss

    def _format_readable_byte_size(self, size: float) -> str:
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        normalized_size = size

        while math.ceil(normalized_size / 1024) > 1:
            normalized_size = normalized_size / 1024
            unit_index += 1

        return f'{normalized_size:.2f}{units[unit_index]}'
