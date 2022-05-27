'''
This module defines the ScopeContents class and a number of its sub classes. These
are used to parse the syntax tree into scopes. These scopes then store the modules
variables and functions that are defined and used within this scope.

These are all automatically generated recursivley by the OuterScope class which can
be found in outerscope.py.
'''
from copy import copy
from sca2d import utilities
from sca2d.scadclasses import Variable, ModuleDef, FunctionDef, ModuleCall, FunctionCall, UnnamedArgument
from sca2d.messages import Message

class ScopeContents:
    '''
    This is the base class of OuterScope and all of the module/function/control
    scopes. It should not be used as it is.
    All ScopeContents include the original Lark parse tree for their scope.
    '''
    def __init__(self, tree, parent, top_level, preassigned_vars=None):
        if not top_level:
            if not isinstance(parent, ScopeContents):
                raise ValueError("Non top-level scopes require a parent scope.")
        self._assigned_vars = []
        if preassigned_vars is None:
            self._preassigned_vars = []
        else:
            self._preassigned_vars = preassigned_vars
        self._used_vars = []
        self._tree = tree
        self._defined_modules = []
        self._used_modules = []
        self._defined_functions = []
        self._used_functions = []
        self._internal_scopes = []
        self._parent = parent
        self.messages = []
        self._this_scope_disabled_messages = []
        #Finally parse the scope
        self._parse_scope()

    def __str__(self):
        """
        The string representation of the scope is the pretty print with all the
        whitespace stripped out except after commas.
        """
        printstr = self.pretty(0,0)
        printstr = printstr.replace('\n','')
        printstr = printstr.replace(' ','')
        printstr = printstr.replace(',',', ')
        return printstr

    @property
    def filename(self):
        '''
        Returns the name of the file this outer scope represents.
        '''
        if self._parent is None:
            return None
        return self._parent.filename

    @property
    def file_contents(self):
        '''
        Returns the contents of the scad file.
        '''
        if self._parent is None:
            return []
        return self._parent.file_contents

    @property
    def tree(self):
        '''
        This is the original unmodified lark.tree.Tree for this scope.
        '''
        return self._tree

    def collate_messages(self):
        """
        Get all messages from subscopes and this scope
        """
        messages = copy(self.messages)
        for scope in self._internal_scopes:
            messages += scope.collate_messages()
        return messages

    def pretty(self, indent=2, this_indent=0):
        """
        This pretty prints the scope. The indent can be customised.
        `this_indent sets the initial indent.`
        """
        indent_txt = ' '*this_indent

        return (indent_txt + "{\n" +
                indent_txt + " " +
                f"\n{indent_txt} ".join(self._printed_var_lists(indent, this_indent)) +
                "\n"+ indent_txt + "}")

    def text_range(self, start=None, end=None):
        """
        Return the text of the input file from the range specified
        `start` and `end` should be two element lists contanting the starting
        line and column (indexing from line 1 column 1). `start` can be set
        to `None` to return from the start of the file. `end` can be set to
        `None` to return to the end of the file.
        """
        return utilities.get_text_range(self.file_contents, start, end)

    def _printed_var_lists(self, indent=2, this_indent=0):
        """
        This is seperate from pretty print so other child classes can
        overload it to add extra information to the print.
        """
        #This might be for pretty printing but it is the ugliest code in the
        #library!
        indent_txt = ' '*this_indent
        def print_list(plist):
            return '[' + ', '.join([str(item) for item in plist]) + ']'
        def print_scope_list(scopes):
            if len(scopes) == 0:
                return []
            return ('\n' + indent_txt + ' [\n'+
                    ',\n'.join([scope.pretty(indent, indent+this_indent) for scope in scopes]) +
                    '\n'+ indent_txt + ' ]')

        var_lists = [f"preassigned_vars: {print_list(self._preassigned_vars)}",
                     f"assigned_vars: {print_list(self._assigned_vars)}",
                     f"used_vars: {print_list(self._used_vars)}",
                     f"defined_modules: {print_list(self._defined_modules)}",
                     f"used_modules: {print_list(self._used_modules)}",
                     f"defined_functions: {print_list(self._defined_functions)}",
                     f"used_functions: {print_list(self._used_functions)}",
                     f"scopes: {print_scope_list(self._internal_scopes)}"]
        return var_lists

    def _record_message(self, code, tree, args=None):
        """
        Appends a message to self._messages.
        """
        if code not in self._this_scope_disabled_messages:
            self.messages.append(Message(self.filename, code, tree, args))

    def _parse_scope(self, overload_tree=None):
        '''This function should be able to parse all rules in `_terminated_statements`
        in the lark file. For any rules that are anonymous (starting with _) the rules
        inside the anonymous rule must be parsed'''
        if overload_tree is None:
            tree = self._tree
        else:
            tree = overload_tree
        for child in tree.children:
            if child.data == "variable_assignment":
                self._parse_assignment(child)
            elif child.data == "module_def":
                self._parse_module_definition(child)
            elif child.data == "function_def":
                self._parse_function_definition(child)
            elif child.data == "module_call":
                self._parse_module_call(child)
            elif child.data == "pointless_scope":
                self._parse_scope(child)
            elif child.data in ["for", "intersection_for"]:
                self._parse_for(child)
            elif child.data == "assign":
                self._record_message('D0001', child)
                self._parse_assign(child)
            elif child.data == "let":
                #Note that let as a module and let as an expression are different!
                self._parse_let_module(child)
            elif child.data == "if":
                self._parse_if(child)
            elif child.data in ["include_statement", "use_statement"]:
                self._parse_use_include(child)
            elif child.data == "modified_flow_or_mod_call":
                self._record_message("I1003", child)
                self._parse_scope(child)
            elif child.data in ["pointless_termination", "pointless_scoped_block"]:
                # These are handled by the outer scope
                pass
            else:
                self._record_message("U0001", child, [child.data])

    def _parse_assignment(self, assign_tree):
        assigned_var, used_vars, func_calls, complex_expressions = utilities.parse_assignment(assign_tree, self._record_message)
        self._assigned_vars.append(assigned_var)
        self._used_vars += used_vars
        self._parse_function_calls(func_calls)
        self._parse_complex_exprs(complex_expressions)

    def _parse_for(self, control_tree):
        scope = SequentialControlScope(control_tree, self)
        self._internal_scopes.append(scope)

    def _parse_let_module(self, control_tree):
        scope = SequentialControlScope(control_tree, self)
        self._internal_scopes.append(scope)

    def _parse_complex_exprs(self, exprs):
        let_exprs = []
        list_comps = []
        assert_exprs = []
        function_literals = []
        for expr in exprs:
            if expr.data == 'let_expr':
                let_exprs.append(expr)
            elif expr.data == 'list_comp_expr':
                list_comps.append(expr)
            elif expr.data == 'assert_func_expr':
                assert_exprs.append(expr)
            elif expr.data == 'function_literal':
                function_literals.append(expr)
            else:
                self._record_message("U0002", expr, [expr.data])
        self._parse_let_exprs(let_exprs)
        self._parse_list_comps(list_comps)
        self._parse_assert_exprs(assert_exprs)
        self._parse_function_literals(function_literals)

    def _parse_let_exprs(self, let_exprs):
        for let_expr in let_exprs:
            scope = LetExprScope(let_expr, self)
            self._internal_scopes.append(scope)

    def _parse_list_comps(self, list_comps):
        for list_comp in list_comps:
            scope = ListCompScope(list_comp, self)
            self._internal_scopes.append(scope)

    def _parse_assert_exprs(self, assert_exprs):
        for assert_expr in assert_exprs:
            scope = AssertExprScope(assert_expr, self)
            self._internal_scopes.append(scope)

    def _parse_function_literals(self, function_literals):
        for function_literal in function_literals:
            _, args = self._parse_header(function_literal.children[0], no_name=True)
            func_vars = self._parse_def_args(args)
            function_scope = function_literal.children[1]
            if utilities.is_termination(function_scope):
                scope = None
            else:
                scope = FunctionDefScope(function_scope,
                                         parent=self,
                                         preassigned_vars=func_vars)
                self._internal_scopes.append(scope)

    def _parse_module_definition(self, mod_def_tree):
        name, args = self._parse_header(mod_def_tree.children[0])
        module_vars = self._parse_def_args(args)
        module_scope = mod_def_tree.children[1]
        if utilities.is_termination(module_scope):
            scope = None
        else:
            scope = ModuleDefScope(module_scope,
                                   parent=self,
                                   preassigned_vars=module_vars)
            self._internal_scopes.append(scope)
        module_def = ModuleDef(name, module_vars, mod_def_tree, scope)
        self._defined_modules.append(module_def)

    def _parse_function_definition(self, func_def_tree):
        name, args = self._parse_header(func_def_tree.children[0])
        func_vars = self._parse_def_args(args)
        function_scope = func_def_tree.children[1]
        if utilities.is_termination(function_scope):
            scope = None
        else:
            scope = FunctionDefScope(function_scope,
                                     parent=self,
                                     preassigned_vars=func_vars)
            self._internal_scopes.append(scope)
        function_def = FunctionDef(name, func_vars, func_def_tree, scope)
        self._defined_functions.append(function_def)

    def _parse_module_call(self, mod_call_tree):
        module_header = mod_call_tree.children[0]
        name, args = self._parse_header(module_header)
        assigned_arguments = self._parse_call_args(args)
        module_scope = mod_call_tree.children[1]
        if utilities.is_termination(module_scope):
            scope = None
        else:
            scope = ModuleCallScope(module_scope, parent=self)
            self._internal_scopes.append(scope)
        module_call = ModuleCall(name, assigned_arguments, mod_call_tree, scope)
        self._used_modules.append(module_call)

    def _parse_function_calls(self, func_call_trees):
        for func_call_tree in func_call_trees:
            name, args = self._parse_header(func_call_tree.children[0])
            assigned_arguments = self._parse_call_args(args)
            function_call = FunctionCall(name, assigned_arguments, func_call_tree)
            self._used_functions.append(function_call)

    def _parse_assign(self, control_tree):
        control_assign_list = control_tree.children[0].children
        assigned_vars = []
        for assignment in  control_assign_list:
            assigned_var, used_vars, func_calls, complex_expressions = utilities.parse_assignment(assignment, self._record_message)
            assigned_vars.append(assigned_var)
            self._used_vars += used_vars
            self._parse_function_calls(func_calls)
            self._parse_complex_exprs(complex_expressions)

        control_scope = control_tree.children[1]
        self._add_control_scope(control_scope, assigned_vars)

    def _parse_if(self, control_tree):
        control_condition = control_tree.children[0]
        var_list, func_calls, complex_expressions = utilities.get_constituents_of_expr(control_condition, self._record_message)
        self._used_vars += var_list
        self._parse_function_calls(func_calls)
        self._parse_complex_exprs(complex_expressions)

        control_scope = control_tree.children[1]
        self._add_control_scope(control_scope)
        if len(control_tree.children)>2:
            #If we are here then the if statment had an else
            control_scope = control_tree.children[3]
            self._add_control_scope(control_scope)

    def _parse_use_include(self, statement_tree):
        self._record_message("E1001", statement_tree)

    def _add_control_scope(self, control_scope, preassigned_vars=None):
        if utilities.is_termination(control_scope):
            scope = None
        else:
            scope = ControlScope(control_scope,
                                 parent=self,
                                 preassigned_vars=preassigned_vars )
            self._internal_scopes.append(scope)

    def _parse_header(self, header_tree, no_name=False):
        """
        This is used to parse the function header for both
        definitions and calls, the argment lists are returned and
        passd to either parse_def_args or parse_call_args
        """
        if no_name:
            name = None
            arg_trees = header_tree.children
        else:
            name = header_tree.children[0].children[0].value
            arg_trees = header_tree.children[1:]
        if utilities.is_empty_arg(arg_trees[0]):
            args = []
        else:
            args = []
            for tree in arg_trees:
                if len(tree.children) == 1:
                    args.append(tree.children[0])
                elif len(tree.children) == 0:
                    self._record_message("E0004", header_tree)
                else:
                    self._record_message("U0003", header_tree)
        return name, args

    def _parse_def_args(self, args):
        """
        This parses the arguments of a function or module definition.
        As it is only for a definition only variables or keyword-arguments
        (kwargs) are allowed.
        """
        assigned_vars = []
        n_kwargs = 0
        for arg in args:
            if arg.data == 'kwarg':
                assigned_var, used_vars, func_calls, complex_expressions = utilities.parse_assignment(arg, self._record_message)
                assigned_var.is_kwarg = True
                assigned_var.default_is_undef = utilities.is_kwarg_undef(arg)
                assigned_vars.append(assigned_var)
                self._used_vars += used_vars
                self._parse_function_calls(func_calls)
                self._parse_complex_exprs(complex_expressions)

                n_kwargs += 1
            elif arg.data == 'variable':
                assigned_vars.append(Variable(arg.children[0]))
                if n_kwargs>0:
                    self._record_message("E0002", arg)
            else:
                self._record_message("E0001", arg)
        return assigned_vars

    def _parse_call_args(self, args):
        """
        This parses the arguments of a function or module call. As such
        any matched expressions are allowed. However kwargs need to be treated
        differently so that the assigned variable can be passed onto the new scope.
        """
        assigned_arguments = []
        n_kwargs = 0
        for arg in args:
            if arg.data == 'kwarg':
                assigned_arg, used_vars, func_calls, complex_expressions = utilities.parse_assignment(arg, self._record_message)
                assigned_arg.is_kwarg = True
                assigned_arguments.append(assigned_arg)
                self._used_vars += used_vars
                self._parse_function_calls(func_calls)
                self._parse_complex_exprs(complex_expressions)
                n_kwargs += 1
            else:
                assigned_arguments.append(UnnamedArgument(arg))
                var_list, func_calls, complex_expressions = utilities.get_constituents_of_expr(arg, self._record_message)
                self._used_vars += var_list
                self._parse_function_calls(func_calls)
                self._parse_complex_exprs(complex_expressions)
                if n_kwargs>0:
                    self._record_message("E0002", arg)

        return assigned_arguments

    def propogate_defs_and_use(self, var_defs, mod_defs, func_defs):
        """
        This should be called from the parent scope. The inputs are
        the variables, modules, and functions defined by the parent
        (or its parents, etc). What is returned is the variable use
        by this scope and all internal scopes.
        """

        self._check_overwrite_var(var_defs)
        self._check_overwrite_mod(mod_defs)
        self._check_overwrite_func(func_defs)

        all_var_defs = var_defs + self._preassigned_vars + self._assigned_vars
        all_mod_defs = mod_defs + self._defined_modules
        all_func_defs = func_defs + self._defined_functions
        all_var_use = copy(self._used_vars)
        all_mod_use = copy(self._used_modules)
        all_func_use = copy(self._used_functions)

        for scope in self._internal_scopes:

            [var_use, mod_use, func_use] = scope.propogate_defs_and_use(all_var_defs,
                                                                        all_mod_defs,
                                                                        all_func_defs)
            all_var_use += var_use
            all_mod_use += mod_use
            all_func_use += func_use

        self._check_var_use(all_var_defs, all_var_use, all_func_use)
        self._check_mod_use(all_mod_defs, all_mod_use)
        self._check_func_use(all_func_defs, all_func_use, all_var_defs)

        return all_var_use, all_mod_use, all_func_use

    def _check_overwrite_var(self, var_defs):
        '''
        Check if variable overwritten in this scope
        '''
        for definition in self._preassigned_vars:
            if definition in var_defs:
                self._record_message("W2002", definition.tree, [definition.name])

        for i, definition in enumerate(self._assigned_vars):
            if not definition.is_special():
                if definition in self._assigned_vars[:i]:
                    self._record_message("W2001", definition.tree, [definition.name])
                elif definition in var_defs:
                    self._record_message("W2002", definition.tree, [definition.name])
                elif definition in self._preassigned_vars:
                    variable = self._preassigned_vars[self._preassigned_vars.index(definition)]
                    if not variable.is_kwarg:
                        self._record_message("W2013", definition.tree, [definition.name])
                    elif not variable.default_is_undef:
                        self._record_message("W2014", definition.tree, [definition.name])
                    #TODO check position of overwrite if kwarg is undef

    def _check_overwrite_mod(self, mod_defs):
        '''
        Check if module defintion overwritten in this scope
        '''
        for i, definition in enumerate(self._defined_modules):
            if definition in self._defined_modules[:i]:
                self._record_message("W2003", definition.tree, [definition.name])
            elif definition in mod_defs:
                self._record_message("W2004", definition.tree, [definition.name])

    def _check_overwrite_func(self,func_defs):
        '''
        Check if function definition overwritten in this scope
        '''
        for i, definition in enumerate(self._defined_functions):
            if definition in self._defined_functions[:i]:
                self._record_message("W2005", definition.tree, [definition.name])
            elif definition in func_defs:
                self._record_message("W2006", definition.tree, [definition.name])

    def _check_var_use(self, all_var_defs, all_var_use, all_func_use):
        '''
        Check if variables defined in this scope is used. Also check all variables used
        in this scope are defined. Only check variables used or defined directly in this
        scope as others will be picked up in the scope they are used/defined in.
        '''
        for var in self._preassigned_vars + self._assigned_vars:
            if var not in all_var_use:
                if var not in all_func_use:
                    if not var.is_special():
                        self._record_message("W2007", var.tree, [var.name])
        for var in self._used_vars:
            if var not in all_var_defs:
                self._record_message("E2001", var.tree, [var.name])

    def _check_mod_use(self, all_mod_defs, all_mod_use):
        '''
        Check if modules defined in this scope is used. Also check all modules used in
        this scope are defined. Only check modules used or defined directly in this
        scope as others will be picked up in the scope they are used/defined in.
        '''
        for mod_def in self._defined_modules:
            if mod_def not in all_mod_use:
                #Note this message will be disabled in outer scopes
                self._record_message("W2008", mod_def.tree, [mod_def.name])
        for mod_call in self._used_modules:
            if mod_call in all_mod_defs:
                mod_def = all_mod_defs[all_mod_defs.index(mod_call)]
                messages = mod_def.check_call(mod_call)
                for message in messages:
                    self._record_message(*message)
            else:
                self._record_message("E2002", mod_call.tree, [mod_call.name])
            if mod_call.has_implicit_scope:
                self._record_message("I0004", mod_call.tree)

    def _check_func_use(self, all_func_defs, all_func_use, all_var_defs):
        '''
        Check if functions defined in this scope is used. Also check all functions used
        in this scope are defined. Only check functions used or defined directly in this
        scope as others will be picked up in the scope they are used/defined in.
        '''
        for func_def in self._defined_functions:
            if func_def not in all_func_use:
                self._record_message("W2009", func_def.tree, [func_def.name])
        for func_call in self._used_functions:
            if func_call in all_func_defs:
                func_def = all_func_defs[all_func_defs.index(func_call)]
                messages = func_def.check_call(func_call)
                for message in messages:
                    self._record_message(*message)
            else:
                if func_call not in all_var_defs:
                    self._record_message("E2003", func_call.tree, [func_call.name])


class ModuleDefScope(ScopeContents):
    '''
    This is a child class of ScopeContents. It holds the defined and used variables
    moduled and functions for the scope of a module definition. i.e. the code in the
    braces after `module foo(a)`.

    For the scope of the called module see ModuleCallScope
    '''
    def __init__(self, tree, parent, preassigned_vars):
        super().__init__(tree, parent, top_level=False, preassigned_vars=preassigned_vars)

class FunctionDefScope(ScopeContents):
    '''
    This is a child class of ScopeContents. It holds the defined and used variables
    (etc) for the scope of a function definition.
    Making a whole class for this scope is perhaps overkill as
    functions are simply an expression. However this exists to be
    future-proof (if OpenSCAD introduce multi line functons) and consistent.
    '''

    def __init__(self, tree, parent, preassigned_vars):
        super().__init__(tree,
                         parent,
                         top_level=False,
                         preassigned_vars=preassigned_vars)

    def _parse_scope(self, overload_tree=None):
        '''
        Overloading parse scope as the expected scope is a simply an expression
        '''
        function_expression = self._tree.children[0]
        var_list, func_calls, complex_expressions = utilities.get_constituents_of_expr(function_expression, self._record_message)
        self._used_vars += var_list
        self._parse_function_calls(func_calls)
        self._parse_complex_exprs(complex_expressions)


class ModuleCallScope(ScopeContents):
    '''
    This is a child class of ScopeContents. It holds the defined and used variables
    moduled and functions for the scope of a module call. i.e. the code in the
    braces of `foo(a){CODE GOES HERE}`. If a single module or flow control element
    (if statement, for loop) follows the module rather than code in braces. This
    class is still used to define that scope.

    For the scope of the module definition see ModuleDefScope.
    '''
    def __init__(self, tree, parent):
        super().__init__(tree, parent, top_level=False)

class ControlScope(ScopeContents):
    '''
    This is a child class of ScopeContents. It holds the defined and used variables
    moduled and functions for the scope inside a flow control statment. This is used
    for the scopes of both `if` and `else` (seperate ControlScope for each) as well as
    `for`, `intersection_for`, `assign`, and `let`.
    '''
    def __init__(self, tree, parent, preassigned_vars):
        super().__init__(tree, parent, top_level=False, preassigned_vars=preassigned_vars)


class SequentialControlScope(ControlScope):
    '''
    This is a child class of ScopeContents. It is used for `for` and `let` as it allows
    assignments to be used in later asignments as such it has to parse each assignment
    sequentially within the scope.
    '''

    def __init__(self, tree, parent):
        # Note that because let expressions read each assigment in order they
        # the varibale are not preassinged they are treated as part of the scope
        super().__init__(tree, parent, preassigned_vars=None)

    def _parse_scope(self, overload_tree=None):
        control_assign_list = self._tree.children[0].children
        internal_let_scope = self._tree.children[1]
        # First parse the assignments list
        for assignment in  control_assign_list:
            self._parse_assignment(assignment)
        # Then parse the scope of the let statement
        super()._parse_scope(internal_let_scope)

class ExprScope(ScopeContents):
    '''
    This is a child class of ScopeContents. It is used for complex scoped expressions
    like let expressions or the expressions in list comprensions
    It holds the defined variables and the used functions and variables for the expression.
    '''

    def __init__(self, tree, parent):
        # Note that because let expressions read each assigment in order they
        # the varibale are not preassinged they are treated as part of the scope
        super().__init__(tree, parent, top_level=False, preassigned_vars=None)

    def _parse_scope(self, overload_tree=None):
        raise NotImplementedError("ExprScope should be subclassed and must implement _parse_scope")

    def _parse_expr_assignment_list(self, assigment_list):
        for assignment in assigment_list:
            self._parse_assignment(assignment)

    def _parse_expression(self, expr):
        """Parse an expression this may be the expression at the end of the scope or conditional
        such as in an if statement"""
        var_list, func_calls, complex_expressions = utilities.get_constituents_of_expr(expr, self._record_message)
        self._used_vars += var_list
        self._parse_function_calls(func_calls)
        self._parse_complex_exprs(complex_expressions)

class LetExprScope(ExprScope):
    '''
    This is a child class of ExprSope. It is used for let expression (i.e. let used in and expression
    rather than let used in a module).
    '''

    def _parse_scope(self, overload_tree=None):
        '''
        Parses the let expression. This will have the full let_expr tree. The two
        children should be the list of assignments and then the actual final expression.
        '''

        assigment_list = self._tree.children[0].children
        self._parse_expr_assignment_list(assigment_list)
        final_expr = self._tree.children[1]
        self._parse_expression(final_expr)

class ForExprScope(ExprScope):
    '''
    This is a child class of ExprSope. It is used for `for` expressions inside list comprehsions.
    For the c-style for loop see CStyleForExprScope
    '''

    def _parse_scope(self, overload_tree=None):
        '''
        Parses the for expression. The two children should be the list of assignments
        and then the actual final expression.
        '''

        assigment_list = self._tree.children[0].children
        self._parse_expr_assignment_list(assigment_list)
        final_expr = self._tree.children[1]
        self._parse_expression(final_expr)

class CStyleForExprScope(ExprScope):
    '''
    This is a child class of ExprSope. It is used for `for` expressions in list comprehnsions that
    use c-style syntax. It is split into two scopes, the first is the initial assignments and the
    end condition and the final expression. This is needed as the end condition and the final expression
    will run before the iterators ever happen. The iterators are in an iterator scope
    (CStyleForIterScope) as they overwrite the variables in the in this scope.
    '''

    def _parse_scope(self, overload_tree=None):
        '''
        Parses the for expression. The two children should be the c-style for loop asignment and
        then the actual final expression.
        '''

        c_style_assignment = self._tree.children[0]
        initial_asignment_list = c_style_assignment.children[0].children
        end_condition = c_style_assignment.children[1]
        iterater_scope = CStyleForIterScope(c_style_assignment.children[2], self)

        self._parse_expr_assignment_list(initial_asignment_list)
        self._parse_expression(end_condition)

        final_expr = self._tree.children[1]
        self._parse_expression(final_expr)
        self._internal_scopes.append(iterater_scope)

class CStyleForIterScope(ExprScope):
    '''
    The iter schope for CStyleForExprScope. This only handles the iterator assigments
    '''

    def __init__(self, tree, parent):
        super().__init__(tree, parent)
        self._this_scope_disabled_messages.append('W2002')

    def _parse_scope(self, overload_tree=None):
        self._parse_expr_assignment_list(self._tree.children)

class EachExprScope(ExprScope):
    '''
    This is a child class of ExprSope. It is used for `each` expressions in list comprehnsions.
    '''

    def _parse_scope(self, overload_tree=None):
        '''
        Parses the expression.
        '''

        final_expr = self._tree.children[0]
        self._parse_expression(final_expr)

class IfExprScope(ExprScope):
    '''
    This is a child class of ExprSope. It is used for `if` expressions in list comprehnsions.
    '''

    def _parse_scope(self, overload_tree=None):
        '''length is 2 if this is just and if, and 4 if it is an if and an else'''

        conditional = self._tree.children[0]
        if_chosen_expr = self._tree.children[1]
        self._parse_expression(conditional)
        self._parse_expression(if_chosen_expr)
        if len(self._tree.children) > 2:
            scope = ElseExprScope(self._tree.children[3], self)
            self._internal_scopes.append(scope)

class ElseExprScope(ExprScope):
    '''
    This is a child class of ExprSope. It is used for `else` expressions in list comprehnsions.
    '''
    def _parse_scope(self, overload_tree=None):
        '''
        Parses the expression.
        '''

        self._parse_expression(self._tree)

class ListCompScope(ScopeContents):
    '''
    This is a child class of ScopeContents. It holds the defined variables and the
    used functions and variables for a let expression (i.e. let used in and expression
    rather than let used in a module).
    '''

    def __init__(self, tree, parent):
        # Note that because let expressions read each assigment in order they
        # the varibale are not preassinged they are treated as part of the scope
        super().__init__(tree, parent, top_level=False, preassigned_vars=None)

    def _parse_scope(self, overload_tree=None):

        list_comp_tree = self._tree.children[0]
        list_comp_type = list_comp_tree.data

        if list_comp_type == "lc_for":
            scope = ForExprScope(list_comp_tree, self)
        elif list_comp_type == "lc_for_c_style":
            scope = CStyleForExprScope(list_comp_tree, self)
        elif list_comp_type == "lc_each":
            scope = EachExprScope(list_comp_tree, self)
        elif list_comp_type == "lc_if":
            scope = IfExprScope(list_comp_tree, self)
        elif list_comp_type == "lc_let_expr":
            scope = LetExprScope(list_comp_tree, self)
        self._internal_scopes.append(scope)

class AssertExprScope(ExprScope):
    '''
    This is a child class of ExprSope. It is used for `assert` expressions. By assert expressions
    we mean when an assert is used inline within an expression. Not the assert module when it is use
    as its own terminated statement.
    '''

    def _parse_scope(self, overload_tree=None):
        '''The scope has two elements these are the assert call and the following expression'''

        assert_call_args = self._tree.children[0].children
        self._parse_assert_call_args(assert_call_args)
        final_expr = self._tree.children[1]
        self._parse_expression(final_expr)

    def _parse_assert_call_args(self, assert_call_args):
        if len(assert_call_args) == 1:
            self._record_message("I2001", self.tree)
        elif len(assert_call_args) != 2:
            self._record_message("E0003", self.tree, ["assert"])
        for arg in assert_call_args:
            self._parse_expression(arg.children[0])
