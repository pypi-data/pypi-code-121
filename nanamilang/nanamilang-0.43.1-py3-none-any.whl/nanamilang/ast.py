"""NanamiLang AST CLass"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List
from functools import wraps

from nanamilang.spec import Spec
from nanamilang import datatypes
from nanamilang.token import Token
from nanamilang.shortcuts import (
    ASSERT_IS_CHILD_OF,
    ASSERT_COLLECTION_NOT_EMPTY,
    ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF
)
from nanamilang.builtin import BuiltinFunctions


def handle(exceptions: tuple, m_name: str):
    """
    NanamiLang AST, handle exceptions:
    1. If exception has been suddenly raised
    2. Try to determine position where it happened
    3. Create & return datatypes.MException instance

    :param exceptions: tuple of exceptions to handle
    :param m_name: name of current nanamilang module
    """

    def wrapped(_fn):
        @wraps(_fn)
        def function(*args, **kwargs):
            try:
                return _fn(*args, **kwargs)
            except exceptions as exception:
                # Try to determine exception occurrence position
                # First, let's make it in the cheapest way ever:
                position = getattr(exception, '_position', None)
                # Non-custom exceptions obviously do not contain
                # _position; as we're working with s-expressions,
                # assume that exception occurred at the start of form.
                if not position:
                    tree: list = args[1]
                    maybe_token: Token = tree[0]
                    if isinstance(maybe_token, Token):
                        position = maybe_token.position()
                # We tried so hard ... but position is still unknown
                # So we use mock position triplet (1st line, 1st char)
                if not position:
                    position = (m_name, 1, 1)
                return datatypes.NException((exception,     position))

        return function

    return wrapped


class ASTBuildInvalidInput(Exception):
    """
    NML AST Build Error: Invalid input
    """

    def __str__(self):
        """NanamiLang ASTBuildInvalidInput"""

        # Do not scare AST._create() please :(
        return 'Unable to create an AST from input'


class ASTBuildInvalidToken(Exception):
    """
    NML AST Build Error: Invalid token
    """

    _token: Token
    _position: tuple

    def __str__(self):
        """NanamiLang ASTBuildInvalidToken"""

        return self._token.reason()

    def __init__(self, token: Token, *args):
        """NanamiLang ASTBuildInvalidToken"""

        self._token = token
        self._position = token.position()

        super(ASTBuildInvalidToken).__init__(*args)


class ASTEvalNotFoundInThisContent(Exception):
    """
    NML AST Eval Error: Not found in this content
    """

    _name: str
    _position: tuple

    def __init__(self, token: Token, *args):
        """NanamiLang ASTEvalNotFoundInThisContent"""

        # token.dt().origin() is the actual identifier name
        self._name = token.dt().origin()
        self._position = token.position()

        super(ASTEvalNotFoundInThisContent).__init__(*args)

    def __str__(self):
        """NanamiLang ASTEvalNotFoundInThisContent"""

        return f"There's no '{self._name}' in this context"


class ASTEvalIsNotAFunctionDataType(Exception):
    """
    NML AST Eval Error: Not a function data type
    """

    _name: str
    _position: tuple

    def __init__(self, token: Token, *args):
        """NanamiLang ASTEvalIsNotAFunctionDataType"""

        # Would be either a name of (re)defined identifier,
        # or name of the data type user has tried to call()
        self._name = token.dt().origin() or token.dt().name
        self._position = token.position()

        super(ASTEvalIsNotAFunctionDataType).__init__(*args)

    def __str__(self):
        """NanamiLang ASTEvalIsNotAFunctionDataType"""

        return f'"{self._name}" is not a Function Data Type'


class ASTEvalInvalidDotExprArity(Exception):
    """
    NML AST Eval Error: Invalid dot-expr arity
    """

    _name: str
    _position: tuple

    def __init__(self, token: Token, *args):
        """NanamiLang ASTEvalInvalidDotExprArity"""

        # Would be either a name of (re)defined identifier,
        # or name of the data type user has tried to call()
        self._name = token.dt().origin() or token.dt().name
        self._position = token.position()

        super(ASTEvalInvalidDotExprArity).__init__(*args)

    def __str__(self):
        """NanamiLang ASTEvalInvalidDotExprArity"""

        return f'{self._name}: invalid dot-expression arity'


class ASTEvalNotExportedMethod(Exception):
    """
    NML AST Eval Error: Method wasn't exported (or missing)
    """

    _name: str
    _position: tuple

    def __init__(self, token: Token, *args):
        """NanamiLang ASTEvalNotExportedMethod"""

        # Would be either a name of (re)defined identifier,
        # or name of the data type user has tried to call()
        self._name = token.dt().origin() or token.dt().name
        self._position = token.position()

        super(ASTEvalNotExportedMethod).__init__(*args)

    def __str__(self):
        """NanamiLang ASTEvalNotExportedMethod"""

        return f'Unable to call method named "{self._name}"'


class AST:
    """
    NanamiLang AST (abstract syntax tree)
    """

    _m_name: str = None
    _tokenized: List[Token] = None
    _wood: List[List[Token] or Token] = None

    def __init__(self, tokenized: List[Token], m_name: str) -> None:
        """
        Initialize a new NanamiLang AST instance

        :param m_name: a module name to built AST for
        :param tokenized: collection of Token instances
        """

        ASSERT_IS_CHILD_OF(m_name, str,
                           'AST: module name needs to be a string')
        ASSERT_COLLECTION_NOT_EMPTY(
            m_name, 'AST: module name could not be an empty string')

        ASSERT_IS_CHILD_OF(tokenized, list,
                           'AST: token instances needs to be a list')
        ASSERT_COLLECTION_NOT_EMPTY(
            tokenized, 'AST: at least 1 token instance was expected')
        ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
            tokenized,
            Token,
            'AST: each tokens instances list item needs to be Token')

        self._m_name = m_name
        self._tokenized = tokenized

        # If something went wrong, cast occurred exception into custom
        # NException instance, and only store NException Token in wood
        try:
            self._wood = self._create()
        except (Exception,) as _:
            exc_traceback = _.__traceback__
            self._wood = [Token(
                Token.NException,
                (ASTBuildInvalidInput().with_traceback(exc_traceback),
                 (m_name, 1, 1)))]

    @staticmethod
    def dot(name, inst, args) -> (None
                                  or datatypes.Base):
        """NanamiLang AST, handle a dot-expression"""

        method = getattr(inst, name, None)
        if not method:
            return None

        exported = getattr(method, 'exported', None)
        if not exported:
            return None

        # export() will cover method with spec rules
        method_spec_rules = getattr(method, 'specs')

        Spec.validate(
            f'{inst}.{name}', args, method_spec_rules)

        return method(*args)  # call and return result

    def wood(self) -> list:
        """NanamiLang AST, self._wood getter"""

        return self._wood

    def _create(self) -> Token or List[Token] or list:
        """NanamiLang AST, create an actual wood of trees"""

        # Initially was written by @buzzer13 (https://gitlab.com/buzzer13)

        items = []
        stack = [items]

        for token in self._tokenized:

            if token.type() == Token.ListBegin:

                wired = []
                stack[-1].append(wired)
                stack.append(wired)

            elif token.type() == Token.ListEnd:

                stack.pop()

            elif token.type() == Token.Invalid:

                # Propagate Invalid token as a NException
                return [Token(
                    Token.NException,
                    (ASTBuildInvalidToken(token), token.position())
                )]

            else:

                stack[-1].append(token)

        return items  # <- finally, return a built wood for a current module

    def evaluate(self, module_env) -> tuple:
        """NanamiLang AST, evaluate entire NanamiLang module recursively"""

        @handle((Exception,), self._m_name)
        def recursive(local_env: dict,
                      token_or_form: Token or List[Token]) -> datatypes.Base:
            if not token_or_form:
                return datatypes.Nil('nil')  # <--- if current tree is empty, return a Nil data type
            if isinstance(token_or_form, Token):
                return recursive(local_env, [Token(Token.Identifier, 'identity'),
                                             token_or_form])  # <--- it is just a temporary solution
            args: List[datatypes.Base] = []
            identifier_token_or_form: List[Token] or Token
            rest: List[Token or List[Token]]
            identifier_token_or_form, *rest = token_or_form
            # If identifier_token_or_form is a Token.Identifier pointing to Macro, handle macro call
            if isinstance(identifier_token_or_form, Token):
                if isinstance(identifier_token_or_form.dt(), datatypes.Macro):
                    macro = identifier_token_or_form.dt()
                    return recursive(local_env, macro.reference()(rest,
                                                                  local_env, module_env, recursive))
            # Start collecting args list to handle Function call, recursively evaluating expressions
            for argument_token_or_form in rest:
                # If the next function argument token (or form) is actually a Token instance, handle
                if isinstance(argument_token_or_form, Token):
                    bundled = argument_token_or_form.dt()  # store a Token's bundled data type first
                    # If Token bundled data type is actually an exception raised above, propagate it
                    if isinstance(bundled, datatypes.NException):
                        return bundled
                    # If token is Identifier, try to lookup for the local, then global user bindings
                    if argument_token_or_form.identifier():
                        mb_bound = local_env.get(bundled.origin(), module_env.get(bundled.origin()))
                        # If user bound data type is actually an exception raised earlier, propagate
                        if mb_bound and isinstance(mb_bound, datatypes.NException):
                            return mb_bound
                        # If Identifier was marked as Undefined and wasn't bound, raise an exception
                        if isinstance(bundled, datatypes.Undefined) and not mb_bound:
                            raise ASTEvalNotFoundInThisContent(argument_token_or_form)
                        args.append(mb_bound or bundled)  # <--- add user bound or bundled data type
                    else:
                        args.append(bundled)  # <----------------------------- add bundled data type
                # If the next function argument token (or form) is actually an expression, handle it
                else:
                    expression_result_or_nexception = recursive(local_env, argument_token_or_form)
                    # Propagate possibly occurred exception raised during recursive form evaluation.
                    if isinstance(expression_result_or_nexception, datatypes.NException):
                        return expression_result_or_nexception
                    # If expression form has been evaluated to an average data type, add it to args.
                    args.append(expression_result_or_nexception)
            # When Function arguments list collection process finished, we can handle Function call.
            if isinstance(identifier_token_or_form, list):
                # Propagate possibly occurred exception raised during recursive expr-form evaluation
                result = recursive(local_env, identifier_token_or_form)
                if isinstance(result, datatypes.NException):
                    return result
                # If expression form has been evaluated to Function or Py3Object, return call result
                if isinstance(result, (datatypes.Function, datatypes.Py3Object)):
                    return result.call(args)
                # If expression form has been evaluated to Keyword, cast it to a 'get' function call
                if isinstance(result, datatypes.Keyword):
                    return BuiltinFunctions.get_func(
                        args + [result]
                        if len(args) == 1 else [args[0], result, args[1]])
                # If expression form has been evaluated to an average data type, raise an exception.
                raise ASTEvalIsNotAFunctionDataType(Token(Token.Proxy, result))
            # If identifier token (or form) is actually a Token pointing to a Keyword, cast fn call
            if identifier_token_or_form.type() == identifier_token_or_form.Keyword:
                return BuiltinFunctions.get_func(
                    args + [identifier_token_or_form.dt()]
                    if len(args) == 1 else [args[0], identifier_token_or_form.dt(), args[1]])
            # If identifier token (or form) is Identifier, lookup for the local and global bindings
            if identifier_token_or_form.identifier():
                bundled = identifier_token_or_form.dt()  # <- store a Token bundled data type first
                # Handle dot-expression form: allows user to call an exported method on a data type
                if bundled.origin().startswith('.'):
                    if len(args) < 1:
                        raise ASTEvalInvalidDotExprArity(identifier_token_or_form)  # <--- (.) only
                    method_name = bundled.origin()[1:]
                    method_instance, *method_arguments = args
                    if dot_expression_result := self.dot(method_name,
                                                         method_instance,
                                                         method_arguments):
                        return dot_expression_result
                    raise ASTEvalNotExportedMethod(identifier_token_or_form)  # <------- or missing
                # If Identifier is not method, try to lookup for the local and global user bindings
                mb_bound = local_env.get(bundled.origin(), module_env.get(bundled.origin()))
                # If Identifier was marked as Undefined first and was not bound, raise an exception
                if isinstance(bundled, datatypes.Undefined) and not mb_bound:
                    print(identifier_token_or_form.dt().origin())
                    raise ASTEvalNotFoundInThisContent(identifier_token_or_form)
                final = mb_bound or bundled  # <-- choose final data type to dispatch function call
                # If final data type is Function or Py3Object, invoke their call() method with args
                if isinstance(final, (datatypes.Function, datatypes.Py3Object)):
                    return final.call(args)
                # If final data type is Keyword, cast it to NanamiLang builtin 'get' function call.
                if isinstance(final, datatypes.Keyword):
                    return BuiltinFunctions.get_func(args + [final]
                                                     if len(args) == 1
                                                     else [args[0], final, args[1]])
            # If identifier token (or form) is a Token pointing to something else, raise exception.
            raise ASTEvalIsNotAFunctionDataType(identifier_token_or_form)
            # That is how we handle built AST recursive evaluation. We almost support all features.
        return tuple(recursive({}, _tree) for _tree in self.wood())
        # Iterate through built AST wood, evaluate each tree, and return tuple of collected results
