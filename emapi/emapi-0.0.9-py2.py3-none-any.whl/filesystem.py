from typing import Tuple, List
from types import ModuleType
from pathlib import Path
from importlib import import_module


def module_from_path(path: Path) -> Tuple[ModuleType, str, List[str]]:
	if path.is_absolute():
		path = path.relative_to(Path.cwd())
	*pkg, module_name = path.parts
	module_name = module_name.replace(".py", "")
	pkg_path = ".".join(pkg)
	module = import_module(f"{pkg_path}.{module_name}", package=pkg_path)
	return module, module_name, pkg
