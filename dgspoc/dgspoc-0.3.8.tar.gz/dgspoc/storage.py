"""Module containing the logic for template storage"""

import yaml
import re
from dgspoc.config import Data
from dgspoc.utils import File
from dgspoc.utils import Misc
from dgspoc.utils import Printer
from dgspoc.utils import Text

from dgspoc.exceptions import TemplateStorageError

from dlapp.utils import convert_wildcard_to_regex


class TemplateStorage:
    message = ''
    filename = Data.template_storage_filename

    @classmethod
    def get(cls, template_id):
        if cls.check(template_id):
            with open(cls.filename) as stream:
                node = yaml.safe_load(stream)
                template = node.get(template_id)
                return template
        else:
            return ''

    @classmethod
    def check(cls, template_id):
        fmt1 = '*** CANT find "{}" template ID because template storage file is empty.'
        fmt2 = '*** CANT find "{}" template ID because template storage file is not created.'
        fmt3 = '{} file has invalid template storage format.'
        if File.is_exist(cls.filename):
            with open(cls.filename) as stream:
                content = stream.read().strip()
                if content:
                    node = yaml.safe_load(content)
                    if Misc.is_dict(node):
                        return template_id in node
                    else:
                        raise TemplateStorageError(fmt3.format(cls.filename))
                else:
                    cls.message = fmt1.format(template_id)
                    return False
        else:
            cls.message = fmt2.format(template_id)
            return False

    @classmethod
    def search(cls, template_id_pattern):
        msg1 = '*** CANT find template ID because template storage file is empty.'
        msg2 = '*** CANT find template ID because template storage file is not created.'
        fmt1 = '{} file has invalid template storage format.'
        fmt2 = '*** There is no template ID matching "{}" pattern.'
        fmt3 = 'Found {} template ID(s) matching "{}" pattern:'
        if File.is_exist(cls.filename):
            with open(cls.filename) as stream:
                content = stream.read().strip()
                if not content:
                    cls.message = Printer.get(msg1)
                    return False

                node = yaml.safe_load(content)

                if not Misc.is_dict(node):
                    raise TemplateStorageError(fmt1.format(cls.filename))

                pattern = convert_wildcard_to_regex(template_id_pattern)
                ids = dict()

                for tmpl_id in sorted(node):
                    if re.search(pattern, tmpl_id, flags=re.I):
                        ids[tmpl_id] = node.get(tmpl_id)

                total = len(ids)

                if total == 0:
                    cls.message = Printer.get(fmt2.format(template_id_pattern))
                    return False

                lst = [fmt3.format(total, template_id_pattern)]
                for tmpl_id in ids:
                    lst.append('  - {}'.format(tmpl_id))

                lst = [Printer.get(lst), '']
                for tmpl_id, template in ids.items():
                    lst.append(Printer.get('Template ID: {}'.format(tmpl_id)))
                    lst.append(template)
                    lst.append('')

                cls.message = '\n'.join(lst)
                return True
        else:
            cls.message = Printer.get(msg2)
            return False

    @classmethod
    def upload(cls, template_id, template, replaced=False):
        try:
            if not File.is_exist(cls.filename):
                File.create(cls.filename)
            if not cls.check(template_id):
                node = File.get_result_from_yaml_file(cls.filename, default=dict())
                node[template_id] = template
                File.save(cls.filename, yaml.safe_dump(node))
                return True
            else:
                if replaced:
                    content = open(cls.filename).read()
                    node = yaml.safe_load(content)
                    node[template_id] = template
                    File.save(cls.filename, yaml.safe_dump(node))
                    return True
                else:
                    fmt = ('CANT upload generated template because of '
                           'duplicate "{}" template ID.  Use replaced '
                           'flag accordingly.')
                    cls.message = fmt.format(template_id)
                    return False
        except Exception as ex:
            cls.message = Text(ex)
            return False

    @classmethod
    def clear(cls, template_id):

        if re.match(r'(?i) *([*]|_+all_+) *$', template_id):
            fmt = 'WONT clear %r because method prohibits multiple clearing template id.'
            cls.message = fmt % template_id
            return False

        yaml_obj = File.get_result_from_yaml_file(cls.filename)
        if template_id in yaml_obj:
            yaml_obj.pop(template_id)
            File.save(cls.filename, yaml.safe_dump(yaml_obj))
            return True
        else:
            fmt = 'CANT clear %r because it is not in storage template.'
            cls.message = fmt % template_id
            return False
