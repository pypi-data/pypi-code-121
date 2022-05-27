'''
Defines the messages used by SCA2D when checks fail.
'''

import hashlib
from dataclasses import dataclass
import logging
from colorama import Fore, Back, Style

def gitlab_summary(messages):
    ''' This returns a list of dictionaries in the form of a gitlab report
    json.'''

    report = []
    for message in messages:
        gl_dict = message_to_gitlab_json(message)
        if gl_dict is not None:
            report.append(gl_dict)
    return report

def message_to_gitlab_json(message):
    ''' This returns a dictionary for one message representing the json
    structure needed for a gitlab code quality report'''

    severity = message_severity_gitlab(message)
    if severity is None:
        return None
    fingerprint = hashlib.md5(message.pretty(colour=False).encode('utf-8'))
    gl_dict = {"description": message.message,
               "fingerprint": fingerprint.hexdigest(),
               "severity": severity,
               "location": {"path": message.filename,
                            "lines": {"begin": message.line}}}
    return gl_dict

def message_severity_gitlab(message):
    '''Convert message code to a gitlab severity level'''
    code_type = message.code[0]
    if code_type == "F":
        return "critical"
    if code_type == "E":
        return "major"
    if code_type == "W":
        return "minor"
    if code_type == "I":
        return "info"
    if code_type == "D":
        return "depreciated"
    #Skip other types
    return None


@dataclass
class MessageSummary:
    '''
    A class to hold the summaries of the number of messages
    '''
    fatal: int = 0
    error: int = 0
    warning: int = 0
    info: int = 0
    deprecated: int = 0
    debug: int = 0

    def __str__(self):
        ret = "\nSCA2D message summary\n=====================\n"
        ret += f"Fatal errors: {self.fatal}\n"
        ret += f"Errors:       {self.error}\n"
        ret += f"Warnings:     {self.warning}\n"
        ret += f"Info:         {self.info}\n"
        ret += f"Depreciated   {self.deprecated}\n"
        return ret

def count_messages(messages):
    """
    Count the number of messages of each type
    """
    summary = MessageSummary()
    for message in messages:
        code_type = message.code[0]
        if code_type == "F":
            summary.fatal += 1
        elif code_type == "E":
            summary.error += 1
        elif code_type == "W":
            summary.warning += 1
        elif code_type == "I":
            summary.info += 1
        elif code_type == "D":
            summary.deprecated += 1
        elif code_type == "U":
            summary.debug += 1
    return summary

def print_messages(messages, filename="INPUT_CODE", colour=False, debug=False):
    """
    Print all collected messages for this file.
    """
    if len(messages) > 0:
        messages.sort(key=lambda msg: (msg.line, msg.column))
        for message in messages:
            if (not debug) and message.code.startswith("U"):
                #If not in debug mode do not print U-type warnings
                continue
            print(message.pretty(colour=colour))
    else:
        no_msg_text = (f"{filename} passed all checks!")
        if colour:
            no_msg_text = Fore.GREEN + no_msg_text + Style.RESET_ALL
        print(no_msg_text)

class Message:
    """Class for storing the analysis messages."""

    def __init__(self, filename, code, tree, args=None):
        if args is None:
            args = []
        self.filename = filename
        self.code = code
        self.tree = tree
        expected_args = self.raw_message.count('%s')
        if expected_args == 0:
            if args != []:
                logging.warning('Unexpected args sent to warning %s. '
                                'This is a problem with SCA2D not with your scad code.',
                                code)
                args = []
        else:
            if len(args) != expected_args:
                logging.warning('Wrong number of args sent to %s.'
                                'This is a problem with SCA2D not with your scad code.',
                                code)
                args = ['X']*expected_args
        self.args = tuple(args)

    def __str__(self):
        return self.pretty()

    def __repr__(self):
        return "<sca2d.messages.Message " + self.pretty() + ">"

    @property
    def line(self):
        '''
        The line in the code where the a check raised this message.
        '''

        return self.tree.line

    @property
    def column(self):
        '''
        The column on Message.line of the code where the a check raised this message.
        '''

        return self.tree.column

    @property
    def raw_message(self):
        '''
        The message describing the check that failed without any arguments from
        this instance of the message
        '''
        if self.code in MESSAGES:
            message_txt = MESSAGES[self.code]
        else:
            message_txt = 'Unknown message'
        return message_txt

    @property
    def message(self):
        '''
        The message describing the check that failed.
        '''
        message_txt = self.raw_message
        expected_args = message_txt.count('%s')
        if expected_args>0:
            return message_txt%self.args
        return message_txt

    def pretty(self, colour=False):
        '''
        Pretty printing the error message. Requires the filename.
        '''
        msg = f'{self.filename}:{self.line}:{self.column}: {self.code}: {self.message}'
        if colour:
            if self.code.startswith('F'):
                msg = Back.RED + msg + Style.RESET_ALL
            elif self.code.startswith('E'):
                msg = Fore.RED + msg + Style.RESET_ALL
            elif self.code.startswith('W'):
                msg = Fore.YELLOW + msg + Style.RESET_ALL
        return msg

MESSAGES = {
    "F0001": ("Cannot read file due to syntax error:%s\nIf you belive"
              " this is a bug in SCA2D please report it to us.\n"),
    "F0002": "Cannot open file.",
    "E0001": "Argument in definition should be a variable or a variable with default value.",
    "E0002": "Defining an non-keyword argument after a keyword argument.",
    "E0003": "Wrong number of input arguments for Built-In call: %s",
    "E0004": "Empty argument in function/module header.",
    "E0005": "Empty item in list.",
    "E1001": "`use` or `include` can only be used in the outer scope.",
    "E2001": "Variable `%s` used but never defined.",
    "E2002": "Module `%s` used but never defined.",
    "E2003": "Function `%s` used but never defined.",
    "E2004": "Attribute style indexing can only use `.x`, `.y` or `.z`",
    "E3001": ("Cannot read file `%s` due to syntax error:%s\n[%s]\nIf you belive"
              " this is a bug in SCA2D please report it to us."),
    "E3002": "Cannot open file `%s`.\n[%s]",
    "E3003": "Cannot include %s as the include definitions form a loop.\n [%s]",
    "W1001": "Used library `%s` is not needed.",
    "W1002": "Included library `%s` is not needed.",
    "W1003": "File is empty!",
    "W2001": "Variable `%s` overwritten within scope.",
    "W2002": "Overwriting `%s` variable from a lower scope.",
    "W2003": "Module `%s` multiply defined within scope.",
    "W2004": "Overwriting `%s` module definition from a lower scope.",
    "W2005": "Function `%s` multiply defined within scope.",
    "W2006": "Overwriting `%s` function definition from a lower scope.",
    "W2007": "Variable `%s` defined but never used.",
    "W2008": "Module `%s` defined but never used.",
    "W2009": "Function `%s` defined but never used.",
    "W2010": "Variable %s is defined by multiple imports",
    "W2011": "Module %s is defined by multiple imports",
    "W2012": "Function %s is defined by multiple imports",
    "W2013": "Overwriting input argument `%s`",
    "W2014": "Overwriting input keyword argument `%s` when keyword is not undef",
    "W2015": "Overwriting keyword `%s` should be done at start of module scope",
    "W3001": "Too many input arguments",
    "W3002": "Too few input arguments",
    "W3003": "Keyword argument `%s` does not match any argument in definition",
    "W3004": "Required argument `%s` is not provided",
    "W3005": "Argument `%s` is assigned multiple times",
    "I0001": "Semicolon not required",
    "I0002": "Pointless scope defined",
    "I0003": "Debug modifier in use.",
    "I0004": "Module call scope is defined implicitly rather than with braces",
    "I0005": "File contains %s global variables.",
    "I0006": "Trailing whitespace.",
    "I1001": "Overly complicated argument contains %s tokens.",
    "I1002": "Overly complicated expression contains %s tokens.",
    "I2001": "Assert called without message. Consider adding a message.",
    "I3001": "Global: %s does not match upper case naming style.",
    "D0001": "Assign is depreciated. Use a regular assignment.",
    "U0001": "Token of type %s cannot be processed. This is a SCA2D problem",
    "U0002": "Token of type %s misidentified as complex expression. This is a SCA2D problem",
    "U0003": "Argument has more than one child. This is a SCA2D problem"
}
