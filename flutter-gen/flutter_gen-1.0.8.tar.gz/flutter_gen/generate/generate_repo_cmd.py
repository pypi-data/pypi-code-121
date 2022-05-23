# coding=utf-8

import os
from ..core.command import Command
from jinja2 import Environment, PackageLoader
from ..utils.utils import *
from ..utils.str_helpers import snake_to_camel, plural_to_singular
from ..utils.file_helpers import create_file, is_file_path_exist
from flutter_gen.utils.print import *
from ..utils.dart_helpers import *


class RepoItem(object):
    def __init__(self, repo, method):
        self.repo = repo
        self.method = method


class GenerateRepoCommand(Command):
    def __init__(self):
        super(GenerateRepoCommand, self).__init__()

    def run(self):
        pi = PrintInfo(name="generate app repository")
        pi.start()
        import_files = []
        new_methods = []
        repo_classes = []
        for file in glob.glob("lib/**/*_repository.dart", recursive=True):
            with open(file, "r+", encoding="utf8") as f:
                content = f.read()
                class_name = get_dart_class_name(content)
                if "App" in class_name:
                    continue
                for item in get_methods_from_path(file):
                    new_methods.append(RepoItem(class_name, item))
                repo_classes.append(class_name)
                import_for_current_file = "import 'package:{}/{}';".format(
                    get_current_dart_package_name(),
                    file.replace('lib/', ''),
                )
                imports = get_imports_from_string(content)
                import_files.append(import_for_current_file)
                import_files += imports
        # Remove duplicate for new data
        import_files = list(dict.fromkeys(import_files))
        new_methods = list(dict.fromkeys(new_methods))
        env = Environment(
            loader=PackageLoader('flutter_gen_templates', 'gen'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template("repository.dart")
        content = template.render(
            import_files=import_files,
            repo_classes=repo_classes,
            methods=new_methods
        )
        output_file = create_file(
            content, "app_repository", "g.dart", "lib/generated")
        format_dart_file_code(output_file)
        pi.end()
