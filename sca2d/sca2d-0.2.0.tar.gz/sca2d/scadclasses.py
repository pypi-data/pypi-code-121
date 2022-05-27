'''
This module contains simple classes to provide easy access to
information about certain objects parsed from the .scad file.
'''

from dataclasses import dataclass
from lark import Tree, Token
from sca2d.definitions import CustomArgDef

class DummyTree():
    '''
    A dummy lark tree. Used for the message class when no tree is available.
    Returns one for line or column if not set. It is not subclassed from Tree
    so it may not behave as expected.
    '''

    def __init__(self, data=None, line=1, column=1):
        if data is None:
            self.data = 'Dummy'
        else:
            self.data = data
        self.children = []
        self._line=line
        self._column=column

    @property
    def line(self):
        '''
        Line number of the tree
        '''
        return self._line

    @property
    def column(self):
        '''
        Column number of the tree
        '''
        return self._column

    @property
    def end_line(self):
        '''
        The end line number of the tree
        '''
        return self._line

    @property
    def end_column(self):
        '''
        The end column number of the tree
        '''
        return self._column

class DummyToken():
    '''
    A dummy lark token. Used for the message class when no tree is available.
    Returns one for line or column if not set. It is not subclassed from Token
    so it may not behave as expected.
    '''

    def __init__(self, type_name=None, value=None, line=1, column=1):
        if type_name is None:
            self._type_name = 'Dummy'
        else:
            self._type_name = type_name
        if value is None:
            self.value = 'Dummy'
        else:
            self.value = value
        self._line=line
        self._column=column

    @property
    def type(self):
        """
        Returns the "type" of token as defined in grammar.
        """
        return self._type_name

    @property
    def line(self):
        '''
        Line number of the token
        '''
        return self._line

    @property
    def column(self):
        '''
        Column number of the token
        '''
        return self._column

    @property
    def end_line(self):
        '''
        The end line number of the token
        '''
        return self._line

    @property
    def end_column(self):
        '''
        The end column number of the token
        '''
        return self._column

class ScadDef:
    '''
    A base class for ModuleDef and FunctionDef
    '''

    def __init__(self, name, arg_defintion, tree, scope, included_by=None):
        self.name = name
        self._arg_defintion = arg_defintion
        self.tree = tree
        self.scope = scope
        self.included_by = included_by

    def check_call(self, call):
        '''
        For a given module call check if input arguments are defined appropriatly.
        Return a list of messages for any issue.
        '''
        if isinstance(self._arg_defintion, CustomArgDef):
            return self._arg_defintion.check_call(call)

        messages = []

        n_args_called = len([arg for arg in call.assigned_arguments if not arg.is_special()])
        n_args = len(self._arg_defintion)
        n_kwargs = len([arg for arg in self._arg_defintion if arg.is_kwarg])
        if n_args_called > n_args:
            messages.append(['W3001', call.tree])
        elif n_args_called < n_args-n_kwargs:
            messages.append(['W3002', call.tree])
        else:
            assgined = [0]*n_args
            for i, arg in enumerate(call.assigned_arguments):
                if isinstance(arg, UnnamedArgument):
                    assgined[i] += 1
                else:
                    if arg in self._arg_defintion:
                        assgined[self._arg_defintion.index(arg)] += 1
                    elif not arg.is_special():
                        messages.append(['W3003', arg.tree, [arg.name]])
            for arg, times_assigned in zip(self._arg_defintion, assgined):
                if times_assigned == 0:
                    if not arg.is_kwarg:
                        messages.append(['W3004', call.tree, [arg.name]])
                if times_assigned > 1:
                    messages.append(['W3005', call.tree, [arg.name]])


        return messages

    def __str__(self):
        return self.name


    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name


class ModuleDef(ScadDef):
    '''
    A class for a module definition. Contains the name of the defined module.
    The number of args (inc. kwargs) and the number of kwargs. The original
    Lark tree and and the ScopeContents for this definition.
    '''

    def __repr__(self):
        return "<sca2d.scadclasses.ModuleDef "+self.name+">"


class FunctionDef(ScadDef):
    '''
    A class for a function definition. Contains the name of the defined function
    The number of args (inc. kwargs) and the number of kwargs. The original
    Lark tree and and the ScopeContents for this definition.
    '''

    def __repr__(self):
        return "<sca2d.scadclasses.FunctionDef "+self.name+">"


@dataclass
class ModuleCall:
    '''
    A class for a module call. Contains the name of the called module.
    The number of args (inc. kwargs) and the number of kwargs. The original
    Lark tree and and the ScopeContents for this definition. A new ModuleCall
    object is created each time the module is called. Using ModuleCall.tree
    the position in the scad file can be located.
    '''
    name: str
    # total number of arguments including keyword arguments
    assigned_arguments: list
    tree: Tree
    scope: object

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<sca2d.scadclasses.ModuleCall "+self.name+">"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name

    @property
    def is_terminated_call(self):
        '''Return boolean. True if call is terminated with ;'''
        return self.scope is None

    @property
    def has_implicit_scope(self):
        '''Return boolean. True if module call has an implicit
        scope. i.e. has a scope not defined with braces.'''
        if not self.is_terminated_call:
            start = [self.scope.tree.line, self.scope.tree.column]
            end = [self.scope.tree.end_line, self.scope.tree.end_column]
            scope_text = self.scope.text_range(start, end)
            return not scope_text.startswith('{')
        return False

@dataclass
class FunctionCall:
    '''
    A class for a function call. Contains the name of the called function.
    The number of args (inc. kwargs) and the number of kwargs. The original
    Lark tree and and the ScopeContents for this definition. A new FunctionCall
    object is created each time the function is called. Using FunctionCall.tree
    the position in the scad file can be located.
    '''
    name: str
    # total number of arguments including keyword arguments
    assigned_arguments: list
    tree: Tree

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<sca2d.scadclasses.FunctionCall "+self.name+">"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name

class Variable:
    '''
    A class for a scad variable. A new Variable object is created each time the
    variable is used or defined. Using Variable.tree the position in the scad file
    can be located.
    '''
    def __init__(self, token):
        if isinstance(token, Tree):
            token = token.children[0]
        elif isinstance(token, (Token, DummyToken)):
            if token.type != 'VARIABLE':
                raise ValueError('Cannot make a variable from a non-variable Token')
        else:
            raise TypeError(f'Cannot make a variable from a {type(token)}.'
                            ' Expecting a Tree or Token.')
        self.name = token.value
        self.token = token
        self.included_by = None
        self.is_kwarg = False
        self.default_is_undef = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<sca2d.scadclasses.Variable "+self.name+">"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name

    @property
    def tree(self):
        """
        returns the token for the variable. This is the same as Variable.token.
        Despite not being a tree this is safe to use when finding line and column
        numbers.
        """
        return self.token

    def is_special(self):
        """
        Returns whether this is an OpenSCAD "special variable" these are ones begining with $
        """
        return self.name.startswith('$')

class UseIncStatment:
    '''
    Class for a scad use or include statment
    '''
    def __init__(self, tree, calling_file):
        self.filename = tree.children[0].value
        self.tree = tree
        self.calling_file = calling_file

    def __str__(self):
        return self.filename

    def __repr__(self):
        return f"<sca2d.scadclasses.UseIncStatment: {self.filename}>"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.filename==other
        if isinstance(other, UseIncStatment):
            return self.filename == other.filename
        return False


class UnnamedArgument:
    '''
    A class for input arguments that are unamed
    '''
    def __init__(self, tree):
        self.tree = tree

    def is_special(self):
        """
        Returns whether this is an OpenSCAD "special variable" , an unamed argument is
        never a special variable
        """
        return False
