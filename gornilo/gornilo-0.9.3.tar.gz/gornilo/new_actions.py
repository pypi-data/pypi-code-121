from gornilo.actions import Checker
from typing import Type, List
from gornilo.sub_checker import VulnChecker
from gornilo.models import api_constants


class NewChecker(Checker):
    def __init__(self):
        super().__init__()

        self.__flag_id_description: List[str] = []

    def define_vuln(self, flag_id_description, vuln_rate=1):
        if not isinstance(flag_id_description, str):
            raise TypeError("Flag id description must be string!")

        self.__flag_id_description.append(flag_id_description)

        def checker_wrapper(cls: Type[VulnChecker]):
            if not issubclass(cls, VulnChecker):
                raise TypeError(f"{cls} should be inherited from {VulnChecker}!")

            impl_class = cls()

            self.define_put(len(self.__flag_id_description), vuln_rate)(impl_class.put)
            self.define_get(len(self.__flag_id_description))(impl_class.get)

            return cls

        return checker_wrapper

    # noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnresolvedReferences,PyProtectedMember
    def _Checker__extract_info_call(self):
        return super()._Checker__extract_info_call() +\
               f"\n{api_constants.FLAG_DESCRIPTION_KEY}{', '.join(self.__flag_id_description)}\n"

    def run(self, *args):
        super(NewChecker, self).run(*args)
