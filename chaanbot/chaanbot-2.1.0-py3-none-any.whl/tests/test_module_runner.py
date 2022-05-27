import time
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from chaanbot.module_runner import ModuleRunner


class TestModuleRunner(IsolatedAsyncioTestCase):

    def test_loads_modules_on_init(self):
        config = Mock()
        matrix = AsyncMock()

        modules = ["modules"]
        module_loader = Mock()
        module_loader.load_modules.return_value = modules
        module_runner = ModuleRunner(config, matrix, module_loader)
        self.assertEqual(modules, module_runner.loaded_modules)

    async def test_runs_loaded_modules(self):
        module1 = AsyncMock()
        module1.run.return_value = False
        module2 = AsyncMock()
        module2.run.return_value = False

        modules = [module1, module2]

        await self._run_module_loader(modules)

        module1.run.assert_called_once()
        module2.run.assert_called_once()

    async def test_always_run_modules_with_always_run_True(self):
        module1 = AsyncMock()
        module1.always_run = None
        module1.run.return_value = True
        module2 = AsyncMock()
        module2.always_run = True
        module2.run.return_value = False

        modules = [module1, module2]

        await self._run_module_loader(modules)

        module1.run.assert_called_once()
        module2.run.assert_called_once()

    async def test_does_not_run_if_event_too_old(self):
        module1 = AsyncMock()
        module1.run.return_value = False
        module2 = AsyncMock()
        module2.run.return_value = False

        modules = [module1, module2]

        event = Mock()
        event.server_timestamp = (time.time() - ModuleRunner.MAX_AGE_OF_EVENT_TO_BE_NEW_SECONDS - 1) * 1000
        await self._run_module_loader_with_event(modules, event)

        module1.run.assert_not_called()
        module2.run.assert_not_called()

    async def _run_module_loader(self, modules):
        module_loader = Mock()
        module_loader.load_modules.return_value = modules
        event = Mock()
        event.server_timestamp = time.time() * 1000
        await self._run_module_loader_with_event(modules, event)

    async def _run_module_loader_with_event(self, modules, event):
        config = Mock()
        matrix = AsyncMock()

        module_loader = Mock()
        module_loader.load_modules.return_value = modules
        module_runner = ModuleRunner(config, matrix, module_loader)
        room = AsyncMock()
        message = Mock()
        await module_runner.run(event, room, message)
