from unittest import TestCase
from unittest.mock import Mock, patch

from chaanbot.module_loader import ModuleLoader


class TestModuleLoader(TestCase):
    def setUp(self):
        database = Mock()
        requests = Mock()
        config = Mock()
        config.get.return_value = None
        self.module_loader = ModuleLoader(config, database, requests)

    def test_load_enabled_and_disabled_config(self):
        database = Mock()
        requests = Mock()
        config = Mock()
        config.get.side_effect = self._get_config_side_effect_with_module1_disabled_and_module2_enabled
        module_loader = ModuleLoader(config, database, requests)
        self.assertEqual("module1", module_loader.disabled_modules[0])
        self.assertEqual("module2", module_loader.enabled_modules[0])

    def test_load_modules(self):
        files = ["module.py"]
        loaded_modules, import_module, isdir, listdir = self.mock_and_load_modules(files, self.module_loader)

        self.assertEqual(1, len(loaded_modules))
        listdir.assert_called_once()
        isdir.assert_called_once()
        import_module.assert_called_once()

    def test_load_subdirectory_modules(self):
        files = ["subdirectory"]
        subdirectory_files = ["module.py"]
        with patch("pkg_resources.resource_listdir") as listdir:
            with patch("pkg_resources.isdir") as isdir:
                with patch("importlib.import_module") as import_module:
                    listdir.side_effect = [files, subdirectory_files]
                    isdir.return_value = True
                    module_mock = Mock()
                    module_class = Mock()
                    module_mock.Module = module_class
                    import_module.return_value = module_class

                    config = Mock()
                    matrix = Mock()

                    loaded_modules = self.module_loader.load_modules(config, matrix)

        self.assertEqual(1, len(loaded_modules))
        listdir.assert_called()
        self.assertEqual(2, listdir.call_count)
        isdir.assert_called_once()
        import_module.assert_called_once()

    def test_dont_load_modules_with_wrong_filetype(self):
        files = ["module.pyc"]
        loaded_modules, import_module, isdir, listdir = self.mock_and_load_modules(files, self.module_loader)

        self.assertFalse(loaded_modules)
        listdir.assert_called_once()
        isdir.assert_called_once()
        import_module.assert_not_called()

    def test_dont_load_disabled_modules(self):
        database = Mock()
        requests = Mock()
        config = Mock()
        config.get.side_effect = self._get_config_side_effect_with_module_disabled
        module_loader = ModuleLoader(config, database, requests)

        files = ["module.py", "module2.py"]
        loaded_modules, import_module, isdir, listdir = self.mock_and_load_modules(files, module_loader)

        self.assertEqual(1, len(loaded_modules))
        listdir.assert_called_once()
        isdir.assert_called()
        import_module.assert_called_once()

    def test_only_load_enabled_modules(self):
        database = Mock()
        requests = Mock()
        config = Mock()
        config.get.side_effect = self._get_config_side_effect_with_module1_disabled_and_module2_enabled
        module_loader = ModuleLoader(config, database, requests)

        files = ["module.py", "module2.py", "module3.py"]
        loaded_modules, import_module, isdir, listdir = self.mock_and_load_modules(files, module_loader)

        self.assertEqual(1, len(loaded_modules))
        listdir.assert_called_once()
        isdir.assert_called()
        import_module.assert_called_once()

    @staticmethod
    def mock_and_load_modules(files, module_loader):
        with patch("pkg_resources.resource_listdir") as listdir:
            with patch("pkg_resources.isdir") as isdir:
                with patch("importlib.import_module") as import_module:
                    listdir.return_value = files
                    isdir.return_value = False
                    module_mock = Mock()
                    module_class = Mock()
                    module_mock.Module = module_class
                    import_module.return_value = module_class

                    config = Mock()
                    matrix = Mock()

                    loaded_modules = module_loader.load_modules(config, matrix)
        return loaded_modules, import_module, isdir, listdir

    def _get_config_side_effect_with_module1_disabled_and_module2_enabled(*args, **kwargs):
        if args[1] == "modules":
            if args[2] == "disabled":
                return "module1"
            elif args[2] == "enabled":
                return "module2"
        return None

    def _get_config_side_effect_with_module_disabled(*args, **kwargs):
        if args[1] == "modules":
            if args[2] == "disabled":
                return "module"
        return None
