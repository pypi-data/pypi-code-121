#NEEDS PROMPT TOOLKIT 3
#TAG Prompt Toolkit Imports
from prompt_toolkit import *
from prompt_toolkit.layout import *
from prompt_toolkit.layout.processors import *
from prompt_toolkit.layout.containers import *
from prompt_toolkit.layout.margins import *
from prompt_toolkit.layout.menus import *
from prompt_toolkit.layout.screen import *
from prompt_toolkit.layout.utils import *
from prompt_toolkit.key_binding import *
from prompt_toolkit.buffer import *
from prompt_toolkit.formatted_text import *
from prompt_toolkit.formatted_text import *
from prompt_toolkit.input import *
from prompt_toolkit.utils import *
from prompt_toolkit.application import *
from prompt_toolkit.cache import *
from prompt_toolkit.document import *
from prompt_toolkit.filters import *
from prompt_toolkit.search import *
from prompt_toolkit.auto_suggest import *
from prompt_toolkit.clipboard import *
from prompt_toolkit.completion import *
from prompt_toolkit.contrib import *
from prompt_toolkit.data_structures import *
from prompt_toolkit.enums import *
from prompt_toolkit.eventloop import *
from prompt_toolkit.history import *
from prompt_toolkit.output import *
from prompt_toolkit.patch_stdout import *
from prompt_toolkit.renderer import *
from prompt_toolkit.selection import *
from prompt_toolkit.shortcuts import *
from prompt_toolkit.styles import *
from prompt_toolkit.token import *
from prompt_toolkit.validation import *
from prompt_toolkit.widgets import *
from prompt_toolkit.key_binding.bindings.focus import *
from prompt_toolkit.key_binding.bindings import *
from prompt_toolkit.key_binding.key_bindings import *
from prompt_toolkit.key_binding.bindings.focus import *
from prompt_toolkit.key_binding.bindings import *
from prompt_toolkit.key_binding.key_bindings import *
from functools import partial
from typing import Callable, Generic, List, Optional, Sequence, Tuple, TypeVar, Union

from prompt_toolkit.application.current import get_app
from prompt_toolkit.auto_suggest import AutoSuggest, DynamicAutoSuggest
from prompt_toolkit.buffer import Buffer, BufferAcceptHandler
from prompt_toolkit.completion import Completer, DynamicCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.filters import (
    Condition,
    FilterOrBool,
    has_focus,
    is_done,
    is_true,
    to_filter,
)
from prompt_toolkit.formatted_text import (
    AnyFormattedText,
    StyleAndTextTuples,
    Template,
    to_formatted_text,
)
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.history import History
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import (
    AnyContainer,
    ConditionalContainer,
    Container,
    DynamicContainer,
    Float,
    FloatContainer,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import (
    BufferControl,
    FormattedTextControl,
    GetLinePrefixCallable,
)
from prompt_toolkit.layout.dimension import AnyDimension
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.dimension import to_dimension
from prompt_toolkit.layout.margins import NumberedMargin, ScrollbarMargin
from prompt_toolkit.layout.processors import (
    AppendAutoSuggestion,
    BeforeInput,
    ConditionalProcessor,
    PasswordProcessor,
    Processor,
)
from prompt_toolkit.lexers import DynamicLexer, Lexer
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType
from prompt_toolkit.utils import get_cwidth
E = KeyPressEvent
_T = TypeVar("_T")











def fuzzy_string_match(string,target,*,case_sensitive=True):
    # >>> fuzzy_string_match('apha','alpha')
    #ans = True
    # >>> fuzzy_string_match('alpha','alpha')
    #ans = True
    # >>> fuzzy_string_match('aa','alpha')
    #ans = True
    # >>> fuzzy_string_match('aqa','alpha')
    #ans = False
    # >>> fuzzy_string_match('e','alpha')
    #ans = False
    # >>> fuzzy_string_match('h','alpha')
    #ans = False
    assert isinstance(string,str)
    assert isinstance(target,str)
    if not case_sensitive:
        string=string.lower()
        target=target.lower()
    import re
    pattern='.*'.join(re.escape(char) for char in string)
    pattern='.*'+pattern+'.*'
    return bool(re.fullmatch(pattern,target))



from rp import *
class FileNavigator():
    #A widget

    def __pt_container__(self):
        #The existence of this function lets us treat this class like a container
        return self.window

    def __init__(self, path='.'):
        

        # self.top_text=Label('',style='bold bg:teal')

        top_text_kb=KeyBindings()
        @top_text_kb.add('enter')
        def _(event):
            self.location=get_relative_path(self.location)
            event.app.layout.focus_next()
        self.top_text=TextArea('',style='bold bg:teal',height=Dimension(max=1),focusable=False)
        self.top_text.control.key_bindings=top_text_kb

        self.original_location=path
        self._set_location(path)

        self._selected_index=0

        # Key bindings.
        kb = KeyBindings()
        kb.add("up"   )(lambda event:self._shift_selected_index(-1))
        kb.add("down" )(lambda event:self._shift_selected_index(+1))
        kb.add("enter")(lambda event:self._enter_handler())
        @kb.add('backspace')
        def _(event):
            # self._set_location(get_parent_directory(self.location))
            self.location=(self.location[:-1])
        @kb.add('escape','backspace')
        def _(event):
            self._set_location(get_parent_directory(self.location))
            # self.location=(self.location[:-1])

        for key in set('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM./1234567890-_\\|!@#$%^&*()_~`?/'):
            def addkey(key):
                @kb.add(key)
                def _(event):
                    self.location=(self.location+key)
            addkey(key)

        # This container's control
        self.control = FormattedTextControl(self._get_text_fragments,
                                            key_bindings=kb,
                                            focusable   =True)

        # This container's window
        self.navigator= Window(content         =self.control,
                             right_margins     =[ScrollbarMargin(display_arrows=True),],
                             dont_extend_height=True,
                             # width=Dimension(min=15,max=15),
                             )

        self.window=HSplit([self.top_text,self.navigator])

    @property
    def location(self):
        return self.top_text.text
    @location.setter
    def location(self,value):
        self.top_text.text=value

    def _set_location(self,new_location):
        self.location=get_relative_path(new_location,self.original_location)#Simplify the path Turn ./a/../a  to ./a
        self.location=path_join(self.location,'')#Turn asoi/asoid/ada into asoi/asoid/ada/
        self._selected_index=0

    def _enter_handler(self):
        values=self.values.copy()
        if not is_a_folder(self.location):#If we wrote a partial directory fix it when we hit enter
            self.location=get_parent_directory(self.location)
        if values:
            value=values[self._selected_index]
            # print(value)
            new_location=path_join(self.location,value)
            if is_a_folder(new_location):
                self._set_location(new_location)

    def _shift_selected_index(self,amount):
        self._selected_index+=amount
        self._selected_index%=len(self.values)

    def _get_values(self):
        try:
            location=self.location
            if not directory_exists(location):
                name=get_path_name(location)
                location=get_parent_directory(location)
                filter=lambda value:fuzzy_string_match(name,value,case_sensitive=False)
            else:
                filter=lambda value:True

            if not directory_exists(location):
                return ['ERROR: Directory does not exist']

            values=get_file_paths(location            ,
                                  include_folders=True,
                                  include_files  =True,
                                  relative       =True,
                                  sort_by        ='name')

            values = sorted(values,key=lambda path:not is_a_folder(path_join(location,path)))#Put all folders first

            values.insert(0,'..')

            values = [value for value in values if filter(value)]
    
        except Exception as E:
            values=['ERROR: '+str(E)]
            values.insert(0,'..')
        return values

    def _get_text_fragments(self):

        self.values=self._get_values()

        if not self.values:return [] #To prevent an error where we pop from the last element

        result=[]

        location=self.location
        if not is_a_folder(location):
            location=get_parent_directory(location)

        for i, value in enumerate(self.values):
            selected = i == self._selected_index

            style = "yellow" if is_a_folder(path_join(location,value)) else 'green'
            if value.startswith('ERROR: '):
                style='red'
            if selected:
                style += " [SetCursorPosition] bg:darkblue"  

            result.extend(to_formatted_text(value, style=style))
            result.append(("", "\n"))

        result.pop()  # Remove last newline.
        return result

def filenavtest():
    with patch_stdout():
        fn1=FileNavigator()
        fn2=FileNavigator()
        fn3=FileNavigator()
        ans=VSplit([fn1,fn2,fn3],padding_char=' ',padding=0)
        ans=fn1
        ans=Layout(ans)
        def quittableapp(x):
            ans=Application(x)
            kb=KeyBindings()
            @kb.add('escape','q')
            def _(event):
                event.app.exit()
            kb.add('tab')(focus_next)
            kb.add('s-tab')(focus_previous)
            ans.key_bindings=kb
            return ans
        quittableapp(ans,).run ()
filenavtest()



