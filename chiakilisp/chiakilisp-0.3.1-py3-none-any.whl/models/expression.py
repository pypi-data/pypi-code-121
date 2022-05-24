# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements

from typing import List, Any, Callable
from chiakilisp.models.token import Token
from chiakilisp.models.operand import Operand, NotFound

Child = Operand or 'Expression'  # define a type for a single child
Children = List[Child]  # define a type describing list of children


def is_identifier(x) -> bool:  # pylint: disable=invalid-name  # x is fine

    """
    Whether x is:
     - Operand (not Expression instance)
     - its token().type() is Token.Identifier

    :param x: literally any valid Python type
    :return: method returns comparison result
    """

    return isinstance(x, Operand) and x.token().type() == Token.Identifier


class Expression:

    """
    Expression is the class that indented to be used to calculate something
    """

    _children: List[Operand or "Expression"]

    def __init__(self, children: List[Operand or 'Expression']) -> None:

        """Initialize Expression instance"""

        self._children = children

    def children(self) -> Children:

        """Returns expression children"""

        return self._children

    def execute(self, environ: dict, top: bool = True) -> Any:

        """Execute here, is the return Python value related to the expression: string, number and vice versa"""

        head: Operand
        tail: Children

        assert self.children(),  'Expression::execute(): current expression has no operands, unable to execute it'

        head, *tail = self.children()
        assert is_identifier(head), 'Expression::execute(): expression head have to be a Token of type Identifier'

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
            assert len(tail) == 2, 'Expression::execute(): try: expected 2 expressions: main, and the catch block'
            main, catch = tail
            assert isinstance(catch, Expression), 'Expression::execute(): try: the catch block have to be a form'
            assert len(catch.children()) == 4, 'Expression::execute(): try: expected exactly three operands here'
            kind, klass, alias, block = catch.children()
            assert is_identifier(kind), 'Expression::execute(): try: handle name have to be Identifier'
            assert kind.token().value() == 'catch', "Expression::execute(): try: only supports a 'catch' handle"
            assert is_identifier(klass), 'Expression::execute(): try: class name have to be Identifier'
            assert is_identifier(alias), 'Expression::execute(): try: alias name have to be Identifier'
            obj = klass.execute(environ, False)  # <---------------------------------- get actual exception object
            closure = {}
            closure.update(environ)  # <-- we do not want to modify global environment to store exception instance
            try:
                main.execute(environ, False)  # <--------------------------------------- try to execute main block
            except obj as exception:  # <------------------------------------------ if exception has been occurred
                closure[alias.token().value()] = exception  # <-------------------------- update local try closure
                return block.execute(closure, False)  # <------------------------ return exception handling result

        if head.token().value() == '->':
            if len(tail) == 1:
                return tail[-1].execute(environ, False)  # <------------ if there is only one argument, execute it

            target, *rest = tail  # <------- split tail for the first time to initialize target and rest variables
            while len(tail) > 1:  # <-- do not leave the loop while there is at least one element left in the tail
                _ = rest[0]
                if isinstance(_, Operand):
                    rest[0] = Expression([_])  # <-------- each argument except first should be cast to Expression
                rest[0].children().insert(1, target)  # <- in case of first-threading-macro, insert as the 1st arg
                tail = [rest[0]] + rest[1:]  # <- override tail: modified expression and the tail rest with offset
                target, *rest = tail  # <--------------------------- do the same we did before entering while-loop

            return target.execute(environ, False)  # <----- at the end, return target' expression execution result

        if head.token().value() == '->>':
            if len(tail) == 1:
                return tail[-1].execute(environ, False)  # <------------ if there is only one argument, execute it

            target, *rest = tail  # <------- split tail for the first time to initialize target and rest variables
            while len(tail) > 1:  # <-- do not leave the loop while there is at least one element left in the tail
                _ = rest[0]
                if isinstance(_, Operand):
                    rest[0] = Expression([_])  # <-------- each argument except first should be cast to Expression
                rest[0].children().append(target)  # <- in case of last-threading-macro, append to the end of args
                tail = [rest[0]] + rest[1:]  # <- override tail: modified expression and the tail rest with offset
                target, *rest = tail  # <--------------------------- do the same we did before entering while-loop

            return target.execute(environ, False)  # <----- at the end, return target' expression execution result

        if head.token().value().startswith('.') and not head.token().value() == '...':  # special handling for ...
            assert len(tail) >= 1, 'Expression::execute(): dot-special-form: expected at least one argument there'
            object_name: Operand
            method_args: Children
            object_name, *method_args = tail
            method_name: str = head.token().value()[1:]
            object_instance = object_name.execute(environ, False)
            method_handler: Callable = getattr(object_instance, method_name, NotFound)  # NotFound is a stub class
            assert method_handler is not NotFound, 'Expression::execute(): dot-special-form: can\'t find a method'
            return method_handler(*(child.execute(environ, False) for child in method_args))  # execute the method

        if head.token().value() == 'if':
            assert len(tail) == 3, 'Expression::execute(): if-special-form: expected exactly three arguments here'
            cond, true, false = tail
            return true.execute(environ, False) if cond.execute(environ, False) else false.execute(environ, False)

        if head.token().value() == 'when':
            assert len(tail) == 2, 'Expression::execute(): when-special-form: expected exactly two arguments here'
            cond, true = tail
            false = Operand(Token(Token.Nil, 'nil'))
            return true.execute(environ, False) if cond.execute(environ, False) else false.execute(environ, False)

        if head.token().value() == 'let':
            assert len(tail) >= 1, 'Expression::execute(): let-special-form: expected at least one argument there'
            bindings, *body = tail
            assert isinstance(bindings, Expression), 'Expression::execute() let-special-form: wrong bindings type'
            let = {}
            items = bindings.children()  # once again, lexically, this sounds a bit weird, we have to deal with it
            assert len(items) % 2 == 0, 'Expression::execute() let-special-form: bindings should have even length'
            let.update(environ)  # we can't just bootstrap 'let' environ, because we do not want instances linking
            for name, value in (items[i:i + 2] for i in range(0, len(items), 2)):
                assert is_identifier(name), 'Expression::execute() let-special-form: name should be an Identifier'
                let.update({name.token().value(): value.execute(let, False)})
            return [child.execute(let, False) for child in body][-1]  # <- then return the last calculation result

        if head.token().value() == 'fn':
            assert len(tail) >= 1, "Expression::execute(): fn-special-form: expected at least two arguments there"
            parameters, *body = tail
            if not body:
                body = [Operand(Token(Token.Nil, 'nil'))]
            assert isinstance(parameters, Expression), 'Expression::execute(): fn-special-form: params not a form'
            names = []
            children = parameters.children()
            ampersand_found = tuple(filter(lambda pair: is_identifier(pair[1]) and pair[1].token().value() == '&',
                                           enumerate(children)))  # <- find a tuple, where 0 - pos, 1 - an operand
            ampersand_position: int = ampersand_found[0][0] if ampersand_found else -1  # <---- 0 - tuple, 1 - pos
            positional_parameters = children[:ampersand_position] if ampersand_found else children  # <-- before &
            for parameter in positional_parameters:
                assert is_identifier(parameter), 'Expression::execute() fn-special-form: parameter not Identifier'
                names.append(parameter.token().value())
            can_take_extras = False  # <-------------------- by default, function can not take any extra arguments
            if ampersand_found:
                assert len(children) - 1 != ampersand_position  # <--- ensure that the ampersand is not at the end
                assert len(children) - 2 == ampersand_position  # <--  ensure that the only one param goes after &
                operand = children[-1]
                assert is_identifier(operand), 'Expression::execute(): defn-special-form: param is not Identifier'
                can_take_extras = True  # <- now we set this to true, as the function now can take extra arguments
                names.append(operand.token().value())  # <- append extra parameter names to all fn parameter names

            def handle(*c_arguments, **kwargs):

                """User-function handle object"""

                arity = len(names)
                if can_take_extras:
                    arity = arity - 1  # <-------------- because the last parameter is not actually a required one
                    assert len(c_arguments) >= arity,    f'fn: wrong arity, expected at least {arity} argument(s)'
                else:
                    assert len(c_arguments) == arity,     f'fn: wrong arity, expected exactly {arity} argument(s)'

                if can_take_extras:
                    if len(c_arguments) > arity:
                        extra_arguments = c_arguments[arity:]
                        c_arguments = c_arguments[:arity] + (extra_arguments,)
                    else:
                        c_arguments = c_arguments + (tuple(),)  # <- if extras are possible but missing, set to ()

                closure = {}
                closure.update(environ)  # <------ update (not bootstrap!) closure environment with the global one
                closure.update(dict(zip(names, c_arguments)))  # <--------- update closure environ with parameters
                closure.update({'kwargs': kwargs})  # <--- currently, there is no way to pass them from ChiakiLisp
                return [child.execute(closure, False) for child in body][-1]  # return the last calculation result

            return handle

        if head.token().value() == 'def':
            assert top, 'Expression::execute(); def-special-form: unable to use (def) on current scope, use (let)'
            assert len(tail) == 2, 'Expression::execute(): def-special-form: incorrect arity, exactly 2 args here'
            name, value = tail
            assert is_identifier(name), 'Expression::execute() def-special-form binding name is not an Identifier'
            executed = value.execute(environ, False)
            environ.update({name.token().value(): executed})
            return executed

        if head.token().value() == 'defn':
            assert top, 'Expression::execute(): defn-special-form, unable to use (defn)  there, use (fn)  instead'
            assert len(tail) >= 2, 'Expression::execute(): defn-special-form: wrong arity, at least two args here'
            name, parameters, *body = tail
            if not body:
                body = [Operand(Token(Token.Nil, 'nil'))]
            assert isinstance(parameters, Expression), 'Expression::execute() defn-special-form: params\'re wrong'
            assert is_identifier(name), 'Expression::execute() defn-special-form: function name is not Identifier'
            names = []
            children = parameters.children()
            ampersand_found = tuple(filter(lambda pair: is_identifier(pair[1]) and pair[1].token().value() == '&',
                                           enumerate(children)))  # <- find a tuple, where 0 - pos, 1 - an operand
            ampersand_position: int = ampersand_found[0][0] if ampersand_found else -1  # <---- 0 - tuple, 1 - pos
            positional_parameters = children[:ampersand_position] if ampersand_found else children  # <-- before &
            for parameter in positional_parameters:
                assert is_identifier(parameter), 'Expression::execute() defn-special-form param\'s not Identifier'
                names.append(parameter.token().value())
            can_take_extras = False  # <-------------------- by default, function can not take any extra arguments
            if ampersand_found:
                assert len(children) - 1 != ampersand_position  # <--- ensure that the ampersand is not at the end
                assert len(children) - 2 == ampersand_position  # <--  ensure that the only one param goes after &
                operand = children[-1]
                assert is_identifier(operand), 'Expression::execute(): defn-special-form: param is not Identifier'
                can_take_extras = True  # <- now we set this to true, as the function now can take extra arguments
                names.append(operand.token().value())  # <- append extra parameter names to all fn parameter names

            def handle(*c_arguments, **kwargs):  # pylint: disable=E0102  # <- handle object couldn't be redefined

                """User-function handle object"""

                arity = len(names)
                if can_take_extras:
                    arity = arity - 1  # <-------------- because the last parameter is not actually a required one
                    assert len(c_arguments) >= arity,    f'fn: wrong arity, expected at least {arity} argument(s)'
                else:
                    assert len(c_arguments) == arity,     f'fn: wrong arity, expected exactly {arity} argument(s)'

                closure = {}
                closure.update(environ)  # <- update closure environment with the global one, not bootstrapping it

                if can_take_extras:
                    if len(c_arguments) > arity:
                        extra_arguments = c_arguments[arity:]
                        c_arguments = c_arguments[:arity] + (extra_arguments,)
                    else:
                        c_arguments = c_arguments + (tuple(),)  # <- if extras are possible but missing, set to ()

                closure.update(dict(zip(names, c_arguments)))  # <- update closure dictionary with parameter names
                closure.update({'kwargs': kwargs})  # <--- currently, there is no way to pass them from ChiakiLisp
                return [child.execute(closure, False) for child in body][-1]  # <-- return last calculation result

            handle.x__custom_name__x = name.token().value()  # assign custom function name to display it by pprint
            environ.update({name.token().value(): handle})  # in case of 'defn', we also need to update global env
            return handle

        if head.token().value() == 'import':
            assert top, 'Expression::execute(): import: you should only call \'import\' at the top of the program'
            assert len(tail) == 1, 'Expression::execute() import: expected exactly one argument: Identifier token'
            name = tail[0]
            assert is_identifier(name), 'Expression::execute() import: module name should be a type of Identifier'
            environ[name.token().value()] = __import__(name.token().value())  # <- update env with a module object
            return None  # <--------------------------------------------------------------------------- return nil

        if head.token().value() == 'require':
            assert top, 'Expression::execute(): require: you should only call \'require\' at the top of a program'
            assert len(tail) == 1, 'Expression::execute() require: expected exactly one argument Identifier token'
            name = tail[0]
            assert is_identifier(name), 'Expression::execute() require module name should be a type of Identifier'
            module = type(name.token().value(), (object,), environ['require'](name.token().value() + '.cl'))  # -|
            environ[name.token().value().split('/')[-1]] = module  # <--update global environ with required module
            return None  # <--------------------------------------------------------------------------- return nil

        handle = head.execute(environ, False)
        arguments = tuple(map(lambda argument: argument.execute(environ, False), tail))
        return handle(*arguments)  # return handle execution result (which is Python 3 value) to the caller object
