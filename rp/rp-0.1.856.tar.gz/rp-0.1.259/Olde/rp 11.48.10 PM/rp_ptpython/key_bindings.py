from __future__ import unicode_literals

from prompt_toolkit.document import Document
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasSelection, IsMultiline, Filter, HasFocus, Condition, ViInsertMode, EmacsInsertMode
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.key_binding.registry import Registry
from prompt_toolkit.keys import Keys,Key

__all__ = (
    'load_python_bindings',
    'load_sidebar_bindings',
    'load_confirm_exit_bindings',
)


class TabShouldInsertWhitespaceFilter(Filter):
    """
    When the 'tab' key is pressed with only whitespace character before the
    cursor, do autocompletion. Otherwise, insert indentation.

    Except for the first character at the first line. Then always do a
    completion. It doesn't make sense to start the first line with
    indentation.
    """
    def __call__(self, cli):
        b = cli.current_buffer
        before_cursor = b.document.current_line_before_cursor

        return bool(b.text and (not before_cursor or before_cursor.isspace()))


def load_python_bindings(python_input):
    """
    Author: Ryan Burgert
    """
    registry = Registry()

    sidebar_visible = Condition(lambda cli: python_input.show_sidebar)
    handle = registry.add_binding
    has_selection = HasSelection()
    vi_mode_enabled = Condition(lambda cli: python_input.vi_mode)

    #region Ryan Burgert Stuff
    from prompt_toolkit.key_binding.input_processor import KeyPressEvent
    from prompt_toolkit.document import Document
    #region Template
    def _(event):# Parenthesis completion
        #
        assert isinstance(event,KeyPressEvent)
        #
        from prompt_toolkit.buffer import Buffer
        buffer=event.cli.current_buffer
        assert isinstance(buffer,Buffer)
        #
        document=buffer.document
        assert isinstance(document,Document)
        document.insert_after()
        #
        text=document.text_after_cursor
        assert isinstance(text,str)
        #
    # buffer.insert_text("(")
    # if not text or text[0] in " \t\n":
    #     buffer.insert_text(")")
    #     buffer.cursor_left(count=1)
#endregion
    @handle(Keys.ShiftLeft)
    def _(event):
        """
        Select from the history.
        """
        event.cli.current_buffer.cursor_left(1000000)
    @handle(Keys.ShiftRight)
    def _(event):
        """
        Select from the history.
        """
        event.cli.current_buffer.cursor_right(1000000)
    #region Bracket Match Writers

    bracket_pairs={"()","[]","{}"}
    def thing(begin,end):
        @handle(begin)
        def _(event):# Parenthesis completion
            buffer=event.cli.current_buffer
            document=buffer.document
            before=document.text_before_cursor
            after= document.text_after_cursor
            buffer.insert_text(begin)
            if not after or after[0].isspace() or before and before[-1]+after[0]in bracket_pairs:
                buffer.insert_text(end)
                buffer.cursor_left(count=1)
        @handle(end)
        def _(event):# Parenthesis completion
            buffer=event.cli.current_buffer
            document=buffer.document
            before=document.text_before_cursor
            after= document.text_after_cursor
            if not after or after[0]!=end:#  or before.count(begin)>before.count(end):#Last part is checking for parenthesis matches. I know somewhere there's a way to do this already thats better and isnt confused by strings but idk where that is
                buffer.insert_text(end)
            else:
                buffer.cursor_right(count=1)
    @handle(" ")
    def _(event):# Spacebar
        # from rp import mini_terminal
        # exec(mini_terminal)
        buffer=event.cli.current_buffer
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor

        before_line=before.split('\n')[-1]# all on same line, but before cursor
        after_line=after.split('\n')[0]# ditto but after cursor
        from rp import space_split,is_namespaceable
        import rp.r_iterm_comm as r_iterm_comm
        split=space_split(before_line)
        from rp import printed
        from_or_import_on_beginning_of_line=before_line.lstrip().startswith("import ") or before_line.lstrip().startswith("from ")
        try:
            if not after_line and all(is_namespaceable(x) for x in split) and len(split)==2 and split[0]=='def':
                buffer.insert_text('():')
                buffer.cursor_left(count=2)
            elif before_line.lstrip() in['if','while','for','with','try','except'] or split and split[-1]=='lambda':
                buffer.insert_text(' :')
                buffer.cursor_left(count=1)
            elif before_line and after_line and before_line[-1]==','and after_line[0]==':':# for after lambda x,a,b,c,cursor:
                buffer.delete_before_cursor(count=1)
                buffer.cursor_right(count=1)
            elif before_line and after_line and before_line[-1]+after_line[0] in ['()','[]','{}']:
                buffer.delete_before_cursor(count=1)
                buffer.cursor_right(count=1)
                buffer.delete_before_cursor(count=1)
                buffer.insert_text(' ')
            elif len(split)>=2 and split[-2]=='lambda' and ':'not in split[-1] or after_line=='):' and not before_line.rstrip().endswith(','):# new argument in def
                buffer.insert_text(',')
            elif not from_or_import_on_beginning_of_line and split and not before_line.endswith(" ") and split[-1] in r_iterm_comm.globa and callable(r_iterm_comm.globa[split[-1]]):
                buffer.insert_text('()')
                buffer.cursor_left(count=1)
            elif not from_or_import_on_beginning_of_line and split and not before_line.endswith(" ") and split[-1] in r_iterm_comm.globa and hasattr(r_iterm_comm.globa[split[-1]],'__getitem__'):
                buffer.insert_text('[]')
                buffer.cursor_left(count=1)
            else:
                buffer.insert_text(' ')
        except Exception as e:
            from rp import print_stack_trace
            print_stack_trace(e)
    @handle(":")
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor

        before_line=before.split('\n')[-1]# all on same line, but before cursor
        after_line=after.split('\n')[0]# ditto but after cursor
        if after_line==':':
            buffer.cursor_right(count=1)
        else:
            buffer.insert_text(':')
    @handle("=")
    def _(event):
        import rp.r_iterm_comm as r_iterm_comm

        buffer=event.cli.current_buffer
        document=buffer.document
        #
        before=document.text_before_cursor
        after= document.text_after_cursor
        char_operators=['','+','-','*','/','%','//','**','&','|','^','>>','<<']
        letter_operators=['and','or','not','==','!=','>=','<=']
        var=r_iterm_comm.last_assignable_comm
        if var and before==var+"=":
            buffer.delete_before_cursor(count=1000)
            buffer.insert_text("==")

        elif var and not after and before in letter_operators:# User hasn't typed anything in yet
            buffer.cursor_left(count=10000)
            buffer.insert_text(var)
            buffer.insert_text("=")
            buffer.insert_text(var)
            if before.isalpha():# and, or, not
                buffer.insert_text(" ")# We need a space
            buffer.cursor_right(count=10000)
        elif var and not after and before in char_operators:# User hasn't typed anything in yet
            buffer.cursor_left(count=10000)
            buffer.insert_text(var)
            buffer.cursor_right(count=10000)
            buffer.insert_text('=')
        else:
            buffer.insert_text('=')

    import os
    if os.name != 'nt':#If we are NOT running windows, which screws EVERYTHING up...
        @handle(Keys.ControlC)
        def _(event):
            buffer=event.cli.current_buffer
            # document=buffer.document
            # before=document.text_before_cursor
            # after= document.text_after_cursor
            buffer.insert_text('RETURN')
        @handle(Keys.ControlH)
        def _(event):
            buffer=event.cli.current_buffer
            buffer.insert_text('HISTORY')
        @handle(Keys.ControlU)
        def _(event):
            buffer=event.cli.current_buffer
            buffer.insert_text('UNDO')
        @handle(Keys.ControlP)
        def _(event):
            buffer=event.cli.current_buffer
            buffer.insert_text('PREV')



    @handle(Keys.Backspace)
    def _(event):
        buffer=event.cli.current_buffer
        document=buffer.document
        before=document.text_before_cursor
        after= document.text_after_cursor
        if before and after:
            pair=before[-1]+after[0]
            if pair in ['()','{}','[]',"''",'""']:
                buffer.cursor_right(count=1)
                buffer.delete_before_cursor(count=2)
                return
        buffer.delete_before_cursor(count=1)

    def inc_dec(inc_or_dec:str):# ++ ⟶ +=1
        @handle(inc_or_dec)
        def _(event):
            buffer=event.cli.current_buffer
            document=buffer.document
            before=document.text_before_cursor
            # after= document.text_after_cursor
            # import r_iterm_comm
            # if not after and r_iterm_comm.last_assignable_comm and before[-1]==inc_or_dec:# So you can do ++ -> assignable ++= (because +=1 -> assignable+=1)
            #     buffer.cursor_left(count=1000)
            #     buffer.insert_text(r_iterm_comm.last_assignable_comm)
            #     buffer.cursor_right(count=1000)
            if before and before[-1]==inc_or_dec:
                buffer.insert_text("=1")
            else:
                buffer.insert_text(inc_or_dec)
    inc_dec('+')
    inc_dec('-')

    # @handle("h")
    # def sploo(x):
    #     print("A")
    # @handle("h")
    # def sploo(x):
    #     print("B")

    for bracket_pair in bracket_pairs:
        thing(bracket_pair[0],bracket_pair[1])
    #endregion

    @handle(Keys.ControlL)
    def _(event):
        """
        Clear whole screen and render again -- also when the sidebar is visible.
        """
        event.cli.renderer.clear()
    @handle(Keys.F2)
    def _(event):
        """
        Show/hide sidebar.
        """
        python_input.show_sidebar = not python_input.show_sidebar

    @handle(Keys.F3)
    def _(event):
        """
        Select from the history.
        """
        python_input.enter_history(event.cli)

    @handle(Keys.F4)
    def _(event):
        """
        Toggle between Vi and Emacs mode.
        """
        python_input.vi_mode = not python_input.vi_mode

    @handle(Keys.F6)
    def _(event):
        """
        Enable/Disable paste mode.
        """
        python_input.paste_mode = not python_input.paste_mode

    @handle(Keys.F1)
    def _(event):
        """
        Enable/Disable mouse mode.
        """
        python_input.enable_mouse_support = not python_input.enable_mouse_support

    @handle(Keys.Tab, filter= ~sidebar_visible & ~has_selection & TabShouldInsertWhitespaceFilter())
    def _(event):
        """
        When tab should insert whitespace, do that instead of completion.
        """
        event.cli.current_buffer.insert_text('    ')

    #region  Ryan Burgert Method
    # @handle(Keys.BackTab, filter= TabShouldInsertWhitespaceFilter())
    # def _(event):
    #     """
    #     When tab should insert whitespace, do that instead of completion.
    #     """
    #     from r import mini_terminal
    #     current_line=event.cli.current_buffer.document.current_line_before_cursor.rstrip()
    #     exec(mini_terminal)
    #     text=current_line# event.cli.current_buffer.document.text
    #     text2=text.lstrip()
    #     text3=text2+' '*min(0,(len(text)-len(text2)-4))# unindent by four characters, presumably spaces
    #     event.cli.current_buffer.document.text=text3
    #endregion


    @handle(Keys.ControlJ, filter= ~sidebar_visible & ~has_selection &(ViInsertMode() | EmacsInsertMode()) &HasFocus(DEFAULT_BUFFER) & IsMultiline())
    def _(event):
        """
        Behaviour of the Enter key.

        Auto indent after newline/Enter.
        (When not in Vi navigaton mode, and when multiline is enabled.)
        """
        b = event.current_buffer
        empty_lines_required = python_input.accept_input_on_enter or 10000

        def at_the_end(b):
            """ we consider the cursor at the end when there is no text after
            the cursor, or only whitespace. """
            text = b.document.text_after_cursor

            #region RYAN BURGERT STUFF
            assert isinstance(text,str)
            if not text or text.split('\n')[0] in ["):",']',')','}',':']:# Presumably at the end of def( a,b,c,d,e^): where ^ is cursor
                event.cli.current_buffer.cursor_right(1000000)# Move cursor to end of line then proceed as normal
                text = b.document.text_after_cursor
            #endregion

            return text == '' or (text.isspace() and not '\n' in text)

        # if at_the_end(b):# TODO Stuff here
            # print("""def a b c d e (enter)
# ->
# def a(b,c,d,e):
# """)
        if python_input.paste_mode:
            # In paste mode, always insert text.
            b.insert_text('\n')

        elif at_the_end(b) and b.document.text.replace(' ', '').endswith('\n' * (empty_lines_required - 1)):
            if b.validate():
                # When the cursor is at the end, and we have an empty line:
                # drop the empty lines, but return the value.
                b.document = Document(
                    text=b.text.rstrip(),
                    cursor_position=len(b.text.rstrip()))

                b.accept_action.validate_and_handle(event.cli, b)
        else:
            auto_newline(b)

    @handle(Keys.ControlD, filter=~sidebar_visible & Condition(lambda cli:
            # Only when the `confirm_exit` flag is set.
            python_input.confirm_exit and
            # And the current buffer is empty.
            cli.current_buffer_name == DEFAULT_BUFFER and
            not cli.current_buffer.text))
    def _(event):
        """
        Override Control-D exit, to ask for confirmation.
        """
        python_input.show_exit_confirmation = True

    return registry


def load_sidebar_bindings(python_input):
    """
    Load bindings for the navigation in the sidebar.
    """
    registry = Registry()

    handle = registry.add_binding
    sidebar_visible = Condition(lambda cli: python_input.show_sidebar)

    @handle(Keys.Up, filter=sidebar_visible)
    @handle(Keys.ControlP, filter=sidebar_visible)
    @handle('k', filter=sidebar_visible)
    def _(event):
        " Go to previous option. "
        python_input.selected_option_index = (
            (python_input.selected_option_index - 1) % python_input.option_count)

    @handle(Keys.Down, filter=sidebar_visible)
    @handle(Keys.ControlN, filter=sidebar_visible)
    @handle('j', filter=sidebar_visible)
    def _(event):
        " Go to next option. "
        python_input.selected_option_index = (
            (python_input.selected_option_index + 1) % python_input.option_count)

    @handle(Keys.Right, filter=sidebar_visible)
    @handle('l', filter=sidebar_visible)
    @handle(' ', filter=sidebar_visible)
    def _(event):
        " Select next value for current option. "
        option = python_input.selected_option
        option.activate_next()

    @handle(Keys.Left, filter=sidebar_visible)
    @handle('h', filter=sidebar_visible)
    def _(event):
        " Select previous value for current option. "
        option = python_input.selected_option
        option.activate_previous()

    @handle(Keys.ControlC, filter=sidebar_visible)
    @handle(Keys.ControlG, filter=sidebar_visible)
    @handle(Keys.ControlD, filter=sidebar_visible)
    @handle(Keys.ControlJ, filter=sidebar_visible)
    @handle(Keys.Escape, filter=sidebar_visible)
    def _(event):
        " Hide sidebar. "
        python_input.show_sidebar = False

    return registry


def load_confirm_exit_bindings(python_input):
    """
    Handle yes/no key presses when the exit confirmation is shown.
    """
    registry = Registry()

    handle = registry.add_binding
    confirmation_visible = Condition(lambda cli: python_input.show_exit_confirmation)

    @handle('y', filter=confirmation_visible)
    @handle('Y', filter=confirmation_visible)
    @handle(Keys.ControlJ, filter=confirmation_visible)
    @handle(Keys.ControlD, filter=confirmation_visible)
    def _(event):
        """
        Really quit.
        """
        event.cli.exit()

    @handle(Keys.Any, filter=confirmation_visible)
    def _(event):
        """
        Cancel exit.
        """
        python_input.show_exit_confirmation = False

    return registry


def auto_newline(buffer):
    r"""
    Insert \n at the cursor position. Also add necessary padding.
    """
    insert_text = buffer.insert_text

    if buffer.document.current_line_after_cursor:
        # When we are in the middle of a line. Always insert a newline.
        insert_text('\n')
    else:
        # Go to new line, but also add indentation.
        current_line = buffer.document.current_line_before_cursor.rstrip()
        insert_text('\n')

        # Unident if the last line ends with 'pass', remove four spaces.
        unindent = current_line.rstrip().endswith(' pass')

        # Copy whitespace from current line
        current_line2 = current_line[4:] if unindent else current_line

        for c in current_line2:
            if c.isspace():
                insert_text(c)
            else:
                break

        # If the last line ends with a colon, add four extra spaces.
        if current_line[-1:] == ':':
            for x in range(4):
                insert_text(' ')
