import os
import shutil
import string

from importlib import import_module
from os.path import join, dirname, abspath, exists, splitext

import scrapy
from scrapy.commands import ScrapyCommand
from scrapy.utils.template import render_templatefile, string_camelcase
from scrapy.exceptions import UsageError


def sanitize_module_name(module_name):
    """Sanitize the given module name, by replacing dashes and points
    with underscores and prefixing it with a letter if it doesn't start
    with one
    """
    module_name = module_name.replace('-', '_').replace('.', '_')
    if module_name[0] not in string.ascii_letters:
        module_name = "a" + module_name
    return module_name


class Command(ScrapyCommand):

    requires_project = False
    default_settings = {'LOG_ENABLED': False}

    def syntax(self):
        return "[options] <somebody> <someproj> <name>"

    def short_desc(self):
        return "Generate new spider using pre-defined templates"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-l", "--list", dest="list", action="store_true",
                          help="List available templates")
        parser.add_option("-e", "--edit", dest="edit", action="store_true",
                          help="Edit spider after creating it")
        parser.add_option("-d", "--dump", dest="dump", metavar="TEMPLATE",
                          help="Dump template to standard output")
        parser.add_option("-t", "--template", dest="template", default="basic",
                          help="Uses a custom template.")
        parser.add_option("--force", dest="force", action="store_true",
                          help="If the spider already exists, overwrite it with the template")

    def run(self, args, opts):
        if opts.list:
            self._list_templates()
            return
        if opts.dump:
            template_file = self._find_template(opts.dump)
            if template_file:
                with open(template_file, "r") as f:
                    print(f.read())
            return

        # by zhizhong change project temp dir
        if len(args) != 3:
            raise UsageError()

        somebody,someproject,name = args[0:3]
        domain = 'baidu.com'
        module = sanitize_module_name(name)
        if not os.path.exists(f"./Scrapy_Prj/spiders/{somebody}"):
            os.makedirs(f"./Scrapy_Prj/spiders/{somebody}")

        if not os.path.exists(f"./Scrapy_Prj/spiders/{somebody}/__init__.py"):
            with open(f"./Scrapy_Prj/spiders/{somebody}/__init__.py","w") as f:pass

        if not os.path.exists(f"./Scrapy_Prj/spiders/{somebody}/{someproject}"):
            os.makedirs(f"./Scrapy_Prj/spiders/{somebody}/{someproject}")
            
        if not os.path.exists(f"./Scrapy_Prj/spiders/{somebody}/{someproject}/__init__.py"):
            with open(f"./Scrapy_Prj/spiders/{somebody}/{someproject}/__init__.py","w") as f:pass

        if not os.path.exists(f"./Scrapy_Prj/spiders/{somebody}/{someproject}/api.http"):
            with open(f"./Scrapy_Prj/spiders/{somebody}/{someproject}/api.http","w",encoding='utf-8') as f:f.write("#目标网站接口文档")

        if self.settings.get('BOT_NAME') == module:
            print("Cannot create a spider with the same name as your project")
            return
        spider_path =f"./Scrapy_Prj/spiders/{somebody}/{someproject}"
        if not opts.force and self._spider_exists(name):
            return

        template_file = self._find_template(opts.template)
        main_file = self._find_main_template('main')
        if template_file:
            self._genspider(module, name, domain, opts.template, template_file,spider_path)
            if opts.edit:
                self.exitcode = os.system(f'scrapy edit "{name}"')
        if main_file:
            self._genmain(module, name, domain, opts.template, main_file,somebody,someproject)
            if opts.edit:
                self.exitcode = os.system(f'scrapy edit "{name}"')

    def _genspider(self, module, name, domain, template_name, template_file,spider_path):
        """Generate the spider module, based on the given template"""
        capitalized_module = ''.join(s.capitalize() for s in module.split('_'))
        tvars = {
            'project_name': self.settings.get('BOT_NAME'),
            'ProjectName': string_camelcase(self.settings.get('BOT_NAME')),
            'module': module,
            'name': name,
            'domain': domain,
            'classname': f'{capitalized_module}Spider'
        }
        if self.settings.get('NEWSPIDER_MODULE'):
            spiders_module = import_module(self.settings['NEWSPIDER_MODULE'])
            spiders_dir = spider_path
        else:
            spiders_module = None
            spiders_dir = "."
        spider_file = f"{join(spiders_dir, module)}.py"
        if not os.path.exists(spider_file):
            shutil.copyfile(template_file, spider_file)
            render_templatefile(spider_file, **tvars)
            print(f"Created spider {name!r} using template {template_name!r} ",
                end=('' if spiders_module else '\n'))
        else:
            print(f"Already existed {template_name!r} ",
                end=('' if spiders_module else '\n'))
        if spiders_module:
            print(f"in module:\n  {spiders_module.__name__}.{module}")

    def _genmain(self, module, name, domain, template_name, template_file,somebody,someproject):
        """Generate the spider module, based on the given template"""
        capitalized_module = ''.join(s.capitalize() for s in module.split('_'))
        prefix = {
            "zhizhong":"zz",
            "yongjie":"yj",
            "xuqi":"xq",
            "juncheng":"jc",
            "yonghao":"yh",
            "siming":"sm",
            "fengchao":"fc",
            "runtao":"rt",
            "yijia":"yj",
        }.get(somebody,'')
        prefix_name = prefix+'_'+name if prefix else name
        tvars = {
            'project_name': self.settings.get('BOT_NAME'),
            'ProjectName': string_camelcase(self.settings.get('BOT_NAME')),
            'module': module,
            'name': name,
            'prefix_name': prefix_name,
            'domain': domain,
            'classname': f'{capitalized_module}Spider'
        }
        if self.settings.get('NEWSPIDER_MODULE'):
            spiders_module = import_module(self.settings['NEWSPIDER_MODULE'])
            spiders_dir = abspath(dirname(spiders_module.__file__))
        else:
            spiders_module = None
            spiders_dir = "."

        spider_file = f"./Command/{somebody}_{someproject}_main.py"
        if not os.path.exists(spider_file):
            shutil.copyfile(template_file, spider_file)
            render_templatefile(spider_file, **tvars)
            print(f"Created {name!r} Main using template ",
                end=('' if spiders_module else '\n'))
        else:
            print(f"Already existed {name!r} Main entrance ",
                end=('\n'))
                
        if spiders_module:
            print(f"in module:\n  {spiders_module.__name__}.{module}")

    def _find_template(self, template):
        template_file = join(self.templates_dir, f'{template}.tmpl')
        if exists(template_file):
            return template_file
        print(f"Unable to find template: {template}\n")
        print('Use "scrapy genspider --list" to see all available templates.')

    def _find_main_template(self, template):
        template_file = join(self.templates_project_dir, f'{template}.tmpl')
        if exists(template_file):
            return template_file
        print(f"Unable to find template: {template}\n")
        print('Use "scrapy genspider --list" to see all available templates.')

    def _list_templates(self):
        print("Available templates:")
        for filename in sorted(os.listdir(self.templates_dir)):
            if filename.endswith('.tmpl'):
                print(f"  {splitext(filename)[0]}")

    def _spider_exists(self, name):
        if not self.settings.get('NEWSPIDER_MODULE'):
            # if run as a standalone command and file with same filename already exists
            if exists(name + ".py"):
                print(f"{abspath(name + '.py')} already exists")
                return True
            return False

        try:
            spidercls = self.crawler_process.spider_loader.load(name)
        except KeyError:
            pass
        else:
            # if spider with same name exists
            print(f"Spider {name!r} already exists in module:")
            print(f"  {spidercls.__module__}")
            return True

        # a file with the same name exists in the target directory
        spiders_module = import_module(self.settings['NEWSPIDER_MODULE'])
        spiders_dir = dirname(spiders_module.__file__)
        spiders_dir_abs = abspath(spiders_dir)
        if exists(join(spiders_dir_abs, name + ".py")):
            print(f"{join(spiders_dir_abs, (name + '.py'))} already exists")
            return True

        return False

    @property
    def templates_dir(self):
        return join(
            self.settings['TEMPLATES_DIR'] or join(scrapy.__path__[0], 'templates'),
            'Scrapy_Prj'
        )
    @property
    def templates_project_dir(self):
        return self.settings['TEMPLATES_DIR'] 
