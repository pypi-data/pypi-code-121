
import ply.lex
import ply.yacc
import re
import os

__version__ = "0.1"

class Lexer(object):
    """Lexer class"""

    t_ANY_ignore = ' \t'
    t_STCOMMENT_ignore = ''
    t_STCONFIGDIRECTIVEQUOTED_ignore = ''

    tokens = [
        'T_COMMENT',
        'T_QUOTE_DOUBLE',
        'T_CONFIG_DIRECTIVE_TAG',
        'T_CONFIG_DIRECTIVE_TAG_CLOSE',
        'T_CONFIG_DIRECTIVE',
        'T_CONFIG_DIRECTIVE_ARGUMENT'
    ]

    states = (
        ('STCOMMENT',                                       'exclusive'),
        ('STCONFIGDIRECTIVE',                               'exclusive'),
        ('STCONFIGDIRECTIVEQUOTED',                         'exclusive'),
    )

    def __init__(self, debug = False, reflags = re.IGNORECASE | re.VERBOSE):
        self.lexer = ply.lex.lex(module=self, debug = debug, reflags = reflags)
        self.st_continue = 0

    def t_ANY_error(self, t):
        act_pos = 0
        a_data = t.lexer.lexdata.split("\n")
        pos_data = {}
        for li in range(len(a_data)):
            pos_data[li] = act_pos
            act_pos += len(a_data[li])+1
            if act_pos > t.lexer.lexpos:
                break
        aff_line = a_data[li]
        pos = t.lexer.lexpos - pos_data[li]
        output = ("Lexer error: illegal token found in line %d at pos %d, column %d\n%s\n%s^" % \
                    (li, t.lexer.lexpos, pos, aff_line, (pos * "~")))
        raise Exception(output)

    def t_ANY_newline(self, t):
        r'\n|\r\n'
        if self.st_continue == 0:
            t.lexer.begin('INITIAL')
        else:
            self.st_continue = 0
        t.lexer.lineno += 1

    # hack for 'unterminated' lines, eg:
    # ServerRoot /foo/bar \
    # <EMPTY>
    def t_ANY_T_BACKSLASH_AND_NEWLINE(self, t):
        r'\\[ \t]*(\r|\n)(\r|\n)'
        self.st_continue = 0
        t.lexer.begin('INITIAL')
        self.st_action_quote = 0
        t.lexer.lineno += 1

    def t_ANY_T_BACKSLASH(self, t):
        r'\\[ \t]*(\r|\n)'
        self.st_continue = 1
        t.lexer.lineno += 1

# Comment

    def t_INITIAL_T_COMMENT(self, t):
        r'\#([^\r\n]+|[\r\n])'
        self.parse_comment(t)
        if t.value[-1] == "\n":
            t.value = t.value.rstrip("\n")
            t.lexer.lineno += 1
        return t

    def t_STCOMMENT_T_COMMENT(self, t):
        r'.*[^\r\n]+'
        self.parse_comment(t)
        return t

    def parse_comment(self, t):
        tval = t.value.strip()
        if tval[-1] == "\\":
            self.st_continue = 1
            t.lexer.begin('STCOMMENT')
        else:
            t.lexer.begin('INITIAL')

# End Comment

# Simple configuration directives and arguments

    def t_INITIAL_T_CONFIG_DIRECTIVE(self, t):
        r'(\s*)[a-z0-9_]+'
        t.lexer.begin('STCONFIGDIRECTIVE')
        return t

    def t_INITIAL_T_CONFIG_DIRECTIVE_TAG(self, t):
        r'<[a-z]+(\s+)[^>]+>'
        return t

    def t_INITIAL_T_CONFIG_DIRECTIVE_TAG_CLOSE(self, t):
        r'</[a-z]+(\s*)>'
        return t

    def t_STCONFIGDIRECTIVE_STCONFIGDIRECTIVEQUOTED_T_QUOTE_DOUBLE(self, t):
        r'(?<!\\)"'
        if t.lexer.lexstate == 'STCONFIGDIRECTIVE':
            t.lexer.begin('STCONFIGDIRECTIVEQUOTED')
        else:
            t.lexer.begin('STCONFIGDIRECTIVE')
        return t

    def t_STCONFIGDIRECTIVE_T_CONFIG_DIRECTIVE_ARGUMENT(self, t):
        r'[^ \n]+'
        return t

    def t_STCONFIGDIRECTIVEQUOTED_T_CONFIG_DIRECTIVE_ARGUMENT(self, t):
        r'([^"\\\n]|\\.)+'
        t.lexer.lineno += len(t.value.split("\n"))-1
        return t

# END Simple configuration directives and arguments

class Parser(object):
    tokens = Lexer.tokens

    def __init__(self):
        self.lexer = Lexer()
        self.parser = ply.yacc.yacc(module=self, tabmodule="httpd_pyparser.apacheparsetab", debug = False)

        self.configlines = []
        self.current = self.configlines
        self._stack = [self.configlines]
        self.quoted = 'no_quote'

    def p_config_directive(self, p):
        """config_lines : comment
                        | config_lines comment
                        | config_directive_with_argument
                        | config_lines config_directive_with_argument
                        | config_directive_tag_token
                        | config_lines config_directive_tag_token"""
        pass

    def p_comment_line(self, p):
        """comment : T_COMMENT"""
        self.current.append({'type': 'comment', 'value': p[1], 'lineno': p.lineno(1)})

    def p_config_directive_with_argument(self, p):
        """config_directive_with_argument : config_directive_token config_directive_argument_list"""
        pass

    def p_config_directive_token(self, p):
        """config_directive_token : T_CONFIG_DIRECTIVE"""
        self.current.append({'type': 'directive', 'value': p[1], 'lineno': p.lineno(1), 'arguments': [], 'blocks': []})

    def p_config_directive_tag_token(self, p):
        """config_directive_tag_token : config_directive_tag_token_open
                                      | config_directive_tag_token_close"""
        pass

    def p_config_directive_tag_token_open(self, p):
        """config_directive_tag_token_open : T_CONFIG_DIRECTIVE_TAG"""
        d = p[1].strip("<").strip(">")
        offset = d.find(" ")
        val = d[:offset]
        valarg = d[offset+1:]
        if valarg[0] == "\"" and valarg[-1] == "\"":
            arg = [{'value': valarg.strip("\""), 'quote_type': 'quoted', 'lineno': p.lineno(1)}]
        else:
            arg = []
            for a in valarg.split(" "):
                if a.strip() != "":
                    arg.append({'value': a.strip(), 'quote_type': 'no_quote', 'lineno': p.lineno(1)})
        self.current.append({'type': 'directive_tag', 'value': val, 'lineno': p.lineno(1), 'arguments': arg, 'blocks': []})
        self.current[-1]['blocks'].append([])
        self._stack.append(self.current[-1]['blocks'][-1])
        self.current = self.current[-1]['blocks'][-1]

    def p_config_directive_tag_token_close(self, p):
        """config_directive_tag_token_close : T_CONFIG_DIRECTIVE_TAG_CLOSE"""
        del(self._stack[-1])
        self.current = self._stack[-1]
        self.current.append({'type': 'directive_tag_close', 'value': p[1].strip("<").strip(">").lstrip("/"), 'lineno': p.lineno(1), 'arguments': [], 'blocks': []})

    def p_config_directive_argument_list(self, p):
        """config_directive_argument_list : config_directive_argument_not_quoted_list
                                          | config_directive_argument_quoted_list
                                          | config_directive_argument_list config_directive_argument_not_quoted_list
                                          | config_directive_argument_list config_directive_argument_quoted_list"""
        pass

    def p_config_directive_argument_quoted_list(self, p):
        """config_directive_argument_quoted_list : config_directive_quoted_token config_directive_argument_not_quoted_list config_directive_quoted_token"""
        pass

    def p_config_directive_argument_not_quoted_list(self, p):
        """config_directive_argument_not_quoted_list : config_directive_argument_token
                                                     | config_directive_argument_not_quoted_list config_directive_argument_token"""
        pass

    def p_config_directive_quote(self, p):
        """config_directive_quoted_token : T_QUOTE_DOUBLE"""
        if self.quoted == 'no_quote':
            self.quoted = 'quoted'
        elif self.quoted == 'quoted':
            self.quoted = 'no_quote'
        pass

    def p_config_directive_argument_token(self, p):
        """config_directive_argument_token : T_CONFIG_DIRECTIVE_ARGUMENT"""
        self.current[-1]['arguments'].append({'value': p[1], 'lineno': p.lineno(1), 'quote_type': self.quoted})

    # handling parser error
    def p_error(self, p):
        if p:
            act_pos = 0
            a_data = p.lexer.lexdata.split("\n")
            pos_data = {}
            for li in range(len(a_data)):
                pos_data[li] = act_pos
                act_pos += len(a_data[li])+1
                if act_pos > p.lexer.lexpos:
                    break
            aff_line = a_data[li]
            pos = p.lexer.lexpos - pos_data[li]
            output = ("Parser error: syntax error in line %d at pos %d, column %d\n%s\n%s^" % \
                    (li+1, p.lexer.lexpos, pos, aff_line, (pos * "~")))
            raise Exception(output)

class Writer(object):
    def __init__(self, data, indentstr = "    "):
        self.lineno = 1
        self.output = []
        self.ident = ""
        self.sdata = data
        self.quote_types = {
            'no_quote': "",
            'quotes': "'",
            'quoted': "\"",
        }
        self.indentstr = indentstr
        self.depth = 0
        self.currline = []

    # the main cycle
    def generate(self, block = None):
        if block == None:
            block = self.sdata
        self.currline = []
        lastlineno = 0
        idx = 0
        while idx < len(block):
            i = block[idx]
            # write empty lines
            while self.lineno < i['lineno']:
                self.output.append(" ".join(self.currline))
                self.lineno += 1
            if i['type'].lower() == "comment":
                self.currline.append("%s" % (i['value']))
            elif i['type'].lower() == "directive":
                self.currline.append("%s" % (i['value']))
                eindent = ""
                for a in i['arguments']:
                    if a['lineno'] > self.lineno:
                        self.currline.append(" \\")
                        self.output.append("%s%s" % (self.indentstr*(self.depth), " ".join(self.currline)))
                        self.currline = []
                        self.lineno = a['lineno']
                        eindent = len(self.indentstr*(self.depth) + i['value'] + " " + i['arguments'][0]['value'] + " ")
                    self.currline.append("%s%s%s%s" % (eindent, self.quote_types[a['quote_type']], a['value'], self.quote_types[a['quote_type']]))
            elif i['type'].lower() == "directive_tag":
                val = [i['value']]
                for a in i['arguments']:
                    val.append("%s%s%s" % (self.quote_types[a['quote_type']], a['value'], self.quote_types[a['quote_type']]))
                self.currline.append("<%s>" % (" ".join(val)))
                self.output.append("%s%s" % (self.indentstr*(self.depth), " ".join(self.currline)))
                self.lineno = i['lineno']
                if 'blocks' in i.keys() and len(i['blocks']) > 0:
                    for b in i['blocks']:
                        self.depth += 1
                        self.lineno += 1
                        self.generate(b)
                        self.depth -= 1
            elif i['type'].lower() == "directive_tag_close":
                self.currline.append("</%s>" % (i['value']))
                self.output.append("%s%s" % (self.indentstr*(self.depth), " ".join(self.currline)))
                self.lineno += 1
                self.currline = []
            if lastlineno != i['lineno'] and len(self.currline) > 0:
                self.output.append("%s%s" % (self.indentstr*(self.depth), " ".join(self.currline)))
                self.lineno += 1
                lastlineno = i['lineno']
            self.currline = []
            idx += 1

class Struct(object):
    linenos = []
    def __init__(self, data, indentstr = "    "):
        self.data = data
        self.items = []
        self.istack = [self.items]
        self.depth = -1
        self.indentstr = indentstr
        self.last_line = 1
        self.indexes = {}
        self.indexstack = []
        self.virtualhosts = []
        #self.linenos = []
        self.build(self.data, self.items)

    def rawdirective(self, key, val):
        arguments = []
        if type(val) == str:
            val = [val]
        for v in val:
            qtype = 'no_quote'
            if len(v) > 3:
                if v[0] == '"' and v[-1] == '"':
                    qtype = 'quoted'
                elif v[0] == "'" and v[-1] == "'":
                    qtype = 'quotes'
            arguments.append({
                'value': v,
                'quote_type': qtype,
                'lineno': 0,
            })
        item = {
            'arguments': arguments,
            'blocks': [],
            'lineno': 0,
            'type': 'directive',
            'value': key
        }
        return item

    def additem(self, item, lineno = None):
        if lineno is None:
            lineno = len(self.items)+1
        item['lineno'] = lineno
        if hasattr(item, 'arguments'):
            for a in item['arguments']:
                a['lineno'] = lineno
        self.items.insert(lineno, item)
        self.data.insert(lineno, item)
        for i in self.data[lineno:]:
            i['lineno'] += 1
        Struct.linenos.insert(lineno, lineno+1)
        for l in Struct.linenos[lineno+1:]:
            print(l)
            l += 1

    def build(self, data, stack):
        self.depth += 1
        last_item = ""
        for b in data:
            while self.last_line < b['lineno'] and last_item != 'directive_tag':
                stack.append(Struct.EmptyLine(self, {'lineno': self.last_line}))
                self.last_line += 1
                last_item = b['type']
            if b['type'] == 'comment':
                stack.append(Struct.Comment(self, b))
            if b['type'] == 'directive_tag':
                stack.append(Struct.Context(self, b))
                if b['value'].lower() == "virtualhost":
                    self.virtualhosts.append(stack[-1])
            if b['type'] == 'directive_tag_close':
                self.last_line -= 1
                if b['value'].lower() in self.indexes:
                    del(self.indexstack[-1])
            elif b['type'] == 'directive':
                stack.append(Struct.Directive(self, b))
            self.last_line += 1
            last_item = b['type']
        self.depth -= 1

    class AbstractItem(object):
        def __init__(self, parent, item):
            self.parent = parent
            self.lineno = item['lineno']
            Struct.linenos.append(self.lineno)
            self.item = item

        @property
        def lineno(self):
            return self.__lineno

        @lineno.setter
        def lineno(self, x):
            self.__lineno = x
            if hasattr(self, 'arguments'):
                for a in self.arguments:
                    a.lineno = x

    class EmptyLine(AbstractItem):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            pass

        def __repr__(self):
            return "Empty line"

    class Comment(AbstractItem):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.comment = self.item['value']

        def __repr__(self):
            return "Comment: '%s'" % (self.comment[0:10] + "..." if len(self.comment) > 10 else self.comment)

    class Context(AbstractItem):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ctx = self.item['value']
            self.tagargs = [Struct.Arg(self, a) for a in self.item['arguments']]
            self.items = []
            self.directives = {}
            self.parent.last_line += 1
            for b in self.item['blocks']:
                self.parent.build(b, self.items)
            for i in self.items:
                if type(i) == Struct.Directive:
                    ikey = i.name.lower()
                    ival = [v.value for v in i.args]
                    if ikey not in self.directives:
                        self.directives[ikey] = ival
                    else:
                        if type(self.directives[ikey]) != list:
                            self.directives[ikey] = [self.directives[ikey]]
                        self.directives[ikey].append(ival)

        def __repr__(self):
            return "'%s' Context" % self.ctx

    class Directive(AbstractItem):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = self.item['value']
            self.args = [Struct.Arg(self, a) for a in self.item['arguments']]
            self.lineno = self.item['lineno']

        def __repr__(self):
            return("'%s' Directive" % (self.name))

    class Arg(AbstractItem):
        def __init__(self, parent, arg):
            self.qtypes = {
                'no_quote': "",
                'quotes': "'",
                'quoted': "\""
            }
            self.parent = parent
            self.value = arg['value']
            self.quote_type = arg['quote_type']
            self.lineno = arg['lineno']

        def __str__(self):
            return "%s%s%s" % (self.qtypes[self.quote_type], self.value, self.qtypes[self.quote_type])

        def __repr__(self):
            return "%s%s%s" % (self.qtypes[self.quote_type], self.value, self.qtypes[self.quote_type])
