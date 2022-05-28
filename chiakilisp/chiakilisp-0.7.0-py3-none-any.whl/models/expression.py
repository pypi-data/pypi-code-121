# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements

from copy import deepcopy
from typing import List, Any, Callable
from chiakilisp.utils import get_assertion_closure
from chiakilisp.models.value import Value, NotFound, Nil

Child = Value or 'Expression'  # define the type for a single child
Children = List[Child]  # define a type describing list of children


class ArityError(SyntaxError):

    """ArityError (just for name)"""


NE_ASSERT = get_assertion_closure(NameError)  # <------ raises a NameError
AR_ASSERT = get_assertion_closure(ArityError)  # <--- raises an ArityError
SE_ASSERT = get_assertion_closure(SyntaxError)  # <-- raises a SyntaxError
RT_ASSERT = get_assertion_closure(RuntimeError)  # <-- raises RuntimeError


def IDENTIFIER_ASSERT(value: Value, message: str) -> None:

    """A handy shortcut to make assertion that Value is Identifier"""

    token = value.token()

    SE_ASSERT(token.position_formatted(), token.is_identifier(), message)


class Expression:

    """
    Expression is the class that indented to be used to calculate something
    """

    _children: Children

    def __init__(self, children: Children) -> None:

        """Initialize Expression instance"""

        self._children = children

    def children(self) -> Children:

        """Returns expression children"""

        return self._children

    def lint(self, _: dict, rule: str, storage: dict) -> None:

        """React to the builtin linter visit"""

        head: Value
        tail: Children
        head, *tail = self.children()
        assert isinstance(head, Value),     'Expression[lint]: head should be a Value, not an Expression instance'

        where = head.token().position_formatted()

        IDENTIFIER_ASSERT(head,                       'Expression[lint]: head of expression should be Identifier')

        if head.token().value() == 'def':
            AR_ASSERT(where, len(tail) == 2,                    'Expression[lint]: def: expected exactly 2 forms')
            name: Value = tail[0]
            assert isinstance(name, Value), 'Expression[lint]: name should be a Value, not an Expression instance'
            IDENTIFIER_ASSERT(name,                         'Expression[lint]: def: name should be an Identifier')

            if rule == 'UnusedGlobalVariables':
                storage[name.token().value()] = 0    # since we define global variable with def, add it to storage

    def generate(self, _e: dict, _, inline: bool):

        """Generate C++ representation of expression"""

        head: Value
        rest: Children
        head, *rest = self.children()

        assert isinstance(head, Value),   'Expression[generate]: head should be a Value object instance'

        IDENTIFIER_ASSERT(head,      'Expression[generate]: head of expression should be an Identifier')

        cpp_function_name = _e.get(head.token().value())  # <--- get the CPP function name from glossary

        lines = [f'{cpp_function_name}(']  # <--- start with the function call: name and opening bracket

        arguments = []  # <------------------ a list holding all the generated "arguments" to a function

        for each in rest:
            arguments.append(each.generate(_e, '', True))  # <- recursively populate a list of arguments

        lines.append(', '.join(arguments))  # <--- join all the function "arguments" by a coma character

        lines.append(')' if inline else ');')  # <- close the function call with closing bracket and ';'

        return ''.join(lines)  # <------------------------------ at the end, return all the lines joined

    def execute(self, environ: dict, top: bool = True) -> Any:

        """Execute here, is the return Python value 3 related to the expression: string, number, and vice versa"""

        head: Value
        tail: Children

        assert self.children(),      'Expression[execute]: current expression has no values, unable to execute it'

        head, *tail = self.children()
        where = head.token().position_formatted()  # <-- when make assertions on expression head, this can be used

        IDENTIFIER_ASSERT(head,             'Expression[execute]: head of the expression should be an Identifier')

        if head.token().value() == 'or':
            if not tail:
                return None  # <-------------------------- if there are no arguments given to the form, return nil
            result = None  # <----------------------------------------------- set result to the null pointer first
            for cond in tail:  # <-------------------------------------------- for each condition in the arguments
                result = cond.execute(environ, False)  # <------------------------------------- compute the result
                if result:
                    return result  # <------------------------------------ and if there is truthy value, return it
            return result  # <------- if all conditions have been evaluated to falsy ones, return the last of them

        if head.token().value() == 'and':
            if not tail:
                return True  # <------------------------- if there are no arguments given to the form, return true
            result = None  # <----------------------------------------------- set result to the null pointer first
            for cond in tail:  # <-------------------------------------------- for each condition in the arguments
                result = cond.execute(environ, False)  # <------------------------------------- compute the result
                if not result:
                    return result  # <----------------------------- and if there is None or False value, return it
            return result  # <------ if all conditions have been evaluated to truthy ones, return the last of them

        if head.token().value() == 'try':
            AR_ASSERT(where, len(tail) == 2,        'Expression[execute]: try: expected main and and catch forms')
            main, catch = tail
            SE_ASSERT(where, isinstance(catch, Expression),    'Expression[execute]: try: catch should be a form')
            AR_ASSERT(where, len(catch.children()) == 4,   'Expression[execute]: try: catch: expected 4 operands')
            kind, klass, alias, block = catch.children()
            IDENTIFIER_ASSERT(kind,                      'Expression[execute]: try: kind should be an Identifier')
            SE_ASSERT(where, kind.token().value() == 'catch',  "Expression[execute]: try: kind should be 'catch'")
            IDENTIFIER_ASSERT(klass,                       'Expression[execute]: try: klass should be Identifier')
            IDENTIFIER_ASSERT(alias,                       'Expression[execute]: try: alias should be Identifier')
            obj = klass.execute(environ, False)  # <---------------------------------- get actual exception object
            closure = {}
            closure.update(environ)  # <-- we do not want to modify global environment to store exception instance
            try:
                return main.execute(environ, False)  # <-------------------------------- try to execute main block
            except obj as exception:  # <------------------------------------------ if exception has been occurred
                closure[alias.token().value()] = exception  # <-------------------------- update local try closure
                return block.execute(closure, False)  # <------------------------ return exception handling result

        if head.token().value() == '->':
            if len(tail) == 1:
                return tail[-1].execute(environ, False)  # <------------ if there is only one argument, execute it

            tail = deepcopy(tail)  # <--------- it could be slow when tail is really complex nested data structure

            target, *rest = tail  # <------- split tail for the first time to initialize target and rest variables
            while len(tail) > 1:  # <-- do not leave the loop while there is at least one element left in the tail
                _ = rest[0]
                if isinstance(_, Value):
                    rest[0] = Expression([_])  # <-------- each argument except first should be cast to Expression
                rest[0].children().insert(1, target)  # <- in case of first-threading-macro, insert as the 1st arg
                tail = [rest[0]] + rest[1:]  # <- override tail: modified expression and the tail rest with offset
                target, *rest = tail  # <--------------------------- do the same we did before entering while-loop

            return target.execute(environ, False)  # <----- at the end, return target' expression execution result

        if head.token().value() == '->>':
            if len(tail) == 1:
                return tail[-1].execute(environ, False)  # <------------ if there is only one argument, execute it

            tail = deepcopy(tail)  # <--------- it could be slow when tail is really complex nested data structure

            target, *rest = tail  # <------- split tail for the first time to initialize target and rest variables
            while len(tail) > 1:  # <-- do not leave the loop while there is at least one element left in the tail
                _ = rest[0]
                if isinstance(_, Value):
                    rest[0] = Expression([_])  # <-------- each argument except first should be cast to Expression
                rest[0].children().append(target)  # <- in case of last-threading-macro, append to the end of args
                tail = [rest[0]] + rest[1:]  # <- override tail: modified expression and the tail rest with offset
                target, *rest = tail  # <--------------------------- do the same we did before entering while-loop

            return target.execute(environ, False)  # <----- at the end, return target' expression execution result

        if head.token().value().startswith('.') and not head.token().value() == '...':   # it could be an Ellipsis
            AR_ASSERT(where, len(tail) >= 1,        'Expression[execute]: dot-form: expected at least 1 operands')
            object_name: Value
            method_args: Children
            object_name, *method_args = tail
            method_name: str = head.token().value()[1:]
            object_instance = object_name.execute(environ, False)
            object_m_object: Callable = getattr(object_instance, method_name, NotFound)  # <---- could be NotFound
            NE_ASSERT(where,
                      object_m_object is not NotFound,
                      f"Expression[execute]: dot-form: no method named '{method_name}' found in '{object_name}'.")
            return object_m_object(*(child.execute(environ, False) for child in method_args))  # return its result

        if head.token().value() == 'if':
            AR_ASSERT(where, len(tail) == 3,                  'Expression[execute]: if: expected exactly 2 forms')
            cond, true, false = tail
            return true.execute(environ, False) if cond.execute(environ, False) else false.execute(environ, False)

        if head.token().value() == 'when':
            AR_ASSERT(where, len(tail) == 2,                  'Expression[execute]: if: expected exactly 2 forms')
            cond, true = tail
            return true.execute(environ, False) if cond.execute(environ, False) else None  # <-- false is just nil

        if head.token().value() == 'cond':
            AR_ASSERT(where, len(tail) % 2 == 0,       'Expression[execute]: cond: expected even number of forms')
            if not tail:
                return None  # <------------------------------------------ if nothing has been passed, return None
            for cond, expr in (tail[i:i + 2] for i in range(0, len(tail), 2)):
                if cond.execute(environ, False):
                    return expr.execute(environ, False)
            return None  # <------------------------------------------------------ if nothing is true, return None

        if head.token().value() == 'let':
            AR_ASSERT(where, len(tail) >= 1,          'Expression[execute]: let: expected at least bindings form')
            bindings, *body = tail
            if not body:
                body = [Nil]  # <----------- let the ... let have an empty body, in this case, result would be nil
            SE_ASSERT(where, isinstance(bindings, Expression), 'Expression[execute]: let: bindings is not a form')
            let = {}
            let.update(environ)  # we can't just bootstrap 'let' environ, because we do not want instances linking
            items = bindings.children()  # once again, lexically, that sounds a bit weird, we have to deal with it
            AR_ASSERT(where, len(items) % 2 == 0,         'Expression[execute]: let: binding form should be even')
            for raw, value in (items[i:i + 2] for i in range(0, len(items), 2)):
                if isinstance(raw, Expression):
                    get = environ.get('get')  # <------ here we go... should it be called like ChiakiLisp interop?
                    RT_ASSERT(get,           "Expression[execute]: let: destructuring requires core/get function")
                    executed = value.execute(let, False)  # <-- pre-execute value in order to treat it like a list
                    for idx, alias in enumerate(map(lambda val: val.token().value(), raw.children())):  # map over
                        let.update({alias: get(executed, idx, None)})  # <- for each alias get a coll value or nil
                else:
                    let.update({raw.token().value(): value.execute(let, False)})  # <---------- populate a closure
            return [child.execute(let, False) for child in body][-1]  # <- then return the last calculation result

        if head.token().value() == 'fn':
            AR_ASSERT(where, len(tail) >= 1,               'Expression[execute]: fn: expected at least 1 operand')
            parameters, *body = tail
            if not body:
                body = [Nil]  # <-- let a function be defined with empty body, in such a case, it will return None
            SE_ASSERT(where, isinstance(parameters, Expression), 'Expression[execute]: fn: parameters not a form')
            names = []
            children = parameters.children()
            ampersand_found = tuple(filter(lambda pr: (isinstance(pr[1], Value) and pr[1].token().value() == '&'),
                                           enumerate(children)))  # <- find a tuple, where 0 - pos, 1 - an operand
            ampersand_position: int = ampersand_found[0][0] if ampersand_found else -1  # <---- 0 - tuple, 1 - pos
            positional_parameters = children[:ampersand_position] if ampersand_found else children  # <-- before &
            for parameter in positional_parameters:
                IDENTIFIER_ASSERT(parameter,            'Expression[execute]: fn: parameter should be Identifier')
                names.append(parameter.token().value())  # <------- append name of the parameter to the names list
            can_take_extras = False  # <-------------------- by default, function can not take any extra arguments
            if ampersand_found:
                SE_ASSERT(where,
                          len(children) - 1 != ampersand_position,
                          'Expression[execute]: fn: you can only mention one alias for the extra arguments tuple')
                SE_ASSERT(where,
                          len(children) - 2 == ampersand_position,
                          'Expression[execute]: fn: you have to mention alias name for the extra arguments tuple')
                operand = children[-1]
                IDENTIFIER_ASSERT(operand, 'Expression[execute]: fn: extra-args-tuple alias should be Identifier')
                can_take_extras = True  # <- now we set this to true, as the function can now take extra arguments
                names.append(operand.token().value())  # <---- append extra args param name to all parameter names

            def handle(*c_arguments, **kwargs):

                """User-function handle object"""

                arity = len(names)
                if can_take_extras:
                    arity = arity - 1  # <------ because the last parameter is not actually a required one
                    AR_ASSERT(where,
                              len(c_arguments) >= arity,
                              f'<anonymous function>: wrong arity, expected at least {arity} argument(s)')
                else:
                    AR_ASSERT(where,
                              len(c_arguments) == arity,
                              f'<anonymous function>: wrong arity, expected exactly {arity} argument(s).')

                if can_take_extras:
                    if len(c_arguments) > arity:
                        e_arguments = c_arguments[arity:]
                        c_arguments = c_arguments[:arity] + (e_arguments,)  # <- can't be rewritten in a short way
                    else:
                        c_arguments = c_arguments + (tuple(),)  # <- if extras are possible but missing, set to ()

                fn = {}
                fn.update(environ)  # <--------- update (not bootstrap) fn closure environment with the global one
                fn.update(dict(zip(names, c_arguments)))  # <------------------- update fn closure with parameters
                fn.update({'kwargs': kwargs})  # <-------- currently, there is no way to pass them from ChiakiLisp
                return [child.execute(fn, False) for child in body][-1]  # <--- return the last calculation result

            handle.x__custom_name__x = '<anonymous function>'  # <-- set function name to the <anonymous function>
            return handle  # <---------------------- return the closure (anonymous function handler) to the caller

        if head.token().value() == 'def':
            SE_ASSERT(where, top,   'Expression[execute]: def: can only use (def) form at the top of the program')
            AR_ASSERT(where, len(tail) == 2,  'Expression[execute]: def: expected binding name and binding value')
            name, value = tail
            IDENTIFIER_ASSERT(name,                 'Expression[execute]: def: binding name should be Identifier')
            executed = value.execute(environ, False)
            environ.update({name.token().value(): executed})
            return executed   # so the reason, we write environment update is that we want to return binding value

        if head.token().value() == 'def?':
            SE_ASSERT(where, top, 'Expression[execute]: def?: can only use (def?) form at the top of the program')
            AR_ASSERT(where, len(tail) == 2, 'Expression[execute]: def?: expected binding name and binding value')
            name, value = tail
            IDENTIFIER_ASSERT(name,                'Expression[execute]: def?: binding name should be Identifier')
            from_env = environ.get(name.token().value()) if (name.token().value() in environ.keys()) else NotFound
            executed = value.execute(environ, False) if from_env is NotFound else from_env  # existing or executed
            environ.update({name.token().value(): executed})  # <--- update current scope' environment in any case
            return executed   # so the reason, we write environment update is that we want to return binding value

        if head.token().value() == 'defn':
            SE_ASSERT(where, top, 'Expression[execute]: defn: can only use (defn) form at the top of the program')
            AR_ASSERT(where, len(tail) >= 2,            'Expression[execute]: defn: expected at least 2 operands')
            name, parameters, *body = tail
            if not body:
                body = [Nil]  # <-- let a function be defined with empty body, in such a case, it will return None
            SE_ASSERT(where, isinstance(parameters, Expression),   'Expression[execute]: defn: params not a form')
            IDENTIFIER_ASSERT(name,               'Expression[execute]: defn: function name should be Identifier')
            names = []
            children = parameters.children()
            ampersand_found = tuple(filter(lambda pr: (isinstance(pr[1], Value) and pr[1].token().value() == '&'),
                                           enumerate(children)))  # <- find a tuple, where 0 - pos, 1 - an operand
            ampersand_position: int = ampersand_found[0][0] if ampersand_found else -1  # <---- 0 - tuple, 1 - pos
            positional_parameters = children[:ampersand_position] if ampersand_found else children  # <-- before &
            for parameter in positional_parameters:
                IDENTIFIER_ASSERT(parameter,          'Expression[execute]: defn: parameter should be Identifier')
                names.append(parameter.token().value())
            can_take_extras = False  # <-------------------- by default, function can not take any extra arguments
            if ampersand_found:
                SE_ASSERT(where,
                          len(children) - 1 != ampersand_position,
                          'Expression[execute]: defn: you can only mention one alias for the extra args\' tuple.')
                SE_ASSERT(where,
                          len(children) - 2 == ampersand_position,
                          'Expression[execute]: defn: you have to mention alias name for the extra args\' tuple.')
                operand = children[-1]
                IDENTIFIER_ASSERT(operand, 'Expression[execute]: defn: extra-args-list name should be Identifier')
                can_take_extras = True  # <- now we set this to true, as the function can now take extra arguments
                names.append(operand.token().value())  # <---- append extra args param name to all parameter names

            def handle(*c_arguments, **kwargs):  # pylint: disable=E0102  # <- handle object couldn't be redefined

                """User-function handle object"""

                arity = len(names)
                if can_take_extras:
                    arity = arity - 1  # <-------- because the last parameter is not actually a required one
                    AR_ASSERT(where,
                              len(c_arguments) >= arity,
                              f'{name.token().value()}: wrong arity, expected at least {arity} argument(s)')
                else:
                    AR_ASSERT(where,
                              len(c_arguments) == arity,
                              f'{name.token().value()}: wrong arity, expected exactly {arity} argument(s).')

                if can_take_extras:
                    if len(c_arguments) > arity:
                        e_arguments = c_arguments[arity:]
                        c_arguments = c_arguments[:arity] + (e_arguments,)  # <- can't be rewritten in a short way
                    else:
                        c_arguments = c_arguments + (tuple(),)  # <- if extras are possible but missing, set to ()

                defn = {}
                defn.update(environ)  # <------- update (not bootstrap) fn closure environment with the global one
                defn.update(dict(zip(names, c_arguments)))  # <--------------- update defn closure with parameters
                defn.update({'kwargs': kwargs})  # <------ currently, there is no way to pass them from ChiakiLisp
                return [child.execute(defn, False) for child in body][-1]  # <--=== return last calculation result

            handle.x__custom_name__x = name.token().value()  # assign custom function name to display it by pprint
            environ.update({name.token().value(): handle})  # in case of 'defn', we also need to update global env
            return handle  # <---------------------- return the closure (anonymous function handler) to the caller

        if head.token().value() == 'import':
            SE_ASSERT(where, top,    'Expression[execute]: import: you should place all the (import)s at the top')
            AR_ASSERT(where, len(tail) == 1, 'Expression[execute]: import: expected name of the module to import')
            name = tail[0]
            IDENTIFIER_ASSERT(name,      'Expression[execute]: import: Python 3 module name should be Identifier')
            environ[name.token().value()] = __import__(name.token().value())  # <- update env with a module object
            return None  # <--------------------------------------------------------------------------- return nil

        if head.token().value() == 'require':
            SE_ASSERT(where, top,  'Expression[execute]: require: you should place all the (require)s at the top')
            AR_ASSERT(where, len(tail) == 1,   'Expression[execute]: require: expected name of ChiakiLisp module')
            name = tail[0]
            IDENTIFIER_ASSERT(name,   'Expression[execute]: require: ChiakiLisp module name should be Identifier')
            module = type(name.token().value(), (object,), environ['require'](name.token().value() + '.cl'))  # -|
            environ[name.token().value().split('/')[-1]] = module  # <- update global environ with required module
            return None  # <--------------------------------------------------------------------------- return nil

        handle = head.execute(environ, False)
        arguments = tuple(map(lambda argument: argument.execute(environ, False), tail))
        return handle(*arguments)  # return handle execution result (which is Python 3 value) to the caller object
