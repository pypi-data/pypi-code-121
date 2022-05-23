# coding=utf-8

import glob
import re
from ..core.command import Command
from jinja2 import Environment, PackageLoader
from ..utils.file_helpers import *
from ..utils.utils import *
from flutter_gen.utils.dart_helpers import format_dart_file_code
from flutter_gen.utils.print import *
from sys import platform


class RouterInfo:
    def __init__(self, class_name, is_include_args, route_name):
        self.class_name = class_name
        self.is_include_args = is_include_args
        self.route_name = route_name

    def __str__(self):
        return f"RouterInfo: {self.class_name} - {self.is_include_args} - {self.route_name}"


class GenerateRouterCommand(Command):
    def __init__(self):
        super(GenerateRouterCommand, self).__init__()

    def run(self):
        pi = PrintInfo(name="generate router")
        pi.start()
        class_name_reg_exp = r"^class (.*)ViewModel(?:.*)=(?:.*)(?:_.*ViewModel)"
        import_files = []
        items = []
        # Find all view model files
        for file in glob.glob("lib/**/*_viewmodel.dart", recursive=True):
            with open(file, "r+", encoding="utf8") as f:
                content = f.read()
                class_name_match = re.findall(
                    class_name_reg_exp, content, re.MULTILINE)
                if class_name_match:
                    class_name = class_name_match[0]
                    if class_name == "App":
                        continue
                    route_name = re.sub(
                        '(?<!^)(?=[A-Z])', '_', class_name).upper()
                    args = class_name + "Args"
                    is_include_args = args in content
                    import_files.append(file)
                    item = RouterInfo(class_name, is_include_args, route_name)
                    items.append(item)

        package_name = get_current_dart_package_name()
        import_files = list(dict.fromkeys(import_files))
        if platform == "darwin":
            import_files = list(map(lambda x: x.replace(
                "lib/", 'package:%s/' % package_name).replace('\\', '/'), import_files))
        else:
            import_files = list(map(lambda x: x.replace(
                "lib\\", 'package:%s/' % package_name).replace('\\', '/'), import_files))

        env = Environment(
            loader=PackageLoader('flutter_gen_templates', 'gen'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template("router.dart")
        content = template.render(
            import_files=import_files,
            package_name=package_name,
            items=items,
        )
        output_file = create_file(
            content, "app_router", "g.dart", "lib/generated")
        format_dart_file_code(output_file)
        pi.end()
