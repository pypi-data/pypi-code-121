
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
        'T_SEMICOLON',
        'T_QUOTE_SINGLE',
        'T_CONFIG_DIRECTIVE',
        'T_CONFIG_DIRECTIVE_ARGUMENT',
        'T_BRACE_OPEN',
        'T_BRACE_CLOSE',
    ]

    states = (
        ('STCOMMENT',                                       'exclusive'),
        ('STCONFIGDIRECTIVE',                               'exclusive'),
        ('STCONFIGDIRECTIVEQUOTED',                         'exclusive'),
    )

    def __init__(self, debug = False, reflags = re.IGNORECASE | re.VERBOSE):
        self.lexer = ply.lex.lex(module=self, debug = debug, reflags = reflags)

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
        t.lexer.lineno += 1

# Semicolon - end of line

    def t_ANY_T_SEMICOLON(self, t):
        r';'
        t.lexer.begin('INITIAL')
        return t

# END Semicolon - end of line

# Braces

    def t_ANY_T_BRACE_OPEN(self, t):
        r'{'
        t.lexer.begin('INITIAL')
        return t

    def t_ANY_T_BRACE_CLOSE(self, t):
        r'}'
        return t

# END Braces

# Comment

    def t_ANY_T_COMMENT(self, t):
        r'\#([^\r\n]+|[\r\n])'
        if t.value[-1] == "\n":
            t.value = t.value.rstrip("\n")
            t.lexer.lineno += 1
        return t

# End Comment

# Simple configuration directives and arguments

    def t_INITIAL_T_CONFIG_DIRECTIVE(self, t):
        r'(\s*)[a-z0-9_]+'
        t.lexer.begin('STCONFIGDIRECTIVE')
        return t

    def t_STCONFIGDIRECTIVE_STCONFIGDIRECTIVEQUOTED_T_QUOTE_SINGLE(self, t):
        r"(?<!\\)'"
        if t.lexer.lexstate == 'STCONFIGDIRECTIVE':
            t.lexer.begin('STCONFIGDIRECTIVEQUOTED')
        else:
            t.lexer.begin('STCONFIGDIRECTIVE')
        return t

    def t_STCONFIGDIRECTIVE_T_CONFIG_DIRECTIVE_ARGUMENT(self, t):
        r'[^ ;{}\n]+'
        return t

    def t_STCONFIGDIRECTIVEQUOTED_T_CONFIG_DIRECTIVE_ARGUMENT(self, t):
        r'[^\']+'
        t.lexer.lineno += len(t.value.split("\n"))-1
        return t

# END Simple configuration directives and arguments

class Parser(object):
    tokens = Lexer.tokens

    def __init__(self):
        self.lexer = Lexer()
        self.parser = ply.yacc.yacc(module=self, tabmodule="httpd_pyparser.nginxparsetab", debug = False)

        self.configlines = []
        self.current = self.configlines
        self._stack = [self.configlines]

    def p_config_directive(self, p):
        """config_lines : config_directive_token semicolon_token
                        | comment
                        | config_lines comment
                        | config_directive_with_argument semicolon_token
                        | config_lines config_directive_token semicolon_token
                        | config_lines config_directive_with_argument semicolon_token
                        | config_directive_token brace_open_token config_lines brace_close_token
                        | config_lines config_directive_token brace_open_token config_lines brace_close_token
                        | config_directive_with_argument brace_open_token config_lines brace_close_token
                        | config_lines config_directive_with_argument brace_open_token config_lines brace_close_token"""
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

    def p_config_directive_argument_list(self, p):
        """config_directive_argument_list : config_directive_argument_token
                                          | config_directive_argument_token_quoted
                                          | config_directive_argument_list config_directive_argument_token
                                          | config_directive_argument_list config_directive_argument_token_quoted"""
        pass

    def p_config_directive_argument_token(self, p):
        """config_directive_argument_token : T_CONFIG_DIRECTIVE_ARGUMENT"""
        self.current[-1]['arguments'].append({'value': p[1], 'lineno': p.lineno(1), 'quote_type': 'no_quote'})

    def p_config_directive_argument_token_quoted(self, p):
        """config_directive_argument_token_quoted : T_QUOTE_SINGLE T_CONFIG_DIRECTIVE_ARGUMENT T_QUOTE_SINGLE"""
        self.current[-1]['arguments'].append({'value': p[2], 'lineno': p.lineno(1), 'quote_type': 'quotes'})

    def p_semicolon_token(self, p):
        """semicolon_token : T_SEMICOLON"""
        self.current[-1]['arguments'].append({'value': None, 'quote_type': 'no_quote'})

    def p_brace_open_token(self, p):
        """brace_open_token : T_BRACE_OPEN"""
        self.current[-1]['blocks'].append([])
        self._stack.append(self.current[-1]['blocks'][-1])
        self.current = self.current[-1]['blocks'][-1]

    def p_brace_close_token(self, p):
        """brace_close_token : T_BRACE_CLOSE"""
        del(self._stack[-1])
        self.current = self._stack[-1]

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

# END Parser class

class Writer(object):
    def __init__(self, data, indentstr = "    "):
        self.lineno = 1
        self.output = []
        self.ident = ""
        self.sdata = data
        self.quote_types = {
            'no_quote': "",
            'quotes': "'",
        }
        self.indentstr = indentstr
        self.depth = 0
        self.currline = []

    def write_directive(self, d):
        self.currline.append("%s" % (d['value']))
        if len(d['arguments']) == 0:
            d['arguments'].append({'value': None})
        aidx = 0
        eindent = 0
        for a in d['arguments']:
            if a['value'] is not None:
                # check if the argument is multiline
                _splitted = a['value'].split("\n")
                if len(_splitted) > 1:
                    newval = [""]
                    newval += [("%s  %s" % (self.indentstr*(self.depth), v.strip())) for v in _splitted[0:-1]]
                    newval += ["%s" % self.indentstr*(self.depth)]
                    a['value'] = "\n".join(newval)
                    self.lineno += len(_splitted)
                else:
                    # next arg is to next line, write the current content before
                    if a['lineno'] > self.lineno:
                        self.output.append("%s%s" % (self.indentstr*(self.depth), " ".join(self.currline)))
                        self.currline = []
                        self.lineno = a['lineno']
                        if aidx > 1:
                            eindent = len(d['value'] + " " + d['arguments'][0]['value'] + " ")
                self.currline.append("%s%s%s%s" % ((" " * eindent), self.quote_types[a['quote_type']], a['value'], self.quote_types[a['quote_type']]))
            else:
                if 'blocks' not in d.keys() or len(d['blocks']) == 0:
                    self.currline[-1] += ";"
            aidx += 1
        # write blocks recursively
        if 'blocks' in d.keys() and len(d['blocks']) > 0:
            for b in d['blocks']:
                self.currline.append("{")
                self.output.append("%s%s" % (self.indentstr*(self.depth), " ".join(self.currline)))
                self.depth += 1
                self.lineno += 1
                self.generate(b)

    # the main cycle
    def generate(self, block = None):
        if block == None:
            # initially, this is the whole config
            # in case of later calling, that's a block, eg http { ... }
            block = self.sdata
        idx = 0
        self.currline = []
        while idx < len(block):
            i = block[idx]
            # write empty lines
            while self.lineno < i['lineno']:
                line = " ".join(self.currline)
                if len(line) > 0:
                    self.output.append("%s%s" % (self.indentstr*(self.depth), line))
                else:
                    self.output.append("")
                self.lineno += 1
                self.currline = []

            if i['type'].lower() == "comment":
                self.currline.append("%s" % (i['value']))

            elif i['type'].lower() == "directive":
                self.write_directive(i)

            idx += 1

        if len(self.currline) > 0:
            self.output.append("%s%s" % (self.indentstr*(self.depth), " ".join(self.currline)))
            self.lineno += 1
            self.currline = []

        if self.depth > 0:
            self.currline.append("}")
            self.lineno += 1
            self.output.append("%s%s" % (self.indentstr*(self.depth-1), " ".join(self.currline)))
            self.currline = []
            self.depth -= 1
