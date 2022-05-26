from unittest import TestCase, mock

from citibox.profiling import Profiling
from citibox.profiling.config import Config
from citibox.profiling import ProfilerService, AlreadyStarted


class FakeProfilerService(ProfilerService):
    def start(self) -> None:
        super().start()


class TestProfiling(TestCase):

    def setUp(self) -> None:
        self.config: Config = Config(service_name='test_service', service_version='0.1.0')
        self.profiler_service: ProfilerService = FakeProfilerService(config=self.config)
        self.profiling: Profiling = Profiling(profiler_service=self.profiler_service)

    def test_constructor_happy(self):
        profiling = Profiling(profiler_service=self.profiler_service)

        self.assertEqual(profiling._profiler_service, self.profiler_service)

    def test_constructor_empty(self):
        with self.assertRaises(TypeError) as context:
            Profiling()

    def test_constructor_without_profiler_service(self):
        with self.assertRaises(TypeError) as context:
            Profiling(config=self.config)

    def test_start_happy(self):
        profiler_service_mock = mock.MagicMock()
        Profiling(profiler_service=profiler_service_mock).start()
        profiler_service_mock.start.assert_called_once()

    def test_start_twice(self):
        self.profiling.start()

        with self.assertRaises(AlreadyStarted) as context:
            self.profiling.start()
