"""NanamiLang Builtin- Macros/Functions classes"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import functools
from typing import List
from copy import deepcopy
from functools import reduce

from nanamilang.destruct import Destructuring
from nanamilang.spec import Spec
from nanamilang.token import Token
from nanamilang import fn, datatypes, loader
from nanamilang.shortcuts import (
    ASSERT_COLL_LENGTH_IS_EVEN,
    NML_M_FORM_IS_A_HASHMAP,
    NML_M_ASSERT_FORM_IS_A_VECTOR,
    NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS,
    NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS_EVEN,
    NML_M_ITERATE_AS_PAIRS, ASSERT_DICT_CONTAINS_KEYS,
    truncated, ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF,
    dashcase2capitalcase, plain2partitioned, randstr, get
)


def nanamilang_vector_to_spec_rules(vector: datatypes.Vector):
    """Recursively convert Vector coll to valid Spec rules list"""

    if isinstance(vector, datatypes.Nil):
        return []  # if vector is nil (no nanamilang-spec actually)

    def recursively_processed(dt):
        if isinstance(dt, datatypes.String):
            return datatypes.DataType.resolve(dt.reference())
        if isinstance(dt, datatypes.Keyword):
            return dashcase2capitalcase(dt.reference())
        if isinstance(dt, datatypes.Vector):
            return [recursively_processed(i) for i in dt.items()]
        return None  # <- unreachable, but to make Pylint happy :)

    return [recursively_processed(item) for item in vector.items()]


def meta(data: dict):
    """
    NanamiLang, apply metadata to the handler function
    'name': function or macro LISP name (to access as)
    'forms': possible function or macro possible forms
    'docstring': what function or macro actually does?
    May contain 'spec' attribute, but could be omitted

    :param data: a function metadata Python dictionary
    """

    def wrapped(_fn):
        @functools.wraps(_fn)
        def function(*args, **kwargs):

            spec = data.get('spec')
            if spec:
                Spec.validate(data.get('name'), args[0], spec)

            return _fn(*args, **kwargs)

        ASSERT_DICT_CONTAINS_KEYS(data,
                                  {'name', 'forms', 'docstring'},
                                  'function meta must have "name", "forms" and "docstring" keys!')

        if 'BuiltinMacro' in function.__qualname__:
            data.update({'kind': 'macro'})
        elif 'BuiltinFunctions' in function.__qualname__:
            data.update({'kind': 'function'})  # <-------------------- dispatch kind automagically

        function.meta = data

        return function

    return wrapped  # <----- register builtin function/macro handle to access it inside NanamiLang


class BuiltinMacros:
    """NanamiLang Builtin Macros"""

    #################################################################################################################

    @staticmethod
    @meta({'name': 'do',
           'forms': ['(do)', '(do form1 form2 ... formN)'],
           'docstring': 'Returns last evaluated form result'})
    def do_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'do' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        evaluated = datatypes.Nil('nil')

        for token_or_form in tree:
            evaluated = eval_function(local_env, token_or_form)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <---- propagate possibly created NException instance

        return Token(Token.Proxy, evaluated)  # <--------------------- return the last evaluated from result

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '->',
           'forms': ['(-> form1 form2 ... formN)'],
           'docstring': 'Each next form wraps previous one'})
    def first_threading_macro(tree: list, *_: tuple) -> list or Token:
        """
        Builtin '->' macro implementation

        :param tree: a form given to this macro
        :param _: unused argument, but I need to mention it here
        :return: the modified or new source tree as it would be expected
        """

        if not len(tree) > 1:
            return tree[-1]  # <------------------------------ if tree contains only one item, return it

        tree = deepcopy(tree)

        for idx, form in enumerate(tree):
            if len(tree) - 1 != idx:
                next_form = tree[idx + 1]
                if isinstance(next_form, list):
                    tree[idx + 1].insert(1, form)
                else:
                    tree[idx + 1] = [next_form, form]

        return tree[-1]  # <----------------------------- will return the last form of the modified tree

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '->>',
           'forms': ['(->> form1 form2 ... formN)'],
           'docstring': 'Each next form wraps previous one'})
    def last_threading_macro(tree: list, *_: tuple) -> list or Token:
        """
        Builtin '->>' macro implementation

        :param tree: a form given to this macro
        :param _: unused argument, but I need to mention it here
        :return: the modified or new source tree as it would be expected
        """

        if not len(tree) > 1:
            return tree[-1]  # <------------------------------ if tree contains only one item, return it

        tree = deepcopy(tree)

        for idx, form in enumerate(tree):
            if len(tree) - 1 != idx:
                next_form = tree[idx + 1]
                if isinstance(next_form, list):
                    tree[idx + 1].append(form)
                else:
                    tree[idx + 1] = [next_form, form]

        return tree[-1]  # <----------------------------- will return the last form of the modified tree

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2, 3]]],
           'name': 'if',
           'forms': ['(if cond then)', '(if cond then else)'],
           'docstring': 'Returns then/else branch depending on a condition'})
    def if_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'if' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        if len(tree) == 3:
            cond, then_branch, else_branch = tree
        else:
            cond, then_branch, else_branch = tree + [Token(Token.Nil, 'nil')]

        evaluated = eval_function(local_env, cond)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <---- propagate possibly created NException instance

        return then_branch if evaluated.truthy() is True else else_branch  # return corresponding branch

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2]],
           'name': 'when',
           'forms': ['(when cond then)'],
           'docstring': 'Returns then branch or nil depending on a condition'})
    def when_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'when' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        cond, then_branch, else_branch = tree + [Token(Token.Nil, 'nil')]

        evaluated = eval_function(local_env, cond)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <---- propagate possibly created NException instance

        return then_branch if evaluated.truthy() is True else else_branch  # return corresponding branch

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityEven]],
           'name': 'cond',
           'forms': ['(cond)', '(cond cond1 expr1 ... condN exprN)'],
           'docstring': 'Returns nil or an expression for first truthy condition'})
    def cond_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'cond' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        for cond, expr in plain2partitioned(tree):

            evaluated = eval_function(local_env, cond)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <-------- propagate possible NException instance

            if evaluated.truthy():
                return expr  # <----- return expression if corresponding evaluated condition is truthy()

        return Token(Token.Nil, 'nil')  # <- if nothing has been supplied to macro, return nil data type

    #################################################################################################################

    @staticmethod
    @meta({'name': 'comment',
           'forms': ['(comment)', '(comment form1 form2 ... formN)'],
           'docstring': 'Replaces all the given forms with a nil type'})
    def comment_macro(*_: tuple) -> list or Token:
        """
        Builtin 'comment' macro implementation

        :param _: unused argument, but I need to mention it here
        :return: the modified or new source tree as it would be expected
        """

        return Token(Token.Nil, 'nil')  # <- as it was said in docstring, we just return a Nil data type

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeast, 1]],
           'name': 'fn',
           'forms': ['(fn [p1 p2 ... pN])',
                     '(fn [p1 p2 ... pN] body)',
                     '(fn name [p1 p2 ... pN] body)'],
           'docstring': 'Defines a local, maybe named, user function type'})
    def fn_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'fn' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        name_token, parameters_form, body_token_or_form = None, [], None

        if len(tree) == 1:
            parameters_form, body_token_or_form = tree + [Token(Token.Nil, 'nil')]
        else:
            if isinstance(tree[0], Token):
                name_token, parameters_form, *rest = tree  # <----- if the first element is a token
            else:
                parameters_form, *rest = tree  # <------ if the first element is an expression form
            body_token_or_form = [Token(Token.Identifier, 'do'), *rest]  # <----- wrap body in 'do'

        if name_token:
            assert name_token.type() == Token.Identifier,      'fn: name needs to be an Identifier'

        NML_M_ASSERT_FORM_IS_A_VECTOR(parameters_form,  'fn: parameters form needs to be a Vector')

        fn_name = name_token.dt().origin() if name_token else randstr()

        fni = fn.Fn(fn_name, parameters_form, body_token_or_form, local_env, eval_function)
        fn_handle = lambda args: fni.handle(tuple(args))  # <-- we cannot use fni.handle() directly

        fn_handle.meta = {'name': fn_name, 'docstring': '', 'kind': 'function', 'forms': fni.forms()}

        payload = {fn_name: datatypes.Function({'function_name': fn_name, 'function_reference': fn_handle})}

        local_env.update(payload)  # <----- update local environment, thus AST will be aware of our function
        fni.closure().update(payload)  # <- and also we need to update function closure for the same purpose

        return Token(Token.Identifier, fn_name)  # <-- gonna return locally defined NanamiLang function name

    #################################################################################################################

    @staticmethod
    @meta({'name': 'or',
           'forms': ['(or)', '(or expr1 expr2 ... exprN)'],
           'docstring': 'Returns nil (default); first truthy expression result'})
    def or_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'or' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        if not tree:
            return Token(Token.Nil, 'nil')  # <------------------------------ by default, gonna return nil data type

        for expression in tree:

            evaluated = eval_function(local_env, expression)
            if isinstance(evaluated, datatypes.NException) or evaluated.truthy():
                return Token(Token.Proxy, evaluated)  # <------------------ return if its NException or a truthy one

        return tree[-1]  # <- like in Clojure and other LISP engines: everything is falsie - return the last element

    #################################################################################################################

    @staticmethod
    @meta({'name': 'and',
           'forms': ['(and)', '(and expr1 expr2 ... exprN)'],
           'docstring': 'Returns true (default); first falsie expression result'})
    def and_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'and' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: the modified or new source tree as it would be expected
        """

        if not tree:
            return Token(Token.Boolean, True)  # <-------------------------- by default, gonna return true data type

        for expression in tree:

            evaluated = eval_function(local_env, expression)
            if isinstance(evaluated, datatypes.NException) or not evaluated.truthy():
                return Token(Token.Proxy, evaluated)  # <------------------ return if its NException or a falsie one

        return tree[-1]  # <- like in Clojure and other LISP engines: everything is truthy - return the last element

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2]],
           'name': 'def',
           'forms': ['(def name value)'],
           'docstring': 'Defines a global data type bound to access it from everywhere'})
    def def_macro(tree: list, local_env: dict, module_env, eval_function) -> list or Token:
        """
        Builtin 'def' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param module_env: module environment we are free to modify
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        name_token, data_type_token_or_form = tree

        assert not isinstance(name_token, list),                                       'def: name could not be a form'
        assert name_token.type() == Token.Identifier,                            'def: name needs to be an Identifier'

        evaluated = eval_function(local_env, data_type_token_or_form)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <----------------- propagate possibly created NException instance

        name = name_token.dt().origin()

        module_env.set(name, evaluated)

        return Token(Token.Identifier, name)  # <- as it would be expected, def returns globally defined binding name

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeast, 2]],
           'name': 'defn',
           'forms': ['(defn name [p1 p2 ... pN])',
                     '(defn name [p1 p2 ... pN] body)',
                     '(defn name docstring [p1 p2 ... pN] body)',
                     '(defn name docstring spec [p1 p2 ... pN] body)'],
           'docstring': 'Defines a global user function type with a docstring, spec rules'})
    def defn_macro(tree: list, local_env: dict, module_env, eval_function) -> list or Token:
        """
        Builtin 'defn' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param module_env: module environment we are free to modify
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        __defs__ = None, None, [], [], None
        name_token, docstring_token, spec_form, parameters_form, body_token_or_form = __defs__

        if len(tree) == 2:
            name_token, parameters_form, body_token_or_form = tree + [Token(Token.Nil, 'nil')]
        else:
            name_token, *questionable = tree

            if isinstance(questionable[0], Token) and questionable[0].type() == Token.String:  # <-- docstr?
                docstring_token = questionable[0]  # <----------------------------------- remember docstring
                if isinstance(questionable[1], list) and NML_M_FORM_IS_A_HASHMAP(questionable[1]):  #  spec?
                    spec_form = questionable[1]  # <------------------------------------ remember spec rules
                    parameters_form = questionable[2]  # <--------- parameters form should follow spec rules
                    body_token_or_form = [Token(Token.Identifier, 'do'), *questionable[3:]]  # <-- wrap 'do'
                else:
                    parameters_form = questionable[1]  # <----- parameters form is the third element of tree
                    body_token_or_form = [Token(Token.Identifier, 'do'), *questionable[2:]]  # <-- wrap 'do'
            else:
                parameters_form = questionable[0]  # <-------- parameters form is the second element of tree
                body_token_or_form = [Token(Token.Identifier, 'do'), *questionable[1:]]  # <--- wrap in 'do'

        assert isinstance(name_token, Token),                   'defn: name needs to be a token, not a form'
        assert name_token.type() == Token.Identifier,                    'defn: name needs to be Identifier'

        ####################################################################################################

        spec_list = []

        if spec_form:
            NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS_EVEN(spec_form,   'defn: spec form needs to be a HashMap')

            evaluated = eval_function(local_env, spec_form)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <- thus, we propagate a possible NException instance

            spec_list = nanamilang_vector_to_spec_rules(evaluated.get(datatypes.Keyword('nanamilang-spec')))

        #####################################################################################################

        NML_M_ASSERT_FORM_IS_A_VECTOR(parameters_form, 'defn: function parameters form needs to be a Vector')

        fn_name = name_token.dt().origin()
        fn_docstring = docstring_token.dt().reference() if docstring_token else ''

        fni = fn.Fn(fn_name, parameters_form, body_token_or_form, local_env, eval_function, spec_list)
        fn_handle = lambda args: fni.handle(tuple(args))  # <---- sadly, we can not use fni.handle() directly

        fn_handle.meta = {'name': fn_name, 'docstring': fn_docstring, 'kind': 'function', 'forms': fni.forms()}

        module_env.set(fn_name, datatypes.Function({'function_name': fn_name, 'function_reference': fn_handle}))

        return Token(Token.Identifier, fn_name)  # <- as it would be expected, defn returns globally defined function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1]],
           'name': 'require',
           'forms': ['(require \'module-name)',
                     '(require [\'module-name])',
                     '(require [\'module-name :refer :all])',
                     '(require [\'module-name :refer [\'foo \'bar ...]]])'],
           'docstring': 'Requires a module from current workdir or from \'NANAMILANG_PATH\''})
    def require_macro(tree: list, local_env: dict, module_env, eval_function) -> list or Token:
        """
        Builtin 'require' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param module_env: module environment we are free to modify
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        argument = tree[0]

        evaluated = eval_function(local_env, argument)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # <--------------------------- propagate possibly created NException

        assert isinstance(evaluated, (datatypes.Symbol,
                                      datatypes.Vector)),        'require: 1st argument should be a Vector or a Symbol'

        refer_names = []  # <------ 'refer: ['foo 'bar]; it means: create aliases for only _these_ target module names

        if isinstance(evaluated, datatypes.Symbol):  # <--------------------- if user form was like: (require 'stdlib)
            module_name = evaluated.reference()  # <-- grab the actual module name from the String data type reference

        else:
            if not evaluated.empty().truthy():  # <------------------------ if user form was like: (require ['stdlib])
                module_name_symbol, *require_opts = evaluated.items()  # <--- first item - module name, rest - options
                assert isinstance(module_name_symbol, datatypes.Symbol),     'require: module name should be a Symbol'
                module_name = module_name_symbol.reference()  # <----------- grab the actual string name of the module
                if require_opts:  # <--------------------------- if user form was like: (require ['stdlib ...opts...])
                    ASSERT_COLL_LENGTH_IS_EVEN(require_opts,                   'require: require-opts should be even')
                    require_opts_hash_map = datatypes.HashMap(tuple(require_opts))   # <---- cast options to a HashMap
                    require_refer_option_or_nil = require_opts_hash_map.get(datatypes.Keyword('refer'))   # try to get
                    if isinstance(require_refer_option_or_nil, datatypes.Vector):  # <-------- if option was :refer []
                        ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
                                                     require_refer_option_or_nil.items(),
                                                     datatypes.Symbol,
                                                     'require: :refer option Vector should only contain Symbol items')
                        refer_names = [symbol.reference() for symbol in require_refer_option_or_nil.items()]         #
                    elif isinstance(require_refer_option_or_nil, datatypes.Keyword):  # <-- if option was: :refer :all
                        assert require_refer_option_or_nil.reference() == 'all',   'require: only support :refer :all'
                        refer_names = ['*']  # <-------------------------------------- set 'refer names' list to ['*']
                    else:
                        if not isinstance(require_refer_option_or_nil, datatypes.Nil):  # <- if :refer value isn't nil
                            raise AssertionError('require: optional :refer option should be either Vector or Keyword')
            else:
                return Token(Token.Nil, 'nil')  # <-- return nil if user has supplied an empty Vector to require macro

        loader.Loader.load(module_name, module_env, refer_names)  # <------------------- load requested module by name

        return Token(Token.Nil, 'nil')  # <------- module could be loaded or not, we gonna return Nil type in any case

    ##################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2]],
           'name': 'for',
           'forms': ['(for [identifier vec] body)'],
           'docstring': 'Iterates through evaluated Vector collection'})
    def for_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'for' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        identifier_coll_vector_form, body_token_or_form = tree

        NML_M_ASSERT_FORM_IS_A_VECTOR(identifier_coll_vector_form,        'for: first argument needs to be a Vector')

        NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS(identifier_coll_vector_form, 2,
                                              'for: incorrect 1st argument arity: expected exactly: identifier, vec')

        identifier_token, coll_token_or_form = tuple(NML_M_ITERATE_AS_PAIRS(identifier_coll_vector_form))

        assert identifier_token.type() == Token.Identifier,               'for: identifier needs to be an Identifier'

        evaluated = eval_function(local_env, coll_token_or_form)
        if isinstance(evaluated, datatypes.NException):
            return Token(Token.Proxy, evaluated)  # ---------------- propagate a possibly created NException instance

        assert isinstance(evaluated, datatypes.Vector),                               'for: vec needs to be a Vector'

        _ = []

        for item in evaluated.items():
            local_env[identifier_token.dt().origin()] = item
            _evaluated = eval_function(local_env, body_token_or_form)
            if isinstance(_evaluated, datatypes.NException):
                return Token(Token.Proxy, _evaluated)  # <------------ propagate possibly created NException instance
            _.append(_evaluated)

        _resulting_vector_data_type = datatypes.Vector(tuple(_))

        return Token(Token.Proxy, _resulting_vector_data_type)  # <- for-cycle will return resulted vector collection

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeast, 1]],
           'name': 'let',
           'forms': ['(let [n1 v2 ... nN vN])',
                     '(let [n1 v2 ... nN vN] body)'],
           'docstring': 'Defines local data type bounds accessible from a block'})
    def let_macro(tree: list, local_env: dict, _, eval_function) -> list or Token:
        """
        Builtin 'let' macro implementation

        :param tree: a form given to this macro
        :param local_env: local environment during expr eval
        :param _: unused argument, but I need to mention it here
        :param eval_function: reference to recursive eval function
        :return: modified or new source tree as it would be expected
        """

        if len(tree) == 1:
            bindings_form, body_token_or_form = tree + [Token(Token.Nil, 'nil')]
        else:
            bindings_form, *rest = tree
            body_token_or_form = [Token(Token.Identifier, 'do'), *rest]  # <-- wrap body token or form in 'do' macro

        NML_M_ASSERT_FORM_IS_A_VECTOR(bindings_form,                      'let: bindings form needs to be a Vector')
        NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS_EVEN(bindings_form,             'let: bindings form needs to be even')

        for [idn_token_or_form, data_type_token_or_form] in NML_M_ITERATE_AS_PAIRS(bindings_form, 2):
            evaluated = eval_function(local_env, data_type_token_or_form)
            if isinstance(evaluated, datatypes.NException):
                return Token(Token.Proxy, evaluated)  # <------------ propagate possibly created NException instance
            local_env.update(Destructuring(idn_token_or_form).destruct(evaluated))  # <-- populate local environment

        return body_token_or_form  # <- we just return body or token form there as is, without any modifications made

    #################################################################################################################


class BuiltinFunctions:
    """NanamiLang Builtin Functions"""

    #################################################################################################################

    @staticmethod
    def install(fn_meta: dict, fn_callback) -> bool:
        """
        Allows others installing their own functions.
        For example: let the REPL install (exit) function

        :param fn_meta: required function meta information
        :param fn_callback: installed function callback reference
        :return: whether function has been successfully installed
        """

        fn_meta.update({'kind': 'function'})
        reference_key = f'{fn_meta.get("name")}_func'
        maybe_existing = getattr(BuiltinFunctions, reference_key, None)
        if maybe_existing:
            delattr(BuiltinFunctions, reference_key)

        setattr(BuiltinFunctions, reference_key, fn_callback)
        getattr(BuiltinFunctions, reference_key, None).meta = fn_meta
        return bool(getattr(BuiltinFunctions, reference_key, None).meta == fn_meta)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Function, datatypes.Vector]]]],
           'name': 'apply',
           'forms': ['(apply function arguments)'],
           'docstring': 'Applies arguments to a Function'})
    def apply_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'apply' function implementation

        :param args: incoming 'apply' function arguments (function and vector of arguments to apply)
        :return: datatypes.Base

        """

        _fn: datatypes.Function
        _argv: datatypes.Vector

        _fn, _argv = args

        return _fn.reference()(_argv.items())  # <------------- return result of the Function call with the arguments

        # 'apply' function allows to produce a Function call, where their arguments specified as a NanamiLang Vector

    #################################################################################################################

    @staticmethod
    @meta({'name': 'prn',
           'forms': ['(prn)', '(prn e1 e2 ... eN)'],
           'docstring': 'Prints all the elements to STDOUT'})
    def prn_func(args: List[datatypes.Base]) -> datatypes.Nil:
        """
        Builtin 'prn' function implementation

        :param args: incoming 'prn' function arguments (elements to print)
        :return: datatypes.Nil

        """

        print(truncated(' '.join(map(lambda x: x.format(), args)), 67))  # <- prints all elements format() to stdout

        return datatypes.Nil('nil')

        # 'print' function utilizes Python 3 'print' method, which takes data, and writes it to the 'standard output'

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1]],
           'name': 'identity',
           'forms': ['(identity something)'],
           'docstring': 'It just behaves as a proxy function'})
    def identity_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'identity' function implementation

        :param args: incoming 'identity' function arguments (only 1)
        :return: datatypes.Base

        """

        return args[0]
        # 'identity' function is required for internal purposes (for example, AST requires it). Can be used elsewhere

    #################################################################################################################

    @staticmethod
    @meta({'name': 'conj',
           'forms': ['(conj)',
                     '(conj collection)',
                     '(conj collection item1 item2 ... itemN)'],
           'docstring': 'Returns empty Vector; collection (maybe with the items appended)'})
    def conj_func(args: List[datatypes.Collection or datatypes.Base]) -> (datatypes.Nil or
                                                                          datatypes.Collection):
        """
        Builtin 'conj' function implementation

        :param args: incoming 'conj' function arguments (collection, list of the items to append).
        :return: datatypes.Collection
        """

        coll: datatypes.Collection
        elements: List[datatypes.Base]

        if len(args) == 0:
            return datatypes.Vector(tuple())  # <------- return an empty Vector, if there are no collection and items
        if len(args) == 1:
            return args[0]  # <----------------- return collection if there is only collection and no items to append

        coll, *elements = args

        assert issubclass(coll.__class__, (datatypes.Nil,
                                           datatypes.Collection,)),    'conj: 1st argument needs to be a coll or nil'

        if isinstance(coll, datatypes.Nil):
            return datatypes.Vector(tuple(elements)) if elements else coll  # <- handle a case when collection is nil

        return coll.conj(elements)  # <- Collection.conj() should return a new collection with all the items appended

        # If no arguments, return empty Vector; if only collection, return collection; collection with items appended

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1],
                    [Spec.EachArgumentTypeIs, datatypes.Function]],
           'name': 'wrapped',
           'forms': ['(wrapped function)'],
           'docstring': 'Returns wrapped Function to use as a callback'})
    def wrapped_func(args: List[datatypes.Function]) -> datatypes.Py3Object:
        """
        Builtin 'wrapped' function implementation

        :param args: incoming 'wrapped' function arguments (a Function Type)
        :return: datatypes.Py3Object

        """

        function: datatypes.Function = args[0]

        def adapted(_args: list, kwargs: dict):

            return (datatypes.HashMap((datatypes.Keyword('args'), datatypes.Py3Inst(_args),
                                       datatypes.Keyword('kwargs'), datatypes.Py3Inst(kwargs))),)

        return datatypes.Py3Object(lambda *_args, **kwargs: function.reference()(adapted(_args, kwargs)).reference())

        # This function will return specially formed Py3Object to call a NanamiLang function handler inside a Python3

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2, 3]],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.HashSet,
                                                        datatypes.Base],
                                                       [datatypes.HashSet,
                                                        datatypes.Base, datatypes.Base],
                                                       [datatypes.Vector,
                                                        datatypes.IntegerNumber],
                                                       [datatypes.Vector,
                                                        datatypes.IntegerNumber, datatypes.Base],
                                                       [datatypes.HashMap,
                                                        datatypes.Base],
                                                       [datatypes.HashMap,
                                                        datatypes.Base, datatypes.Base],
                                                       [datatypes.Py3Inst,
                                                        datatypes.Keyword],
                                                       [datatypes.Py3Inst,
                                                        datatypes.Keyword, datatypes.Base],
                                                       [datatypes.Py3Object,
                                                        datatypes.Keyword],
                                                       [datatypes.Py3Object,
                                                        datatypes.Keyword, datatypes.Base],
                                                       [datatypes.String,
                                                        datatypes.IntegerNumber],
                                                       [datatypes.String,
                                                        datatypes.IntegerNumber, datatypes.String]]]],
           'name': 'get',
           'forms': ['(get coll-string-or-interop by)',
                     '(get coll-string-or-interop by default)'],
           'docstring': 'Returns element from the collection or string; returns interop type\' symbol'})
    def get_func(args: List[datatypes.Base]) -> datatypes.Base:
        """
        Builtin 'get' function implementation

        :param args: incoming 'get' function arguments (coll/string/interop type and key, index, element)
        :return: datatypes.Base
        """

        coll_string_or_interop_data_type: datatypes.Collection or datatypes.Py3Object or datatypes.Py3Inst
        by: datatypes.Base
        by_default: datatypes.Base

        coll_string_or_interop_data_type, by, by_default = args if len(args) == 3 else args + [datatypes.Nil('nil')]

        return coll_string_or_interop_data_type.get(by, default=by_default)
        # Function can take 2 or 3 arguments, optional third argument is a 'default' value, which is a Nil by default

    #################################################################################################################

    @staticmethod
    @meta({'name': 'str',
           'forms': ['(str)',
                     '(str e1 e2 ... eX)'],
           'docstring': 'Compiles all given elements to String'})
    def str_func(args: List[datatypes.Base]) -> datatypes.String:
        """
        Builtin 'str' function implementation

        :param args: incoming 'str' function arguments (elements).
        :return: datatypes.Vector
        """

        return datatypes.String(''.join([x.to_py_str() for x in args]))
        # Using each element to_py_str() method in order to build a str

    #################################################################################################################

    @staticmethod
    @meta({'name': 'make-vector',
           'forms': ['(make-vector)',
                     '(make-vector e1 e2 ... eX)'],
           'docstring': 'Creates a(n empty) Vector data structure'})
    def make_vector_func(args: List[datatypes.Base]) -> datatypes.Vector:
        """
        Builtin 'make-vector' function implementation

        :param args: incoming 'make-vector' function arguments (elements).
        :return: datatypes.Vector
        """

        return datatypes.Vector(tuple(args))
        # Let the Collection.__init__() handle Vector structure construction

    #################################################################################################################

    @staticmethod
    @meta({'name': 'make-hashset',
           'forms': ['(make-hashset)',
                     '(make-hashset e1 e2 ... eX)'],
           'docstring': 'Creates a(n empty) HashSet data structure'})
    def make_hashset_func(args: List[datatypes.Base]) -> datatypes.HashSet:
        """
        Builtin 'make-hashset' function implementation

        :param args: incoming 'make-hashset' function arguments (elements).
        :return: datatypes.HashSet
        """

        return datatypes.HashSet(tuple(args))
        # Let the Collection.__init__() handle HashSet structure construction

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityEven]],
           'name': 'make-hashmap',
           'forms': ['(make-hashmap)',
                     '(make-hashmap k1 v2 ... kX vX)'],
           'docstring': 'Creates a(n empty) HashMap data structure'})
    def make_hashmap_func(args: List[datatypes.Base]) -> datatypes.HashMap:
        """
        Builtin 'make-hashmap' function implementation

        :param args: incoming 'make-hashmap' function arguments (elements).
        :return: datatypes.HashMap
        """

        return datatypes.HashMap(tuple(args))
        # Let the Collection.__init__() handle HashMap structure construction

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Symbol],
                                                       [datatypes.Vector]]]],
           'name': 'import',
           'forms': ['(import \'name)',
                     '(import [\'name])',
                     '(import [\'name :refer :all])',
                     '(import [\'name :refer [\'foo \'bar ...]])'],
           'docstring': 'Returns imported Python 3 module wrapped as a Py3Object or Nil'})
    def import_func(args: List[datatypes.Symbol or datatypes.Vector]) -> (datatypes.Nil or
                                                                          datatypes.Py3Object):
        """
        Builtin 'import' function implementation

        :param args: incoming 'import' function arguments (vector with the options or a symbol).
        :return: datatypes.Py3Object
        """

        argument = args[0]

        refer_names = []

        nil = datatypes.Nil('nil')

        if isinstance(argument, datatypes.Symbol):
            return datatypes.Py3Object(__import__(argument.reference()))  # <---------- that's it

        argument: datatypes.Vector  # <--- tell the Python that 1st argument is actually a Vector

        if not argument.items():
            return nil  # <------------------ if argument is actually an empty Vector, return nil

        module_name_symbol, *import_opts = argument.items()

        if not isinstance(module_name_symbol, datatypes.Symbol):
            return nil  # <--------------------------- if module name is not a Symbol, return nil

        module_name_symbol: datatypes.Symbol  # <--- tell the Python that it is actually a Symbol

        if not import_opts or len(import_opts) % 2 != 0:  # <----- import opts missing or invalid
            return datatypes.Py3Object(__import__(module_name_symbol.reference()))  # <--- import

        import_opts_hash_map = datatypes.HashMap(import_opts)  # <--- make a HashMap from options
        import_refer_option_or_nil = import_opts_hash_map.get(datatypes.Keyword('refer'))       #

        if (isinstance(import_refer_option_or_nil, datatypes.Vector)
                and import_refer_option_or_nil.items()):  # <---- it is a Vector, it is non-empty
            # TODO: maybe check that all Vector elements are actually Symbol data type instances?
            refer_names = [nsymbol.reference() for nsymbol in import_refer_option_or_nil.items()]

        elif (isinstance(import_refer_option_or_nil, datatypes.Keyword)
              and import_refer_option_or_nil.reference() == 'all'):  # <--- it's the :all Keyword
            refer_names = ['*']  # <-------- '*' tells the __import__ to actually refer all names

        if refer_names:
            return datatypes.Py3Object(__import__(
                module_name_symbol.reference(),
                fromlist=refer_names,
                level=0))  # <----------------------------- import, referring required names only
        return datatypes.Py3Object(__import__(module_name_symbol.reference()))  # <------- import

        # Returns an imported Python 3 module wrapped using Nanamilang Py3Object data type or Nil

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 1]],
           'name': 'not',
           'forms': ['(not something)'],
           'docstring': 'Returns something\' truth inverted'})
    def not_func(args: List[datatypes.Base]) -> datatypes.Boolean:
        """
        Builtin 'not' function implementation

        :param args: incoming 'not' function arguments
        :return: datatypes.String
        """

        return datatypes.Boolean(not args[0].truthy())
        # All NanamiLang Data Types require their truthy() retval to be explicitly cast into NanamiLang Boolean type.

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne]],
           'name': '=',
           'forms': ['(= e1 e2 ... eX)'],
           'docstring': 'Returns equity comparison result'})
    def eq_func(args: List[datatypes.Base]) -> datatypes.Boolean:
        """
        Builtin '=' function implementation

        :param args: incoming '=' function arguments (any known data types)
        :return: datatypes.Boolean
        """

        _eq = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                _eq = True
                break
            _eq = curr.hashed() == _next.hashed()
            if not _eq:
                break

        return datatypes.Boolean(_eq)  # once '_eq == False', or there is no next element to compare, exit = function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '<',
           'forms': ['(< n1 n2 ... nX)'],
           'docstring': 'Returns \'less than\' comparison result'})
    def less_than_func(args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '<' function implementation

        :param args: incoming '<' function arguments (only numeric values allowed)
        :return: datatypes.Boolean
        """

        _lt = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                _lt = True
                break
            _lt = curr.reference() < _next.reference()
            if not _lt:
                break

        return datatypes.Boolean(_lt)  # once '_lt == False', or there is no next element to compare, exit < function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '>',
           'forms': ['(> n1 n2 ... nX)'],
           'docstring': 'Returns \'greater than\' comparison result'})
    def greater_than_func(args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '>' function implementation

        :param args: incoming '>' function arguments (only numeric values allowed)
        :return: datatypes.Boolean
        """

        _gt = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                _gt = True
                break
            _gt = curr.reference() > _next.reference()
            if not _gt:
                break

        return datatypes.Boolean(_gt)  # once '_gt == False', or there is no next element to compare, exit < function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '<=',
           'forms': ['(<= n1 n2 ... nX)'],
           'docstring': 'Returns \'less-than-equal\' comparison result'})
    def less_than_eq_func(args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '<=' function implementation

        :param args: incoming '<=' function arguments (numeric data types only allowed)
        :return: datatypes.Boolean
        """

        _lte = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                _lte = True
                break
            _lte = curr.reference() <= _next.reference()
            if not _lte:
                break

        return datatypes.Boolean(_lte)  # once '_lte == False', or there is no next element to compare, exit function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '>=',
           'forms': ['(>= n1 n2 ... nX)'],
           'docstring': 'Returns \'greater-than-equal\' comparison result'})
    def greater_than_eq_func(args: List[datatypes.Numeric]) -> datatypes.Boolean:
        """
        Builtin '>=' function implementation

        :param args: incoming '>=' function arguments (only numeric data types allowed)
        :return: datatypes.Boolean
        """

        _gte = False
        for idx, curr in enumerate(args):
            _next = get(args, idx + 1, None)
            if not _next:
                _gte = True
                break
            _gte = curr.reference() >= _next.reference()
            if not _gte:
                break

        return datatypes.Boolean(_gte)  # once '_gte == False', or there is no next element to compare, exit function

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '+',
           'forms': ['(+)', '(+ n1 n2 ... nX)'],
           'docstring': 'Applies "+" operation to given numbers'})
    def add_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '+' function implementation

        :param args: incoming '+' function arguments (only numeric here)
        :return: either datatypes.IntegerNumber or datatypes.FloatNumber
        """

        if not args:
            return datatypes.IntegerNumber(0)

        result = reduce(lambda _, x: _ + x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '-',
           'forms': ['(- n1 n2 ... nX)'],
           'docstring': 'Applies "-" operation to given numbers'})
    def sub_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '-' function implementation

        :param args: incoming '-' function arguments (only numeric here)
        :return: either datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ - x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '*',
           'forms': ['(*)', '(* n1 n2 ... nX)'],
           'docstring': 'Applies "*" operation to given numbers'})
    def mul_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '*' function implementation

        :param args: incoming '*' function arguments (only numeric here)
        :return: either datatypes.IntegerNumber or datatypes.FloatNumber
        """

        if not args:
            return datatypes.IntegerNumber(1)

        result = reduce(lambda _, x: _ * x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': '/',
           'forms': ['(/ n1 n2 ... nX)'],
           'docstring': 'Applies "/" operation to given numbers'})
    def divide_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin '/' function implementation

        :param args: incoming '/' function arguments (only numeric here)
        :return: either datatypes.IntegerNumber or datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ / x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityAtLeastOne],
                    [Spec.EachArgumentTypeIs, datatypes.Numeric]],
           'name': 'mod',
           'forms': ['(mod n1 n2 ... nX)'],
           'docstring': 'Applies "mod" operation to given numbers'})
    def modulo_func(args: List[datatypes.Numeric]) -> datatypes.Numeric:
        """
        Builtin 'mod' function implementation

        :param args: incoming 'mod' function arguments (only numeric here)
        :return: either datatypes.IntegerNumber or a datatypes.FloatNumber
        """

        result = reduce(lambda _, x: _ % x, map(lambda n: n.reference(), args))

        return datatypes.IntegerNumber(result) if isinstance(result, int) else datatypes.FloatNumber(result)

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityVariants, [2, 3]],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Function, datatypes.String],
                                                       [datatypes.Function, datatypes.Base, datatypes.String],
                                                       [datatypes.Function, datatypes.Collection],
                                                       [datatypes.Function, datatypes.Base, datatypes.Collection]]]],
           'name': 'reduce',
           'forms': ['(reduce function collection-or-string)',
                     '(reduce function initial collection-or-string)'],
           'docstring': 'Allows to reduce collection-or-string elements with the given (anonymous) Function'})
    def reduce_func(args: List[datatypes.Base]) -> datatypes.Base or datatypes.NException:
        """
        Builtin 'reduce' function implementation

        :param args: incoming 'reduce' function arguments (coll/string (initial value), and maybe anonymous function)
        :return: datatypes.Base
        """

        function: datatypes.Function
        initial: datatypes.Base or datatypes.Nil
        resulted: datatypes.Base or datatypes.Nil
        collection_or_string: datatypes.Collection

        initial = None  # <--------------------------------------------------------------- dispatch actual value next

        if len(args) == 2:
            function, collection_or_string = args  # <--- if user has only supplied function and collection to reduce
        else:
            function, initial, collection_or_string = args  # <------------------- if user has supplied initial value

        items = collection_or_string.items()

        if len(items) == 1 and not initial:
            return items[0]  # <- if coll has only one item (and there is no initial),return it; do not call function

        if not items:

            if initial:
                return initial  # <----- if collection is empty, but user has passed initial value, return it instead

            return function.reference()([])  # <------ if collection is empty, return function call with no arguments

        items = items if not initial else (initial,) + items  # <------------------------ build the final items tuple
        resulted = items[0]  # <------------------------------------------------ start with the first collection item

        for item in items[1:]:
            resulted = function.reference()([resulted, item])  # each time, function gets res and new collection item
            if isinstance(resulted, datatypes.NException):
                return resulted  # <------------------------------ if we ran into NException, we need to propagate it

        return resulted  # <--------------------------------------------------------------- return resulted data type

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Keyword, datatypes.Collection],
                                                       [datatypes.Function, datatypes.String],
                                                       [datatypes.Function, datatypes.Collection]]]],
           'name': 'map',
           'forms': ['(map function coll-or-string)'],
           'docstring': 'Allows to map coll/string elements with the given (anonymous) Function or Keyword-Fn'})
    def map_func(args: List[datatypes.Base]) -> datatypes.Vector or datatypes.NException:
        """
        Builtin 'map' function implementation

        :param args: incoming 'map' function arguments  (coll/string and maybe anonymous function or keyword-fn)
        :return: datatypes.Vector
        """

        function: datatypes.Function or datatypes.Keyword
        coll_or_string: datatypes.Collection or datatypes.String

        function, coll_or_string = args

        if isinstance(function, datatypes.Keyword):
            k = function
            function = datatypes.Function(
                {'function_name': randstr(),
                 'function_reference': lambda _a_: BuiltinFunctions.get_func(_a_ + [k])})

        _ = []
        for item in coll_or_string.items():
            res = function.reference()([item])
            if isinstance(res, datatypes.NException):
                return res  # <----------------------------------- if we ran into NException, we need to propagate it
            _.append(res)

        return datatypes.Vector(tuple(_))  # <----------- return a resulting vector of the mapped collection elements

    #################################################################################################################

    @staticmethod
    @meta({'spec': [[Spec.ArityIs, 2],
                    [Spec.ArgumentsTypeChainVariants, [[datatypes.Keyword, datatypes.Collection],
                                                       [datatypes.Function, datatypes.String],
                                                       [datatypes.Function, datatypes.Collection]]]],
           'name': 'filter',
           'forms': ['(filter function coll-or-string)'],
           'docstring': 'Allows to filter coll/string elements with the given (anonymous) Function or Keyword-Fn'})
    def filter_func(args: List[datatypes.Base]) -> datatypes.Vector or datatypes.NException:
        """
        Builtin 'filter' function implementation

        :param args: incoming 'filter' function arguments  (coll/string and maybe anonymous function or a keyword-fn)
        :return: datatypes.Vector
        """

        function: datatypes.Function or datatypes.Keyword
        coll_or_string: datatypes.Collection or datatypes.String

        function, coll_or_string = args

        if isinstance(function, datatypes.Keyword):
            k = function
            function = datatypes.Function(
                {'function_name': randstr(),
                 'function_reference': lambda _a_: BuiltinFunctions.get_func(_a_ + [k])})

        _ = []
        for item in coll_or_string.items():
            res = function.reference()([item])
            if isinstance(res, datatypes.NException):
                return res  # <----------------------------------- if we ran into NException, we need to propagate it
            if res.truthy():
                _.append(item)

        return datatypes.Vector(tuple(_))  # <--------- return a resulting vector of the filtered collection elements

    #################################################################################################################
