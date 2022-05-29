from __future__ import unicode_literals

from pygments.token import Token, Keyword, Name, Comment, String, Operator, Number
from pygments.styles import get_style_by_name, get_all_styles
from prompt_toolkit.styles import DEFAULT_STYLE_EXTENSIONS, style_from_dict
from prompt_toolkit.utils import is_windows, is_conemu_ansi

__all__ = (
    'get_all_code_styles',
    'get_all_ui_styles',
    'generate_style',
)


def get_all_code_styles():
    """
    Return a mapping from style names to their classes.
    """
    result = dict((name, get_style_by_name(name).styles) for name in get_all_styles())
    # from rp import mini_terminal_for_pythonista
    # exec(mini_terminal_for_pythonista)
    result['win32'] = win32_code_style
    result['ryan']=ryan_style
    return result

ryan_style={# A rich, colored scheme I made (based on monokai)
    Token :"",
Token.Comment :"  #75715e",
Token.Comment.Hashbang :"",
Token.Comment.Multiline :"",
Token.Comment.Preproc :"",
Token.Comment.PreprocFile :"",
Token.Comment.Single :"",
Token.Comment.Special :"",
Token.Error :"  #960050 bg:#1e0010",
Token.Escape :" bold",
Token.Generic :"",
Token.Generic.Deleted :"  #f92672",
Token.Generic.Emph :"  italic",
Token.Generic.Error :"",
Token.Generic.Heading :"",
Token.Generic.Inserted :"  #a6e22e",
Token.Generic.Output :"",
Token.Generic.Prompt :"",
Token.Generic.Strong :"  bold",
Token.Generic.Subheading :"  #75715e",
Token.Generic.Traceback :"",
Token.Keyword :"  #66d9ef",
Token.Keyword.Constant :"",
Token.Keyword.Declaration :"",
Token.Keyword.Namespace :"  #f92672",
Token.Keyword.Pseudo :"",
Token.Keyword.Reserved :"",
Token.Keyword.Type :"",
Token.Literal :"  #ae81ff",
Token.Literal.Date :"  #e6db74",
Token.Literal.Number :"  #ae81ff",
Token.Literal.Number.Bin :"",
Token.Literal.Number.Float :"",
Token.Literal.Number.Hex :"",
Token.Literal.Number.Integer :"",
Token.Literal.Number.Integer.Long :"",
Token.Literal.Number.Oct :"",
Token.Literal.String :"  #e6db74",
Token.Literal.String.Backtick :"",
Token.Literal.String.Char :"",
Token.Literal.String.Doc :"",
Token.Literal.String.Double :"",
Token.Literal.String.Escape :"  #ae81ff",
Token.Literal.String.Heredoc :"",
Token.Literal.String.Interpol :"",
Token.Literal.String.Other :"",
Token.Literal.String.Regex :"",
Token.Literal.String.Single :"",
Token.Literal.String.Symbol :"",
Token.Name :"  #f8f8f2",
Token.Name.Attribute :"  #a6e22e",
Token.Name.Builtin :"",
Token.Name.Builtin.Pseudo :"",
Token.Name.Class :"  #a6e22e",
Token.Name.Constant :"  #66d9ef",
Token.Name.Decorator :"  #a6e22e",
Token.Name.Entity :"",
Token.Name.Exception :"  #a6e22e",
Token.Name.Function :"  #a6e22e",
Token.Name.Label :"",
Token.Name.Namespace :"",
Token.Name.Other :"  #a6e22e",
Token.Name.Property :"",
Token.Name.Tag :"  #f92672",
Token.Name.Variable :"#ff0000",
Token.Name.Variable.Class :"#ffd60a",
Token.Name.Variable.Global :"",
Token.Name.Variable.Instance :"",
Token.Operator :"  #f92672",
Token.Operator.Word :"",
Token.Other :"",
Token.Punctuation :"  #f8f8f2",
Token.Text :"  #f8f8f2",
Token.Text.Whitespace :"",
}
# ryan_style= \
#     {
#         # A rich, colored scheme I made (based on monokai)
#         Comment:"#00ff00",
#         Keyword:'#44ff44',
#         Number:'#378cba',
#         Operator:'',
#         String:'#26b534',
#         Token.Literal.String.Escape :"  #ae81ff",
#         #
#         Name:'',
#         Name.Decorator:'#ff4444',
#         Name.Class:'#ff4444',
#         Name.Function:'#ff4444',
#         Name.Builtin:'#ff4444',
#         #
#         Name.Attribute:'',
#         Name.Constant:'',
#         Name.Entity:'',
#         Name.Exception:'',
#         Name.Label:'',
#         Name.Namespace:'#dcff2d',
#         Name.Tag:'',
#         Name.Variable:'',
#     }

def get_all_ui_styles():
    """
    Return a dict mapping {ui_style_name -> style_dict}.
    """
    return {
        'default': default_ui_style,
        'blue': blue_ui_style,
    }


def generate_style(python_style, ui_style):
    """
    Generate Pygments Style class from two dictionaries
    containing style rules.
    """
    assert isinstance(python_style, dict)
    assert isinstance(ui_style, dict)

    styles = {}
    styles.update(DEFAULT_STYLE_EXTENSIONS)
    styles.update(python_style)
    styles.update(ui_style)

    return style_from_dict(styles)


# Code style for Windows consoles. They support only 16 colors,
# so we choose a combination that displays nicely.
win32_code_style = {
    Comment:                   "#00ff00",
    Keyword:                   '#44ff44',
    Number:                    '',
    Operator:                  '',
    String:                    '#ff44ff',

    Name:                      '',
    Name.Decorator:            '#ff4444',
    Name.Class:                '#ff4444',
    Name.Function:             '#ff4444',
    Name.Builtin:              '#ff4444',

    Name.Attribute:            '',
    Name.Constant:             '',
    Name.Entity:               '',
    Name.Exception:            '',
    Name.Label:                '',
    Name.Namespace:            '',
    Name.Tag:                  '',
    Name.Variable:             '',
}


default_ui_style = {
        # Classic prompt.
        Token.Prompt:                                 'bold',
        Token.Prompt.Dots:                            'noinherit',

        # (IPython <5.0) Prompt: "In [1]:"
        Token.In:                                     'bold #008800',
        Token.In.Number:                              '',

        # Return value.
        Token.Out:                                    '#ff0000',
        Token.Out.Number:                             '#ff0000',

        # Separator between windows. (Used above docstring.)
        Token.Separator:                              '#bbbbbb',

        # Search toolbar.
        Token.Toolbar.Search:                         '#22aaaa noinherit',
        Token.Toolbar.Search.Text:                    'noinherit',

        # System toolbar
        Token.Toolbar.System:                         '#22aaaa noinherit',

        # "arg" toolbar.
        Token.Toolbar.Arg:                            '#22aaaa noinherit',
        Token.Toolbar.Arg.Text:                       'noinherit',

        # Signature toolbar.
        Token.Toolbar.Signature:                      'bg:#44bbbb #000000',
        Token.Toolbar.Signature.CurrentName:          'bg:#008888 #ffffff bold',
        Token.Toolbar.Signature.Operator:             '#000000 bold',

        Token.Docstring:                              '#888888',

        # Validation toolbar.
        Token.Toolbar.Validation:                     'bg:#440000 #aaaaaa',

        # Status toolbar.
        Token.Toolbar.Status:                         'bg:#222222 #aaaaaa',
        Token.Toolbar.Status.BatteryPluggedIn:        'bg:#222222 #22aa22',
        Token.Toolbar.Status.BatteryNotPluggedIn:     'bg:#222222 #aa2222',
        Token.Toolbar.Status.Title:                   'underline',
        Token.Toolbar.Status.InputMode:               'bg:#222222 #ffffaa',
        Token.Toolbar.Status.Key:                     'bg:#000000 #888888',
        Token.Toolbar.Status.PasteModeOn:             'bg:#aa4444 #ffffff',
        Token.Toolbar.Status.PseudoTerminalCurrentVariable:
                                                      'bg:#662266 #aaaaaa',# RYAN BURGERT STUFF
        Token.Toolbar.Status.PythonVersion:           'bg:#222222 #ffffff bold',

        # When Control-C has been pressed. Grayed.
        Token.Aborted:                                '#888888',

        # The options sidebar.
        Token.Sidebar:                                'bg:#bbbbbb #000000',
        Token.Sidebar.Title:                          'bg:#668866 #ffffff',
        Token.Sidebar.Label:                          'bg:#bbbbbb #222222',
        Token.Sidebar.Status:                         'bg:#dddddd #000011',
        Token.Sidebar.Selected.Label:                 'bg:#222222 #eeeeee',
        Token.Sidebar.Selected.Status:                'bg:#444444 #ffffff bold',

        Token.Sidebar.Separator:                      'bg:#bbbbbb #ffffff underline',
        Token.Sidebar.Key:                            'bg:#bbddbb #000000 bold',
        Token.Sidebar.Key.Description:                'bg:#bbbbbb #000000',
        Token.Sidebar.HelpText:                       'bg:#fdf6e3 #000011',

        # Styling for the history layout.
        Token.History.Line:                          '',
        Token.History.Line.Selected:                 'bg:#008800  #000000',
        Token.History.Line.Current:                  'bg:#ffffff #000000',
        Token.History.Line.Selected.Current:         'bg:#88ff88 #000000',
        Token.History.ExistingInput:                  '#888888',

        # Help Window.
        Token.Window.Border:                          '#bbbbbb',
        Token.Window.Title:                           'bg:#bbbbbb #000000',
        Token.Window.TIItleV2:                         'bg:#6688bb #000000 bold',

        # Meta-enter message.
        Token.AcceptMessage:                          'bg:#ffff88 #444444',

        # Exit confirmation.
        Token.ExitConfirmation:                       'bg:#884444 #ffffff',
}


# Some changes to get a bit more contrast on Windows consoles.
# (They only support 16 colors.)
if is_windows() and not is_conemu_ansi():
    default_ui_style.update({
        Token.Sidebar.Title:                          'bg:#00ff00 #ffffff',
        Token.ExitConfirmation:                       'bg:#ff4444 #ffffff',
        Token.Toolbar.Validation:                     'bg:#ff4444 #ffffff',

        Token.Menu.Completions.Completion:            'bg:#ffffff #000000',
        Token.Menu.Completions.Completion.Current:    'bg:#aaaaaa #000000',
    })


blue_ui_style = {}
blue_ui_style.update(default_ui_style)
blue_ui_style.update({
        # Line numbers.
        Token.LineNumber:                             '#aa6666',

        # Highlighting of search matches in document.
        Token.SearchMatch:                            '#ffffff bg:#4444aa',
        Token.SearchMatch.Current:                    '#ffffff bg:#44aa44',

        # Highlighting of select text in document.
        Token.SelectedText:                           '#ffffff bg:#6666aa',

        # Completer toolbar.
        Token.Toolbar.Completions:                    'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Arrow:              'bg:#44bbbb #000000 bold',
        Token.Toolbar.Completions.Completion:         'bg:#44bbbb #000000',
        Token.Toolbar.Completions.Completion.Current: 'bg:#008888 #ffffff',

        # Completer menu.
        Token.Menu.Completions.Completion:            'bg:#44bbbb #000000',
        Token.Menu.Completions.Completion.Current:    'bg:#008888 #ffffff',
        Token.Menu.Completions.Meta:                  'bg:#449999 #000000',
        Token.Menu.Completions.Meta.Current:          'bg:#00aaaa #000000',
        Token.Menu.Completions.ProgressBar:           'bg:#aaaaaa',
        Token.Menu.Completions.ProgressButton:        'bg:#000000',
})
