"""NanamiLang Fn Handler Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from copy import copy

from nanamilang import destruct
from nanamilang import datatypes
from nanamilang.spec import Spec
from nanamilang.token import Token


class Fn:
    """NanamiLang Fn Handler Class"""

    _function_name: str = None
    _function_positional_parameters: list
    _function_body_token_or_form: list
    _forms: list = None
    _closure: dict = None
    _recursive_evaluate_function = None
    _nanamilang_function_spec: list = None
    _function_positional_parameters_count: int
    _function_optional_accumulator_tof: Token or list = None

    def __init__(self,
                 function_name: str,
                 function_parameters_form: list,
                 function_body_token_or_form: list,
                 closure: dict,
                 recursive_evaluate_function,
                 nanamilang_function_spec: list = None) -> None:
        """NanamiLang Fn Handler, initialize a new Fn instance"""

        self._function_name = function_name
        self._function_body_token_or_form = function_body_token_or_form
        self._closure = copy(closure)  # <-- capture a function closure
        self._recursive_evaluate_function = recursive_evaluate_function
        self._nanamilang_function_spec = nanamilang_function_spec or []  # <-- will be updated later
        self._process_function_parameters_form(function_parameters_form[1:])  # <-- omit make-vector

    def _process_function_parameters_form(self, function_parameters_form_actual):
        """NanamiLang Fn Handler, process function parameters form, and populate required fields"""

        form_parts = [self._function_name]  # <------- initialize parts of the function form string
        self._forms = []  # <------------------------------------------------ initialize forms list
        self._function_positional_parameters = []  # <------- initialize positional parameters list

        for idx, tof in enumerate(function_parameters_form_actual):
            if isinstance(tof, Token) and tof.identifier() and tof.dt().origin() == '&':
                assert len(function_parameters_form_actual) - 2 == idx, (
                    'fn/defn: optional parameter syntax error'  # <-- when [&], [& a b], [& a & b]
                )
                self._function_optional_accumulator_tof = function_parameters_form_actual[idx + 1]
                form_parts.append('&')
                tof = function_parameters_form_actual[idx + 1]  # <---- get the next token or form
                form_parts.append(tof.dt().origin() if isinstance(tof, Token) else "coll/interop")
                break  # <------ because we do not need to continue collecting function parameters
            self._function_positional_parameters.append(tof)  # <---- append current token of form
            form_parts.append(tof.dt().origin() if isinstance(tof, Token) else "coll/interop")   #

        self._function_positional_parameters_count = len(self._function_positional_parameters)   #
        self._forms.append('(' + ' '.join(form_parts) + ')')  # <------------ generate form string

        self._nanamilang_function_spec.append(
            [Spec.ArityIs, self._function_positional_parameters_count]
            if not self._function_optional_accumulator_tof
            else [Spec.ArityAtLeast, self._function_positional_parameters_count])  # <- arity spec

    def forms(self) -> list:
        """NanamiLang Fn Handler, self._forms private getter"""

        return self._forms

    def closure(self) -> dict:
        """NanamiLang Fn Handler, self._closure private getter"""

        return self._closure

    def handle(self, args: tuple) -> datatypes.Base:
        """NanamiLang Fn Handler, handle function call using function closure with merged specs"""

        Spec.validate(self._function_name, args, self._nanamilang_function_spec)

        _curr_closure = copy(self._closure)  # <-------------- prevent function 'closure' mutation

        posargs = args[:self._function_positional_parameters_count + 1]  # <- only positional args

        for parameter_token_or_form, fn_arg in zip(self._function_positional_parameters, posargs):
            _curr_closure.update(destruct.Destructuring(parameter_token_or_form).destruct(fn_arg))

        optargs = args[self._function_positional_parameters_count:]  # rest of args to accumulate.

        _curr_closure.update(destruct.Destructuring(
            self._function_optional_accumulator_tof).destruct(
            datatypes.Vector(tuple(optargs)) if optargs else datatypes.Nil('nil')))  # [], or nil.

        return self._recursive_evaluate_function(_curr_closure, self._function_body_token_or_form)
