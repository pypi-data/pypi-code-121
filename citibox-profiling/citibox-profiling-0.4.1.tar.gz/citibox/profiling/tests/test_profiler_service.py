from unittest import TestCase

from citibox.profiling import Config
from citibox.profiling import ProfilerService, AlreadyStarted


class FakeProfilerService(ProfilerService):

    def start(self):
        super().start()


class TestProfilerService(TestCase):

    def setUp(self) -> None:
        self.config: Config = Config(service_name='test_service', service_version='0.1.0')
        self.profiler_service = FakeProfilerService(config=self.config)

    def test_constructor_happy(self):
        profiler_service = FakeProfilerService(config=self.config)

        self.assertIsInstance(profiler_service._config, Config)
        self.assertFalse(profiler_service._started)

    def test_initialize_happy(self):
        self.assertIsInstance(self.profiler_service._config, Config)
        self.assertFalse(self.profiler_service._started)

    def test_start_happy(self):
        self.profiler_service.start()
        self.assertTrue(self.profiler_service._started)

    def test_start_twice(self):
        self.profiler_service.start()
        with self.assertRaises(AlreadyStarted) as context:
            self.profiler_service.start()

