import re
import uuid
import random
import string
import inspect
import pkgutil
import importlib
from generic_utils.interfaces import ReflectionClassUtilsInterface as Rcui


class CleanDevGenericUtils:

    @staticmethod
    def get_total_page(row_for_page: int, total_row: int):
        pages = 0
        modulo: int = total_row % row_for_page
        if modulo > 0:
            pages += 1
        pages += total_row / row_for_page
        return int(pages)

    @staticmethod
    def get_uuid4() -> str:
        """
            Retorna un string en formato uuid
        """
        return uuid.uuid4().__str__()

    @staticmethod
    def check_uudi_4(uuid_string: str) -> bool:
        """
            Comprueba que la cadena tiene el formato uuid4
        """
        try:
            uuid.UUID(uuid_string, version=4)
        except:
            return False
        else:
            return True

    @staticmethod
    def check_email_format(email: str) -> bool:
        """
            Comprueba que la cadena tiene un formato de email valido
        """
        rex_email = re.compile('[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,3}')
        if rex_email.match(email):
            return True
        return False

    @staticmethod
    def get_random_string(length=5) -> str:
        """
        Retorna una cadena aleatoria con numero y letras
        """
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def to_camel_case(name):
        lower_first_char = lambda s: s[:1].lower() + s[1:] if s else ''
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return lower_first_char(''.join(word.title() for word in name.split('_')))

    @staticmethod
    def camel_to_snake(name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class ReflectionClassUtils(Rcui):

    @staticmethod
    def get_sub_packages(parent_package: str) -> list:
        """
        Retorna una lista de string con el paquete padre y todos los paquetes hijos del paquete
        """
        list_packages: list = [parent_package]
        module = importlib.import_module(parent_package)
        for modname in pkgutil.iter_modules(module.__path__):
            list_packages.append(f"{parent_package}.{modname.name}")
        return list_packages

    @classmethod
    def get_class_from_package(cls, parent_package: str, class_name: str):
        """
        Dado el nombre de un paquete y el nombre de una clase, busca en el interior del paquete y sub paquetes
        dados y retorna una clase en lugar de su instancia.
        """
        sub_packages: list = cls.get_sub_packages(parent_package)
        for package in sub_packages:
            module = importlib.import_module(package)
            for name, obj in inspect.getmembers(module):
                if name == class_name:
                    return getattr(module, name)
        return None

    @classmethod
    def get_class_filter_parent(cls, parent_package: str, parent_class: str) -> list:
        """
            Dado un paquete y una clase, se busca todas aquellas clases que como clase padre tenga el mismo nombre
            que la clase dada.
        """
        sub_packages: list = cls.get_sub_packages(parent_package)
        list_filter_class: list = []
        for package in sub_packages:
            module = importlib.import_module(package)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__base__.__name__ == parent_class:
                    list_filter_class.append(name)
        return list_filter_class
