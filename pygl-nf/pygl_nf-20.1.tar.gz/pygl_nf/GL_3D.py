import os
import sys



from ursina import window
from ursina import Ursina
from ursina import color
from ursina import Entity
from ursina import PointLight
from ursina import held_keys
from ursina import mouse
from ursina import Text


from pygl_nf.GL import Sub_events_


from ursina import Slider




class Engine:
    def __init__(self,
                    TITLE =' Program',
                    FULLSCREEN = False,
                    BORDERLESS = False,
                    EXIT_BUTTON_VISIBLE = True,
                    FPS_COUNTER = True,
                    VSYNC = True,
                    COLOR = color.dark_gray,
                    SIZE = (800,600),
                    ):
        self.TITLE =TITLE
        self.FULLSCREEN = FULLSCREEN
        self.EXIT_BUTTON_VISIBLE = EXIT_BUTTON_VISIBLE
        self.FPS_COUNTER = FPS_COUNTER
        self.BORDERLESS = BORDERLESS
        self.COLOR = COLOR
        self.VSYNC = VSYNC
        self.SIZE = SIZE


        self.APP = Ursina()  
        self.win = window

        self.win.title = self.TITLE
        self.win.borderless = self.BORDERLESS
        self.win.exit_button.visible = self.EXIT_BUTTON_VISIBLE
        self.win.fps_counter.enabled = self.FPS_COUNTER
        self.win.vsync = self.VSYNC
        self.win.color = self.COLOR
        self.win.size = self.SIZE
        self.win.fullscreen = self.FULLSCREEN
        


    def Run(self):
        self.APP.run()

    def Set_Size(self,size):
        self.win.size = size

    def Exit(self):
        if Sub_events_.Board_init().PRESS_SUB('esc'):
            sys.exit()

    def Get_Title(self):
        return self.TITLE

    def Set_Color(self,color):
        self.win.color = color


class Color(object):
    def __init__(self):
        pass

    class _rgb:
        def __init__(self,r,g,b):
            self.r = r
            self.g = g
            self.b = b
            self.color = [self.r,self.g,self.b]
            self.get = color.rgb(self.r,self.g,self.b)

    class _hsv:
        def __init__(self,h,s,v):
            self.h = h
            self.s = s
            self.v = v
            self.color = [self.h,self.s,self.v]
            self.get = color.hsv(self.h,self.s,self.v)

    class _rgba:
        def __init__(self,r,g,b,a):
            self.r = r
            self.g = g
            self.b = b
            self.a = a
            self.color = [self.r,self.g,self.b,self.a]
            self.get = color.rgba(self.r,self.g,self.b,self.a)


class Entitys(object):
    def __init__(self,
                    shape = 'cube',
                    color = None,
                    position = (0,0,0),
                    full__scale = 1,
                    texture = 'brick',
                    rotation = (0,0,45)
                    ):

        self.shape = shape
        self.color = color
        self.position = position
        self.full__scale = full__scale
        self.texture = texture
        self.rotation = rotation

        self.obj = Entity(
            model = self.shape,
            color = self.color,
            position = self.position,
            scale = self.full__scale,
            texture=self.texture,
            rotation = self.rotation
        )

    def _Color(self,color):
        self.obj.color = color

    def _Rotate_x(self,angle):
        self.obj.rotation_x = angle

    def _Rotate_y(self,angle):
        self.obj.rotation_y = angle


class PointLights(object):
    def __init__(self,
                    x = 0,
                    y = 2,
                    z = 0,
                    color=color.white):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        PointLight(
            x = self.x,
            y = self.y,
            z = self.z,
            color = self.color)


class Keys():
    def __init__(self):
        pass
    def PressEvent(self, key='r'):
        return held_keys[key]


class Mouse():
    def __init__(self):
        pass

    def Get_moving(self):
        return mouse.moving
    
    def x(self):
        return mouse.position.x

    def y(self):
        return mouse.position.y

    def left(self):
        return mouse.left

    def right(self):
        return mouse.right


class Widgets():
    def __init__(self):
        pass
    class Slider(object):
        def __init__(self):
            self.slider = Slider(
                0,
                5,
                1,
                height = Text.size*3,
                y=0,
                x=-0.5,
                step=0.1,
                vertical = True
                )

        def value(self):
            return self.slider.value














