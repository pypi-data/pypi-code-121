from unittest import TestCase
from unittest.mock import patch

from citibox.profiling import ErrorStartingProfiling
from citibox.profiling import ProfilerServiceGoogle, GoogleConfig, Config


@patch('googlecloudprofiler.start')
class TestProfilerServiceGoogle(TestCase):

    def setUp(self) -> None:
        self.config: GoogleConfig = GoogleConfig(
            service_name='test_service', service_version='0.1.0', project_id='test_project_id')
        self.profiler_service: ProfilerServiceGoogle = ProfilerServiceGoogle(config=self.config)

    def test_constructor_happy(self, mock_google_start):
        profiler_service: ProfilerServiceGoogle = ProfilerServiceGoogle(config=self.config)
        self.assertIsInstance(profiler_service._config, GoogleConfig)

    def test_constructor_base_config(self, mock_google_start):
        config = Config(service_name='test', service_version='0.0.1')
        with self.assertRaises(AssertionError) as context:
            profiler_service: ProfilerServiceGoogle = ProfilerServiceGoogle(config=config)

    def test_start_happy(self, mock_google_start):
        self.profiler_service.start()

        mock_google_start.assert_called_with(
                service=self.config.service_name,
                verbose=self.config.verbose,
                service_version=self.config.service_version,
                project_id=self.config.project_id,
                service_account_json_file=None)

        self.assertTrue(self.profiler_service._started)

    def test_start_with_value_error(self, mock_google_start):
        mock_google_start.side_effect = ValueError()

        with self.assertRaises(ErrorStartingProfiling) as context:
            self.profiler_service.start()

        self.assertFalse(self.profiler_service._started)

    def test_start_with_not_implemented_error(self, mock_google_start):
        mock_google_start.side_effect = NotImplementedError()

        with self.assertRaises(ErrorStartingProfiling) as context:
            self.profiler_service.start()

        self.assertFalse(self.profiler_service._started)

    def test_start_with_not_know_error(self, mock_google_start):
        mock_google_start.side_effect = Exception()

        with self.assertRaises(Exception) as context:
            self.profiler_service.start()

        self.assertFalse(self.profiler_service._started)
