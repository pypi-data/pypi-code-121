"""
This contains a number of useful functions used by other modules.
"""
import os
from copy import copy
import platform
from lark.tree import Tree
from sca2d.scadclasses import Variable

#TODO split up utilities to avoid cyclic imports

def is_empty_arg(tree):
    """
    Checks if an argument is empty. This is needed becuse
    lark returns and empty arg tree when `foo()` is encountered.
    This function is trivial but makes code clearer.
    """
    return len(tree.children) == 0

def is_termination(tree_or_token):
    """
    Checks if the tree or token is a termination character. i.e ";".
    This is useful when deciding how to pass a module call scope as
    the module may be called with a scope following or terminated. It is
    Used for all module and control scopes as terminating them isntantly
    with a semicolon is always valid .scad even if it does not make sense
    to do so.
    """
    if isinstance(tree_or_token, Tree):
        return False
    return tree_or_token.type == 'TERMINATION'

def check_lists(list_trees, record_message):
    """
    Iterate over all lists checking for empty items
    """
    for list_tree in list_trees:
        list_item_trees = get_all_matching_subtrees(list_tree,
                                                    'list_item',
                                                    include_nested=False)
        #Don't check last item in list. This allows empty lists and trailing commas
        for list_item_tree in list_item_trees[:-1]:
            if len(list_item_tree.children) == 0:
                record_message('E0005', list_tree)

def get_constituents_of_expr(expr, record_message):
    """
    Returns a list of the variables used and functions called in the input
    expression. Two lists are returned. For variables the list is of
    sca2d.scadclasses.Variable objects but for the function calls they are
    lark.tree.Tree as they will require further processing in the calling scope.
    """
    complex_tree_types = ['let_expr', 'list_comp_expr', 'assert_func_expr', 'function_literal']
    excluded_trees = complex_tree_types + ['echo_func']
    if expr.data == 'function_call':
        return [], [expr], []
    if expr.data in complex_tree_types:
        return [], [], [expr]
    list_trees = get_all_matching_subtrees(expr,
                                           'list',
                                           include_self=True,
                                           exclude_trees=excluded_trees)
    check_lists(list_trees, record_message)
    #Assigned vars are excluded when searching for variable tokens as they are keywords in function assignment
    var_tokens = get_all_matching_tokens(expr, 'VARIABLE', exclude_trees=excluded_trees+['assigned_var'])
    func_trees = get_all_matching_subtrees(expr , 'function_call', exclude_trees=excluded_trees)
    lc_trees = get_all_matching_subtrees(expr , 'list_comp_expr', include_nested=False, exclude_trees=excluded_trees)
    let_expr_trees = get_all_matching_subtrees(expr , 'let_expr', include_nested=False, exclude_trees=excluded_trees)
    assert_exprs = get_all_matching_subtrees(expr , 'assert_func_expr', include_nested=False, exclude_trees=excluded_trees)
    function_literals = get_all_matching_subtrees(expr , 'function_literal', include_nested=False, exclude_trees=excluded_trees)
    complex_expressions = lc_trees + let_expr_trees + assert_exprs + function_literals
    variables = [Variable(token) for token in var_tokens]
    return variables, func_trees, complex_expressions

def is_kwarg_undef(kwarg):
    """
    For keyword definition return true if is set as =undef
    """
    expr = kwarg.children[1]
    return expr.data=='undef'


def parse_assignment(assign_tree, record_message):
    """
    Split assignment (could be a kwarg or a control assignment)
    into the assigned variable and the expression.
    """
    assigned_var = Variable(assign_tree.children[0])
    expr = assign_tree.children[1]
    used_vars, used_functions, complex_expressions = get_constituents_of_expr(expr, record_message)
    return assigned_var, used_vars, used_functions, complex_expressions

def get_all_matching_subtrees(tree,
                              tree_name,
                              include_self=False,
                              include_nested=True,
                              exclude_trees=None):
    """
    Returns a list of all matching subtrees in the order they appear in the
    code. Trees match if Tree.data (i.e. the rule name in the .lark definion)
    matches the input "tree_name". If include nested then nested trees of the
    same type will be found.
    """
    if exclude_trees is not None:
        if tree.data in exclude_trees:
            return []

    if include_self and tree.data == tree_name:
        subtrees = [tree]
        if not include_nested:
            return subtrees
    else:
        subtrees = []
    for child in tree.children:
        if isinstance(child, Tree):
            if child.data == tree_name:
                subtrees.append(child)
                if not include_nested:
                    # Don't try to match subtrees if include_nested is false
                    continue
            subtrees += get_all_matching_subtrees(child,
                                                  tree_name,
                                                  include_nested=include_nested,
                                                  exclude_trees=exclude_trees)
    return subtrees

def get_parent(tree_or_token, full_tree):
    """
    return the parent of the tree or token
    """
    for child in full_tree.children:
        if child is tree_or_token:
            return full_tree
        if isinstance(child, Tree):
            parent = get_parent(tree_or_token, child)
            if parent is not None:
                return parent
    return None

def get_all_matching_tokens(tree, token, exclude_trees=None):
    """
    Returns a list of all matching tokens in the order they appear in the
    code. Tokens match if Token. Type matches the input.
    Any tokens inside excluded tree types are not returned.
    """
    if exclude_trees is not None:
        if tree.data in exclude_trees:
            return []

    tokens = []
    for child in tree.children:
        if isinstance(child, Tree):
            tokens += get_all_matching_tokens(child, token, exclude_trees=exclude_trees)
        else:
            if child.type == token:
                tokens.append(child)
    return tokens

def get_all_tokens(tree, exclude_trees=None):
    """
    Returns all tokens in a given lark Tree. Note that the tokens are the terminus or leaf
    of each branch of the tree, but not all trees terminate in tokens.
    """
    if exclude_trees is not None:
        if tree.data in exclude_trees:
            return []

    tokens = []
    for child in tree.children:
        if isinstance(child, Tree):
            tokens += get_all_tokens(child, exclude_trees=exclude_trees)
        else:
            tokens.append(child)
    return tokens

def library_path():
    """
    Return the openscad librarypath
    """
    if platform.system() == 'Windows':
        return [r"C:\My Documents\OpenSCAD\libraries"]
    if platform.system() == 'Darwin':
        return ["/Documents/OpenSCAD/libraries"]
    return ["~/.local/share/OpenSCAD/libraries", "/usr/share/openscad/libraries"]

def openscadpath():
    """
    Return the paths defined in the os encironment variable OPENSCADPATH
    """
    path_var = os.environ.get('OPENSCADPATH', None)
    if path_var is None:
        return []
    return path_var.split(os.pathsep)

def locate_file(use_inc_statement):
    """
    Locate the used/included file from the input use/include statment.
    """
    required_file = use_inc_statement.filename
    calling_file = use_inc_statement.calling_file
    if os.path.isabs(required_file):
        return required_file
    call_dir = os.path.dirname(calling_file)
    local_file =  os.path.normpath(os.path.join(call_dir, required_file))
    if os.path.exists(local_file):
        return local_file
    for lib_dir in library_path()+openscadpath():
        library_file =  os.path.normpath(os.path.join(lib_dir, required_file))
        if os.path.exists(library_file):
            return library_file
    # If it cannot be found just return the original file.
    return required_file

def get_text_range(text, start, end):
    """
    Returns the text in a given range. `start` and `end` should be
    two element lists contanting the starting line and column (indexing from
    line 1 column 1). `start` can be set to None to return from the start of
    the file. `end` can be set to None to return to the end of the file
    """
    if isinstance(text, str):
        text = text.split('\n')
    if not isinstance(text, list):
        raise TypeError('Text should be a string or a list of strings')
    if start is None:
        start_line = 0
        start_col = 0
    else:
        start_line = start[0]-1
        start_col = start[1]-1
    if end is None:
        end_line = None
        end_col = None
    else:
        end_line = end[0]
        end_col = end[1]-1
    lines = text[start_line:end_line]
    if len(lines) == 1:
        return lines[0][start_col:end_col]
    lines[0] = lines[0][start_col:]
    lines[-1] = lines[-1][0:end_col]
    return '\n'.join(lines)

def estimate_complexity(tree):
    """
    Estimate the complexity of an expression. Each token (string, variable, function name, etc)
    is counted as 1 point. Except in a list. A list is the complexity of its two most complex
    elements, to stop simple lists being tagged as complex.
    Note: this does not analyse the complexity of expressions inside a let statement. These expressions
    should be analysed sepereately.

    Improvements needed:
    * List comprehensions are always assigned a complexity of 4. This needs to be improved.
    * Function calls with lots of arguments increase complexity too much
    * Function literals are largely ignored
    * Ternaries especially when nested give very high complexity (but this is often unavoidable)

    """
    complex_expressions = ['list', 'let_expr', 'assert_func', 'list_comp_expr', 'function_literal']
    tokens = get_all_tokens(tree, exclude_trees=complex_expressions + ['attribute'])
    complexity = len(tokens)
    list_exclude = copy(complex_expressions)
    list_exclude.remove('list')
    list_trees = get_all_matching_subtrees(tree,
                                           'list',
                                           include_self=True,
                                           include_nested=False,
                                           exclude_trees=list_exclude)
    for list_tree in list_trees:
        complexity += estimate_list_complexity(list_tree)
    list_comp_exclude = copy(complex_expressions)
    list_comp_exclude.remove('list_comp_expr')
    list_comp_trees = get_all_matching_subtrees(tree,
                                                'list_comp_expr',
                                                include_self=True,
                                                include_nested=False,
                                                exclude_trees=list_comp_exclude)

    complexity += 4 * len(list_comp_trees)
    let_trees = get_all_matching_subtrees(tree, 'let_expr', include_self=True, include_nested=False)
    for let_tree in let_trees:
        # Only look at the return statment of the let
        complexity += estimate_complexity(let_tree.children[1])
    return complexity

def estimate_list_complexity(list_tree):
    """
    Return an estimate of the complexity of a list
    """
    item_complexities = []
    list_item_trees = get_all_matching_subtrees(list_tree,
                                                'list_item',
                                                include_nested=False)
    for list_item_tree in list_item_trees:
        item_complexities.append(estimate_complexity(list_item_tree))
    list_len = len(list_item_trees)
    if list_len == 0:
        return 1
    if list_len == 1:
        return item_complexities[0]
    item_complexities.sort(reverse=True)
    return item_complexities[0] + item_complexities[1]
