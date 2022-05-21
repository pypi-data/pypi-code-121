import importlib.util
import shutil

import questionary as q

from pathlib import Path
from types import ModuleType
from typing import Union, Set, Optional, List, Any, Dict

from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment

from pkm.utils.archives import extract_archive
from pkm.utils.commons import unone
from pkm.utils.files import temp_dir, name_without_ext
from pkm.utils.resources import ResourcePath


class ScaffoldingEngine:

    def __init__(self):
        self._jinja = SandboxedEnvironment(loader=FileSystemLoader("/"))

    # noinspection PyMethodMayBeStatic
    def render_doc(
            self, template_dir: Union[Path, str],
            template_descriptor: Optional[str] = None,
            command_prefix: str = "pkm new") -> str:

        """
        :param template_dir: the directory holding the template
        :param template_descriptor: the descriptor that used to resolve the template directory, if not provided,
                                    the template directory will be considered as the descriptor
        :param command_prefix: the prefix of the commandline that should be used to generate this template
        :return: a generated documentation for this template
        """

        import pkm_cli.scaffold.doc_generator as dg
        return dg.generate(Path(template_dir), template_descriptor, command_prefix)

    def render(self, template_path: Union[Path, str, ResourcePath], target_dir: Union[Path, str],
               args: Optional[List[str]] = None, kwargs: Optional[Dict[str, str]] = None,
               extra_context: Optional[Dict[str, Any]] = None, *,
               excluded_files: Optional[List[Path]] = None, allow_overwrite: bool = False):

        """
        renders the given template into the target directory

        :param template_path: the directory/resource holding the template
        :param target_dir: the directory to output the generated content into
        :param args: positional arguments for the template
        :param kwargs: named arguments for the template
        :param extra_context: extra variables that will be available inside proto.py
        :param excluded_files:  list of path objects that represents files in the template directory that should be
                                excluded from the generation process
        :param allow_overwrite: if True, files that are already exists will be overridden by the template
        """

        if isinstance(template_path, ResourcePath):
            with template_path.use() as path, temp_dir() as tdir:
                extract_archive(path, tdir)

                if (not (tdir / 'scaffold.py').exists()) and \
                        (scaffold_path := tdir / name_without_ext(path) / 'scaffold.py').exists():
                    tdir = scaffold_path.parent

                return self.render(
                    tdir, target_dir, args, kwargs, extra_context, excluded_files=excluded_files,
                    allow_overwrite=allow_overwrite)

        args = unone(args, list)
        kwargs = unone(kwargs, dict)
        extra_context = unone(extra_context, dict)

        template_path = (template_path if isinstance(template_path, Path) else Path(template_path)).absolute()
        target_dir = (target_dir if isinstance(target_dir, Path) else Path(target_dir)).absolute()
        excluded_files = [*(excluded_files or []), template_path / "scaffold.py", template_path / "__pycache__"]

        target_dir.mkdir(exist_ok=True)

        ui = _UserInteractor(args, kwargs)
        module = _load_proto(template_path.joinpath("scaffold.py"), ui,
                             {**extra_context, "args": args, "kwargs": kwargs})

        context = {k: v for k, v in vars(module).items() if not k.startswith("_")}

        ignored_files = set(self._load_ignored_files_list(template_path))
        ignored_files.update(p.absolute() for p in excluded_files)

        if not allow_overwrite:
            self._check_override(template_path, target_dir, context, ignored_files)

        self._render(template_path, target_dir, context, ignored_files)

        if hasattr(module, "post_generation") and callable(module.post_generation):
            module.post_generation()

    def _check_override(self, template_dir: Path, target_dir: Path, context: dict, ignored_files: Set[Path]):

        jinja = self._jinja

        for template_child in template_dir.iterdir():
            if template_child in ignored_files:
                continue

            name = jinja.from_string(template_child.name).render(context)

            if not name:  # empty names indicate unneeded files
                continue

            target_child = (target_dir / name).resolve()

            if not target_child.parent.exists():
                return

            if template_child.is_dir():
                if template_child.exists():
                    self._check_override(template_child, target_child, context, ignored_files)
            else:
                if target_child.suffix == '.tmpl':
                    target_child = target_child.with_suffix('')

                if target_child.exists():
                    raise IOError(f"file already exists: {target_child}")

    def _render(self, template_dir: Path, target_dir: Path, context: dict, ignored_files: Set[Path]):

        jinja = self._jinja

        for template_child in template_dir.iterdir():
            if template_child in ignored_files:
                continue

            name = jinja.from_string(template_child.name).render(context)

            if not name:  # empty names indicate unneeded files
                continue

            target_child = (target_dir / name).resolve()

            if not target_child.parent.exists():
                target_child.parent.mkdir(parents=True)

            if template_child.is_dir():
                if (template_child / ".scaffoldpreserve").exists():
                    shutil.copytree(str(template_child.absolute()), str(target_child.absolute()))
                    return

                target_child.mkdir(exist_ok=True)
                self._render(template_child, target_child, context, ignored_files)
            elif target_child.suffix == ".tmpl":
                with target_child.with_suffix("").open("w") as f:
                    jinja.from_string(template_child.read_text()).stream(context).dump(f)
            else:
                shutil.copy(template_child, target_child)

    def _load_ignored_files_list(self, template_root: Path):
        result = []
        pi_file = template_root.joinpath(".scaffoldignore")

        if pi_file.exists():
            lines = pi_file.read_text().splitlines()
            result = [f.absolute() for line in lines if line.strip() for f in template_root.glob(line)]

        for sub_dir in template_root.iterdir():
            if sub_dir.is_dir():
                result.extend(self._load_ignored_files_list(sub_dir))

        return result


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class _UserInteractor:
    def __init__(self, args: List, kwargs: Dict):
        self._args = args or []
        self._kwargs = kwargs

    def _pre_answered(self, named_arg: str, positional_arg: int) -> Optional[str]:
        if named_arg in self._kwargs:
            return self._kwargs[named_arg]

        if 0 <= positional_arg < len(self._args):
            return self._args[positional_arg]

        return None

    def say(self, msg: str, style: str):
        """
        display a message to the user
        :param msg: the message to display
        :param style: the style to use
        """
        q.print(msg, style)

    def confirm(
            self, named_arg: str, *, prompt: str, doc: str = "", default: bool = True,
            positional_arg: int = -1) -> bool:

        """
        ask the user for yes/no confirmation
        (either retrieving it from the command line or from the user supplied arguments)
        :param named_arg: the name of the argument that may contain the value for this function to return
                          (supports the values y,yes,n,no)
        :param prompt: (optional - defaults to a string generated from named_arg) the prompt to show to the user
        :param default: (optional - defaults to True = 'yes') the default value to suggest the user
        :param positional_arg: (optional - defaults to -1) the index of the positional argument that may contain the
                                value for this function to return
        :param doc: documentation to show in the commandline (must be a string literal)
        :return: True if the user confirmed or False otherwise
        """

        pre_answered = self._pre_answered(named_arg, positional_arg)
        if pre_answered:
            return pre_answered.lower() in ('y', 'yes', 'true')

        r = q.confirm(prompt, default=default).ask()
        return r if isinstance(r, bool) else str(r).lower() in ('y', 'yes')

    def arg(self, named_arg: str, *, doc: str = "", default: str = "", positional_arg=-1):
        """
        fetch a value from the commandline arguments, without asking the user for it if not provided
        :param named_arg: the name of the argument that may contain the value for this function to return
                          (supports the values y,yes,n,no)
        :param doc: documentation to show in the commandline (must be a string literal)
        :param default: (optional - defaults to None) the default value to suggest the user
        :param positional_arg:  (optional - defaults to -1) the index of the positional argument that may contain the
                                value for this function to return
        :return: the requested user value
        """
        pre_answered = self._pre_answered(named_arg, positional_arg)
        return pre_answered if pre_answered is not None else default

    def ask(self, named_arg: str, *, prompt: str = None, default: Any = "", options: Optional[List[str]] = None,
            secret: bool = False, positional_arg: int = -1, autocomplete: bool = False, multiselect: bool = False,
            path: bool = False, doc: str = ""):

        """
        ask the user for information (either retrieving it from the command line or from the user supplied arguments)
        :param named_arg: the name of the argument that may contain the value for this function to return
        :param prompt: (optional - defaults to a string generated from named_arg) the prompt to show to the user
        :param default: (optional - defaults to None) the default value to suggest the user
        :param options: (optional - defaults to None) list of choices to restrict the user input to
        :param secret: (optional - defaults to False) set to True to hide the user input
        :param positional_arg:  (optional - defaults to -1) the index of the positional argument that may contain the
                                value for this function to return
        :param multiselect: if true, multiple options can be selected
        :param autocomplete: if true, options are suggested via auto-complete
        :param path: if true, will require the user to enter a valid path as a result to the prompt
        :param doc: documentation to show in the commandline (must be a string literal)

        :return: the requested user input
        """

        if not prompt:
            prompt = named_arg.replace("_", " ").title()

        pre_answered = self._pre_answered(named_arg, positional_arg)
        if pre_answered:
            return pre_answered

        if options:
            options = list(options)  # ensure we have a list
            default = default or options[0]
            if multiselect:
                return q.checkbox(prompt, choices=options, default=default).ask()
            elif autocomplete:
                return q.autocomplete(prompt, choices=options, default=default).ask()
            else:
                return q.select(prompt, choices=options, default=default).ask()
        else:
            if secret:
                return q.password(prompt, default=default).ask()
            elif path:
                return q.path(prompt, default=default).ask()
            else:
                return q.text(prompt, default=default).ask()

    def install(self, module: ModuleType):
        module.ask = self.ask
        module.confirm = self.confirm
        module.say = self.say
        module.arg = self.arg


def _load_proto(proto_file: Path, ui: "_UserInteractor", context: dict):
    try:
        spec = importlib.util.spec_from_file_location("__PROTO__", proto_file)
        module = importlib.util.module_from_spec(spec)

        ui.install(module)
        for k, v in context.items():
            setattr(module, k, v)

        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise RuntimeError(f"Error while evaluating: {proto_file}") from e
