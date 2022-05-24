import re
from string import Template


class _TestCase(object):  # pragma: no cover
    def __init__(self, n_positional, var_positional, n_keyword, var_keyword):
        self.n_positional = n_positional
        self.var_positional = var_positional
        self.n_keyword = n_keyword
        self.var_keyword = var_keyword
        self._method_name = None
        self.nargs = None
        self.put_help = bool((n_positional + n_keyword) % 2)
        self.decorator = None

    @property
    def method_name(self):
        def generate_partial_method_name(var, qtde, n):
            name = ''
            if qtde > 0:
                name = str(qtde)
            if n:
                if name:
                    name += '_plus_'
                name += 'n'
            if name:
                name += '_' + var
            return name

        if self._method_name is None:
            _args = generate_partial_method_name('arg', self.n_positional, self.var_positional)
            kwargs = generate_partial_method_name('kwarg', self.n_keyword, self.var_keyword)
            _method_name = self.decorator.lower() + '_with_'
            if _args and kwargs:
                return _method_name + _args + '_and_' + kwargs
            if _args or kwargs:
                return _method_name + _args + kwargs
            self._method_name = _method_name + 'no_args'

        return self._method_name

    @property
    def signature(self):
        signature = []
        for p in range(self.n_positional):
            signature.append('positional_%d' % (p + 1))

        if self.var_positional:
            signature.append('*var_positional')

        for k in range(self.n_keyword):
            signature.append('keyword_%d=\'default_%d\'' % ((k + 1), (k + 1)))

        if self.var_keyword:
            signature.append('**var_keyword')

        return ', '.join(signature)

    def method_call(self, n_positional=None, var_positional=None, n_keyword=None, var_keyword=None):
        raise NotImplementedError

    def positional_args(self, n_positional=None, var_positional=None):
        if n_positional is None:
            n_positional = self.n_positional
        if var_positional is None:
            var_positional = self.var_positional

        args = []
        for p in range(n_positional):
            args.append('positional_%d' % (p + 1))

        if var_positional:
            args.append('var_positional_1')
            args.append('var_positional_2')

        return args

    def keyword_args(self, n_keyword=None, var_keyword=None, return_default_values=False):
        raise NotImplementedError

    @property
    def help(self):
        if self.put_help:
            return 'Help for %s' % self.method_name
        return ''

    @property
    def method_return(self):
        return re.sub(r'=.*?\d', '', self.signature.replace('*', '').replace('\'', ''))

    def method_return_assert(self, n_positional=None, var_positional=None,
                             n_keyword=None, var_keyword=None,
                             return_default_values=False):
        if self.method_return:
            args = []
            var_positionals = tuple()
            for a in self.positional_args(n_positional, var_positional):
                if a.startswith('var'):
                    var_positionals += (a, )
                else:
                    args.append(a)

            if var_positionals:
                args.append(var_positionals)

            var_keywords = {}
            for a in self.keyword_args(n_keyword, var_keyword, return_default_values):
                if a.startswith('--'):
                    a = a[2:]
                if a.startswith('var'):
                    key, _, value = a.partition('=')
                    var_keywords[key] = value
                else:
                    _, _, value = a.partition('=')
                    args.append(value)

            if var_keywords:
                args.append(var_keywords)

            if len(args) == 1:
                ret = args[0]
            else:
                ret = tuple(args)
            return re.escape(str(ret)).replace('\'', '\\\'')
        return ''

    @property
    def method_usage(self):
        raise NotImplementedError

    @property
    def usage_args(self):
        args = []
        for p in range(self.n_positional):
            args.append('positional_%d' % (p + 1))
        if self.var_positional:
            args.append(r'\[var_positional \[var_positional ...]]')
        for k in range(self.n_keyword):
            args.append(r'\[keyword_%d=VALUE]' % (k + 1))
        if self.var_keyword:
            args.append(r'\[var_keyword=VALUE \[var_keyword=VALUE ...]]')
        return args

    @property
    def method_help(self):
        return self.method_usage + '.*' + self.help

    @staticmethod
    def get_action_nargs(name):
        from polidoro_argument.argument import Argument
        # noinspection PyProtectedMember
        for a in Argument._arguments:
            if a.method_name == name:
                if isinstance(a.nargs, str) and '+' in a.nargs:
                    return re.sub(r'(.*)\+', 'at least \\1', a.nargs)
                return str(a.nargs)

    @property
    def method_template(self):
        template = """
    @${decorator}
    def ${method_name}(${signature}):
        print('${method_name} called')
        return ${method_return}
"""
        return Template(template).substitute(
            decorator=self.decorator + ('(help=\'%s\')' % self.help if self.put_help else ''),
            method_name=self.method_name,
            signature=self.signature,
            method_return=self.method_return
        )

    @property
    def usage_test(self):
        template = """
def test_usage_${method_name}(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args(['-h'])
    assert exit_info.value.code == 0
    
    output = capsys.readouterr().out
    assert re.search(r'usage:.*${method_usage}', output, flags=re.DOTALL), output
"""
        return Template(template).substitute(
            method_call=self.method_call().strip(),
            method_name=self.method_name,
            method_help=self.method_help,
            method_usage=self.method_usage
        )

    @property
    def help_test(self):
        template = """
def test_help_${method_name}(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args(['--help'])
    assert exit_info.value.code == 0
    
    output = capsys.readouterr().out
    assert re.search(r' *${method_help}.*\\n', output, flags=re.DOTALL), output
"""
        return Template(template).substitute(
            method_call=self.method_call().strip(),
            method_name=self.method_name,
            method_help=self.method_help,
            method_usage=self.method_usage
        )

    @property
    def call_test(self):
        template = """
def test_call_${method_name}(capsys):
    parser.parse_args('${method_call}'.split())
    
    output = capsys.readouterr().out
    assert re.search(r'${method_name} called\\n${method_return_assert}', output), output
"""
        return Template(template).substitute(
            method_call=self.method_call(),
            method_name=self.method_name,
            method_return_assert=self.method_return_assert()
        )

    @property
    def one_less_arg_test(self):
        raise NotImplementedError

    @property
    def one_more_arg_test(self):
        if self.var_positional:
            return ''

        template = """
def test_call_${method_name}_with_one_more_arg_test(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args('${method_call}'.split())
    assert exit_info.value.code == 2
    
    output = capsys.readouterr().err
    assert re.search(r'test${decorator}: error: unrecognized arguments: positional_\\d', output), output
"""
        return Template(template).substitute(
            method_call=self.method_call(n_positional=self.n_positional + 1),
            method_name=self.method_name,
            decorator=self.decorator
        )

    @property
    def one_more_kwarg_test(self):
        raise NotImplementedError

    @property
    def one_less_kwarg_test(self):
        if self.var_keyword:
            return ''

        template = """
def test_call_${method_name}_with_one_less_kwarg_test(capsys):
    parser.parse_args('${method_call}'.split())
    
    output = capsys.readouterr().out
    assert re.search(r'${method_name} called\\n${method_return_assert}', output), output
"""
        return Template(template).substitute(
            method_call=self.method_call(n_keyword=self.n_keyword - 1, var_keyword=False),
            method_name=self.method_name,
            method_return_assert=self.method_return_assert(
                n_keyword=self.n_keyword - 1, var_keyword=False, return_default_values=True
            )
        )


class ArgumentTestCase(_TestCase):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super(ArgumentTestCase, self).__init__(*args, **kwargs)
        self.decorator = 'Argument'

    @property
    def method_usage(self):
        return r'\[' + ('--%s[ \\n]*%s' % (self.method_name, '[ \\n]*'.join(self.usage_args))).strip() + ']'

    def method_call(self, n_positional=None, var_positional=None, n_keyword=None, var_keyword=None):
        args = self.positional_args(n_positional, var_positional)
        args.extend(self.keyword_args(n_keyword, var_keyword))

        return '--%s %s' % (self.method_name, ' '.join(args))

    def keyword_args(self, n_keyword=None, var_keyword=None, return_default_values=False):
        if n_keyword is None:
            n_keyword = self.n_keyword
        if var_keyword is None:
            var_keyword = self.var_keyword

        args = []
        for k in range(n_keyword):
            args.append('keyword_%d=value_%d' % ((k + 1,) * 2))

        if return_default_values and self.n_keyword > 0:
            for k in range(n_keyword, self.n_keyword):
                args.append('keyword_%d=default_%d' % ((k + 1,) * 2))

        if var_keyword:
            args.append('var_keyword_1=value_1')
            args.append('var_keyword_2=value_2')

        return args

    @property
    def one_less_arg_test(self):
        if self.n_positional == 0:
            return ''
        template = """
def test_call_${method_name}_with_one_less_arg_test(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args('${method_call}'.split())
    assert exit_info.value.code == 2
    
    output = capsys.readouterr().err
    assert re.search(r'test${decorator}: error: argument --${method_name}: expected %s argument' % _TestCase.get_action_nargs('${method_name}'), output), output
"""
        return Template(template).substitute(
            method_call=self.method_call(n_positional=self.n_positional - 1, var_positional=False),
            method_name=self.method_name,
            decorator=self.decorator
        )

    @property
    def one_more_kwarg_test(self):
        if self.var_keyword:
            return ''

        template = """
def test_call_${method_name}_with_one_more_kwarg_test(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args('${method_call}'.split())
    assert exit_info.value.code == 2
    
    output = capsys.readouterr().err
    assert re.search(r'test${decorator}: error: unrecognized arguments: keyword_\\d=value_\\d', output), output
"""
        return Template(template).substitute(
            method_call=self.method_call(n_keyword=self.n_keyword + 1),
            method_name=self.method_name,
            decorator=self.decorator
        )


class CommandTestCase(_TestCase):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super(CommandTestCase, self).__init__(*args, **kwargs)
        self.decorator = 'Command'

    @property
    def method_usage(self):
        return self.method_name

    @property
    def internal_method_usage(self):
        return ('[ \\n]*%s' % ('[ \\n]*'.join(self.usage_args))).strip()

    def method_call(self, n_positional=None, var_positional=None, n_keyword=None, var_keyword=None):
        args = self.positional_args(n_positional, var_positional)
        args.extend(self.keyword_args(n_keyword, var_keyword))

        return '%s %s' % (self.method_name, ' '.join(args))

    def keyword_args(self, n_keyword=None, var_keyword=None, return_default_values=False):
        if n_keyword is None:
            n_keyword = self.n_keyword
        if var_keyword is None:
            var_keyword = self.var_keyword

        args = []
        for k in range(n_keyword):
            args.append('--keyword_%d=value_%d' % ((k + 1,) * 2))

        if return_default_values and self.n_keyword > 0:
            for k in range(n_keyword, self.n_keyword):
                args.append('--keyword_%d=default_%d' % ((k + 1,) * 2))

        if var_keyword:
            args.append('--var_keyword_1=value_1')
            args.append('--var_keyword_2=value_2')

        return args

    @property
    def usage_test(self):
        default = super(CommandTestCase, self).usage_test
        template = """
def test_internal_usage_${method_name}(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args(['${method_name}', '-h'])
    assert exit_info.value.code == 0
    
    output = capsys.readouterr().out
    assert re.search(r'usage: testCommand ${method_name}.*${internal_method_usage}', output, flags=re.DOTALL), output
"""
        return default + '\n' + Template(template).substitute(
            method_call=self.method_call().strip(),
            method_name=self.method_name,
            method_help=self.method_help,
            method_usage=self.method_usage,
            internal_method_usage=self.internal_method_usage
        )

    @property
    def help_test(self):
        default = super(CommandTestCase, self).help_test
        template = """
def test_internal_help_${method_name}(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args(['--help'])
    assert exit_info.value.code == 0
    
    output = capsys.readouterr().out
    assert re.search(r' *${method_help}.*\\n', output, flags=re.DOTALL), output
"""
        return default + '\n' + Template(template).substitute(
            method_call=self.method_call().strip(),
            method_name=self.method_name,
            method_help=self.method_help,
            method_usage=self.method_usage,
            internal_method_usage=self.internal_method_usage
        )

    @property
    def one_less_arg_test(self):
        if self.n_positional == 0:
            return ''
        template = """
def test_call_${method_name}_with_one_less_arg_test(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args('${method_call}'.split())
    assert exit_info.value.code == 2
    
    output = capsys.readouterr().err
    assert re.search(r'test${decorator} ${method_name}: error: the following arguments are required: %s' % ' '.join(${positional_args}), output), output
"""
        return Template(template).substitute(
            method_call=self.method_call(n_positional=self.n_positional - 1, var_positional=False),
            method_name=self.method_name,
            positional_args=self.positional_args(var_positional=0),
            decorator=self.decorator
        )

    @property
    def one_more_kwarg_test(self):
        if self.var_keyword:
            return ''

        template = """
def test_call_${method_name}_with_one_more_kwarg_test(capsys):
    with pytest.raises(SystemExit) as exit_info:
        parser.parse_args('${method_call}'.split())
    assert exit_info.value.code == 2
    
    output = capsys.readouterr().err
    assert re.search(r'test${decorator}: error: unrecognized arguments: --keyword_\\d=value_\\d', output), output
"""
        return Template(template).substitute(
            method_call=self.method_call(n_keyword=self.n_keyword + 1),
            method_name=self.method_name,
            decorator=self.decorator
        )
