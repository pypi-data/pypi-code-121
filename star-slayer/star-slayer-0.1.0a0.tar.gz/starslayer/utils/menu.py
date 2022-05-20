"""
Menu Module. A Menu is a container of buttons
(and their handlers).
"""

from typing import TYPE_CHECKING, List, Optional

from ..checks import left_click, on_press
from ..consts import HEIGHT, WIDTH
from ..files import StrDict
from .button import Button, ButtonHandler, ButtonsList
from .hitbox import FloatTuple4

if TYPE_CHECKING:

    from ..scene import Scene
    from ..state import Game

StrList = List[str]

MenuVariables = Optional[int | bool]
MenuDict = dict[str, MenuVariables]
ButtonKwargs = dict[str, StrDict | str]

class Menu:
    """
    Class for defining a game menu.

    This Menu adds support for dynamically adding buttons, and accessing
    their handlers.
    """

    def __init__(self, area_corners: FloatTuple4, **kwargs: MenuDict) -> None:
        """
        Initializes an instance of type 'Menu'.

        The following kwargs are the only valid:

        'area_corners' must be a tuple of exactly 4 integers as its values.

        -

        And the kwargs:

        'max_rows' cannot be an integer lower than 1.

        'self.how_many_columns' is the the number of columns to be used.

        'space_between' is the default value for dead space between buttons.

        'space_between_x' is the horizontal value for dead space between
        buttons. If not provided, it defaults to 'space between'.

        'space_between_y' is the vertical value for dead space between buttons.
        If not provided, it defaults to 'space between'.

        'parent_menu' is another instance of type 'Menu' that has this instance
        as its child.

        'force_button_resize' means if the menu must use all the space in the area
        it is specified, which can resize the buttons.

        'special_btn_on_right' means if the buttons for pages navigation should be
        on the right or left of the menu.

        'button_anchor' refers to the point from which the text of each button is
        generated. It can be any combination of two chars from 'n' - 'w' - 'e' - 's';
        otherwise it can also be 'c'.

        'offset_x' is the offset to be used in the X coordinate, if 'button_anchor' is 'c'.

        'offset_y' is the offset to be used in the Y coordinate, if 'button_anchor' is 'c'.

        'show_return' means if the menu should show the return button.

        'hidden' means if the menu should begin with being able to show itself.
        """

        # Define default values
        max_rows: int = kwargs.get("max_rows", 4)
        self.how_many_columns: int = kwargs.get("how_many_columns", 1)
        self.space_between: int = kwargs.get("space_between", 10)
        self.space_between_x: int = kwargs.get("space_between_x", self.space_between)
        self.space_between_y: int = kwargs.get("space_between_y", self.space_between)
        force_button_resize: bool = kwargs.get("force_button_resize", False)
        special_btn_on_right: bool = kwargs.get("special_btn_on_right", True)

        # some control booleans
        self._show_return: bool = kwargs.get("show_return", False)

        # Graphics-related
        self.button_anchor: str = kwargs.get("button_anchor", 'c')

        self.offset_x: int = kwargs.get("offset_x", 0)
        self.offset_y: int = kwargs.get("offset_y", 0)

        self.hidden: bool = kwargs.get("hidden", False)

        if max_rows < 1:

            raise ValueError("'max_rows' must be an integer of 1 or higher.")

        if not len(area_corners) == 4:

            raise ValueError(f"area_corners has {len(area_corners)} values. " +
                             "It must have exactly 4 integers as values.")

        # Button Lists
        self._buttons_list: ButtonsList = []
        self._off_buttons_list: ButtonsList = []
        self.buttons_on_screen: ButtonsList = []

        if force_button_resize and self.how_many_rows < max_rows:

            max_rows = self.how_many_rows

        # Measures
        self.area_x1, self.area_y1, self.area_x2, self.area_y2 = area_corners
        self.max_columns: int = self.how_many_columns
        self.max_rows: int = max_rows

        self.x_space: int = (self.area_x2 - self.area_x1) // self.max_columns
        self.y_space: int = (self.area_y2 - self.area_y1) // self.max_rows

        # Pages-related calculations
        self.current_page: int = 1

        # scene-related
        self.current_scene = None

        # Special Buttons
        special_x1: int = ((self.area_x2 + self.space_between)
                            if special_btn_on_right else (self.area_x1 - (self.y_space // 2)))
        special_x2: int = ((self.area_x2 + (self.y_space // 2))
                            if special_btn_on_right else (self.area_x1 - self.space_between_y))


        @left_click()
        @on_press()
        def page_up(_game: "Game",
                    _scene: "Scene",
                    _btn: Button,
                    **_kwargs: ButtonKwargs) -> None:
            """
            Changes the page for the previous one.
            """

            self.change_page(False)


        @left_click()
        @on_press()
        def page_down(_game: "Game",
                      _scene: "Scene",
                      _btn: Button,
                      **_kwargs: ButtonKwargs) -> None:
            """
            Changes the page for the next one.
            """

            self.change_page(True)


        @left_click()
        @on_press()
        def go_to_parent(game: "Game",
                         scene: "Scene",
                         _btn: Button,
                         **_kwargs: ButtonKwargs) -> None:
            """
            Turns the current scene to its parent, if any.
            """

            if scene.parent:
                game.change_scene(scene.parent.id)


        self.pgup_button: Button = Button(x1=special_x1,
                                          y1=self.area_y1,
                                          x2=special_x2,
                                          y2=(self.area_y1 + (self.y_space // 2)),
                                          message="/\\",
                                          handler=page_up)
        self.pgdn_button: Button = Button(x1=special_x1,
                                          y1=(self.area_y2 - (self.y_space // 2)),
                                          x2=special_x2,
                                          y2=self.area_y2,
                                          message="\\/",
                                          handler=page_down)
        self.return_button: Button = Button(x1=self.area_x1,
                                            y1=self.area_y1 - (HEIGHT // 20),
                                            x2=self.area_x1 + (WIDTH // 20),
                                            y2=self.area_y1 - self.space_between_y,
                                            message='<',
                                            handler=go_to_parent)
        self._special_buttons: ButtonsList = [self.pgup_button,
                                              self.pgdn_button,
                                              self.return_button]

        # Generating the buttons
        self.generate_coords()
        self.update_buttons()


    @property
    def area(self) -> FloatTuple4:
        """
        Shows the area occupied by the menu.
        """

        return self.area_x1, self.area_y1, self.area_x2, self.area_y2


    @property
    def buttons_len(self) -> int:
        """
        Returns how many buttons there are.
        """

        return len(self.buttons)


    @property
    def how_many_rows(self) -> int:
        """
        Returns how many rows are to be used.
        """

        btn_len = self.buttons_len
        return ((btn_len // self.how_many_columns)
                if any((self.how_many_columns == 1, btn_len % self.how_many_columns == 0))
                else (btn_len // self.how_many_columns) + 1)


    @property
    def max_pages(self) -> int:
        """
        Returns the maximum number of pages to be used.
        """

        max_pages = (((self.how_many_rows // self.max_rows) + 1)
                               if all((not self.how_many_rows == self.max_rows,
                                       not self.how_many_rows % self.max_rows == 0))
                               else self.how_many_rows // self.max_rows)
        if not max_pages:
            max_pages += 1

        return max_pages


    @property
    def buttons(self) -> ButtonsList:
        """
        Returns a list of all the buttons on the menu.
        """

        return self._buttons_list


    @buttons.setter
    def buttons(self, new_buttons: ButtonsList) -> None:
        """
        Changes the list of buttons, if valid.
        """

        for btn in new_buttons:
            if not isinstance(btn, Button):
                raise TypeError("Not all the elements in the list are buttons.")

        self._buttons_list = new_buttons
        self.generate_coords()
        self.update_buttons()


    @property
    def off_buttons(self) -> ButtonsList:
        """
        Returns a list of the buttons that are no ordered automatically
        by the menu.
        """

        return self._off_buttons_list


    @off_buttons.setter
    def off_buttons(self, new_off_buttons: ButtonsList) -> None:
        """
        Changes the list of off-buttons, if valid.
        """

        self._off_buttons_list = new_off_buttons
        self.update_buttons()


    @property
    def show_return(self) -> bool:
        """
        Returns if the menu should show the return button.
        """

        return self._show_return


    @show_return.setter
    def show_return(self, new_value: bool) -> None:
        """
        Change if the return button should be shown.
        """

        if not isinstance(new_value, bool):
            raise TypeError("The new value must be a boolean.")

        self._show_return = new_value
        self.generate_coords()
        self.update_buttons()


    def clear_buttons(self) -> None:
        """
        Deletes all buttons made for this menu.
        """

        self.buttons.clear()
        self.off_buttons.clear()


    # pylint: disable=invalid-name
    def button(self,
               *,
               btn: Optional[Button] = None,
               x1: Optional[int]=None,
               y1: Optional[int]=None,
               x2: Optional[int]=None,
               y2: Optional[int]=None,
               message: str='') -> ButtonHandler:
        """
        Creates a button, and registers a handler.

        A handler must be a Callable with the following parameters:

        * a `Game` instance.
        * a `Scene` instance.
        * a `Button` instance.

        At the moment of calling the handler, these 3 parameters will have
        different values depending on the interaction context. (i.e. the scene
        the button was pressed in, etc...)
        """

        if btn:

            if btn in self.buttons:
                is_off = False
            else:
                is_off = True
            button = btn

        else:

            if all((coord is None) for coord in (x1, y1, x2, y2)): # Empty
                x1, y1, x2, y2 = 10, 10, 20, 20 # Trash values
                is_off = False
            elif all((coord is not None) for coord in (x1, y1, x2, y2)): # Full
                is_off = True
            else:
                raise ValueError("Etiher all of the coords or none of them must be present.")

            button = Button(x1=x1, y1=y1, x2=x2, y2=y2, message=message)

        def decorator(handler_func: ButtonHandler) -> ButtonHandler:
            """
            Decorates the button to add its handler.
            """

            btn_list = (self.off_buttons if is_off else self.buttons)

            if button not in btn_list:
                button.handler = handler_func
                if is_off:
                    self.off_buttons += [button]
                else:
                    self.buttons += [button]

            return handler_func

        return decorator


    def execute_btn(self,
                    game: "Game",
                    scene: "Scene",
                    x: int,
                    y: int,
                    **kwargs: ButtonKwargs) -> bool:
        """
        Ultimately execute the buttons handler, if possible.
        If it is successful, it returns 'True', otherwise 'False'.
        """

        for btn in self.buttons_on_screen:

            if (not btn.is_inside(x, y) or (hasattr(btn.handler, "__btn_checks__")
                                            and not all(checker(game, btn, **kwargs)
                                                        for checker
                                                        in btn.handler.__btn_checks__))):
                continue

            btn.handler(game, scene, btn, **kwargs)
            return True

        return False


    def generate_coords(self) -> None:
        """
        Generate buttons based on the effective area of the menu and the buttons list.
        'space_between' determines how much dead space there is between each button in said area.
        """

        cols_counter = 0
        rows_counter = 0

        for btn in self.buttons:

            cols_counter %= self.max_columns
            rows_counter %= self.max_rows

            btn.x1 = ((cols_counter * self.x_space) + self.area_x1 +
                     (0 if cols_counter == 0 else self.space_between_x // 2))
            btn.x2 = (((cols_counter + 1) * self.x_space) + self.area_x1 -
                     (0 if cols_counter == (self.max_columns - 1) else self.space_between_x // 2))
            btn.y1 = ((rows_counter * self.y_space) + self.area_y1 +
                     (0 if rows_counter == 0 else self.space_between_y // 2))
            btn.y2 = (((rows_counter + 1) * self.y_space) + self.area_y1 -
                      (0 if rows_counter == (self.max_rows - 1) else self.space_between_y // 2))

            cols_counter += 1

            # Go to next row only if the current column is filled first
            if cols_counter % self.max_columns == 0:

                rows_counter += 1


    def update_buttons(self, page: int=1) -> None:
        """
        Updates the buttons list if the menu changes pages.

        The page number must be between 1 and the max values for the pages.
        """

        if 1 > page or self.max_pages < page:

            raise ValueError(f"Page number is {page}. It must be between 1 and " +
                             f"{self.max_pages} inclusive.")

        buttons_list: ButtonsList = []

        for i in range((page - 1) * self.max_columns * self.max_rows,
                       page * self.max_columns * self.max_rows):

            if i < len(self.buttons):

                buttons_list.append(self.buttons[i])

        if self.current_page < self.max_pages:

            buttons_list.append(self.pgdn_button)

        if self.current_page > 1:

            buttons_list.append(self.pgup_button)

        if self.show_return: # add return button only if it has a parent menu

            buttons_list.append(self.return_button)

        self.buttons_on_screen = buttons_list + self.off_buttons


    def change_page(self, to_next: bool=True, forced: bool=False) -> None:
        """
        Changes the current page to the previous or next one, depending of the parameter 'to_next'.
        If the new page is outside of the number of pages, does nothing if 'forced' is False,
        otherwise it rotates between the pages.
        """
        if forced:

            new_page = (self.max_pages % self.current_page) + 1

        else:

            new_page = (self.current_page + 1 if to_next else self.current_page - 1)

        if 1 <= new_page <= self.max_pages:

            self.current_page = new_page
            self.update_buttons(new_page)


    def change_buttons(self, new_button_list: ButtonsList) -> None:
        """
        Changes all the buttons in the Menu.
        """

        self.buttons = new_button_list


    def prompt(self, *_args, **_kwargs) -> bool:
        """
        Defines custom functionality for prompting the user.

        This method must be overriden to be useful.
        """

        return False


    def refresh_sub_menu(self, _game: "Game") -> None:
        """
        Attemps to refresh the possible sub-menu this menu has.

        This method must be overriden to be useful.
        """

        ...
