from typing import List
from pathlib import Path
from inspect import getmembers, isclass

from .tortoise import EmapiDbModel
from .filesystem import module_from_path


def read_app_models(rel_to: str = "app.") -> List[str]:
	app_models = []
	models_path = Path.cwd() / "app" / "models"
	for path in models_path.rglob("*.py"):
		module, module_name, pkg_path = module_from_path(path)
		models = list(getmembers(module, lambda obj: isclass(obj) and issubclass(obj, EmapiDbModel)))
		if models:
			app_models.append(f"{rel_to}{'.'.join(pkg_path[1:])}.{module_name}")
	return app_models
