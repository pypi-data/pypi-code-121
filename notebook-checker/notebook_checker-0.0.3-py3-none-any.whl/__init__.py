import ast, os
from collections import defaultdict
from enum import Enum
from IPython.core.magic import register_line_magic

VarAccess = Enum('VarAccess', 'STORE LOAD DELETE')


class ScopeNode:
    ast_mapping = []

    def __init__(self, node, parent):
        self.node_type = type(node)
        self.parent = parent
      
        self.lineno = node.lineno if hasattr(node, 'lineno') else 1
        
        self.node_fields = {}
        self.ast_node_fields = {}

        if node:
            for fieldname, value in ast.iter_fields(node):
                # Store original AST fields
                self.ast_node_fields[fieldname] = value

                # Store Scope node instances
                if isinstance(value, ast.AST):
                    self.node_fields[fieldname] = self.create_node(value, self)
                elif isinstance(value, list):
                    self.node_fields[fieldname] = [self.create_node(el, self) for el in value]
                else:
                    self.node_fields[fieldname] = value
    
    @classmethod
    def create_node(cls, node, parent):
        # Search mapping from most specific subclass to general base class
        for ast_type, node_type in cls.ast_mapping[::-1]:
            if isinstance(node, ast_type):
                return node_type(node, parent)
                
        return node
    
    @classmethod    
    def add_mapping(cls, *ast_sources):
        for source in ast_sources:
            cls.ast_mapping.append((source, cls))

    def get_children(self):
        for child in self.node_fields.values():
            if isinstance(child, ScopeNode):
                yield child
            elif isinstance(child, list):
                for sibling in child:
                    if isinstance(sibling, ScopeNode):
                        yield sibling
    
    def traverse_apply(self, func, *args, **kwargs):
        if hasattr(self, func): 
            getattr(self, func)(*args, **kwargs)

        for child in self.get_children():
            child.traverse_apply(func, *args, **kwargs)

    def get_instances(self, *node_types, outer=False):
        instances = []
        if isinstance(self, tuple(node_types)) or self.node_type in node_types:
            instances.append(self)
            
        if outer and instances != []:
            return instances

        for child in self.get_children():
            instances.extend(child.get_instances(*node_types, outer=outer))

        return instances
        
    def inject_code(self, template, offset=0, **kwargs):
        code = ast.parse(template.format(**kwargs))

        for i, node in enumerate(code.body):
            self.ast_body.insert(i + offset, node)
    
    def inject_before(self, template, **kwargs):
        prev = self
        parent = self.parent
        
        while not hasattr(parent, 'body') or prev not in parent.body:
            prev = parent
            parent = parent.parent

        index = parent.body.index(prev)
        parent.inject_code(template, offset=index, **kwargs)
    
    def __getattr__(self, name):
        # These functions get auto-passed up to the parent
        if name in ['_store_var', '_load_var'] and self.parent:
            return getattr(self.parent, name)

        # Original AST Node fields are retained in ScopeNode objects
        split_name = name.split('_')
        if len(split_name) > 0 and split_name[0] == 'ast':
            return self.ast_node_fields['_'.join(split_name[1:])]
        elif name in self.node_fields:
            return self.node_fields[name]

        raise AttributeError

ScopeNode.add_mapping(ast.AST)


class VariableNode(ScopeNode):
    access_mapping = {ast.Load: VarAccess.LOAD,
                      ast.Store: VarAccess.STORE,
                      ast.Del: VarAccess.DELETE}
    
    def __init__(self, node, parent):
        super().__init__(node, parent)        
        self.access = VariableNode.access_mapping[self.ctx.node_type]

    def scope_store(self):
        if self.access is VarAccess.STORE:
            self._store_var(self.id, self)
        
    def scope_load(self):
        if self.access is VarAccess.LOAD:
            self._load_var(self.id, self)

VariableNode.add_mapping(ast.Name)


class ArgumentNode(ScopeNode):
    def scope_store(self):
        self._store_var(self.arg, self)

ArgumentNode.add_mapping(ast.arg)


class DelimitedScope(ScopeNode):
    def __init__(self, node, parent):
        super().__init__(node, parent)        
        self.store = defaultdict(list)

    def _store_var(self, name, node):
        self.store[name].append(node)
   
DelimitedScope.add_mapping(ast.ClassDef)


class EnclosedScope(DelimitedScope):
    def __init__(self, node, parent):
        super().__init__(node, parent)
        self.load = defaultdict(list)
    
    def _load_var(self, name, node):
        self.load[name].append(node)
        if name not in self.store and self.parent:
            self.parent._load_var(name, node)

EnclosedScope.add_mapping(ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


class FunctionScope(EnclosedScope):
    def free_vars(self):
        return [(var, occ) for var, occ in self.load.items() if var not in self.store]

FunctionScope.add_mapping(ast.FunctionDef, ast.AsyncFunctionDef)


class CellScope(ScopeNode):
    def __init__(self, node, parent, raw, run_count):
        super().__init__(node, parent)

        self.raw = raw
        self.run_count = run_count

    def run_checks(self, check_globals=True, check_keywords=True, **kwargs):
        # First determine local scopes (which is the compiler order)
        self.traverse_apply('scope_store')
        # Then load variables in scopes
        self.traverse_apply('scope_load')
       
        # Restart the logging store for each cell 
        self.inject_code(self.get_template('clear_log'))
        if self.first_cell():
            self.inject_code(self.get_template('load_logger')) 

        # Using stored stope information, inject code for actual checks
        if check_globals:
            self.check_globals()

        if check_keywords:
            self.check_keywords()

    def check_globals(self):
        for func in self.get_instances(FunctionScope, outer=True):
            for name, occurrences in func.free_vars():
                for var_load in occurrences: 
                    globals_err = self.build_error(f'Global variable {name} referenced '+
                                                    f'in function {func.name}', var_load.lineno)
                    
                    var_load.inject_before(self.get_template('global_check'),
                                                    name=name, err_msg=globals_err)

    def check_keywords(self):
        for glob in self.get_instances(ast.Global, ast.Nonlocal):
            keyword = glob.node_type.__name__.lower()
            err_message = self.build_error(f'Disallowed {keyword} keyword', glob.lineno)
            
            glob.inject_before(self.get_template('log_error'), err_msg=err_message)

    def first_cell(self):
        return len(self.parent.cells) == 1

    def get_template(self, name):
        return self.parent.templates[name]

    def build_error(self, message, line_number=None):
        pre = 'In [{run_count}]: line {line_number},  '
        post= '\n\n    {code_line}\n'
        
        if line_number:
            pre = pre.format(run_count=self.run_count, line_number=line_number)
            post = post.format(code_line=self.raw[line_number-1].strip())

        return pre+message+post


class GlobalScope(EnclosedScope):
    def __init__(self, *args, **kwargs):
        super().__init__(None, None)
        
        self.node_fields['cells'] =  []
        
        self.check_args = args
        self.check_kwargs = kwargs
        
        self.templates = {}
        self.load_templates()
    
    def add_cell(self, node, raw, run_count):
        self.cells.append(CellScope(node, self, raw, run_count))

    def run_checks(self):
        self.cells[-1].run_checks(*self.check_args, **self.check_kwargs)
    
    def load_templates(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        for filename in os.listdir(template_dir):
            if filename.endswith('.py'):
                with open(os.path.join(template_dir, filename)) as f:
                    self.templates[filename[:-3]] = f.read()


class ChecksTransformer(ast.NodeTransformer):
    def __init__(self, shell, *args, usr_err=True, **kwargs):
        self.shell = shell
        self.usr_err = usr_err
        
        self.global_scope = GlobalScope(*args, **kwargs)

    def visit_Module(self, node):
        try:
            run_count = self.shell.execution_count
            raw = self.get_raw_cell(run_count)

            self.global_scope.add_cell(node, raw, run_count)
            self.global_scope.run_checks()
            
        except Exception:
            if self.usr_err:
                import logging
                logging.error(f' {err}\n\nChecker crashed while parsing cell. '+
                    'Please email your current notebook to minorai@mprog.nl to report this bug.')
            else:
                import traceback
                traceback.print_exc()

        return node

    def get_raw_cell(self, run_count):
        hist_gen = self.shell.history_manager.get_range(0, run_count, run_count+1, raw=True)
        _, _, lines = next(hist_gen)
        return lines.split('\n')


@register_line_magic
def start_checks(line):
    ipython_shell = get_ipython()
 
    checks = [transformer for transformer in ipython_shell.ast_transformers
                                if isinstance(transformer, ChecksTransformer)]

    # Delete existing instances. Note: This also deletes the currently stored global scope!
    for check in checks:
        ipython_shell.ast_transformers.remove(check)

    # Checks are enabled by default, adding arguments turns off those specific checks 
    kwargs = {elem: False for elem in line.split()}
    
    ipython_shell.ast_transformers.append(ChecksTransformer(ipython_shell, **kwargs))

