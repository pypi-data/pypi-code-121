import pygame as py             # PYGAME
from pygame.locals import *     # PYGAME constant & functions

from sys import exit            # exit script
from typing import overload, Union    # overload init
from math import sqrt, atan, pi


import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')


class Vector2:
    """
    class Vecteur 2 dimension pour un stockage des position et range plus facile qu'avec un array tuple
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def lenght(self):
        return sqrt(self.x**2 + self.y**2)

    @property
    def unity(self):
        return Vector2(self.x / self.lenght, self.y / self.lenght) if self.lenght > 0 else Vector2(0, 0)

    @property
    def arg(self):
        if self.x > 0:
            return atan(self.y / self.x)
        elif self.x < 0 and self.y >= 0:
            return atan(self.y / self.x) + pi
        elif self.x < 0 and self.y < 0:
            return atan(self.y / self.x) - pi
        elif self.x == 0 and self.y < 0:
            return -pi / 2
        elif self.x == 0 and self.y > 0:
            return pi / 2
        else:
            return None

    def __str__(self) -> str:
        return f'({self.x},{self.y})'

    def __call__(self) -> tuple:
        """return a tuple of the vector"""
        return (self.x, self.y)

    def copy(self):
        return Vector2(self.x, self.y)

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, other):
        if type(other) is Vector2:
            return Vector2(self.x + other.x, self.y + other.y)
        if type(other) is tuple:
            return Vector2(self.x + other[0], self.y + other[1])
        else:
            raise TypeError(
                "You can just add Vector2 between them but you pass :", type(other))

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if type(other) is Vector2:
            return Vector2(self.x - other.x, self.y - other.y)
        if type(other) is tuple:
            return Vector2(self.x - other[0], self.y - other[1])
        else:
            raise TypeError(
                "You can just substract Vector2 between them but you pass :", type(other))

    def __isub__(self, other):
        return self.__min__(other)

    def __mul__(self, other):
        if type(other) in (int, float):
            return Vector2(self.x * other, self.y * other)


class Menu_Manager(object):
    """
    class principale de pygame qui gère la fenetre
    """
    @overload
    def __init__(self, name=None, size: Vector2 = None,
                 background=None, icon=None) -> None: ...

    @overload
    def __init__(self, window: py.Surface = None, background=None) -> None: ...

    def __init__(self, window: py.Surface = None, name=None, size: Vector2 = None, background=None, icon=None) -> None:
        """
        initialisation de pygame et de la fenêtre et des variables globales

        :param window: pass an existing surface to blit your menu
        """
        py.init()

        if window is not None:
            self.screen: py.Surface = window
            size = Vector2(*window.get_size())
        elif size:
            self.screen: py.Surface = py.display.set_mode(size(), 0, 32)
            if name:
                py.display.set_caption(name)
            if icon:
                py.display.set_icon(icon)
        else:
            raise Exception(
                "You must pass either your window either the size of your new window")

        self.menus: list[Menu] = []
        self.running = False

        if background:
            try:
                self.background = py.image.load(
                    background).convert()  # tuile pour le background
                self.background = py.transform.scale(
                    self.background, (size.x, size.y))
            except FileNotFoundError:
                logging.error(
                    "File not found : the background of your menu was not found")
                raise FileNotFoundError
        else:
            self.background = py.Surface(size())

        def func(*arg, **kargs): ...
        self.play_effect: function = func

    __menu = None

    @property
    def actual_menu(self):
        return self.__menu

    @actual_menu.setter
    def actual_menu(self, __val):
        if type(__val) is Menu:
            self.__menu = __val
            self.__menu.setup()
        else:
            raise TypeError("actual menu must be a Menu")

    def set_font(self, path):
        self.FONT = path

    def run(self):
        """
        fonction principale du jeu qui gère la fenetre
        """
        self.running = True
        while self.running:
            if self.actual_menu is not None:
                if self.actual_menu.background is None:
                    self.screen.blit(self.background, (0, 0))
                else:
                    self.screen.blit(self.actual_menu.background, (0, 0))
                self.actual_menu.Update()
            else:
                logging.warning(
                    "No menu was setup, nothing will be executed this loop.")
            py.display.update()

    def Update(self):
        if self.running:
            if self.actual_menu is not None:
                if self.actual_menu.background is None:
                    self.screen.blit(self.background, (0, 0))
                else:
                    self.screen.blit(self.actual_menu.background, (0, 0))
                self.actual_menu.Update()
        else:
            raise SystemExit

    def stop(self):
        """
        stop the current thread de la classe
        """
        self.running = False

    @staticmethod
    def destroy():
        """
        Use to stop the local thread
        """
        exit()


class sprite(py.sprite.Sprite):
    def __init__(self, name, path, manager: Menu_Manager, isactive=True, layer=0):
        super().__init__()
        self.name = name
        self.layer = layer
        self.isactive = isactive
        self._manager = manager

        self.handles = []
        try:
            self.image: py.Surface = py.image.load(path).convert_alpha()
        except FileNotFoundError:
            logging.error(
                f"File not found : your image for your sprite {self.name} was not found")
            raise FileNotFoundError

        self.rect = self.image.get_rect(topleft=(0, 0))
        self.initial_size = Vector2(
            self.image.get_width(), self.image.get_height())

    def set_position(self, pos: Vector2, TopLeft=False, parent=None):
        """
        attribue les valeur du vecteur à la position de l'image, si les valeur sont en float alors elle sont considérer comme un multiplicateur
        """
        x, y = pos.x, pos.y
        if type(pos.x) is float:
            if parent:
                x = int(parent.image.get_width() * pos.x) + parent.rect.left
            else:
                x = int(self._manager.screen.get_width() * pos.x)
        elif parent:
            x = pos.x + parent.rect.left
        if type(pos.y) is float:
            if parent:
                y = int(parent.image.get_height() * pos.y) + parent.rect.top
            else:
                y = int(self._manager.screen.get_height() * pos.y)
        elif parent:
            y = pos.y + parent.rect.top

        # asignation of the position
        if TopLeft:
            self.rect = self.image.get_rect(topleft=(x, y))
        else:
            self.rect = self.image.get_rect(center=(x, y))

    def set_scale(self, sca: Vector2, TopLeft=False):
        """
        attribue les valeur du vecteur à la taille de l'image, si les valeur sont en float alors elle sont considérer comme un multiplicateur
        """
        x, y = sca.x, sca.y
        if type(sca.x) is float:
            x = int(self.initial_size.x * sca.x)
        if type(sca.y) is float:
            y = int(self.initial_size.y * sca.y)

        # if we want to actualize the position by the center of the im
        if TopLeft:
            self.image = py.transform.scale(self.image, (x, y))
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        else:
            self.image = py.transform.scale(self.image, (x, y))
            self.rect = self.image.get_rect(center=self.rect.center)

    def Event(self, event):
        """
        Ce décorateur crée une fonction qui ajoute celle ci à la liste des fonctions.
        La fonction passé en décoration n'est executé que si l'évènement est appellé.
        Si l'event passé est nulle alors la fonction est attribué à la fonction Update executé
        juste avant l'affichage
        """
        def decorator(func):
            if event is not None:
                def wrap(_event: py.event.Event, *args, **kwargs):
                    if _event.type == event:
                        return func(_event, *args, **kwargs)
                self.handles.append(wrap)
            else:
                def wrap(*args, **kwargs):
                    if self.isactive:
                        return func(*args, **kwargs)
                setattr(self, "update", wrap)
            return True
        return decorator

    def Handle(self, *arg, **kargs):
        if self.isactive:
            for func in self.handles:
                func(*arg, **kargs)


class textZone(sprite):
    """class pour ajouter automatiquement du text"""

    def __init__(self, name, size: Vector2, manager, isactive=True, text_color='white', interline=0.8, layer=0):
        py.sprite.Sprite.__init__(self)
        self.name = name
        self.isactive = isactive
        self.layer = layer
        self.handles = []
        self._manager = manager

        self.image = py.Surface(size(), flags=py.SRCALPHA)
        self.image.fill((255, 0, 0, 100))
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.text_color = text_color
        self.FONT = py.font.Font(self._manager.FONT, 36)
        self.font_path = self._manager.FONT
        self.text = ""
        self.interline = interline

    def set_text(self, text: str, align=(False, False)):
        self.align = align

        if "\n" in text:
            text = text.replace("\n", "")
            logging.warn("You can't use the \\n in your text")

        self.text = text

        self.render(self.fit_to_size())

    def render(self, matrix):
        if not matrix:
            matrix = self.fit_to_size()

        self.image.fill((0, 0, 0, 0))
        # calcul positions
        x = 0
        y = 0
        _surf = py.Surface(self.rect.size, flags=SRCALPHA)
        _final_text = []

        _text = self.text.split(" ")
        for i in range(len(_text) - 1):
            _text[i] += " "

        for i, line in enumerate(matrix):
            _final_text.append("")
            for j in range(line):
                _final_text[i] += _text.pop(0)

        for line in _final_text:
            if self.align[0]:
                x = (self.rect.width - self.FONT.size(line)[0]) / 2
            _surf.blit(self.FONT.render(line, True, self.text_color), (x, y))
            y += self.FONT.get_height() * (1 + self.interline)

        y_off = 0
        if self.align[1]:
            y -= self.FONT.get_height() * self.interline
            y_off = (self.rect.height - y) // 2

        # Blit the text
        self.image.blit(_surf, (0, y_off))

    def set_font(self, path, size=36):
        self.FONT = py.font.Font(path, size)
        self.font_path = path

    def fit_to_size(self, size=None):
        """
        Returns a text surface that fits inside given surface. The text
        will have a font size of 'max_size' or less.
        """
        if size is not None:
            self.FONT = py.font.Font(self.font_path, size)
        else:
            size = int(sqrt(self.rect.w * self.rect.h / len(self.text)))
        words = self.text.split(" ")

        for i in range(len(words) - 1):
            words[i] += " "

        sizes = [self.FONT.size(word) for word in words]
        lines = []

        for word in sizes:
            i = len(lines)
            if not i:
                lines.append([word])
            elif sum([word[0] for word in lines[i - 1]]) + word[0] < self.rect.width:
                lines[i - 1].append(word)
            else:
                lines.append([word])

        height = sum(max([word[1] for word in line]) for line in lines)
        nb_i = len(lines)
        height += nb_i * self.interline * sizes[0][1]  # add the interline

        if height > self.rect.height:
            return self.fit_to_size(size - 1)
        else:
            return [len(line) for line in lines]


class Button(sprite):
    """
    classe de bouton simple avec méthode rapide pour Event et On_Click
    """

    def on_click(self, _effect=None):
        """
        nouvelle fonction qui n'executera que la fonction en cas de click du boutton
        la nouvelle fonction est ajouté dans la liste des function à executé
        """
        def Wrap(func):
            def wrap(_event: py.event.Event, *args, **kargs):
                if _event.type == py.MOUSEBUTTONUP:
                    if "pos" in kargs:
                        if (
                            self.rect.collidepoint(kargs["pos"])
                            and _event.button == 1
                            and self.check_layer()
                        ):
                            del kargs["pos"]
                            func(*args, **kargs)
                            if _effect is not None:
                                self._manager.play_effect(_effect)
                    else:
                        if (
                            self.rect.collidepoint(py.mouse.get_pos())
                            and _event.button == 1
                            and self.check_layer()
                        ):
                            func(*args, **kargs)
                            if _effect is not None:
                                self._manager.play_effect(_effect)
            self.handles.append(wrap)

        return Wrap

    def check_layer(self):
        return all(not (
            _sprite.isactive
            and _sprite.rect.collidepoint(py.mouse.get_pos())
            and _sprite.layer > self.layer
        ) for _sprite in self._manager.actual_menu.sprites()) and self in self._manager.actual_menu.sprites()

    def set_text(self, text, color="white", padding=0.05):
        _size = Vector2(self.rect.width*(1 - padding),
                        self.rect.height*(1 - padding))
        _text = textZone(
            name=f"textZone_{self.name}",
            size=Vector2(*_size),
            manager=self._manager,
            text_color=color
        )

        _text.set_text(text, align=(True, True))
        _text.fit_to_size()
        _text.render()

        self.image.blit(_text.image, (self.rect.width *
                        (padding/2), self.rect.height*(padding/2)))
#! rewrite


class InputBox(sprite):
    """
    class de InputBox autonome, permet de rentrer du texte facilement
    """

    def __init__(self, name, path, manager: Menu_Manager, paceHolder='Enter text...', color='black', text_color='grey', alter_text_color="white", max_char=16, isactive=True, layer=0):

        super().__init__(name, path, manager, isactive, layer)

        self.color = Color(color)
        self.text = ''
        self.paceHolder = paceHolder
        self.max_char = max_char
        self.text_color = Color(text_color)
        self.text_color_inactive = Color(text_color)
        self.text_color_active = Color(alter_text_color)

        self.text_size = self.get_text_size()
        if self._manager.FONT is None:
            raise AttributeError(
                "You must define the FONT of your MenuManager to use Inputbox")
        self.FONT = py.font.Font(self._manager.FONT, self.text_size)
        self.txt_surface = self.FONT.render(
            self.paceHolder, True, self.text_color)
        self.active = False

    def get_text_size(self):
        i = self.surface.get_height()
        temp = py.font.Font(None, i)
        size_temp = temp.size("A" * max(self.max_char, len(self.paceHolder)))
        while int(self.surface.get_height() * 0.80) < size_temp[1] or int(self.surface.get_width() * 0.9) < size_temp[0]:
            i -= 1
            temp = py.font.Font(None, i)
            size_temp = temp.size(
                "A" * max(self.max_char, len(self.paceHolder)))
        return(i)

    def on_enter(self, func):
        """
        Ce décorateur crée une fonction qui ajoute celle ci à la liste des fonctions.
        La fonction passé en décoration n'est executé que si la touche Enter est pressé.
        """
        def wrap(_event, *args, **kwargs):
            if (
                _event.type == KEYDOWN
                and self.isactive and self.active
                and _event.key == K_RETURN
            ):
                return func(*args, **kwargs)
        setattr(self, "Enter_func", wrap)
        return True

    def Handle(self, event: py.event.Event):
        if event.type == MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                self.text_color = self.text_color_active if self.active else self.text_color_inactive
            else:
                self.active = False
                self.text_color = self.text_color_inactive
        if self.active:
            if event.type == KEYDOWN and event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            if (
                event.type == TEXTINPUT
                and len(self.text) < self.max_char
            ):
                self.text += event.text
        self.Enter_func(event)

    def draw(self, ecran):
        render = self.surface.copy()

        self.txt_surface = self.FONT.render(
            self.text or self.paceHolder, True, self.text_color)

        # calcul positions
        x = int(render.get_width() * 0.05)
        y = int(render.get_height() // 2 - self.txt_surface.get_height() // 2)
        # Blit the text.
        render.blit(self.txt_surface, (x, y))
        if py.time.get_ticks() % 1000 > 500 and self.active:
            cursor = Rect(self.txt_surface.get_rect(
                topleft=(x, y - 5)).topright, (3, self.txt_surface.get_rect().height))
            py.draw.rect(render, self.text_color, cursor)
        if self.isactive:
            ecran.blit(render, (self.position.x, self.position.y))

    def Enter_func(self, _event): ...
#! rewrite


class AlertBox(sprite):
    """
    class de alertbox autonome, permet de rentrer d'afficher une erreur facilement
    """

    def __init__(self, name, path, manager: Menu_Manager, color='black', text_color='grey', padding=0.05, isactive=True, layer=0):
        super().__init__(name, path, manager, isactive, layer)

        self.color = Color(color)
        self.text = ''
        self.text_color = Color(text_color)
        self.padding = padding

        if self._manager.FONT is None:
            raise AttributeError(
                "You must define the FONT of your MenuManager to use Inputbox")
        self.FONT = py.font.Font(self._manager.FONT, self.text_size)

        self.childs: list[Button] = []

    def set_scale(self, sca: Vector2):
        """
        attribue les valeur du vecteur à la taille de l'image, si les valeur sont en float alors elle sont considérer comme un multiplicateur
        """
        x, y = sca.x, sca.y
        if type(sca.x) is float:
            x = int(self.surface.get_width() * sca.x)
        if type(sca.y) is float:
            y = int(self.surface.get_height() * sca.y)
        self.scale = Vector2(x, y)

        self.actualize_child_position()
        self.actualize_scale()

    def actualize_child_position(self):
        # calcul pourcentage d'augmentation
        offset = Vector2(
            x=self.scale.x / self.surface.get_width(),
            y=self.scale.y / self.surface.get_height()
        )
        for _button in self.childs:
            # calcul position pourcentage du centre du parent
            pos = Vector2(
                ((_button.position.x + _button.scale.x / 2) - self.position.x -
                 self.surface.get_width() / 2) / self.surface.get_width(),
                ((_button.position.y + _button.scale.y / 2) - self.position.y -
                 self.surface.get_height() / 2) / self.surface.get_height()
            )
            # calcul nouvelle position par rapport au coin haut gauche du parent
            pos.x = pos.x * offset.x + 0.5
            pos.y = pos.y * offset.y + 0.5
            _button.set_position(pos, parent=self)

    def set_rect(self, coord: Vector2):
        super().set_rect(coord)
        for _button in self.childs:
            self.rect = self.rect.union(_button.rect)

    def on_enter(self, func):
        """
        Ce décorateur crée une fonction qui ajoute celle ci à la liste des fonctions.
        La fonction passé en décoration n'est executé que si la touche Enter est pressé.
        """
        def wrap(_event, *args, **kwargs):
            if (
                _event.type == KEYDOWN
                and self.isactive
                and _event.key == K_RETURN
            ):
                return func(*args, **kwargs)
        setattr(self, "Enter_func", wrap)
        return True

    def add_button(self, func):
        _button = func()

        if type(_button) is Button:
            self.childs.append(_button)
            self.set_rect(self.position)
        else:
            logging.warning(
                "Add button function only take button type, your sprite wasn't added to your alertbox")

    def set_text(self, text, wrap_lenght=None, align_center=False):
        self.text = text

        _text = textZone(
            name=f'text_{self.name}',
            text_color=self.text_color
        )

        _text.set_text(text, wrap_lenght, align_center)

        _size = Vector2(self.surface.get_width() * (1 - self.padding * 2), self.surface.get_height() * (1 - self.padding * 2)) if type(
            self.padding) is float else Vector2(self.surface.get_width() - self.padding, self.surface.get_height() - self.padding)

        _text.size_to_scale(_size)

        _render = _text.render()

        _pos = (
            self.surface.get_width() // 2 - _render.get_width() // 2,
            self.surface.get_height() // 2 - _render.get_height() // 2
        )

        self.surface.blit(_render, _pos)

    def Event(self, event): ...

    def Handle(self, event: py.event.Event):
        self.Enter_func(event)
        for _button in self.childs:
            _button.Handle(event)

    def draw(self, ecran):
        super().draw(ecran)
        for _button in self.childs:
            _button.draw(ecran)

    def Update(self, *args, **kargs):
        for _button in self.childs:
            _button.Update(*args, **kargs)

    def Enter_func(self, _event): ...


class ScrollableBox(sprite):

    def __init__(self, name, size, manager: Menu_Manager, path: str = None, width_cursor=20, speed=1, isactive=True, layer=0):
        super(sprite, self).__init__()
        self.name = name
        self.layer = layer
        self.isactive = isactive
        self._manager = manager

        self.handles = []
        self.sprites: list[sprite] = []
        self.speed = size[1] / 120 * speed

        self.rect = py.Rect(0, 0, *size)
        self.initial_size = Vector2(self.rect.width, self.rect.height)
        self.offset = Vector2(0, 0)

        if not path:
            self.__cursor = py.Surface(
                (width_cursor, self.rect.height - self.get_max()), flags=SRCALPHA)
        else:
            self.__cursor: py.Surface = py.image.load(path)
        self.cursor = self.__cursor

    @ property
    def image(self):
        _surf = py.Surface(self.rect.size, flags=py.SRCALPHA)
        _object = py.Surface(
            (self.rect.width, self.rect.height + self.get_max()), flags=py.SRCALPHA)

        for _sprite in self.sprites:
            _pos = py.Rect(_sprite.rect.left - self.rect.left,
                           _sprite.rect.top - self.rect.top, *_sprite.rect.size)
            _object.blit(_sprite.image, _pos)

        factor = (self.rect.height / (self.rect.height + self.get_max()))
        y = self.offset.y * factor
        _surf.blit(self.cursor, (self.rect.width - self.cursor.get_width(), y))
        _surf.blit(_object, (self.offset * -1)())

        return _surf

    def add_sprite(self, func):
        """
        decorateur qui ajoute automatiquement le retour de la fonction à la liste
        """
        _sprite = func()
        if sprite in _sprite.__class__.__bases__ or type(_sprite) is sprite:
            self.sprites.append(_sprite)
            factor = self.rect.height / (self.rect.height + self.get_max())
            height = self.rect.height * factor
            width = self.rect.w * 0.015
            self.cursor = self.scale_cursor(height, width)
        else:
            raise TypeError(
                "You must return a sprite based class to add, type returned was :", type(_sprite))

    def update(self, *args, **kwargs):
        for _sp in self.sprites:
            _sp.update(*args, **kwargs)
        return super(sprite, self).update(*args, **kwargs)

    def Handle(self, _event: py.event.Event, *arg, **kargs):
        if _event.type == py.MOUSEWHEEL:
            self.offset.y -= _event.y * self.speed
            if self.offset.y < 0:
                self.offset.y = 0
            elif self.offset.y > self.get_max():
                self.offset.y = self.get_max()

        if _event.type == py.MOUSEBUTTONUP:
            for _sprite in self.sprites:
                _sprite.Handle(_event, pos=(py.mouse.get_pos()[0], py.mouse.get_pos()[
                               1] + self.offset.y), *arg, **kargs)
        else:
            for _sprite in self.sprites:
                _sprite.Handle(_event, *arg, **kargs)
        return super().Handle(_event, *arg, **kargs)

    def get_max(self) -> int:
        max = 0
        for _sp in self.sprites:
            i = _sp.rect.top - self.rect.top + _sp.rect.height
            if i > max:
                max = i
        res = max - self.rect.height
        return res if res > 0 else 0

    def set_scale(self, sca: Vector2, TopLeft=False): ...

    def get_sprite(self, name):
        for sprite in self.sprites:
            if sprite.name == name:
                return sprite

    def scale_cursor(self, y, x=0):
        w, h = self.__cursor.get_width(), self.__cursor.get_height()
        top = self.__cursor.subsurface(py.Rect(0, 0, w, h * 0.1)).copy()
        middle = self.__cursor.subsurface(
            py.Rect(0, h * 0.1, w, h * 0.8)).copy()
        bot = self.__cursor.subsurface(
            py.Rect(0, h - int(h * 0.1), w, int(h * 0.1))).copy()
        top = py.transform.scale(top, (x or w, y * 0.1))
        middle = py.transform.scale(middle, (x or w, y * 0.8))
        bot = py.transform.scale(bot, (x or w, y * 0.1))
        _surf = py.Surface((x or w, y), flags=SRCALPHA)
        _surf.blit(top, (0, 0))
        _y = top.get_height()
        _surf.blit(middle, (0, _y))
        _y += middle.get_height()
        _surf.blit(bot, (0, _y))

        return _surf


class Menu(py.sprite.Group):
    """
    classe principale du Menu
    """

    def __init__(self, name, manager, parent=None, childs=None, background=None):
        super().__init__()
        self.name: str = name
        self.parent: str = parent
        self.childs: list[str] = [childs] if type(childs) is str else childs
        self._manager = manager
        self._manager.menus.append(self)

        if background is not None:
            try:
                self.background = py.image.load(
                    background).convert()  # tuile pour le background
                self.background = py.transform.scale(
                    self.background, (self._manager.screen.get_width(), self._manager.screen.get_height()))
            except FileNotFoundError:
                logging.error(
                    f"File not found : Youf background for your menu {self.name} was not found")
                raise FileNotFoundError
        else:
            self.background = None

    def add_sprite(self, func):
        """
        decorateur qui ajoute automatiquement le retour de la fonction à la liste
        """
        _sprite = func()
        if sprite in _sprite.__class__.__bases__ or type(_sprite) is sprite:
            self.add(_sprite)
        else:
            raise TypeError(
                "You must return a sprite based class to add, type returned was :", type(_sprite))

    def Update(self):
        """
        fonction update des bouton du menu avec en premier les event, ensuite les function effectué chaque frame et finalement l'affichage
        """
        for _event in py.event.get():
            if py.QUIT == _event.type:
                self._manager.destroy()
            for sprite in self.sprites():
                sprite.Handle(_event)
        for sprite in self.sprites():
            sprite.update()
        self.draw(self._manager.screen)

    def draw(self, surface: py.Surface):
        sprites = self.sprites()
        if hasattr(surface, "blits"):
            self.spritedict.update(
                zip(sprites, surface.blits((spr.image, spr.rect)
                    for spr in sprites if spr.isactive))
            )

    def get_childs(self):
        """
        fonction pour récupérer les menus enfants
        """
        for _menu in self._manager.menus:
            if _menu.name in self.childs:
                yield _menu

    def get_child(self, child_name):
        """
        fonction pour récupérer un menu enfants nomé
        """
        for _menu in self._manager.menus:
            if _menu.name in self.childs and _menu.name == child_name:
                return _menu

        raise Exception("Menu not found")

    def get_parent(self):
        """
        fonction pour récupérer le menu parent
        """
        for _menu in self._manager.menus:
            if _menu.name == self.parent:
                return _menu

    def get_sprite(self, name):
        for sprite in self.sprites():
            if sprite.name == name:
                return sprite

    def set_setup(self, func):
        """
        this function add a setup function execute when the menu is change
        """
        setattr(self, "setup", func)

    def setup(self): ...
