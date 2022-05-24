import re
from os import (
    listdir,
)

from django.conf import (
    settings,
)
from django.db.backends.base.base import (
    BaseDatabaseWrapper,
)
from django.db.backends.base.introspection import (
    BaseDatabaseIntrospection,
)
from lxml import (
    etree,
)


def get_by_xpath(element, xpath):
    """
    Возвращает все объекты по xpath
    """
    return element.xpath(
        xpath,
        namespaces={'xs': "http://www.w3.org/2001/XMLSchema"}
    )


def get_first_by_xpath(element, xpath):
    """
    Возвращает первый объект по xpath
    """
    return get_by_xpath(element, xpath)[0]


class XSDField:
    """
    Поле в стуктуре XSD
    """

    # соотвествие атрибутов XSD и атрибутов объекта с конверторами
    attr_map = {
        'maxLength': ('internal_size', int),
        'length': ('internal_size', int),
    }

    # индексы полей при обращении через порядковый номер
    indexes = {
        0: 'name',
        1: 'type_code',
        2: 'display_size',
        3: 'internal_size',
        4: 'precision',
        5: 'scale',
        6: 'null_ok',
        7: 'default',
        8: 'collation',
        9: 'description',
        10: 'path',
    }

    def __init__(self, element):
        super().__init__()

        self.name = element.get('name', '').lower()
        self.type_code = None
        self.display_size = None
        self.internal_size = None
        self.precision = None
        self.scale = None
        self.null_ok = element.get('use') != 'required'
        self.default = None
        self.collation = None

        self.description = element[0][0].text.replace('\n', ' ')

        try:
            attrs = get_first_by_xpath(
                element,
                'xs:simpleType/xs:restriction[1]'
            )
        except IndexError:
            self.type_code = element.get('type')
        else:
            self.type_code = attrs.get('base')
            for attr_element in attrs:
                local_name = etree.QName(attr_element).localname
                if local_name in self.attr_map:
                    attr_name, convertor = self.attr_map[local_name]
                    setattr(
                        self,
                        attr_name,
                        convertor(
                            attr_element.get('value')
                        ),
                    )

        if self.type_code:
            self.type_code = self.type_code.replace(f'{element.prefix}:', '')

            if self.name in ['isactive', 'isactual'] and self.type_code == 'integer':
                self.type_code = 'boolean'

        else:
            self.type_code = 'string'
            self.null_ok = True
            self.default = ''

    def __getitem__(self, i):
        return getattr(self, self.indexes[i])


class XSDObject:
    """
    XSD объект
    """

    def __init__(self, folder_path, file_name):
        super().__init__()

        self.name = self.get_name(file_name)
        self.file_name = file_name
        # для совместимости с типом "Таблица" с точки зрения DataBaseEngine
        self.type = 't'

        root = etree.parse(str(folder_path / file_name)).getroot()

        elements = get_by_xpath(root, 'xs:element')
        elements_len = len(elements)

        if elements_len == 1:
            element = get_first_by_xpath(
                elements[0],
                'xs:complexType/xs:sequence/xs:element[1]',
            )

            self.description = get_first_by_xpath(
                element,
                'xs:annotation/xs:documentation[1]/text()',
            )
            self.fields = [
                XSDField(el) for el in get_first_by_xpath(element, 'xs:complexType')
            ]

        elif elements_len == 2:
            self.description = get_first_by_xpath(
                elements[0],
                'xs:complexType/xs:sequence/xs:element/xs:annotation/xs:documentation[1]/text()',
            )

            self.fields = [
                XSDField(el) for el in get_first_by_xpath(elements[1], 'xs:complexType')
            ]

    def get_name(self, file_name):
        """
        Возвращает имя по имени файла
        """
        p = re.compile("_[a-zA-Z_]+")
        name = p.search(file_name).group(0)[1:-1]

        return name


class XSDFolder:
    """
    Директория с XSD
    """

    def __init__(self, folder_path):
        super().__init__()

        self.files = {}

        files = [
            f for f
            in listdir(folder_path)
            if (folder_path / f).is_file() and f.endswith('.xsd')
        ]

        for file_ in files:
            xsd_obj = XSDObject(folder_path, file_)
            self.files[xsd_obj.name] = xsd_obj

    def get_files_list(self):
        return self.files.values()

    def get_file(self, name):
        return self.files[name]


class XSDFolderCursor:
    """
    "Указатель" для взаимодействия
    """

    def __init__(self, xsd_path):
        super().__init__()

        self.xsd_path = xsd_path
        self.folder = None

    def __enter__(self):
        self.folder = XSDFolder(self.xsd_path)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_files_list(self):
        """
        Возвращает перечень файлов
        """
        return self.folder.get_files_list()

    def get_file(self, name):
        """
        Возвращает файл по имени
        """
        return self.folder.get_file(name)


class XSDFolderIntrospection(BaseDatabaseIntrospection):
    """
    Анализатор директории с xsd
    """

    data_types_reverse = {
        'boolean': 'BooleanField',
        'long': 'BigIntegerField',
        'integer': 'IntegerField',
        'string': 'CharField',
        'date': 'DateField',
    }

    def get_table_list(self, cursor):
        """
        Возвращает перечень файлов
        """
        return cursor.get_files_list()

    def get_relations(self, cursor, table_name):
        """
        Возвращает перечнь связей между файлами (пока считаем, что их нет)
        """
        return {}

    def get_primary_key_column(self, cursor, table_name):
        return self.get_table_description(cursor, table_name)[0].name

    def get_table_description(self, cursor, table_name):
        """
        Возвращает перечень полей определенного файла
        """
        return cursor.get_file(table_name).fields


class FakeClient:
    def __init__(self, wrapper):
        pass


class DatabaseWrapper(BaseDatabaseWrapper):
    """
    Обертка на "базой данных", которая представляет из себя директорию с XSD
    """

    client_class = creation_class = features_class = ops_class = FakeClient
    introspection_class = XSDFolderIntrospection

    def cursor(self):
        return XSDFolderCursor(settings.GAR_SCHEMAS_FOLDER)
