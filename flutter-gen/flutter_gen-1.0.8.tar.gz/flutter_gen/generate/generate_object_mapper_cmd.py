# coding=utf-8

import glob
import re
from ..core.command import Command
from jinja2 import Environment, PackageLoader
from ..utils.file_helpers import *
from ..utils.utils import *
from flutter_gen.utils.print import *
from flutter_gen.utils.dart_helpers import format_dart_file_code
from sys import platform


class GenerateObjectMapperCommand(Command):
    def __init__(self):
        super(GenerateObjectMapperCommand, self).__init__()

    def run(self):
        pi = PrintInfo(name="generate object mapper")
        pi.start()
        import_files = []
        classes = []
        regex_mappable = re.compile(
            r"class (.*) (?:with Mappable|extends BaseAPIOutput|extends APIOutput)")
        regex_class = re.compile(r"class(?:.*){([\s\S]*?\n)}")
        for path in glob.glob('lib/**/*.dart', recursive=True):
            # Code gen
            with open(path, "r+", encoding="utf8") as f:
                content = f.read()
                for class_name in regex_mappable.findall(content):
                    import_files.append(path)
                    classes.append(class_name)
                    if "lib/data/api" not in path:
                        if "toString" not in content:
                            for match in regex_class.findall(content):
                                # content = content.replace(
                                #     match, match)
                                # f.seek(0)
                                # f.write(content)
                                # f.truncate()
                                # f.close()
                                # format_dart_file_code(path)
                                print()
        classes = list(dict.fromkeys(classes))
        import_files = list(dict.fromkeys(import_files))
        if not classes:
            print_error("Can't find any mapper file")
            return
        package_name = get_current_dart_package_name()
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
        template = env.get_template("entities.dart")
        content = template.render(
            import_files=import_files,
            classes=classes
        )
        output_file = create_file(
            content, "entities", "g.dart", "lib/generated")
        pi.end()
