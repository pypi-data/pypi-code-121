
import colorama
import sys
import pymunk
import pymunk.pygame_util



# My decorators
def printl():
    def wrapper(fun):
        ret = fun()
        print(ret)
    return wrapper









# My metods
def Obj_type(obj):
    return obj.__class__.__name__
def Obj_type_print(obj):
    print(colorama.Fore.YELLOW+obj.__class__.__name__+colorama.Fore.RESET)





from colored import (bg as BG , fg as FG , attr as ATTR ,stylize)


import pyganim

from pyclbr import Function

import os

import pygame.gfxdraw
import pygame_widgets
import pygame
import keyboard
import math
import time
import random
import mouse
import numpy

import pygame.camera

from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.progressbar import ProgressBar




start_time = 0
anim_time = 1

startTime = time.time()

pygame.init()


def Pass():
    pass
def Get_Сamera_Сolor_Ыpace():
        return ['RGB','HSV','YUV']
def Mod(num):
    if num < 0:num = -num
    return num
def Get_pyGL_Version():
    print(colorama.Fore.BLUE+'Pygl version (20.1)'+colorama.Fore.RESET)
def Get_GL_Functions():
        print(colorama.Fore.GREEN+'GL_FUNCTIONS---')
        print('''   
        Draw f- D-none
        Obv f- O-(rrr)(ggg)(bbb)-THICKNESS
        DrOb f- OD-(rrr)(ggg)(bbb)-THICKNESS
        '''+colorama.Fore.RESET)
# Sliders data base
Sliders_base = {}
def Print_Sliders_Base():
    for i in Sliders_base:
        print(i , '  ', Sliders_base[i])

# Text box data base
TextBoxs_base = {}
def Print_Text_Box_Base():
    for i in TextBoxs_base:
        print(i , '  ', TextBoxs_base[i])

# Buttons data base
Buttons_base = {}
def Print_Text_Box_Base():
    for i in Buttons_base:
        print(i , '  ', Buttons_base[i])

# Toggles data base
Toggles_base = {}
def Print_Text_Box_Base():
    for i in Toggles_base:
        print(i , '  ', Toggles_base[i])

# Drop downs data base
DropDowns_base = {}
def Print_Text_Box_Base():
    for i in DropDowns_base:
        print(i , '  ', DropDowns_base[i])

# Progress bar data base
ProgressBar_base = {}
def Print_Text_Box_Base():
    for i in ProgressBar_base:
        print(i , '  ', ProgressBar_base[i])

# Triggers        
def Get_Triggers():
    print(colorama.Fore.GREEN+'''
Exit Trigger,
Break Trigger'''+colorama.Fore.RESET)
    
# Events
Events = None

# Widget type
WT_Slider = 'Slider'
WT_Button = 'Button'
WT_DropDown = 'DropDown'
WT_TextBox = 'TextBox'
WT_Toggle = 'Toggle'
WT_ProgressBar = 'ProgressBar'

# Progress_bar
Progress_bar_time = 10
Progres_bar_buffer = lambda:  1 - (time.time() - startTime) / Progress_bar_time

# Display
D_Full = 'FULL'
D_Resize = 'RESZ'
D_Nones = 'NONE'

#Camera_space
CAM_rgb = 'RGB'
CAM_hsv = 'HSV'
CAM_yuv = 'YUV'

# Colors
class Color_:
    class _rgb(object):
        def __init__(self,r,g,b,hsv=0):
            self.hsv = hsv
            self.r = r
            self.b = b
            self.g = g
            if self.r == 'r' or self.r == 'R':self.r = random.randint(0,255)
            if self.g == 'r' or self.g == 'R':self.g = random.randint(0,255)
            if self.b == 'r' or self.b == 'R':self.b = random.randint(0,255)
            self.r = self.r - self.hsv
            self.g = self.g - self.hsv
            self.b = self.b - self.hsv
            if self.r < 0:    self.r = 0
            if self.g < 0:    self.g = 0
            if self.b < 0:    self.b = 0
            if self.r > 255:  self.r = 255
            if self.g > 255:  self.g = 255
            if self.b > 255:  self.b = 255
            self.COLOR = (self.r,self.g,self.b)

        def SETHSV(self,hsv):
            self.hsv = hsv
            self.r = self.r - self.hsv
            self.g = self.g - self.hsv
            self.b = self.b - self.hsv
            if self.r < 0:    self.r = 0
            if self.g < 0:    self.g = 0
            if self.b < 0:    self.b = 0
            if self.r > 255:  self.r = 255
            if self.g > 255:  self.g = 255
            if self.b > 255:  self.b = 255
            self.color = (self.r,self.g,self.b)
            return self.color

        def Color_mesh(self,color,mesh=0.5):
            hsv = (self.hsv + color.hsv)/mesh
            r = (self.r + color.r)/mesh
            g = (self.g + color.g)/mesh
            b = (self.b + color.b)/mesh
            color = Color_(r,g,b,hsv)
            return color 

        def Color_Reverse(self):
            if self.r <= 127.5:r = 127.5+(127.5-self.r) 
            if self.g <= 127.5:g = 127.5+(127.5-self.g) 
            if self.b <= 127.5:b = 127.5+(127.5-self.b)  
            if self.r >  127.5:r = 127.5-(self.r - 127.5 ) 
            if self.g >  127.5:g = 127.5-(self.g - 127.5 ) 
            if self.b >  127.5:b = 127.5-(self.b - 127.5 ) 
            hsv = -self.hsv
            color = Color_(r,g,b,hsv)
            return color

        def Set_chb(self):
            gr = (self.color[0]+self.color[1]+self.color[2])/3
            hsv = 0
            col = Color_(gr,gr,gr,hsv)
            return col
        
        def Get_(self):
            return self.COLOR

    class _html(object):
        def __init__(self,code='') -> None:
            self.COLOR = code
        def Get_(self):
            return self.COLOR
class c_POSICIONAL_R_G(object):
    def __init__(self,POSITION=[]):    
        POSITION[0] = POSITION[0]/10
        POSITION[1] = POSITION[1]/10
        self.color = (POSITION[0],POSITION[1],0)
    def Get(self):
        return self.color
class c_POSICIONAL_R_B(object):
    def __init__(self,POSITION=[]):
        POSITION[0] = POSITION[0]/10
        POSITION[1] = POSITION[1]/10
        self.color = (POSITION[0],0,POSITION[1])
    def Get(self):
        return self.color
class c_POSICIONAL_G_B(object):
    def __init__(self,POSITION=[]):
        POSITION[0] = POSITION[0]/10
        POSITION[1] = POSITION[1]/10
        self.color = (0,POSITION[1],POSITION[0])
    def Get(self):  
        return self.color
class Color_gradient(object):
    def __init__(self,SURF=None, left_colour=(), right_colour=(), target_rect=None):

        
        self.left_colour = left_colour
        self.right_colour = right_colour
        self.target_rect = target_rect
        self.colour_rect = pygame.Surface( ( 2,2 ) )                                   # tiny! 2x2 bitmap
        pygame.draw.line( self.colour_rect, self.left_colour,  ( 0,0 ), ( 0,1 ) )            # left colour line
        pygame.draw.line( self.colour_rect, self.right_colour, ( 1,0 ), ( 1,1 ) )            # right colour line
        colour_rect = pygame.transform.smoothscale( self.colour_rect, ( self.target_rect.width, self.target_rect.height ) )  # stretch!
        SURF.blit( colour_rect, self.target_rect )  



        

        
c_RED = Color_._rgb(255, 0, 0)
c_GREEN = Color_._rgb(0, 128, 0)
c_BLUE = Color_._rgb(0, 0, 255)
c_YELLOW = Color_._rgb(255, 255, 0)
c_WHITE = Color_._rgb(255, 255, 255)
c_BLACK = Color_._rgb(0, 0, 0)
c_CYAN = Color_._rgb(0, 255, 255)
c_LIME = Color_._rgb(0, 255, 0)
c_DARK_GREEN = Color_._rgb(0, 100, 0)
c_CRIMSON = Color_._rgb(220, 20, 60)
c_PINK = Color_._rgb(255, 192, 203)
c_VIOLET = Color_._rgb(238, 130, 238)
c_PURPLE = Color_._rgb(128, 0, 128)
c_NAVY = Color_._rgb(0, 0, 128)
c_SKY_BLUE = Color_._rgb(135, 206, 250)
c_AQUA = Color_._rgb(0, 255, 255)
c_MAROON = Color_._rgb(128, 0, 0)
c_SILVER = Color_._rgb(192, 192, 192)
c_GRAY = Color_._rgb(128, 128, 128)
c_ORANGE = Color_._rgb(255, 165, 0)
c_DARK_ORANGE = Color_._rgb(255, 140, 0)
c_TOMATO = Color_._rgb(255, 99, 71)
c_GOLD = Color_._rgb(255, 215, 0)
c_INDIGO = Color_._rgb(75, 0, 130)
c_MAGENTA = Color_._rgb(255, 0, 255)
c_DARK_VIOLET = Color_._rgb(148, 0, 211)
c_BLUE_VIOLET = Color_._rgb(138, 43, 226)





class New_metods:
    class Nstr:
        def __init__(self,str : str) -> None:
            self.str = str

        def __GL_len__(self):
            return len(self.str)

        def __GL_ToSym__(self,sym):
            for i in self.str:
                if sym == i:
                    return True
                    break
            return False

        def __call__(self):
            return self.str

        def __GL_SymCount__(self,sym):
            count = 0
            for i in self.str:
                if sym == i:
                    count+=1
            return count

        def __GL_IsInt__(self):
            r_int = ''
            nums = ['1','2','3','4','5','6','7','8','9','0']
            for i in self.str:
                for num in nums:
                    if i == num:
                        r_int+=i
            return int(r_int)


class Maping_:
    class _2D_MAPS:
        def __init__(self, size = [int,int], obj = [1,0]):
            self.map = []
            self.obj = obj
            self.size = size
            for i in range(self.size[0]):
                map_s = []
                for i in range(self.size[1]):
                    map_s.append(self.obj[random.randint(0,len(self.obj)-1)] )
                self.map.append(map_s)

        def GET(self) -> list:   
            return self.map     

    class _1D_MAPS:
        def __init__(self, size = int, obj = [1,0]):
            self.map = []
            self.obj = obj
            self.size = size
            for i in range(self.size):  
                self.map.append( self.obj [ random.randint(0,len(self.obj)-1) ] )  

        def GET(self) -> list:
            return self.map

                









        
# 1 Fonts
class Fonts_(object):
    def __init__(self):
        global Fonts
        self.Fonts = pygame.font.get_fonts()
        Fonts = self.Fonts
        
    def Get_index_(self,index):
        return self.Fonts[index]

    class Print_():
        def __init__(self,Nums=False):
            if Nums == False:
                for i in range(len(Fonts)):
                    print(colorama.Fore.GREEN + Fonts[i] + colorama.Fore.RESET)

            elif Nums == True:
                for i in range(len(Fonts)):
                    print(colorama.Fore.YELLOW +  '['+str(i)+'] - ' + colorama.Fore.RESET , end='') 
                    print(colorama.Fore.GREEN + Fonts[i] + colorama.Fore.RESET)      
# 2 Vector_2D
class Vec2_:
        def __init__(self,vect2d_start=[-1],vect2d_end=[-1],pos=[0,0]): 
            if vect2d_start[0]!=-1 and vect2d_end[0]!=-1:
                self.vect2d_start = vect2d_start
                self.vect2d_end = vect2d_end
                self.vec2D = [self.vect2d_start,self.vect2d_end]
                self.x = vect2d_end[0]-vect2d_start[0]
                self.y = vect2d_end[1]-vect2d_start[1]
            else:
                self.x = pos[0]
                self.y = pos[1]
            self.size = int(math.sqrt(self.x**2+self.y**2))
            self.absv = Mod(self.size)
            self.pos1 = [self.x,self.y]

        def RAV_2D(self,vector2D):
            parperx_st_ = int(vector2D.vect2d_start[0]-self.vect2d_start[0])
            parperx_en_ = int(vector2D.vect2d_end[0]-self.vect2d_end[0])
            parpery_st_ = int(vector2D.vect2d_start[1]-self.vect2d_start[1])
            parpery_en_ = int(vector2D.vect2d_end[1]-self.vect2d_end[1])
            if Mod(parperx_st_) == Mod(parperx_en_) and Mod(parpery_st_) == Mod(parpery_en_):
                return True
            else:
                return False

        def POV_2D(self,ugl):
            pos = [int(self.x*math.cos(ugl)-self.y*math.sin(ugl)),int(self.y*math.cos(ugl)+self.x*math.sin(ugl))]
            vec3 = Vec2_(pos=pos)
            return vec3

        def SUM(self,vector2D):
            pos=[self.x+vector2D.x,self.y+vector2D.y]
            vec3 = Vec2_(pos=pos)
            return vec3

        def RAZ(self,vector2D):
            pos=[self.x-vector2D.x,self.y-vector2D.y]
            vec3 = Vec2_(pos=pos)
            return vec3

        def UMN(self,delta):
            pos=[self.x*delta,self.y*delta]
            vec3 = Vec2_(pos=pos)
            return vec3

        def SCAL(self,vector2D):
            scl = self.x*vector2D.x+self.y*vector2D.y
            return scl

        def NUL(self):
            if self.vect2d_end==self.vect2d_start:return True
            else:return False

        def NAP(self,vector2D):
            parperx_st_ = int(vector2D.vect2d_start[0]-self.vect2d_start[0])
            parperx_en_ = int(vector2D.vect2d_end[0]-self.vect2d_end[0])
            parpery_st_ = int(vector2D.vect2d_start[1]-self.vect2d_start[1])
            parpery_en_ = int(vector2D.vect2d_end[1]-self.vect2d_end[1])
            
            if parperx_en_ == parperx_st_ and parpery_en_ == parpery_st_ :
                    return True
            else:
                    return False     
# 3 Surfases
class Surfases_(object):
    def __init__(self,SIZE=[],POSITION=[0,0],COLOR=(200,200,200),ALPHA=255):
        self.screen = pygame.Surface((SIZE[0],SIZE[1]))
        self.screen.fill(COLOR)
        self.color = COLOR
        self.size = SIZE
        self.alpha = ALPHA
        self.pos = POSITION
        if self.alpha > 255:self.alpha=255
        if self.alpha < 0:self.alpha=0
        self.screen.set_alpha(self.alpha)

    def SET_ALPHA(self,al):
        if al > 255:al=255
        if al < 0:al=0
        self.screen.set_alpha(al)
        
    def GET_PIXEL_COLOR(self,pos):
        col = self.screen.get_at(pos)
        return [col[0],col[1],col[2]]
        
    def DRAW_(self,screen_surf,pos=None):
        if pos!=None:self.pos = pos
        screen_surf.blit(self.screen,(self.pos[0],self.pos[1]))

    def SAVE_SURF(self,filename):
        pygame.image.save(self.screen,filename)

    def SET_BG_COLOR(self,color):
        self.color = color
    
    def GET_BG_COLOR(self):
        return self.color

    def UPDATE(self):
        self.screen.fill(self.color)

    def FILL_SURF(self,col=()):
        self.screen.fill(col)

    def GET_SIZE(self):
        return self.size
    
    def GET_WIDTH(self):
        return self.size[0]

    def GET_POS(self):
        return self.pos

    def GET_HEIGHT(self):
        return self.size[1]

    def SET_POS(self,pos=[]):
        if pos[0]=='s':self.pos[0]=self.pos[0]
        else:          self.pos[0]=pos[0]
        if pos[1]=='s':self.pos[1]=self.pos[1]
        else:          self.pos[1]=pos[1]

    def GET_LEFT(self):
        return [self.pos[0],self.pos[1]+self.size[1]/2]

    def GET_RIGHT(self):
        return [self.pos[0]+self.size[0],self.pos[1]+self.size[1]/2]

    def GET_UP(self):
        return [self.pos[0]+self.size[0]/2,self.pos[1]]

    def GET_DOWN(self):
        return [self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]]
# 4 Kamera      
class Kamera_:
    def __init__(self,SIZE=[],COLOR_SPACE='RGB',NUM=0):
        self.size = SIZE
        pygame.camera.init()
        self.cam = pygame.camera.Camera(pygame.camera.list_cameras()[NUM],(self.size[0],self.size[1]), COLOR_SPACE)
        self.cam.set_controls(True,False,1)
        
    def LIST_CAM(self):
        cams = pygame.camera.list_cameras()
        return cams
    
    def START(self):self.cam.start()

    def END(self):self.cam.stop()

    def GET_IMG(self):
        img = self.cam.get_image()
        image = Img_(img)
        return image

    def GET_SIZE(self):
        width , height = self.cam.get_size()
        return width , height
    
    def SET_SETINGS(self,wflip,hflip,sun):
        self.cam.set_controls(wflip,hflip,sun)

    def GET_SETINGS(self):
        cont = self.cam.get_controls()
        return cont
# 5 Time
class Time_:
    def __init__(self):
        pass
    def DELLAY(self,MILISECONDS):
        pygame.time.delay(MILISECONDS)
    def WAIT(self,MILISECONDS):
        pygame.time.wait(MILISECONDS)
    class TIMER():
        def __init__(self):
            clock = pygame.time.Clock()
            self.time = clock.get_time()
        def return_time(self):
            return self.time
# 6 Text
class Text_:
    def __init__(self,TEXT='',GLASS=False,COLOR=(),FONT='arial',SIZE=0,POSITION=[],BG_COLOR=None,SURF = None):  
        pygame.font.init()    
        self.text = TEXT
        self.pos = POSITION
        self.pix = SIZE
        self.font = FONT

        self.x = self.pos[0]
        self.y = self.pos[1]

        self.pos = [self.x,self.y]

        self.glass = GLASS
        self.col = COLOR
        self.bg_color = BG_COLOR

        self.text_blink_speed = 1



        self.screen = SURF
        

    def RENDER(self,POSITION=[None,None]): 
        if POSITION[0]!=None and POSITION[1]!=None:
            self.x = POSITION[0] ; self.y = POSITION[1]

        self.RENDER_TEXT = pygame.font.SysFont(self.font,self.pix)
        RENDERING = self.RENDER_TEXT.render(
             self.text,
             self.glass,
             self.col,
             self.bg_color
        ) 
        self.RENDERING = RENDERING
        self.screen.blit(self.RENDERING,(self.x,self.y))

    def SET_TEXT(self,text=''):
        self.text = text

    def GET_POSITION(self):
        return self.pos

    def SET_FONT(self,FONT=None):
        self.font = FONT
        self.RENDER_TEXT = pygame.font.SysFont(self.font,self.pix)
        RENDERING = self.RENDER_TEXT.render(self.text,self.glass,self.col,self.bg_color) 
        self.RENDERING = RENDERING

    def GET_FONT(self):
        return self.font

    def SET_SURF(self, surface):
        self.screen = surface

    def __GL_BLINK__(self,max_size=30,min_size=10,sped =1):
        self.text_blink_speed*=sped
        if self.pix > max_size :
            self.text_blink_speed =- self.text_blink_speed
        elif self.pix < min_size :
            self.text_blink_speed =- self.text_blink_speed
        self.pix+=self.text_blink_speed
        self.x += -self.text_blink_speed*2
        self.y += -self.text_blink_speed

    def SET_UNDERLINE(self,UNDERLINE=True):
        self.RENDER_TEXT.set_underline(UNDERLINE)

    def SET_POS(self,POSITION=[]):
        self.pos = POSITION
        self.x = POSITION[0]
        self.y = POSITION[1]  

    def SET_TEXT_COLOR(self,COLOR=None):
        self.col = COLOR
        self.RENDERING = self.RENDER_TEXT.render(self.text,self.glass,self.col,self.bg_color)

    def GET_TEXT_COLOR(self):
        return self.col

    def GET_BG_COLOR(self):
        return self.bg_color

    def GET_TEXT(self):
        return self.text

    def Set_SIZE(self,size):
        self.pix = size

    def SET_BG_COLOR(self,COLOR=None):
        self.bg_color = COLOR
        self.RENDERING = self.RENDER_TEXT.render(self.text,self.glass,self.col,self.bg_color)

    def __GL_text__(self,p=True):
        if p:       print('Text --> '+self.text)
        else:       return self.text

    def __GL_x__(self):
        return self.x

    def __GL_y__(self):
        return self.y
# 7 Math
class Math_:
    def __init__(self):
        pass

    def COS(self,ugl):
        return math.cos(ugl)

    def SIN(self,ugl):
        return math.sin(ugl) 

    def RAST(self,pos1=[],pos2=[]):
        if pos1[0]>pos2[0]:w = pos1[0]-pos2[0]
        else:              w = pos2[0]-pos1[0]
        if pos1[1]>pos2[1]:h = pos1[1]-pos2[1]
        else:              h = pos2[1]-pos1[1]
        dl = math.sqrt(w*w+h*h)
        return dl   

    class Randomings():
        def __init__(self):
            pass

        class Randints():
            def __init__(self,a,b):
                self.a = a
                self.b = b
                self.num = random.randint(self.a,self.b)
            def Get(self):
                return self.num

        class Randrages():
            def __init__(self,a,b,step):
                self.a = a
                self.b = b
                self.step = step
                self.num = random.randrange(self.a,self.b,self.step)
            def Get(self):
                return self.num

        class Randoms():
            def __init__(self):
                self.num = random.random()
            def Get(self):
                return self.num
# 9 Mouse and keyboard
class Sub_events_:
    def __init__(self):
        pass
    class Board_init:
        def __init__(self):
            pass

        def PRESS_SUB(self,key):
            on = keyboard.is_pressed(key)
            return on

        def PRESS_FUNCTION(self,key,function):
            if True==keyboard.is_pressed(key):
                function()

        def PRESS_AND_WAIT_KEY(self,key):
            keyboard.press(key)
        
        def KEY_RELEASE(self,key):
            keyboard.release(key)

        def KEY_SAND(self,key):
            keyboard.send(key)

        def WRITE(self,text,deley=0.1):
            keyboard.write(text,deley)
            
    class Mouse_init:
        def __init__(self):
            self.sped_x = 0
            self.sped_y = 0
            self.end_pos_x = 0
            self.end_pos_y = 0

        def GET_POSITION(self,PYGL_WINDOW='y'): 
            if PYGL_WINDOW=='y':
                pos = pygame.mouse.get_pos();  
                pos = [pos[0],pos[1]]
                return pos
            elif PYGL_WINDOW=='n':
                pos = mouse.get_position(); 
                pos = [pos[0],pos[1]]
                return pos
            else:
                print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'None flag'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'''flags : y , n'''+colorama.Fore.RESET)
                sys.exit()

        def GET_PRESS_ON_DISPLAY(self,BUTTON='left'):
            if BUTTON!='left' and BUTTON!='right' :
                print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'None flag'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'''flags : left , right'''+colorama.Fore.RESET)
                sys.exit()
            bol = mouse.is_pressed(BUTTON)
            return bol

        def X_win(self):
            return mouse.get_position()[0]

        def Y_win(self):
            return mouse.get_position()[1]

        def X_gl(self):
            return pygame.mouse.get_pos()[0]

        def Y_gl(self):
            return pygame.mouse.get_pos()[1]

        def GET_OUT_ON_DISPLAY(self,BUTTON='left'):
            
            for ev in pygame.event.get():
                if ev.type == pygame.MOUSEBUTTONUP:
                    print(ev.but)
                    break
                    
               

        def GET_FOCUSED_IN_PYGL_WINDOW(self):
            return pygame.mouse.get_focused()
                    
        def GET_SCROLING(self,dir=None):
            eve = 0
            for ev in pygame.event.get():
                if ev.type == pygame.MOUSEWHEEL:
                    eve = ev.y
                    if dir == '':
                        eve = 0
                        return [False,False]
                    if dir == 'down' and eve == 1:
                        eve = 0
                        return [False,True]
                    if dir == 'up' and eve == -1:
                        eve = 0
                        return [True,False]
                
        def GET_PRESS_ON_PYGL_WINDOW(self,BUTTON="l"):
            if BUTTON!='l' and BUTTON!='r' and BUTTON!='m':
                print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'None flag'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'''flags : l , r'''+colorama.Fore.RESET)
                sys.exit()
            pr = pygame.mouse.get_pressed()
            if BUTTON == "l":  return pr[0]
            elif BUTTON == "r":  return pr[2]
            elif BUTTON == "m":  return pr[1]

        def PRESS_FUNCTION_ON_PYGL_WINDOW(self,button,function):
            pr = pygame.mouse.get_pressed()
            if button == "l" and pr[0] == True:  
                function()
            elif button == "r" and pr[2] == True:  
                function()
            elif button == "m" and pr[1] == True:  
                function()

        def SET_VISIBLE_ON_PYGL_WINDOW(self,viz):
            pygame.mouse.set_visible(viz)  

        def SET_POS_ON_PYGL_WINDOW(self,pos=[]):
            pygame.mouse.set_pos([pos[0],pos[1]])

        def SET_POS_ON_DISPLAY(self,pos=[]):
            mouse.move(pos[0],pos[1])

        def ON_DISPLAY_MOVE(self,pos=[],absolute=True,second=0):
            mouse.move(pos[0],pos[1],absolute,second)

        def ON_CLICK(self,BUTTON='left'):
            if BUTTON!='left' and BUTTON!='right':
                print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'None flag'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'''flags : left , right'''+colorama.Fore.RESET)
                sys.exit()
            mouse.click(BUTTON)

        def ON_DUBLE_CLICK(self,BUTTON='left'):
            if BUTTON!='left' and BUTTON!='right':
                print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'None flag'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'''flags : left , right'''+colorama.Fore.RESET)
                sys.exit()
            mouse.double_click(BUTTON)
# Mouse and Board
Open_mouse = Sub_events_.Mouse_init()
Open_board = Sub_events_.Board_init()



# 10 Display and GL
class Display_init_:
    
    def __init__(self,size=[600,400],caption='Program',flags=D_Nones,BG_COLOR=c_WHITE):
        global screen,SHAPE_COUNT
        self.caption = caption

        pygame.init()
        pygame.display.init()
        
        self.flags = flags
        clock = pygame.time.Clock()
        if flags == 'FULL':
            screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
            pygame.display.set_mode()
        elif flags == 'RESZ':
            self.width = size[0]
            self.height = size[1]
            screen = pygame.display.set_mode((self.width,self.height),pygame.RESIZABLE)
        elif flags == 'NONE':
            self.width = size[0]
            self.height = size[1]
            screen = pygame.display.set_mode((self.width,self.height))
        else:
            print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'None flag'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'''flags : FULL - this is full screen
        NONE - this is none'''+colorama.Fore.RESET)
            sys.exit()

        self.width = screen.get_size()[0]
        self.height = screen.get_size()[1]
        self.win_size = screen.get_size()
        
        self.col = BG_COLOR 
        

        self.up = 0
        self.down = self.height
        self.left = 0
        self.right = self.width

        self.clock = clock
        self.clock.tick()
        self.screen = screen

        SHAPE_COUNT = 0

        self.exit_button_show = False


        
        self.pymunk_init = False



        pygame.display.set_caption(self.caption)

    def __GL_physics_init__(self):
        try:
            import pymunk
        except ImportError:
            print('Error;\n pymunk is not detected')
            sys.exit()

        self.pymunk_init = True

    def __GL_posityv_y_is_up__():
        pymunk.pygame_util.positive_y_is_up = False

    class Physics:
        def __init__(self):
            pass
        class Space:
            def __init__(self,SURF=None, GRAVITY = [int,int]):
                global space
                self.gravity = GRAVITY
                self.gravity_with_x = GRAVITY[0]
                self.gravity_with_y = GRAVITY[1]

                self.surf = SURF
                self.space = pymunk.Space()
                space = self.space
                self.gravity = (self.gravity_with_x, self.gravity_with_y)


                self.options = pymunk.pygame_util.DrawOptions(self.surf)
                

            def Update(self):
                self.space.step(1/60)
                self.space.debug_draw(self.options)

            class Shapes:
                def __init__(self) -> None:
                    pass
                class Segment():
                    def __init__(self,TYPE=None,START_POS=[],END_POS=[],SIZE=26,ELASTICITY=0,FRICTION=1) -> None:
                        
                        self.type = TYPE
                        self.start_pos = (START_POS[0],START_POS[1])
                        self.end_pos = (END_POS[0],END_POS[1])
                        self.size = SIZE
                        self.elasticity = ELASTICITY
                        self.friction = FRICTION

                        self.segment_shape = pymunk.Segment(self.type,self.start_pos,self.end_pos,self.size)
                        self.segment_shape.elasticity = self.elasticity
                        self.segment_shape.friction = self.friction

                    def Add(self):
                        space.add(self.segment_shape)

                class Rect():
                    def __init__(self,POSITION = [], SIZE = [], COLOR = 'red', ELASTICITY = 0.8, FRICTION = 1, MASS = 1) -> None:
                        self.position = (POSITION[0],POSITION[1])
                        self.size = (SIZE[0],SIZE[1])
                        self.color = COLOR
                        self.elasticity = ELASTICITY
                        self.friction = FRICTION
                        self.mass = MASS

                        self.rect_moment = pymunk.moment_for_box(self.mass,self.size)
                        self.rect_body = pymunk.Body(self.mass,self.rect_moment)
                        self.rect_body.position = self.position
                        
                        self.rect_shape = pymunk.Poly.create_box(self.rect_body,self.size)
                        self.rect_shape.elasticity = self.elasticity
                        self.rect_shape.friction = self.friction
                        #self.rect_shape.color = color
                    
                    def Add(self):
                        space.add(self.rect_body,self.rect_shape)



                
                


    def __GL_captions__(self,p=True):
        if p:       print('Caption --> ',self.caption)
        else:       return self.caption

    def __GL_background_color__(self,p=True):
        if p:       print('Background color --> ',self.col)
        else:       return self.col
        
    def __GL_width__(self,p=True):
        if p:       print('Width --> ',self.width)
        else:       return self.width
        
    def __GL_height__(self,p=True):
        if p:       print('Height --> ',self.height)
        else:       return self.height

    def __GL_fps__(self,p=True):
        if p:       print('FPS --> '+str(int(self.clock.get_fps())))
        else:       return int(self.clock.get_fps())

    def __GL_win_start_type__(self,p=True):
        if p:       print('Start Type --> ',self.flags)
        else:       return self.flags

    def __GL_type__(self,p=True):
        if p:       print('Type --> ',screen.__class__.__name__)
        else:       return self.screen.__class__.__name__

    def __GL_show_exit_button__(self,bool : bool = False):
        if bool==True:
            self.exit_button_show = True
            self.eb = Widgets_.Buttons(self.screen,[1900,0],[20,20],'X',(255,255,255),20,20,(200,10,20),(255,20,30),(100,30,30),0,Pass)
        else:
            self.exit_button_show = False
            
    def IN_WINDOW(self,position=[]):
        if (position[0]>=0 and
            position[0]<=self.width and
            position[1]>=0 and 
            position[1]<=self.height):
            return True
        else: return False

    def GET_DISPLAY_INFO(self):
        return pygame.display.Info()

    def GET_SHAPES_COUNT(self):
        return SHAPE_COUNT

    def SET_FULL(self):
        self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

    def LOCK(self):
        self.screen.lock()

    def UNLOCK(self):
        self.screen.unlock()

    def SET_RESIZE(self):
        self.screen = pygame.display.set_mode((self.width,self.height),pygame.RESIZABLE)
        
    def SET_NONE(self):
        self.screen = pygame.display.set_mode((self.width,self.height))

    def GET_TOGGLE_FULLSCREEN(self):
        return pygame.display.toggle_fullscreen()

    def SET_CAPTION(self,caption=''):
        self.caption = caption
        pygame.display.set_caption(self.caption)

    def GET_ACTIVE(self):
        return pygame.display.get_active()
    
    def SET_ALPHA(self,alp):
        screen.set_alpha(alp)

    def GET_COLOR(self,x,y):
        col = screen.get_at([x,y])
        col1 = [col[0],col[1],col[2]]
        return col1

    def GET_WIN_CENTER(self):
        xc = self.screen.get_width()/2
        yc = self.screen.get_height()/2
        return xc , yc

    def SET_FPS(self,fps):
        if type(fps)==str:
            if fps == "MAX":fps = 1000
            elif fps == "MIN":fps = 30
            else:
                print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                print(colorama.Fore.YELLOW+'None fps'+colorama.Fore.RESET)
                sys.exit()
        self.clock.tick(fps)

    def GET_INIT(self):
        return pygame.display.get_init()
    
    def GET_DISPLAY_DRIVER(self):
        return pygame.display.get_driver()

    def GET_TOP(self,cor='X',storona='left'):   
        if cor=='X' or cor=='x' and storona=='left':return 0
        elif cor=='X' or cor=='x' and storona=='right':return self.screen.get_width()
        elif cor=='Y' or cor=='y' and storona=='left':return 0
        elif cor=='Y' or cor=='y' and storona=='right':return 0
        else:
            print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'None cordinate'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'Uses left or fight'+colorama.Fore.RESET)
            sys.exit()

    def GET_DOWN(self,cor='X',storona='left'):
        if cor=='X' or cor=='x' and storona=='left':return 0
        elif cor=='X' or cor=='x' and storona=='right':return self.screen.get_width()
        elif cor=='Y' or cor=='y' and storona=='left':return self.screen.get_height()
        elif cor=='Y' or cor=='y' and storona=='right':return self.screen.get_height()
        else:
            print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'None cordinate'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'Uses left or fight'+colorama.Fore.RESET)
            sys.exit()

    def GET_LEFT(self,cor='X',storona='up'):
        if cor=='X' or cor=='x' and storona=='up':return 0
        elif cor=='X' or cor=='x' and storona=='down':return 0
        elif cor=='Y' or cor=='y' and storona=='up':return 0
        elif cor=='Y' or cor=='y' and storona=='down':return self.screen.get_height()
        else:
            print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'None cordinate'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'Uses up or down'+colorama.Fore.RESET)
            sys.exit()

    def GET_RIGHT(self,cor='X',storona='up'):
        if cor=='X' or cor=='x' and storona=='up':return self.screen.get_width()
        elif cor=='X' or cor=='x' and storona=='down':return self.screen.get_width()
        elif cor=='Y' or cor=='y' and storona=='up':return 0
        elif cor=='Y' or cor=='y' and storona=='down':return self.screen.get_height()
        else:
            print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'None cordinate'+colorama.Fore.RESET)
            print(colorama.Fore.YELLOW+'Uses up or down'+colorama.Fore.RESET)
            sys.exit()

    def GET_FPS(self) -> int:
        return int(self.clock.get_fps())

    def CE(self,running=True,EXIT_BUTTON='esc') -> bool:  
        global Events
        for event in pygame.event.get():
            Events = event
            if event.type == pygame.QUIT:
                running = False
        events = pygame.event.get() 
      
        pygame_widgets.update(events)
        if keyboard.is_pressed(EXIT_BUTTON):
            sys.exit()

        if self.exit_button_show:
            self.eb.Update()
            if self.eb.Get_pressed():
                sys.exit()
        return running

    def CEU(self,running=True,EXIT_BUTTON='esc',COLOR=None) -> bool:  
        global Events


        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        for event in pygame.event.get():
            Events = event
            if event.type == pygame.QUIT:
                running = False
                
                
        events = pygame.event.get() 
      
        pygame_widgets.update(events)
        if keyboard.is_pressed(EXIT_BUTTON):
            sys.exit()

        pygame.display.flip()
        if COLOR is None:
                COLOR = 'white'
        screen.fill(COLOR)

        if self.exit_button_show:
            self.eb.Update()
            if self.eb.Get_pressed():
                sys.exit()

        return running

    def CEUF(self,running=True,EXIT_BUTTON='esc',COLOR=None,FPS=60) -> bool:  
        global Events

        self.clock.tick(FPS)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        for event in pygame.event.get():
            Events = event
            if event.type == pygame.QUIT:
                running = False
                
                
        events = pygame.event.get() 
      
        pygame_widgets.update(events)
        if keyboard.is_pressed(EXIT_BUTTON):
            sys.exit()

        pygame.display.flip()
        if COLOR is None:
                COLOR = 'white'
        screen.fill(COLOR)

        if self.exit_button_show:
            self.eb.Update()
            if self.eb.Get_pressed():
                sys.exit()


        return running

    def EXIT(self,EXIT_BUTTON='esc') -> None:
        if keyboard.is_pressed(EXIT_BUTTON):
            sys.exit()
    
    def GET_WIN_SIZE(self) -> list[int,int]:
        return self.screen.get_size()

    def GET_WIN_WIDTH(self) -> int:
        return self.screen.get_size()[0]

    def GET_WIN_HEIGHT(self) -> int:
        return self.screen.get_size()[1]
        
    def GET_EVENT(self) -> list:
        events = pygame.event.get()
        return events

    class FUNCTION(object):
        def __init__(self,Name='function',functions=[]):
            self.name = Name
            self.functions = functions
        
        def LOOP(self) -> None:
            for i in range(len(self.functions)):
                self.functions[i]()

        def GET_NAME(self) -> str:
            return self.name

    def UPDATE_SCREEN(self) -> None:
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

    class UPDATE(object):
        def __init__(self) -> None:     
            pygame.display.flip()

        def GETTIME(self) -> None:
            global start_time
            start_time+=1
            return start_time    

        def SET_BG_COLOR(self,COLOR=None) -> None:
            if COLOR is None:
                COLOR = 'white'
            screen.fill(COLOR)

    class GL():
                                            def __init__():
                                                pass

                                            def GET_SHAPES():
                                                return [
                                                    'Rect',
                                                    'Circle',
                                                    'Ellips',
                                                    'Triangle',
                                                    'Line',
                                                    'lines',
                                                    'Poligon',
                                                    'Pixel',
                                                    'Arc'
                                                ]

                                            class Rect:
                                                def __init__(self,COLOR=(),POSITION=[],SIZE=[],THICKNESS=0,SURF=None,FUNCTION='none',R=0):
                                                    global SHAPE_COUNT
                                                    SHAPE_COUNT +=1


                                                    sh2 = 1
                                                    center =  [POSITION[0] + SIZE[0]/2,POSITION[1]+SIZE[1]/2]
                                                    pos=[POSITION[0],POSITION[1]]
                                                    up = [POSITION[0],POSITION[1]]
                                                    down = [POSITION[0]+SIZE[1],POSITION[1]+SIZE[0]]
                                                    right = [POSITION[0]+SIZE[1],POSITION[1]+SIZE[0]]
                                                    left = [POSITION[0],POSITION[1]]
                                                    self.pos = pos
                                                    self.size = SIZE

                                                    if SURF=='s' and type(SURF)==str:self.surf = screen
                                                    else:self.surf = SURF
                                                    
                                                    self.col = COLOR
                                                    self.obv_color = 'black'
                                                    self.sh = THICKNESS
                                                    self.sh2 = sh2
                                                    self.center = center    
                                                    self.up = up
                                                    self.down = down   
                                                    self.left = left 
                                                    self.right = right   

                                                    
                                                    
                                                    self.cant_pos = self.pos
                                                    self.cant_size = self.size
                                                         
                                                    if R>self.cant_size[0]/2 or R>self.cant_size[1]/2:  
                                                        self.r = self.size[0]/2 if self.size[0]<self.size[1] else self.size[1]/2
                                                        
                                                    else:
                                                        self.r = R

                                                    self.cant_pos[0]+=self.r
                                                    self.cant_pos[1]+=self.r
                                                    self.cant_size[0]-=self.r*2
                                                    self.cant_size[1]-=self.r*2
                                                    

                                                    self.DL_diagonal = math.sqrt(SIZE[0]**2+SIZE[1]**2)

                                                    if FUNCTION=='D':
                                                        rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                        pygame.draw.rect(self.surf,self.col,rect,self.sh)

                                                    elif FUNCTION[1]=='D':
                                                        col = [int(FUNCTION[3:6]),int(FUNCTION[7:10]),int(FUNCTION[11:14])]
                                                        sh2 = int(FUNCTION[15:len(FUNCTION)])
                                                        if col!=None:self.obv_color = col
                                                        if sh2!=None:self.sh2 = sh2
                                                        rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                        pygame.draw.rect(self.surf,self.col,rect,self.sh)     
                                                        pygame.draw.rect(self.surf,self.obv_color,rect,self.sh2)  

                                                    elif FUNCTION[0]=='O':
                                                        col = [int(FUNCTION[2:5]),int(FUNCTION[6:9]),int(FUNCTION[10:13])]
                                                        sh2 = int(FUNCTION[14:len(FUNCTION)])
                                                        if col!=[0,0,0]:self.obv_color = col
                                                        if sh2!=None:self.sh2 = sh2
                                                        rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                        pygame.draw.rect(self.surf,self.obv_color,rect,self.sh2)    
                                                    else:
                                                        pass  

                                                def FILL(self):
                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                    pygame.draw.rect(self.surf,self.col,rect,self.sh)
                                                    Display_init_.GL.Circle(self.col,self.cant_pos,self.r,0,self.surf,'D')
                                                    Display_init_.GL.Circle(self.col,[self.cant_pos[0]+self.cant_size[0],self.cant_pos[1]],self.r,0,self.surf,'D')
                                                    Display_init_.GL.Circle(self.col,[self.cant_pos[0]+self.cant_size[0],self.cant_pos[1]+self.cant_size[1]],self.r,0,self.surf,'D')
                                                    Display_init_.GL.Circle(self.col,[self.cant_pos[0],self.cant_pos[1]+self.cant_size[1]],self.r,0,self.surf,'D')

                                                    Display_init_.GL.Rect(self.col,[ self.pos[0],self.pos[1]-self.r ],[ self.size[0],self.size[1]+2*self.r ],0,self.surf,'D')
                                                    Display_init_.GL.Rect(self.col,[ self.pos[0]-self.r,self.pos[1] ],[ self.size[0]+2*self.r,self.size[1] ],0,self.surf,'D')

                                                def FILLOUT(self,COLOR=None,THICKNESS=None):
                                                    if COLOR!=None:self.obv_color = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                    pygame.draw.rect(self.surf,self.col,rect,self.sh)     
                                                    pygame.draw.rect(self.surf,self.obv_color,rect,self.sh2)  

                                                def OUTLINE(self,COLOR=None,THICKNESS=None):
                                                    if COLOR!=None:self.obv_color = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                    pygame.draw.rect(self.surf,self.obv_color,rect,self.sh2)   

                                                def POUTLINE(self,COLOR=None,THICKNESS=None,PLS=10):
                                                    if COLOR!=None:self.obv_color = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    Display_init_.GL.Dashed_line(self.obv_color,self.pos,[self.pos[0]+self.size[0],self.pos[1]],self.sh2,PLS,self.surf,'D')
                                                    Display_init_.GL.Dashed_line(self.obv_color,self.pos,[self.pos[0],self.pos[1]+self.size[1]],self.sh2,PLS,self.surf,'D')
                                                    Display_init_.GL.Dashed_line(self.obv_color,[self.pos[0],self.pos[1]+self.size[1]],[self.pos[0]+self.size[0],self.pos[1]+self.size[1]],self.sh2,PLS,self.surf,'D')
                                                    Display_init_.GL.Dashed_line(self.obv_color,[self.pos[0]+self.size[0],self.pos[1]],[self.pos[0]+self.size[0],self.pos[1]+self.size[1]],self.sh2,PLS,self.surf,'D')
                                                
                                                def FILLPOUT(self,COLOR=None,THICKNESS=None,PLS=20):
                                                    if COLOR!=None:self.obv_color = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                    pygame.draw.rect(self.surf,self.col,rect,self.sh)  
                                                    Display_init_.GL.Dashed_line(self.obv_color,self.pos,[self.pos[0]+self.size[0],self.pos[1]],self.sh2,PLS,self.surf,'D')
                                                    Display_init_.GL.Dashed_line(self.obv_color,self.pos,[self.pos[0],self.pos[1]+self.size[1]],self.sh2,PLS,self.surf,'D')
                                                    Display_init_.GL.Dashed_line(self.obv_color,[self.pos[0],self.pos[1]+self.size[1]],[self.pos[0]+self.size[0],self.pos[1]+self.size[1]],self.sh2,PLS,self.surf,'D')
                                                    Display_init_.GL.Dashed_line(self.obv_color,[self.pos[0]+self.size[0],self.pos[1]],[self.pos[0]+self.size[0],self.pos[1]+self.size[1]],self.sh2,PLS,self.surf,'D')

                                                def SET_SIZE(self,SIZE=[]):
                                                    self.size = SIZE

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.sh = THICKNESS

                                                def SET_COLOR(self,COLOR=()):
                                                    self.col = COLOR

                                                def SET_RADIUS(self,R):
                                                    

                                                    if R>self.cant_size[0]/2 or R>self.cant_size[1]/2:  
                                                        self.r = self.size[0]/2 if self.size[0]<self.size[1] else self.size[1]/2    
                                                    else:
                                                        self.r = R

                                                    #self.cant_pos[0]+=self.r
                                                    #self.cant_pos[1]+=self.r
                                                    #self.cant_size[0]-=self.r*2
                                                    #self.cant_size[1]-=self.r*2

                                                def GET_SIZE(self):
                                                    return self.size

                                                def GET_THICKNESS(self):
                                                    return self.sh

                                                def SET_OUTLINE_THICKNESS(self,THICKNESS):
                                                    self.sh2=THICKNESS

                                                def GET_CENTER(self):
                                                    return self.center

                                                def GET_SURF(self):
                                                    return self.surf

                                                def GET_OUTLINE_THICKNESS(self):
                                                    return self.sh2

                                                def X(self):
                                                    return self.pos[0]

                                                def Y(self):
                                                    return self.pos[1]

                                                def WIDTH(self):
                                                    return self.size[0]

                                                def HEIGHT(self):
                                                    return self.size[1]

                                                def SET_POSITION(self,POSITION = []):
                                                        if type(POSITION[0])==int:
                                                            self.pos[0]=POSITION[0]
                                                        elif type(POSITION[0])==str:
                                                            self.pos[0]+=int(POSITION[0][1])

                                                        if type(POSITION[1])==int:
                                                            self.pos[1]=POSITION[1]
                                                        elif type(POSITION[1])==str:
                                                            self.pos[1]+=int(POSITION[1][1])
                                                    
                                                def GET_POSITION(self):
                                                    return self.pos

                                                def __GL_type__(self,p=True):
                                                    if p:       print('Type --> ','GL_rect')
                                                    else:       return 'GL_rect'
                                                    
                                            class Poligon:
                                                def __init__(self,COLOR=(),POINTS=(),THICKNESS=0,SURF=None,FUNCTION='none'):
                                                    global SHAPE_COUNT
                                                    SHAPE_COUNT += 1

                                                    self.points = POINTS
                                                    self.col = COLOR
                                                    self.sh = THICKNESS
                                                    self.sh2 = 1

                                                    if SURF=='s' and type(SURF)==str:self.surf=screen
                                                    else:self.surf = SURF

                                                    self.obv_col = 'black'
                                                    if FUNCTION=='D':
                                                        pygame.draw.polygon(self.surf,self.col,self.points,self.sh)
                                                    elif FUNCTION[1]=='D':
                                                        COLOR = [int(FUNCTION[3:6]),int(FUNCTION[7:10]),int(FUNCTION[11:14])]
                                                        THICKNESS = int(FUNCTION[15:len(FUNCTION)])
                                                        pygame.draw.polygon(self.surf,self.col,self.points,self.sh)
                                                        if COLOR!=None:self.obv_col = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS
                                                        pygame.draw.polygon(self.surf,self.obv_col,self.points,self.sh2) 
                                                    elif FUNCTION[0]=='O':
                                                        COLOR = [int(FUNCTION[2:5]),int(FUNCTION[6:9]),int(FUNCTION[10:13])]
                                                        THICKNESS = int(FUNCTION[14:len(FUNCTION)])
                                                        if COLOR!=None:self.obv_col = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS
                                                        pygame.draw.polygon(self.surf,self.obv_col,self.points,self.sh2) 
                                                    else:
                                                        pass

                                                def FILL(self):
                                                    pygame.draw.polygon(self.surf,self.col,self.points,self.sh)

                                                def OUTLINE(self,COLOR=None,THICKNESS=None):
                                                    if COLOR!=None:self.obv_col = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    pygame.draw.polygon(self.surf,self.obv_col,self.points,self.sh2)

                                                def FILLOUT(self,COLOR=None,THICKNESS=None):
                                                    pygame.draw.polygon(self.surf,self.col,self.points,self.sh)
                                                    if COLOR!=None:self.obv_col = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    pygame.draw.polygon(self.surf,self.obv_col,self.points,self.sh2) 

                                                def GET_POINTS(self):
                                                    return self.points

                                                def GET_COLOR(self):
                                                    return self.col

                                                def GET_OUTLINE_COLOR(self):
                                                    return self.obv_col

                                                def GET_THICKNESS(self):
                                                    return self.sh

                                                def GET_OUTLINE_THICKNESS(self):
                                                    return self.sh2

                                                def GET_SURF(self):
                                                    return self.surf

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.sh = THICKNESS

                                                def SET_OUTLINE_THICKNESS(self,THICKNESS):
                                                    self.sh2 = THICKNESS

                                                def SET_OUTLINE_COLOR(self,COLOR=()):
                                                    self.obv_col = COLOR

                                                def SET_COLOR(self,COLOR=()):
                                                    self.col = COLOR

                                                def __GL_type__(self,p=True):
                                                    if p:       print('Type --> ','GL_poligon')
                                                    else:       return 'GL_poligon'

                                            class Circle:
                                                def __init__(self,COLOR=(),POSITION=[],RADIUS=0,THICKNESS=0,SURF=0,FUNCTION='none'):
                                                    global g_c_pos , g_c_rad , SHAPE_COUNT
                                                    SHAPE_COUNT += 1

                                                    center = [POSITION[0],POSITION[1]]
                                                    sh2 = 1
                                                    self.sh2 = sh2
                                                    self.col = COLOR
                                                    self.sh = THICKNESS
                                                    self.rad = RADIUS ; g_c_rad = self.rad
                                                    self.obv_col = (0,0,0)

                                                    if SURF=='s' and type(SURF)==str:self.surf=screen
                                                    else:self.surf = SURF

                                                    self.center = center
                                                    self.pos = POSITION ; g_c_pos = self.pos
                                                    up_cic = [POSITION[0],POSITION[1]-self.rad] ; self.up = up_cic
                                                    down_cic = [POSITION[0],POSITION[1]+self.rad] ; self.down = down_cic
                                                    left_cic = [POSITION[0]-self.rad,POSITION[1]] ; self.left = left_cic
                                                    right_cic = [POSITION[0]+self.rad,POSITION[1]] ; self.right = right_cic

                                                    if FUNCTION=='D':
                                                        pygame.draw.circle(self.surf,self.col,(self.pos[0],self.pos[1]),self.rad,self.sh)  
                                                    elif FUNCTION[1]=='D':
                                                        COLOR = [int(FUNCTION[3:6]),int(FUNCTION[7:10]),int(FUNCTION[11:14])]
                                                        THICKNESS = int(FUNCTION[15:len(FUNCTION)])
                                                        pygame.draw.circle(self.surf,self.col,(self.pos[0],self.pos[1]),self.rad,self.sh) 
                                                        if COLOR!=None:self.obv_col = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS  
                                                        pygame.draw.circle(self.surf,COLOR,(self.pos[0],self.pos[1]),self.rad,self.sh2)
                                                    elif FUNCTION[0]=='O':
                                                        COLOR = [int(FUNCTION[2:5]),int(FUNCTION[6:9]),int(FUNCTION[10:13])]
                                                        THICKNESS = int(FUNCTION[14:len(FUNCTION)])
                                                        if COLOR!=None:self.obv_col = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS
                                                        pygame.draw.circle(self.surf,COLOR,(self.pos[0],self.pos[1]),self.rad,self.sh2)
                                                    else:
                                                        pass
                                                        
                                                def FILL(self):
                                                    global g_c_pos
                                                    if g_c_pos!=None:self.pos = g_c_pos
                                                    pygame.draw.circle(self.surf,self.col,(self.pos[0],self.pos[1]),self.rad,self.sh)     

                                                def OUTLINE(self,COLOR=None,THICKNESS=None):
                                                    global g_c_pos
                                                    if g_c_pos!=None:self.pos = g_c_pos
                                                    if COLOR!=None:self.obv_col = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    pygame.draw.circle(self.surf,self.obv_col,(self.pos[0],self.pos[1]),self.rad,self.sh2)

                                                def FILLOUT(self,COLOR=None,THICKNESS=None):
                                                    global g_c_pos
                                                    if g_c_pos!=None:self.pos = g_c_pos
                                                    pygame.draw.circle(self.surf,self.col,(self.pos[0],self.pos[1]),self.rad,self.sh)
                                                    if COLOR!=None:self.obv_col = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    pygame.draw.circle(self.surf,self.obv_col,(self.pos[0],self.pos[1]),self.rad,self.sh2)  

                                                def SET_RADIUS(self,RADIUS):
                                                    self.rad = RADIUS

                                                def SET_COLOR(self,COLOR=()):
                                                    self.col = COLOR

                                                def GET_RADIUS(self):
                                                    return self.rad

                                                def GET_THICKNESS(self):
                                                    return self.sh

                                                def GET_CENTER(self):
                                                    return self.center

                                                def GET_SURF(self):
                                                    return self.surf

                                                def SET_OUTLINE_THICKNESS(self,sh2):
                                                    self.sh2 = sh2

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.sh=THICKNESS

                                                def GET_OUTLINE_THICKNESS(self):
                                                    return self.sh2

                                                class SET_POSITION():
                                                    def __init__(self,POSITION=[]):
                                                        global g_c_rad , g_c_pos
                                                        self.POSITION = POSITION
                                                        g_c_pos = [POSITION[0]+g_c_rad, POSITION[1]+g_c_rad]
                                                        up_cic = [POSITION[0],POSITION[1]-g_c_rad]
                                                        down_cic = [POSITION[0],POSITION[1]+g_c_rad]
                                                        left_cic = [POSITION[0]-g_c_rad,POSITION[1]]
                                                        right_cic = [POSITION[0]+g_c_rad,POSITION[1]]
                                                        self.up = up_cic
                                                        self.down = down_cic
                                                        self.left = left_cic
                                                        self.right = right_cic
                                                    def ON_CENTER(self):
                                                        global g_c_rad , g_c_pos
                                                        POSITION = self.POSITION
                                                        g_c_pos = POSITION
                                                        up_cic = [POSITION[0],POSITION[1]-g_c_rad]
                                                        down_cic = [POSITION[0],POSITION[1]+g_c_rad]
                                                        left_cic = [POSITION[0]-g_c_rad,POSITION[1]]
                                                        right_cic = [POSITION[0]+g_c_rad,POSITION[1]]
                                                        self.up = up_cic
                                                        self.down = down_cic
                                                        self.left = left_cic
                                                        self.right = right_cic

                                                def GET_POSITION(self):
                                                    return self.pos

                                                def __GL_type__(self,p=True):
                                                    if p:       print('Type --> ','GL_circle')
                                                    else:       return 'GL_circle'

                                            class Ellips:
                                                def __init__(self,COLOR=(),POSITION=[],SIZE=[],THICKNESS=0,SURF=0,FUNCTION='none'):
                                                    global g_e_size , g_e_pos , SHAPE_COUNT
                                                    SHAPE_COUNT += 1

                                                    center =  [POSITION[0] + SIZE[0]/2,POSITION[1] + SIZE[1]/2]
                                                    
                                                    self.sh2 = 1
                                                    self.sh = THICKNESS
                                                    self.center = center
                                                    self.size = SIZE ; g_e_size = self.size
                                                    self.col = COLOR
                                                    self.obv_color = 'black'
                                                    self.pos = POSITION ; g_e_pos = self.pos
                                                    

                                                    if SURF=='s' and type(SURF)==str:self.surf=screen
                                                    else:self.surf = SURF

                                                    el_up = [POSITION[0]+SIZE[0]/2,POSITION[1]] ; self.up = el_up
                                                    el_down = [POSITION[0]+SIZE[0]/2,POSITION[1]+SIZE[1]] ; self.down = el_down
                                                    el_left = [POSITION[0],POSITION[1]+SIZE[1]/2] ; self.left = el_left
                                                    el_right = [POSITION[0]+SIZE[0],POSITION[1]+SIZE[1]/2] ; self.right = el_right
                                                    
                                                    if FUNCTION=='D':    
                                                        if g_e_pos!=None:self.pos = g_e_pos
                                                        rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                        pygame.draw.ellipse(self.surf,self.col,rect,self.sh)
                                                    elif FUNCTION[1]=='D':
                                                        COLOR = [int(FUNCTION[3:6]),int(FUNCTION[7:10]),int(FUNCTION[11:14])]
                                                        THICKNESS = int(FUNCTION[15:len(FUNCTION)])
                                                        if g_e_pos!=None:self.pos = g_e_pos

                                                        rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])   
                                                        pygame.draw.ellipse(self.surf,self.col,rect,self.sh)

                                                        if COLOR!=None:self.obv_color = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS

                                                        rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1]) 
                                                        pygame.draw.ellipse(self.surf,self.obv_color,rect,self.sh2)
                                                    elif FUNCTION[0]=='O':
                                                        COLOR = [int(FUNCTION[2:5]),int(FUNCTION[6:9]),int(FUNCTION[10:13])]
                                                        THICKNESS = int(FUNCTION[14:len(FUNCTION)])
                                                        if COLOR!=None:self.obv_color = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS
                                                        if g_e_pos!=None:self.pos = g_e_pos

                                                        rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                        pygame.draw.ellipse(self.surf,self.obv_color,rect,self.sh2)
                                                    else:
                                                        pass

                                                def FILL(self):
                                                    global g_e_pos
                                                    if g_e_pos!=None:self.pos = g_e_pos
                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                    pygame.draw.ellipse(self.surf,self.col,rect,self.sh)

                                                def OUTLINE(self,COLOR=None,THICKNESS=None):
                                                    global g_e_pos
                                                    if COLOR!=None:self.obv_color = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    if g_e_pos!=None:self.pos = g_e_pos

                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
                                                    pygame.draw.ellipse(self.surf,self.obv_color,rect,self.sh2)

                                                def FILLOUT(self,COLOR=None,THICKNESS=None):
                                                    global g_e_pos
                                                    if g_e_pos!=None:self.pos = g_e_pos

                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])   
                                                    pygame.draw.ellipse(self.surf,self.col,rect,self.sh)

                                                    if COLOR!=None:self.obv_color = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS

                                                    rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1]) 
                                                    pygame.draw.ellipse(self.surf,self.obv_color,rect,self.sh2)

                                                def SET_SIZE(self,SIZE=[]):
                                                    self.size = SIZE

                                                def GET_CENTER(self):
                                                    return self.center

                                                def GET_THICKNESS(self):
                                                    return self.sh

                                                def GET_SURF(self):
                                                    return self.surf

                                                def SET_COLOR(self,COLOR=()):
                                                    self.col = COLOR

                                                def GET_SIZE(self):
                                                    return self.size

                                                def GET_OUTLINE_THICKNESS(self):
                                                    return self.sh2

                                                def SET_OUTLINE_THICKNESS(self,OUTLINE_THICKNESS):
                                                    self.sh2 = OUTLINE_THICKNESS

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.sh = THICKNESS

                                                def SET_OUTLINE_COLOR(self,OUTLINE_COLOR):
                                                    self.obv_col = OUTLINE_COLOR
                                                    
                                                class SET_POSITION():
                                                    def __init__(self,POSITION=[]):
                                                        global g_e_pos , g_e_size
                                                        self.POSITION = POSITION
                                                        g_e_pos = POSITION

                                                        el_up = [POSITION[0]+g_e_size[0]/2,POSITION[1]]
                                                        el_down = [POSITION[0]+g_e_size[0]/2,POSITION[1]+g_e_size[1]]
                                                        el_left = [POSITION[0],POSITION[1]+g_e_size[1]/2]
                                                        el_right = [POSITION[0]+g_e_size[0],POSITION[1]+g_e_size[1]/2]
                                                        self.up = el_up
                                                        self.down = el_down
                                                        self.left = el_left
                                                        self.right = el_right

                                                    def ON_CENTER(self):
                                                        global g_e_pos
                                                        POSITION = self.POSITION
                                                        g_e_pos = [POSITION[0]-g_e_size[0]/2,POSITION[1]-g_e_size[1]/2]

                                                        el_up = [POSITION[0]+g_e_size[0]/2,POSITION[1]]
                                                        el_down = [POSITION[0]+g_e_size[0]/2,POSITION[1]+g_e_size[1]]
                                                        el_left = [POSITION[0],POSITION[1]+g_e_size[1]/2]
                                                        el_right = [POSITION[0]+g_e_size[0],POSITION[1]+g_e_size[1]/2]
                                                        self.up = el_up
                                                        self.down = el_down
                                                        self.left = el_left
                                                        self.right = el_right
                                                def __GL_type__(self,p=True):
                                                    if p:       print('Type --> ','GL_ellips')
                                                    else:       return 'GL_ellips'
                                                    
                                            class Triangl:
                                                def __init__(self,COLOR=(),POSITION_1=[],POSITION_2=[],POSITION_3=[],THICKNESS=0,SURF=None,FUNCTION=None):  
                                                    global SHAPE_COUNT
                                                    SHAPE_COUNT += 1


                                                    self.sh2 = 1
                                                    self.col = COLOR
                                                    self.pos1 = POSITION_1
                                                    self.pos2 = POSITION_2
                                                    self.pos3 = POSITION_3
                                                    self.poses = [self.pos1,self.pos2,self.pos3]
                                                    self.sh = THICKNESS
                                                    self.obv_col = 'black'

                                                    if SURF=='s' and type(SURF)==str:self.surf = screen
                                                    else:self.surf = SURF

                                                    if FUNCTION==None:pass
                                                    elif FUNCTION=='D':

                                                        pygame.draw.polygon(
                                                            self.surf,
                                                            self.col,
                                                            [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                            self.sh)

                                                    elif FUNCTION[1]=='D':
                                                        COLOR = [int(FUNCTION[3:6]),int(FUNCTION[7:10]),int(FUNCTION[11:14])]
                                                        THICKNESS = int(FUNCTION[15:len(FUNCTION)])
                                                        if COLOR!=None:self.obv_col = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS
                                                        pygame.draw.polygon(
                                                            self.surf,
                                                            self.col,
                                                            [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                            self.sh)
                                                        pygame.draw.polygon(
                                                            self.surf,
                                                            self.obv_col,
                                                            [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                            self.sh2)
                                                    elif FUNCTION[0]=='O':
                                                        COLOR = [int(FUNCTION[2:5]),int(FUNCTION[6:9]),int(FUNCTION[10:13])]
                                                        THICKNESS = int(FUNCTION[14:len(FUNCTION)])
                                                        if COLOR!=None:self.obv_col = COLOR
                                                        if THICKNESS!=None:self.sh2 = THICKNESS
                                                        pygame.draw.polygon(
                                                            self.surf,
                                                            self.obv_col,
                                                            [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                            self.sh2) 
                                                    else:
                                                        pass  

                                                def FILL(self):
                                                    pygame.draw.polygon(
                                                        self.surf,
                                                        self.col,
                                                        [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                        self.sh)

                                                def OUTLINE(self,COLOR=None,THICKNESS=None):
                                                    if COLOR!=None:self.obv_col = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    pygame.draw.polygon(
                                                        self.surf,
                                                        self.obv_col,
                                                        [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                        self.sh2)

                                                def FILLOUT(self,COLOR=None,THICKNESS=None):
                                                    if COLOR!=None:self.obv_col = COLOR
                                                    if THICKNESS!=None:self.sh2 = THICKNESS
                                                    pygame.draw.polygon(
                                                        self.surf,
                                                        self.col,
                                                        [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                        self.sh)
                                                    pygame.draw.polygon(
                                                        self.surf,
                                                        self.obv_col,
                                                        [(self.pos1[0],self.pos1[1]),(self.pos2[0],self.pos2[1]),(self.pos3[0],self.pos3[1])],
                                                        self.sh2)

                                                def GET_THICKNESS(self):
                                                    return self.sh

                                                def GET_OUTLINE_THICKNESS(self):
                                                    return self.sh2

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.sh = THICKNESS

                                                def SET_OUTLINE_THICKNESS(self,THICKNESS):
                                                    self.sh2 = THICKNESS

                                                def SET_COLOR(self,COLOR=()):
                                                    self.col = COLOR

                                                def GET_COLOR(self):
                                                    return self.col

                                                def GET_OUTLINE_COLOR(self):
                                                    return self.obv_col

                                                def SET_POSITIONS(self,POSITIONS=[]):
                                                    self.poses = POSITIONS
                                                    self.pos1 = POSITIONS[0]
                                                    self.pos2 = POSITIONS[1]
                                                    self.pos3 = POSITIONS[2]

                                                def SET_POSITION_1(self,POSITION=[]):
                                                    self.pos1 = POSITION

                                                def SET_POSITION_2(self,POSITION=[]):
                                                    self.pos2 = POSITION

                                                def SET_POSITION_3(self,POSITION=[]):
                                                    self.pos3 = POSITION

                                                def GET_POSITION(self):
                                                    return self.poses

                                                def GET_POSITION_1(self):
                                                    return self.pos1

                                                def GET_POSITION_2(self):
                                                    return self.pos2

                                                def GET_POSITION_3(self):
                                                    return self.pos3

                                                def __GL_type__(self,p=True):
                                                    if p:       print('Type --> ','GL_triangl')
                                                    else:       return 'GL_triangl'

                                            class Line:
                                                def __init__(self,COLOR=(),START_POSITION=[],END_POSITION=[],THICKNESS=1,SURF=None,TYPE='R',FUNCTION='none'):
                                                    global SHAPE_COUNT
                                                    SHAPE_COUNT += 1

                                                    xcnt = START_POSITION[0]+(END_POSITION[0]-START_POSITION[0])/2
                                                    ycnt = START_POSITION[1]+(END_POSITION[1]-START_POSITION[1])/2

                                                    center = [xcnt,ycnt]
                                                    self.x_center = xcnt
                                                    self.y_center = ycnt
                                                    self.center = center
                                                    self.col = COLOR
                                                    self.start_pos = START_POSITION
                                                    self.end_pos = END_POSITION
                                                    self.sh = THICKNESS
                                                    self.type = TYPE
                                                    self.poses = [self.start_pos,self.end_pos]


                                                    if SURF=='s' and type(SURF)==str:self.surf = screen
                                                    else:self.surf = SURF

                                                    if FUNCTION=='D':
                                                        pygame.draw.line( 
                                                        self.surf,
                                                        self.col,
                                                        (self.start_pos[0],self.start_pos[1]),
                                                        (self.end_pos[0],self.end_pos[1]),
                                                        self.sh
                                                        )
                                                        if self.type == 'S' or self.type == 's':
                                                            
                                                            Display_init_.GL.Circle(self.col,[self.start_pos[0]+self.sh/12-1,self.start_pos[1]+1]
                                                            ,self.sh/2,0,self.surf).FILL()
                                                            Display_init_.GL.Circle(self.col,[self.end_pos[0]+self.sh/12-1,self.end_pos[1]+1]
                                                            ,self.sh/2,0,self.surf).FILL()
                                                        elif self.type == 'r' or self.type == 'R':
                                                            pass
                                                        else:
                                                            print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                                                            print(colorama.Fore.YELLOW+'(none) type detected'+colorama.Fore.RESET)
                                                            print(colorama.Fore.YELLOW+'Uses s(S) or r(R)'+colorama.Fore.RESET)
                                                            sys.exit()
                                                    else:
                                                        pass

                                                    

                                                def OUTLINE(self):
                                                    pygame.draw.line( 
                                                        self.surf,
                                                        self.col,
                                                        (self.start_pos[0],self.start_pos[1]),
                                                        (self.end_pos[0],self.end_pos[1]),
                                                        self.sh
                                                    )
                                                    if self.type == 'S' or self.type == 's':
                                                        Display_init_.GL.Circle(self.col,[self.start_pos[0]+self.sh/12-1,self.start_pos[1]+1]
                                                        ,self.sh/2,0,self.surf).FILL()
                                                        Display_init_.GL.Circle(self.col,[self.end_pos[0]+self.sh/12-1,self.end_pos[1]+1]
                                                        ,self.sh/2,0,self.surf).FILL()
                                                    elif self.type == 'r' or self.type == 'R':
                                                        pass
                                                    else:
                                                        print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                                                        print(colorama.Fore.YELLOW+'(none) type detected'+colorama.Fore.RESET)
                                                        print(colorama.Fore.YELLOW+'Uses s(S) or r(R)'+colorama.Fore.RESET)
                                                        sys.exit()

                                                def SET_COLOR(self,COLOR):
                                                    self.col = COLOR

                                                def SET_TYPE(self,TYPE=''):
                                                    self.type = TYPE

                                                def SET_POSITIONS(self,POSITIONS=[]):
                                                    self.poses = POSITIONS
                                                    self.start_pos = POSITIONS[0]
                                                    self.end_pos = POSITIONS[1]

                                                def SET_START_POSITION(self,POSITION=[]):
                                                    self.start_pos = POSITION

                                                def SET_END_POSITION(self,POSITION=[]):
                                                    self.end_pos = POSITION

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.sh = THICKNESS

                                                def GET_COLOR(self):
                                                    return self.col

                                                def GET_POSITIONS(self):
                                                    return self.poses

                                                def GET_START_POSITION(self):
                                                    return self.start_pos

                                                def GET_END_POSITION(self):
                                                    return self.end_pos

                                                def GET_THICKNESS(self):
                                                    return self.sh

                                                def __GL_type__(self,p=True):
                                                    if p:       print('Type --> ','GL_line')
                                                    else:       return 'GL_line'

                                            class Dashed_line:
                                                def __init__(self,COLOR=(),START_POSITION=[],END_POSITION=[],THICKNESS=1,DASH_LENGTH=10,SURF=None,FUNCTION='none'):
                                                    global SHAPE_COUNT
                                                    SHAPE_COUNT +=1


                                                    self.COLOR = COLOR
                                                    self.START_POSITION = START_POSITION
                                                    self.END_POSITION = END_POSITION
                                                    self.THICKNESS = THICKNESS
                                                    self.DASH_LENGTH = DASH_LENGTH
                                                    
                                                    if SURF=='s' and type(SURF)==str:self.SURF = screen
                                                    elif type(SURF)==str and SURF!='s':
                                                        print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                                                        print(colorama.Fore.YELLOW+'None surf'+colorama.Fore.RESET)
                                                    else:self.SURF = SURF

                                                    

                                                    self.FUNCTION = FUNCTION

                                                    if self.FUNCTION=='D':
                                                        x1, y1 = self.START_POSITION
                                                        x2, y2 = self.END_POSITION
                                                        dl = self.DASH_LENGTH

                                                        if (x1 == x2):
                                                            ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
                                                            xcoords = [x1] * len(ycoords)
                                                        elif (y1 == y2):
                                                            xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
                                                            ycoords = [y1] * len(xcoords)
                                                        else:
                                                            a = abs(x2 - x1)
                                                            b = abs(y2 - y1)
                                                            c = round(math.sqrt(a**2 + b**2))
                                                            dx = dl * a / c
                                                            dy = dl * b / c

                                                            xcoords = [x for x in numpy.arange(x1, x2, dx if x1 < x2 else -dx)]
                                                            ycoords = [y for y in numpy.arange(y1, y2, dy if y1 < y2 else -dy)]

                                                        next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
                                                        last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
                                                        for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
                                                            start = (round(x1), round(y1))
                                                            end = (round(x2), round(y2))
                                                            Display_init_.GL.Line(self.COLOR, start, end,self.THICKNESS,self.SURF,'R','D')
                                                    else:
                                                        pass
                                                    
                                                def OUTLINE(self):
                                                    x1, y1 = self.START_POSITION
                                                    x2, y2 = self.END_POSITION
                                                    dl = self.DASH_LENGTH

                                                    if (x1 == x2):
                                                        ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
                                                        xcoords = [x1] * len(ycoords)
                                                    elif (y1 == y2):
                                                        xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
                                                        ycoords = [y1] * len(xcoords)
                                                    else:
                                                        a = abs(x2 - x1)
                                                        b = abs(y2 - y1)
                                                        c = round(math.sqrt(a**2 + b**2))
                                                        dx = dl * a / c
                                                        dy = dl * b / c

                                                        xcoords = [x for x in numpy.arange(x1, x2, dx if x1 < x2 else -dx)]
                                                        ycoords = [y for y in numpy.arange(y1, y2, dy if y1 < y2 else -dy)]

                                                    next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
                                                    last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
                                                    for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
                                                        start = (round(x1), round(y1))
                                                        end = (round(x2), round(y2))
                                                        Display_init_.GL.Line(self.COLOR, start, end,self.THICKNESS,self.SURF,'R','D')

                                                def GET_START_POSITION(self):
                                                    return self.START_POSITION

                                                def GET_END_POSITION(self):
                                                    return self.END_POSITION

                                                def GET_THICKNESS(self):
                                                    return self.THICKNESS

                                                def GET_DASH_LENGTH(self):
                                                    return self.DASH_LENGTH

                                                def GET_SURF(self):
                                                    return self.SURF

                                                def GET_COLOR(self):
                                                    return self.COLOR

                                                def SET_COLOR(self,COLOR=()):
                                                    self.COLOR = COLOR

                                                def SET_START_POSITION(self,POSITION=[]):
                                                    self.START_POSITION = POSITION

                                                def SET_END_POSITION(self,POSITION=[]):
                                                    self.END_POSITION = POSITION

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.THICKNESS = THICKNESS

                                                def SET_DASH_LENGTH(self,DASH_LENGTH):
                                                    self.DASH_LENGTH = DASH_LENGTH

                                                def __GL_type__(self,p=True):
                                                    if p:       print('Type --> ','GL_dashed_line')
                                                    else:       return 'GL_dashed_line'

                                            class Liness:
                                                def __init__(self,col=(),points=(),snap=False,sh=1,surf=0):
                                                    rectt = [points,col,snap,sh]

                                                    self.col = col
                                                    self.points = points
                                                    self.snap = snap
                                                    self.sh = sh
                                                    self.surf = surf
                                                    self.rectt = rectt  
                                                def Draw(self):
                                                    pygame.draw.lines( 
                                                        self.surf,
                                                        self.col,
                                                        self.snap,
                                                        self.points,
                                                        self.sh
                                                    )
                                                def Get_points_ind(self,index=0,cor=None):
                                                    if cor == None:
                                                        return self.points[index]
                                                    elif cor == "x" or cor == "X":
                                                        return self.points[index][0]
                                                    elif cor == "y" or cor == "Y":
                                                        return self.points[index][1]
                                                    else:
                                                        print(colorama.Fore.RED+'Error'+colorama.Fore.RESET)
                                                        print(colorama.Fore.YELLOW+'None 2D cords detected.'+colorama.Fore.RESET)
                                                        sys.exit()
                                                def Get_points(self):
                                                    return self.points
                                                def Get_col(self):
                                                    return self.col
                                                def Get_sh(self):
                                                    return self.sh
                                                def Get_snap(self):
                                                    return self.snap
                                                def Set_col(self,col):
                                                    self.col = col
                                                def Set_sh(self,sh2):
                                                    self.sh = sh2

                                            class Pixel:
                                                def __init__(self,COLOR=(),POSITION=[],THICKNESS=1,SURF=None,FUNCTION='none'):    
                                                    global SHAPE_COUNT
                                                    SHAPE_COUNT += 1

                                                    self.pos = POSITION
                                                    self.col = COLOR
                                                    self.sh = THICKNESS

                                                    if SURF=='s' and type(SURF)==str:self.surf = screen
                                                    else:self.surf = SURF

                                                    if FUNCTION=='D':
                                                        pygame.draw.line(   
                                                        self.surf,
                                                        self.col,
                                                        (self.pos[0],self.pos[1]),
                                                        (self.pos[0],self.pos[1]),
                                                        self.sh
                                                    )
                                                    else:
                                                        pass

                                                def OUTLINE(self):
                                                    pygame.draw.line(   
                                                        self.surf,
                                                        self.col,
                                                        (self.pos[0],self.pos[1]),
                                                        (self.pos[0],self.pos[1]),
                                                        self.sh
                                                    )

                                                def GET_POSITION(self):
                                                    return self.pos

                                                def GET_COLOR(self):
                                                    return self.col

                                                def GET_THICKNESS(self):
                                                    return self.sh

                                                def SET_COLOR(self,COLOR=()):
                                                    self.col = COLOR

                                                def SET_POSITION(self,POSITION=[]):
                                                    self.pos = POSITION

                                                def SET_THICKNESS(self,THICKNESS):
                                                    self.sh = THICKNESS

                                            class Arc:
                                                def __init__(self,COLOR=(),POSITION=[],START_ANGLE=0,STOP_ANGLE=0,RADIUS=1,THICKNESS=1,ST='-',SURF=None):
                                                    grad = 56.5
                                                    ugl1 = START_ANGLE/grad
                                                    

                                                    self.grad = grad
                                                    self.ugl = ugl1
                                                    self.start_angl = START_ANGLE
                                                    self.end_angl = STOP_ANGLE
                                                    self.col = COLOR
                                                    self.pos = POSITION
                                                    self.rad = RADIUS
                                                    self.sh = THICKNESS
                                                    self.st = ST
                                                    self.surf = SURF
                                
                                                def Draw(self):
                                                    
                                                    for l in range(int(self.end_angl*3.5)):
                                                        if self.st=='-': self.ugl+=0.005
                                                        elif self.st=='+': self.ugl-=0.005
                                                        else:
                                                            print('no positions detected.')
                                                            sys.exit()
                                                        for i in range(0,self.rad,2): 
                                                            xl=self.pos[0]+i*math.sin(self.ugl);yl=self.pos[1]+i*math.cos(self.ugl)
                                                            if i == self.rad - self.sh:
                                                                xpos = xl;ypos = yl
                                                        pygame.draw.line(self.surf,
                                                                        self.col,
                                                                        [xl,yl],
                                                                        [xpos,ypos],
                                                                        5)   

                                                def Set_end_ugl(self,ugl):
                                                    self.end_angl = ugl  

                                                def Set_start_ugl(self,ugl):
                                                    self.start_angl = ugl

                                                def Set_st(self,st='-'):
                                                    self.st = st     

                                                def Get_st(self):
                                                    return self.st

                                                def Get_col(self):
                                                    return self.col

                                                def Set_col(self,col):
                                                    self.col = col

                                                def Set_rad(self,rad):
                                                    self.rad = rad

                                                def Get_rad(self):
                                                    return self.rad

                                                def Set_sh(self,sh2):
                                                    self.sh = sh2

                                                def Get_sh(self):
                                                    return self.sh


Open_rw = False
Open_fw = False
Open_nw = False

Open_w : Display_init_

def __GL_win_init__(type = 'n'):
    global Open_nw , Open_fw , Open_rw , Open_w
    if type == 'n':
        Open_w = Open_nw = Display_init_(flags=D_Nones)
    elif type == 'f':
        Open_w = Open_fw = Display_init_(flags=D_Full)
    elif type == 'r':
        Open_w = Open_rw = Display_init_(flags=D_Resize)

def __GL_set_open_window_size__(SIZE : list = []):
    global Open_nw, Open_rw , Open_w
    if Open_nw != False:
        Open_w = Open_nw = Display_init_(size=SIZE)
    if Open_rw != False:
        Open_w = Open_rw = Display_init_(flags=D_Resize,size=SIZE)

def __GL_set_open_window_capture__(NAME : str = ''):
    global Open_rw, Open_nw, Open_fw
    Open_w.SET_CAPTION(NAME)
    if Open_nw != False:
        Open_nw.SET_CAPTION(NAME)
        
    if Open_rw != False:
        Open_rw.SET_CAPTION(NAME)
        
    if Open_fw != False:
        Open_fw.SET_CAPTION(NAME)
        


# 11 Sprites
class Sprites_(Surfases_):
    def __init__(self,file='',pos=[]):
        self.img = pygame.image.load(file)
        self.pos = pos
           
    def Draw(self):
        self.rect = self.img.get_rect(bottomright=(self.pos[0]+self.img.get_width(),self.pos[1]+self.img.get_height())) 
        screen.blit(self.img,self.rect)

    def Set_pos(self,pos=[]):
        self.pos = pos

    def Scale(self,size=[]):
        self.img = pygame.transform.scale(self.img,(size[0],size[1]))
    
    def Rotate(self,ugl):
        self.img = pygame.transform.rotate(self.start_img,ugl)

    def Save(self,file_name = ''):
        pygame.image.save(self.img,file_name)

    def Get_pos(self):
        return self.pos




# 13 Graph
class Graphick_:
    def __init__(self):
        pass
    def SETcirclGRAPH(self,col=[],znh=[]):
        pit = [col,znh]
        return pit
    def DRcirclGRAPH_2D(self,r=1,xp=1,yp=1,grph=[]):
        kf = 0
        ugl = 1;ugl1=1
        c=r
        g1 = 0
        for g in range(len(grph[0])):
            kf = kf + grph[0][g]

        for g in range(len(grph[1])):
            coll = grph[1][g]
            ugl = ugl1
            for n in range(int(700/kf*grph[0][g1])):
                xl = xp + c * math.sin(ugl)
                yl = yp + c * math.cos(ugl)
                ugl+=0.009
                pygame.draw.line(screen,coll,(xp,yp),(xl,yl),4)
                ugl1 = ugl


            g1 +=1
# 14 Widgets
class Widgets_:
    def __init__(self,):
        self.widgets = [
            'Slider',
            'Button',
            'Toggle',
            'TextBox',
            'DropDown',
            'ProgrsBar'
        ]      
        
    def Get_Widget_in_base(self,type,id=''):
        if type == WT_DropDown: return DropDowns_base[id]
        elif type == WT_Button: return Buttons_base[id]
        elif type == WT_ProgressBar: return ProgressBar_base[id]
        elif type == WT_Slider: return Sliders_base[id]
        elif type == WT_Toggle: return Toggles_base[id]
        elif type == WT_TextBox: return TextBoxs_base[id]

    def Get_Print_Widgets(self,index=None):
        if index is None:
            for i in range(len(self.widgets)):
                print(colorama.Fore.RED + f'[ {i+1} ] - ' + colorama.Fore.RESET,end='')
                print(colorama.Fore.YELLOW + self.widgets[i] + colorama.Fore.RESET)

        elif index is not None:
            print(self.widgets)

    def Get_Widgets(self):
        return self.widgets

    class Sliders:
        def __init__(self,  plane :                         Display_init_,
                            pos :                           list = [],
                            len :                           int = 100,
                            size:                           int = 10,
                            min :                           int = 0,
                            max :                           int = 100,
                            step :                          int = 1,
                            color_slider :                  Color_ = Color_._rgb(0,0,0).COLOR,
                            handl_color :                   Color_ = Color_._rgb(30,30,30).COLOR,
                            handl_radius :                  int = 10,
                            curved :                        bool = True,
                            id :                            str = ''
                            ):
            
            self.id = id
            if self.id == '':
                self.id = 'NONE'
            self.plane = plane
            self.pos = pos
            self.posx = pos[0]
            self.posy = pos[1]
            self.len = len
            self.curved = curved
            self.size = size
            self.min = min
            self.max = max
            self.step = step
            self.color_slider = color_slider
            self.handl_color = handl_color
            self.handl_radius = handl_radius

            slide = Slider(self.plane,
                            self.posx,
                            self.posy,
                            self.len,
                            self.size,
                            min = self.min,
                            max = self.max,
                            step = self.step,
                            colour = self.color_slider,
                            handleColour = self.handl_color,
                            handleRadius = self.handl_radius,
                            curved = self.curved)
            self.slide = slide

        

        def Get_value(self):
            val = self.slide.getValue()
            return val

        def Update(self):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame_widgets.update(events)
            

        def Wiew_Text_Value(self,glass=True,text_color='white',font = 'arial',size=20,plane = 0):
            cond = round( self.max/self.len ,5)
            

            text = Text_(
                TEXT = f'{self.slide.getValue()}',
                GLASS = glass,
                COLOR = text_color,
                FONT=font,
                SIZE = size,
                POSITION = [
                    (self.pos[0]+((self.slide.getValue())/cond)-5),
                    self.pos[1]+self.size+self.handl_radius
                    ],
                SURF=plane
                
            )
            if int(text.text)>=10 and int(text.text)<100:
                text.SET_POS([
                    text.GET_POSITION()[0]-5,
                    text.GET_POSITION()[1]
                ])
            elif int(text.text)>=100 and int(text.text)<1000:
                text.SET_POS([
                    text.GET_POSITION()[0]-10,
                    text.GET_POSITION()[1]
                ])
            elif int(text.text)>=1000:
                text.SET_POS([
                    text.GET_POSITION()[0]-15,
                    text.GET_POSITION()[1]
                ])
            else:
                pass
            text.RENDER()

        def DSave(self,filename,open_type = 'a'):
            if open_type == 'a':text = open(filename,'a')
            elif open_type == 'w':text = open(filename,'w')

            
            text.write('Type [Slider] ; ID == '+self.id+'\n')
            text.write(f'|  Position [ {self.posx} : {self.posy} ]\n')
            text.write(f'|  Size [ {self.len} : {self.size} ]\n')
            text.write(f'|  Min [ {self.min} ]\n')
            text.write(f'|  Max [ {self.max} ]\n')
            text.write(f'|  Step [ {self.step} ]\n')
            text.write(f'|  Curved [ {str(self.curved)} ]\n')
            text.write(f'|  Handle radius [ {self.handl_radius} ]\n')
            text.write(f'|  Colors :\n')
            text.write(f'|     | Slider color rgb{self.color_slider} \n')
            text.write(f'|     | Handle color rgb{self.handl_color} \n')
            text.write('\n')

            text.close()
            os.system('cls')
            print(Terminal_Colorized_().Stylezate('Save',Terminal_Colorized_().t_green))

        def Set_pos(self,pos=[]):
            self.pos = pos
            self.posx = pos[0]
            self.posy = pos[1]
            self.slide.setX(pos[0])
            self.slide.setY(pos[1])

        def Set_posx(self,x):
            self.posx = x
            self.slide.setX(x)

        def Set_posy(self,y):
            self.posy = y
            self.slide.setY(y)

        def Set_width(self,width):
            self.len = width
            self.slide.setWidth(width)

        def Set_height(self,height):
            self.size = height
            self.slide.setHeight(height)

        def Set_size(self,size=[]):
            self.size = size[1]
            self.len = size[0]
            self.slide.setHeight(size[1])
            self.slide.setWidth(size[0])

        def Hide(self):
            self.slide.hide()

        def Show(self):
            self.slide.show()

        def Set_value(self,value):
            self.slide.setValue(value)

        def Set_height(self,height):
            self.slide.setHeight(height)
        
        def Set_width(self,width):
            self.slide.setWidth(width)

        def Get_curved(self):
            return self.curved

        def Get_pos(self):
            return self.pos

        def Get_posx(self):
            return self.posx

        def Get_posy(self):
            return self.posy

        def Get_size(self):
            return self.size

        def Get_len(self):
            return self.len

        def Get_value(self):
            return self.slide.getValue()

        def Get_min(self):
            return self.min

        def Get_max(self):
            return self.max

        def Get_step(self):
            return self.step

        def Get_slider_color(self):
            return self.color_slider

        def Get_handl_color(self):
            return self.handl_color

        def Get_handl_radius(self):
            return self.handl_radius

        def Disable(self):
            self.slide.disable()

        def Enable(self):
            self.slide.enable()

        def Set_orintation(self,orint):
            self.slide.vertical = orint

        def Get_selected(self):
            return self.slide.selected

    class TextBoxs:
        def __init__(self,  plane :                         Display_init_,
                            pos :                           list = [],
                            size :                          list = [],
                            font_size :                     int = 30,
                            border_color :                  Color_ = Color_._rgb(0,0,0).COLOR,
                            text_color :                    Color_ = Color_._rgb(0,0,0).COLOR,
                            onSub :                         list = None,
                            radius :                        int = 1,
                            border_size :                   int = 5,
                            id :                            str = ''
                            ):

            self.id = id
            if self.id == '':
                self.id = 'NONE'
            self.plane = plane
            self.pos = pos
            self.size = size
            self.width = size[0]
            self.height = size[1]
            self.font_size = font_size
            self.border_color = border_color
            self.text_color = text_color
            self.radius = radius
            self.border_size = border_size
            self.posx = self.pos[0]
            self.posy = self.pos[1]
            

            tb = TextBox(self.plane,
                            self.posx,self.posy,
                            self.width,self.height,
                            fontSize = self.font_size,
                            borderColour = self.border_color,
                            textColour = text_color,
                            onSubmit = onSub,
                            radius = self.radius,
                            borderThickness = self.border_size)
            self.tb = tb
            self.text = self.tb.getText()

        def DSave(self,filename,open_type = 'a'):
            if open_type == 'a':text = open(filename,'a')
            elif open_type == 'w':text = open(filename,'w')

            
            text.write('Type [TextBox] ; ID == '+self.id+'\n')
            text.write(f'|  Position [ {self.posx} : {self.posy} ]\n')
            text.write(f'|  Size [ {self.size[0]} : {self.size[1]} ]\n')
            text.write(f'|  Font size [ {self.font_size} ]\n')
            text.write(f'|  Radius [ {self.radius} ]\n')
            text.write(f'|  Text [ {self.text} ]\n')
            text.write(f'|  Border size [ {self.border_size} ]\n')
            text.write(f'|  Colors :\n')
            text.write(f'|     | Text color rgb{self.text_color} \n')
            text.write(f'|     | Border color rgb{self.border_color} \n')
            text.write('\n')

            text.close()
            os.system('cls')
            print(Terminal_Colorized_().Stylezate('Save',Terminal_Colorized_().t_green))

        def Get_text(self):
            text = self.tb.getText()
            return text

        def Set_text(self,text=''):
            self.tb.setText(text)

        def Update(self):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame_widgets.update(events)

            self.posx = self.tb.getX()
            self.posy = self.tb.getY()
            self.width = self.tb.getWidth()
            self.height = self.tb.getHeight()
            self.text = self.tb.getText()
            self.pos = [self.tb.getX(),self.tb.getY]
            self.size = [self.tb.getWidth(),self.tb.getHeight()]

        def Set_size(self,size=[]):
            self.width = size[0]
            self.height = size[1]
            self.tb.setWidth(size[0])
            self.tb.setHeight(size[1])

        def Set_posx(self,x):
            self.posx = x
            self.tb.setX(x)

        def Set_posy(self,y):
            self.posy = y
            self.tb.setY(y)

        def Set_pos(self,pos=[]):
            self.posy = pos[1]
            self.tb.setY(pos[1])
            self.posx = pos[0]
            self.tb.setX(pos[0])

        def Hide(self):
            self.tb.hide()

        def Show(self):
            self.tb.show()

        def Set_output_disable(self):
            self.tb.disable()

        def Set_output_enable(self):
            self.tb.enable()

        def Set_width(self,width):
            self.width = width
            self.tb.setWidth(width)

        def Set_height(self,height):
            self.height = height
            self.tb.setHeight = height

        def Get_height(self):
            return self.tb.getHeight()

        def Get_width(self):
            return self.tb.getWidth()

        def Get_pos(self):
            return self.pos

        def Get_posx(self):
            return self.posx

        def Get_posy(self):
            return self.posy

        def Get_size(self):
            return self.size

        def Get_font_size(self):
            return self.font_size

        def Get_border_color(self):
            return self.border_color

        def Get_text_color(self):
            return self.text_color

        def Get_radius(self):
            return self.radius

        def Get_border_size(self):
            return self.border_size  

        def Disable(self):
            self.tb.disable()

        def Enable(self):
            self.tb.enable()

        def Get_selected(self):
            return self.tb.selected

    class Buttons:
        def __init__(self,  plane :                         Display_init_,
                            pos :                           list = [],
                            size :                          list = [],
                            text :                          str = '',
                            text_color :                    Color_ = (0,0,0),
                            font_size :                     int = 20,
                            margin :                        int = 20,
                            no_activ_color :                Color_ = Color_._rgb(10,10,10).COLOR,
                            activ_color :                   Color_ = Color_._rgb(30,30,30).COLOR,
                            pressed_color :                 Color_= Color_._rgb(60,60,60).COLOR,
                            radius :                        int = 20,
                            functions :                     list = None,
                            shadow_dist :                   int = 0,
                            shadow_color :                  Color_ = (0,0,0),
                            id :                            str = ''
                            ):

            self.id = id
            if self.id == '':
                self.id = 'NONE'
            self.plane = plane
            self.pos = pos
            self.size = size
            self.posx = self.pos[0]
            self.posy = self.pos[1]
            self.width = self.size[0]
            self.height = self.size[1]
            self.text = text
            self.font_size = font_size
            self.margin = margin
            self.no_activ_color = no_activ_color
            self.activ_color = activ_color
            self.pressed_color = pressed_color
            self.radius = radius
            self.text_color = text_color
            self.shadow_dist = shadow_dist
            self.shadow_color = shadow_color
            self.Mouse_pos_x = 0
            self.Mouse_pos_y = 0

            bt = Button(
                self.plane,
                self.posx,self.posy,
                self.width,self.height,
                text=self.text,
                fontSize = self.font_size,
                margin = self.margin,
                inactiveColour = self.no_activ_color,
                hoverColour = self.activ_color,
                pressedColour = self.pressed_color,
                radius = self.radius,
                onClick = functions,
                textColour = self.text_color,
                shadowColour = self.shadow_color,
                shadowDistance = self.shadow_dist
            )
            self.bt = bt

        def DSave(self,filename,open_type = 'a'):
            if open_type == 'a':text = open(filename,'a')
            elif open_type == 'w':text = open(filename,'w')

            
            text.write('Type [Button] ; ID == '+self.id+'\n')
            text.write(f'|  Position [ {self.posx} : {self.posy} ]\n')
            text.write(f'|  Size [ {self.size[0]} : {self.size[1]} ]\n')
            text.write(f'|  Font size [ {self.font_size} ]\n')
            text.write(f'|  Radius [ {self.radius} ]\n')
            text.write(f'|  Text [ {self.text} ]\n')
            text.write(f'|  Margin [ {self.margin} ]\n')
            text.write(f'|  Shadow dict [ {self.shadow_dist} ]\n')
            text.write(f'|  Colors :\n')
            text.write(f'|     | No activ color rgb{self.no_activ_color} \n')
            text.write(f'|     | Activ color rgb{self.activ_color} \n')
            text.write(f'|     | Pressed color rgb{self.pressed_color} \n')
            text.write(f'|     | Shadow color rgb{self.shadow_color} \n')
            text.write('\n')

            text.close()
            os.system('cls')
            print(Terminal_Colorized_().Stylezate('Save',Terminal_Colorized_().t_green))

        def Update(self):

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame_widgets.update(events)

            self.Mouse_pos_x=self.bt.getX()
            self.Mouse_pos_y=self.bt.getY()

        def Set_mouse_speed(self, mouse : Sub_events_.Mouse_init , value : int):
            
            sx = -(self.Mouse_pos_x-mouse.GET_POSITION()[0])/value
            sy = -(self.Mouse_pos_y-mouse.GET_POSITION()[1])/value


            self.Mouse_pos_x = mouse.GET_POSITION()[0]
            self.Mouse_pos_y = mouse.GET_POSITION()[1]

            self.bt.setX(self.bt.getX()+sx)
            self.bt.setY(self.bt.getY()+sy)
         
        def Set_posx(self,x):
            self.posx = x
            self.bt.setX(x)

        def Set_posy(self,y):
            self.posy = y
            self.bt.setY(y)      

        def Set_width(self,width):
            self.width = width
            self.bt.setWidth(width)

        def Set_height(self,height):
            self.height = height
            self.bt.setHeight(height)

        def Set_size(self,size=[]):
            self.height = size[1]
            self.width = size[0]
            self.bt.setWidth(size[0])
            self.bt.setHeight(size[1])

        def Set_pos(self,pos = []):
            self.posx = pos[0]
            self.posy = pos[1]
            self.bt.setX(pos[0])
            self.bt.setY(pos[1])

        def Set_pressed_color(self,color):
            self.pressed_color = color
            self.bt.setPressedColour(color)

        def Set_activ_color(self,color):
            self.activ_color = color
            self.bt.setHoverColour(color)

        def Set_no_activ_color(self,color):
            self.no_activ_color = color
            self.bt.setInactiveColour(color)

        def Get_pos(self):
            return self.pos

        def Get_posx(self):
            return self.posx

        def Get_posy(self):
            return self.posy

        def Get_size(self):
            return self.size

        def Get_width(self):
            return self.width

        def Get_height(self):
            return self.height

        def Get_text(self):
            return self.text

        def Get_font_size(self):
            return self.font_size

        def Get_margin(self):
            return self.margin

        def Get_no_activ_color(self):
            return self.no_activ_color

        def Get_activ_color(self):
            return self.activ_color

        def Get_pressed_color(self):
            return self.pressed_color

        def Get_radius(self):
            return self.radius

        def Get_text_color(self):
            return self.text_color

        def Get_shadow_color(self):
            return self.shadow_color

        def Get_shadow_distance(self):
            return self.shadow_dist

        def Show(self):
            self.bt.show()

        def Hide(self):
            self.bt.hide()

        def Get_pressed(self):
            return self.bt.clicked

        def Sleep(self):
            self.bt.disable()

        def Stendup(self):
            self.bt.enable()

        def Disable(self):
            self.bt.disable()

        def Enable(self):
            self.bt.enable()

    class Toggles:
        def __init__(self,  plane :                         Display_init_,
                            pos :                           list = [],
                            size :                          list = [],
                            startType :                     bool = False,
                            oncolor :                       Color_ = Color_._rgb(141, 185, 244).COLOR,
                            offcolor :                      Color_ = Color_._rgb(150, 150, 150).COLOR,
                            handl_oncolor :                 Color_ = Color_._rgb(26, 115, 232).COLOR,
                            handl_offcolor :                Color_ = Color_._rgb(200, 200, 200).COLOR,
                            radius :                        int = 20,
                            id :                            str = ''
                            ):

            self.id = id
            if self.id == '':
                self.id = 'NONE'
            
            self.plane = plane
            self.pos = pos
            self.posx = self.pos[0]
            self.posy = self.pos[1]
            self.size = size
            self.width = self.size[0]
            self.height = self.size[1]
            self.startType = startType
            self.oncolor = oncolor
            self.offcolor = offcolor
            self.handl_oncolor = handl_oncolor
            self.handl_offcolor = handl_offcolor
            self.radius = radius

            tg = Toggle(
                self.plane,
                self.posx,self.posy,
                self.width,self.height,
                startOn = self.startType,
                offColour = self.offcolor,
                onColour = self.oncolor,
                handleOnColour = self.handl_oncolor,
                handleOffColour = self.handl_offcolor,
                handleRadius = self.radius
            )
            self.tg = tg

        def Update(self):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame_widgets.update(events)

        def DSave(self,filename,open_type = 'a'):
            if open_type == 'a':text = open(filename,'a')
            elif open_type == 'w':text = open(filename,'w')

            
            text.write('Type [Toggle] ; ID == '+self.id+'\n')
            text.write(f'|  Position [ {self.posx} : {self.posy} ]\n')
            text.write(f'|  Size [ {self.size[0]} : {self.size[1]} ]\n')
            text.write(f'|  Radius [ {self.radius} ]\n')
            text.write(f'|  Start type [ {self.startType} ]\n')
            text.write(f'|  Colors :\n')
            text.write(f'|     | On color rgb{self.oncolor} \n')
            text.write(f'|     | Off color rgb{self.offcolor} \n')
            text.write(f'|     | On handel color rgb{self.handl_oncolor} \n')
            text.write(f'|     | Off handel color rgb{self.handl_offcolor} \n')
            text.write('\n')

            text.close()
            os.system('cls')
            print(Terminal_Colorized_().Stylezate('Save',Terminal_Colorized_().t_green))

        def Set_pos(self,pos=[]):
            self.posx = pos[0]
            self.posy = pos[1]
            self.tg.setX(pos[0])
            self.tg.setY(pos[1])

        def Set_posx(self,x):
            self.posx = x
            self.tg.setX(x)

        def Set_posy(self,y):
            self.posy = y
            self.tg.setY(y)

        def Set_width(self,width):
            self.width = width
            self.tg.setWidth(width)

        def Set_height(self,height):
            self.height = height
            self.tg.setHeight(height)

        def Hide(self):
            self.tg.hide()

        def Show(self):
            self.tg.show()

        def Get_value(self):
            val = self.tg.getValue()
            return val

        def Get_height(self):
            return self.tg.getHeight()

        def Get_width(self):
            return self.tg.getWidth()

        def Get_size(self):
            return self.size

        def Get_pos(self):
            return self.pos

        def Get_posx(self):
            return self.posx

        def Get_posy(self):
            return self.posy

        def Get_start_Type(self):
            return self.startType

        def Get_oncolor(self):
            return self.oncolor

        def Get_offcolor(self):
            return self.offcolor

        def Get_handl_oncolor(self):
            return self.handl_oncolor

        def Get_handl_offcolor(self):
            return self.handl_offcolor

        def Get_radius(self):
            return self.radius

    class DropDowns:       
        def __init__(self,  plane : Display_init_,
                            pos : list = [],
                            size = [],
                            name = '',
                            choices = [],
                            radius = 0,
                            color = (),
                            values = [],
                            direction = 'down',
                            issubwidget = False,
                            text_color = Color_._rgb(0,0,0).COLOR,
                            font = None,
                            font_size = 20,
                            id = '',
                            Visible = True):

            self.id = id
            if self.id == '':
                self.id = 'NONE'

            self.plane = plane

            self.pos = pos
            self.posx = pos[0]
            self.posy = pos[1]

            self.size = size
            self.width = size[0]
            self.height = size[1]

            self.name = name

            self.choices = choices

            self.radius = radius

            self.color = color

            self.values = values

            self.direction = direction

            self.visible = Visible

            self.issubwidget = issubwidget

            self.text_color = text_color

            self.font = font
            self.font_size = font_size

            dd = Dropdown(
                self.plane,
                self.posx,self.posy,
                self.width,self.height,
                self.name,
                self.choices,
                self.issubwidget, 
                borderRadius = self.radius,
                colour = self.color,
                values = self.values,
                direction = self.direction,
                textColour = self.text_color,
                fontSize = self.font_size
            )
            self.dd = dd

        def DSave(self,filename,open_type = 'a'):
            if open_type == 'a':text = open(filename,'a')
            elif open_type == 'w':text = open(filename,'w')

            
            text.write('Type [DropDown] ; ID == '+self.id+'\n')
            text.write(f'|  Position [ {self.posx} : {self.posy} ]\n')
            text.write(f'|  Size [ {self.size[0]} : {self.size[1]} ]\n')
            text.write(f'|  Radius [ {self.radius} ]\n')
            text.write(f'|  Name [ {self.name} ]\n')
            text.write(f'|  Choices [ {self.choices} ]\n')
            text.write(f'|  Values [ {self.values} ]\n')
            text.write(f'|  Direction [ {self.direction} ]\n')
            text.write(f'|  Is sub widget [ {self.issubwidget} ]\n')
            text.write(f'|  Font [ {self.font} ]\n')
            text.write(f'|  Font size [ {self.font_size} ]\n')
            text.write(f'|  Colors :\n')
            text.write(f'|     | Color rgb{self.color} \n')
            text.write(f'|     | Text color rgb{self.text_color} \n')
            text.write('\n')

            text.close()
            os.system('cls')
            print(Terminal_Colorized_().Stylezate('Save',Terminal_Colorized_().t_green))

        def Update(self):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame_widgets.update(events)
            self.pos = [self.dd.getX(),self.dd.getY()]
            self.posx = self.pos[0]
            self.posy = self.pos[1]

        def Get_selected(self):
            return self.dd.getSelected()

        def Get_dropped(self):
            return self.dd.isDropped()

        def Get_x(self):
            return self.dd.getX()

        def Get_y(self):
            return self.dd.getY()

        def Set_pos(self,pos=[]):
            self.posx = pos[0]
            self.posy = pos[1]
            self.dd.setX(pos[0])
            self.dd.setY(pos[1])

        def Get_pos(self):
            return [self.dd.getX(),self.dd.getY()]

        def Get_size(self):
            return [self.dd.getWidth(),self.dd.getHeight()]

        def Get_width(self):
            return self.dd.getWidth()
        
        def Get_height(self):
            return self.dd.getHeight()

        def Set_height(self, height):
            self.height = height
            self.dd.setHeight(height)

        def Set_width(self, width):
            self.width = width
            self.dd.setWidth(width)

        def Set_posx(self,x):
            self.posx = x
            self.dd.setX(x)

        def Set_posy(self,y):
            self.posy = y
            self.dd.setY(y)

        def Hide(self):
            self.dd.hide()

        def Show(self):
            self.dd.show()

        def Enable(self):
            self.dd.enable()

        def Disable(self):
            self.dd.disable()

        def __GL_setvisible__(self,bool=True):
            self.visible = bool
            if self.visible == False:
                self.dd.hide()
            elif self.visible == True:
                self.dd.show()

        def __GL_id__(self):
            return self.id

        def __GL_x__(self):
            return self.posx
        
        def __GL_y__(self):
            return self.posy

    class ProgressBar:
        def __init__(self,plane,
                        pos = [],
                        size = [],
                        Progress_function = None,
                        Completed_color = Color_._rgb(0,200,0).COLOR,
                        Incompleted_color = Color_._rgb(100,100,100).COLOR,
                        Curved = False,
                        id = '',
                        Visible = True
                        ):

            self.id = id
            if self.id == '':
                self.id = 'NONE'
            self.plane = plane

            self.pos = pos

            self.posx = self.pos[0]
            self.posy = self.pos[1]

            self.size = size

            self.visible = Visible

            self.Completed_color = Completed_color
            self.Incompleted_color = Incompleted_color

            self.Curved = Curved

            self.pb = ProgressBar(
                self.plane,
                self.pos[0],self.pos[1],
                self.size[0],self.size[1],
                Progress_function,
                completedColour = self.Completed_color,
                incompletedColour = self.Incompleted_color,
                curved = self.Curved
            )

        def Update(self):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame_widgets.update(events)
            self.pos = [self.pb.getX(),self.pb.getY()]
            self.posx = self.pos[0]
            self.posy = self.pos[1]

        def DSave(self,filename,open_type = 'a'):
            if open_type == 'a':text = open(filename,'a')
            elif open_type == 'w':text = open(filename,'w')

            
            text.write('Type [ProgressBar] ; ID == '+self.id+'\n')
            text.write(f'|  Position [ {self.posx} : {self.posy} ]\n')
            text.write(f'|  Size [ {self.size[0]} : {self.size[1]} ]\n')
            text.write(f'|  Curved [ {self.Curved} ]\n')
            text.write(f'|  Colors :\n')
            text.write(f'|     | Completed color rgb{self.Completed_color} \n')
            text.write(f'|     | Incompleted color rgb{self.Incompleted_color} \n')
            text.write('\n')

            text.close()
            os.system('cls')
            print(Terminal_Colorized_().Stylezate('Save',Terminal_Colorized_().t_green))

        def Get_prcent(self):
            return self.pb.percent

        def Get_width(self):
            return self.pb.getWidth()

        def Get_height(self):
            return self.pb.getHeight()

        def Get_pos(self):
            return [self.pb.getX(), self.pb.getY()]

        def Get_size(self):
            return [self.pb.getWidth(), self.pb.getHeight()]

        def Get_posx(self):
            return self.pb.getX()

        def Get_posy(self):
            return self.pb.getY()

        def Set_size(self, size=[]):
            self.pb.setHeight(size[1])
            self.pb.setWidth(size[0])

        def Set_width(self,width):
            self.pb.setWidth(width)

        def Set_height(self,height):
            self.pb.setHeight(height)

        def Hide(self):
            self.pb.hide()

        def Show(self):
            self.pb.show()

        def Disable(self):
            self.pb.disable()

        def Enable(self):
            self.pb.enable()

        def __GL_setvisible__(self,bool=True):
            self.visible = bool
            if self.visible == False:
                self.pb.hide()
            elif self.visible == True:
                self.pb.show()

        def __GL_id__(self):
            return self.id

        def __GL_x__(self):
            return self.posx
        
        def __GL_y__(self):
            return self.posy
            
    class TScollingSurf:
        def __init__(self,plane,
                            pos = [],
                            size = [],
                            color = (),
                            alpha = 255,
                            scroling_on_x = False,
                            scroling_on_y = True,
                            visible = True,
                            id = ''):
            self.pos = pos
            self.size = size
            self.color = color
            self.alpha = alpha
            self.plane = plane

            self.dt_poli_visib = False
            self.detecting_poli = GL_Detectings_.Rect([self.pos[0]-2,self.pos[1]-2],[self.size[0]+4,self.size[1]+4])
            

            self.scroling_on_x = scroling_on_x
            self.scroling_on_y = scroling_on_y

            self._obj_ : Text_ = []

            self.speedx = 1
            self.speedy = 1

            self.id = id
            if self.id == '':
                self.id = 'NONE'

            self.mposx = 0
            self.mposy = 0

            self.sx = 0
            self.sy = 0

            self.scrol_surf = Surfases_(self.size,self.pos,self.color,self.alpha)

            self.visible = visible

        def Update(self):
            if self.dt_poli_visib:
                self.detecting_poli.View(self.plane,True)

            if self.visible:
                self.scrol_surf.DRAW_(self.plane)
                self.scrol_surf.UPDATE()
                for i in range(len(self._obj_)):
                    if self._obj_[i][0]=='text_':
                        self._obj_[i][1].RENDER()
            self.sy*=0.99
            if self.sy<0.01 and self.sy>-0.01 :self.sy = 0

        
        def Add_Text(self,_objects_:any,type='text_'):
            if type == 'text_':
                self._obj_.append([type,_objects_])

        
        def Scroll_mouse(self,mouse : Sub_events_.Mouse_init,mouse_button = 'l'):
            if mouse.GET_PRESS_ON_PYGL_WINDOW(mouse_button):
                if self.detecting_poli._ON_MOUSE_(mouse):
                    if self.scroling_on_x:
                        self.sx = -(self.mposx-mouse.GET_POSITION()[0])/self.speedx
                    if self.scroling_on_y:
                        self.sy = -(self.mposy-mouse.GET_POSITION()[1])/self.speedy
 
            self.mposx = mouse.GET_POSITION()[0]
            self.mposy = mouse.GET_POSITION()[1]
            for i in range(len(self._obj_)):
                if self._obj_[i][0]=='text_':
                    self._obj_[i][1].SET_POS([self._obj_[i][1].GET_POSITION()[0]+self.sx,
                    self._obj_[i][1].GET_POSITION()[1]+self.sy])

        def __GL_getobj__(self):
            return self._obj_

        def __GL_setvisible__(self,bool=True):
            self.visible = bool

        def Show(self):
            self.visible = True

        def Hide(self):
            self.visible = False

        def __GL_set_visible_detect_poli__(self,bool=False):
            self.dt_poli_visib = bool

        def Get_pos(self):
            return self.pos

        def Get_size(self):
            return self.size

        def Get_posx(self):
            return self.pos[0]

        def Get_posy(self):
            return self.pos[1]

        def Get_width(self):
            return self.size[0]

        def Get_height(self):
            return self.size[1]

        def Set_pos(self,pos=[]):
            self.pos = pos

        def Set_size(self,size=[]):
            self.size = size
            self.scrol_surf = Surfases_(self.size,self.pos,self.color,self.alpha)
            self.detecting_poli = GL_Detectings_.Rect([self.pos[0]-2,self.pos[1]-2],[self.size[0]+4,self.size[1]+4])
        
        def Set_posx(self,x):
            self.pos[0] = x

        def Set_posy(self,y):
            self.pos[1] = y
            
        def Get_speedy(self):
            return self.speedy

        def Get_speedx(self):
            return self.speedx
        
        def Set_surf_color(self,color:Color_):
            self.color = color
            self.scrol_surf = Surfases_(self.size,self.pos,self.color,self.alpha)

        def __GL_set_speedx__(self,speed):
            self.speedx = speed

        def __GL_set_speedy__(self,speed):
            self.speedy = speed

        def __GL_mposx__(self):
            return self.mposx

        def __GL_mposy__(self):
            return self.mposy

        def __GL_sx__(self):
            return self.sx

        def __GL_sy__(self):
            return self.sy

        def __GL_mouse_on_polly__(self):
            return self.detecting_poli._ON_MOUSE_(Sub_events_.Mouse_init())

        def __GL_id__(self):
            return self.id

        def __GL_x__(self):
            return self.pos[0]

        def __GL_y__(self):
            return self.pos[1]
# 15 Objects massiv
class Objectes_:
    def __init__(self,name='obj'):
        self.name = name
        self.pack = []

    def Add(self,obj,mass=False):
        if mass == True:
            self.pack.append(obj)
        else:
            if len(obj)>1:
                for i in range(len(obj)):
                    self.pack.append(obj[i])
            else:
                self.pack.append(obj)   

    def Del_min(self,index):
        self.pack.pop(index)

    def Del_max(self,a_index,b_index):
        del self.pack[a_index-1:b_index]

    def Get_name(self):
        return self.name

    def Set_name(self,name):
        self.name = name

    def Get_pack(self):
        return self.pack
# 16 Img
class Img_:
    def __init__(self,surface):
        self.surface = surface
        
    def Draw(self,pos = []):
        self.pos = pos
        self.rect = self.surface.get_rect(bottomright=(pos[0]+self.surface.get_width(),pos[1]+self.surface.get_height())) 
        screen.blit(self.surface,self.rect)

    def Get_size(self):
        return self.surface.get_size()
# 17 Sound
class Sound_mixer_(object):
    def __init__(self,file_name=''):
        self.sound = pygame.mixer.Sound(file_name)    

    def Set_volume(self,VOLUME=None):
        if VOLUME != None:self.sound.set_volume(VOLUME)

    def Play(self):
        self.sound.play()

    def Stop(self):
        self.sound.stop()
# 18 Music
class Music_mixer_(object):
    def __init__(self,file_name=''):
        pygame.mixer.music.load(file_name) 
    def Play_Music(self):
        pygame.mixer.music.play()
    def Pause_Music(self):
        pygame.mixer.music.pause()
    def Unload(self):
        pygame.mixer.music.unload()   
    def Set_Volume(self,volume):
        pygame.mixer.music.set_volume(volume)    
# 19 Colored_text
class Terminal_Colorized_():
    def __init__(self,Text__color__for__html=None,Background__Color__for__html=None):
        if Text__color__for__html!=None:
            self.tc = FG(Text__color__for__html)
        else:self.tc = None
        if Background__Color__for__html!=None:
            self.bgc = BG(Background__Color__for__html)
        else:self.bgc = None

        self.resset = ATTR('reset')

        self.t_red = FG('red')
        self.t_green = FG('green')
        self.t_blue = FG('blue')
        self.t_cyan = FG('cyan')


        self.s_bold = ATTR('bold')
        self.s_dim = ATTR('dim')
        self.s_blink = ATTR('blink')
        self.s_reverse = ATTR('reverse')
        self.s_angre = self.s_bold + self.t_red


    def Stylezate(self,str_text,style):
        text = stylize(str_text,style)
        return text

    def Get__tc(self):
        if self.tc != None:
            return self.tc
    
    def Get__bgc(self):
        if self.bgc != None:
            return self.bgc
# 20 Automation
class Automations_:
    def __init__(self) -> None:
        pass
    def A_I(self,daley = 0,text_write_time = 0.1):
        for i in range(100):
            keyboard.press('del')      
        time.sleep(daley)
        keyboard.write('''from pygl_nf import GL_3D
''',text_write_time)
        time.sleep(0.1)
        keyboard.write('''from pygl_nf import GL_DT\n
''',text_write_time)
        time.sleep(0.1)
        keyboard.write('''from pygl_nf import GL_PREFABS\n
''',text_write_time)
    
    def A_C_Tree(self,daley = 0,text_write_time = 0.1): 
        for i in range(100):
            keyboard.press('del')
        time.sleep(daley)
        keyboard.write('''win = GL.Display_init_(flags=GL.D_Resize)


''',text_write_time)
        keyboard.write('''while win.CE():
    win.UPDATE().SET_BG_COLOR('white')''',text_write_time)

    def A_C_Button(self,daley = 0,text_write_time = 0.1):
        for i in range(75):
            keyboard.press('del')
        time.sleep(daley)
        keyboard.write('''
button = GL.Widgets_.Buttons(
    win.screen,
[10,10],[100,30],
'button',
id = 'button_1',
radius = 5,
no_activ_color = (30,170,200),
activ_color = (20,140,220),
functions = GL.Passing''',text_write_time)

    def A_C_Slider(self,daley = 0,text_write_time = 0.1):
        for i in range(80):
            keyboard.press('del')
        time.sleep(daley)
        keyboard.write('''
slider = GL.Widgets_.Sliders(
    win.screen,
[10,10],
100,10,0,100,1,
(0,0,0),
(30,30,30),
10,
id = 'slider_1',
curved = True''',text_write_time)
# 21 Animations
class Animations_:
    def __init__(self,cadrs=[],screen=None,loop = True):
        self.cadrs = cadrs
        self.loop = loop
        self.screen = screen
        self.anim_obj = pyganim.PygAnimation(
            self.cadrs,
            self.loop
        )
    def Play(self):
        self.anim_obj.play()

    def Blit(self,pos=()):
        self.anim_obj.blit(self.screen,pos)

    def Pause(self):
        self.anim_obj.pause()

    def Stop(self):
        self.anim_obj.stop()

    def Scale2X(self):
        self.anim_obj.scale2x()

    def Scale(self,scale=[]):
        self.anim_obj.scale(scale)
# 22      
class GL_Detectings_():
    def __init__(self) -> None:
        pass

    class Circle(object):
            def __init__(self,pos = [], radius = None) -> None:
                self.pos = pos
                self.radius = radius

            def View(self,surf,on_m=None):
                Display_init_.GL.Circle('black',self.pos,self.radius,1,surf,'D')
                if on_m == True:
                    if Math_().RAST( Sub_events_.Mouse_init().GET_POSITION(),self.pos ) < self.radius:
                        Display_init_.GL.Circle('green',self.pos,self.radius,1,surf,'D')
                    else:
                        Display_init_.GL.Circle('red',self.pos,self.radius,1,surf,'D')
            
            def _ON_MOUSE_(self,mouse=Sub_events_.Mouse_init()):
                m_POS = mouse.GET_POSITION('y')
                if  Math_().RAST( m_POS, self.pos)<self.radius:                   return True
                else:                                                             return False

            def _ON_POSITION_(self,pos=[]):
                m_POS = pos
                if  Math_().RAST( m_POS, self.pos)<self.radius:                   return True
                else:                                                             return False
           
            def _ON_CLICK_(self,mouse=Sub_events_.Mouse_init(),button='l'):
                m_POS = mouse.GET_POSITION('y')
                if  Math_().RAST( m_POS, self.pos)<self.radius and mouse.GET_PRESS_ON_PYGL_WINDOW(button):      return True
                else:                                                                                           return False

            def _SET_POSITION_(self,pos=[]):
                self.pos = pos

    class Rect(object):
            def __init__(self,pos = [], size = []) -> None:
                self.pos = pos
                self.size = size

            def View(self,surf,on_m=None):
                Display_init_.GL.Rect('black',self.pos,self.size,1,surf,'D')
                if on_m == True:
                    if (Sub_events_.Mouse_init().GET_POSITION()[0]>self.pos[0] and Sub_events_.Mouse_init().GET_POSITION()[0]<self.pos[0]+self.size[0] and
                        Sub_events_.Mouse_init().GET_POSITION()[1]>self.pos[1] and Sub_events_.Mouse_init().GET_POSITION()[1]<self.pos[1]+self.size[1]):
                        Display_init_.GL.Rect('green',self.pos,self.size,3,surf,'D')
                    else:
                        Display_init_.GL.Rect('red',self.pos,self.size,3,surf,'D')
            
            def _ON_MOUSE_(self,mouse=Sub_events_.Mouse_init()):
                m_POS = mouse.GET_POSITION('y')
                if (m_POS[0]>self.pos[0] and m_POS[0]<self.pos[0]+self.size[0] and
                    m_POS[1]>self.pos[1] and m_POS[1]<self.pos[1]+self.size[1]):  return True
                else:                                                             return False       
            
            def _ON_POSITION_(self,pos=[]):
                m_POS = pos
                if (m_POS[0]>self.pos[0] and m_POS[0]<self.pos[0]+self.size[0] and
                    m_POS[1]>self.pos[1] and m_POS[1]<self.pos[1]+self.size[1]):  return True
                else:                                                             return False 
            
            def _ON_CLICK_(self,mouse=Sub_events_.Mouse_init(),button='l'):
                m_POS = mouse.GET_POSITION('y')
                if (m_POS[0]>self.pos[0] and m_POS[0]<self.pos[0]+self.size[0] and
                    m_POS[1]>self.pos[1] and m_POS[1]<self.pos[1]+self.size[1] and
                    mouse.GET_PRESS_ON_PYGL_WINDOW(button)):                      return True
                else:                                                             return False

            def _SET_POSITION_(self,pos = []):
                self.pos = [
                    pos[0]-self.size[0]/2,
                    pos[1]-self.size[1]/2
                ]
            
            def _GET_POSITION_(self):
                return self.pos

            def _SET_SIZE_(self,size):
                self.size = size

class Particles():
    class Point():
        def __init__(self,surf,point_pos, gravity, shape_data, life_time = 2, speed=1, particle_count=5, spawn_time = 10, size_resize=True, size_deller = 0.1, max_particles=300) -> None:
            self.point_pos = Vec2_(pos=point_pos)
            self.gravity = Vec2_(pos=gravity)
            self.spawn_time = spawn_time
            self.timer = 0
            self.speed = speed
            self.life_time = life_time
            self.surf = surf
            self.max_particles = max_particles
            
            self.size_resize = size_resize
            self.size_deller = size_deller

            self.shape = shape_data[0]
            self.color = shape_data[1]
            self.size =  shape_data[2]


            self.particle_count = particle_count
            
            self.particles = []

        def Emiter(self):
            self.timer+=1
            if self.timer%self.spawn_time==0:

              for i in range(self.particle_count):
                    sped_vector = Vec2_(pos = [random.randint(-self.speed,self.speed)*random.random(),random.randint(-self.speed,self.speed)*random.random()] )
                    particle = [self.point_pos,sped_vector,self.life_time,self.size]
                    self.particles.append(particle)

        def Lifeter(self):
            for i in range(len(self.particles)):
                self.particles[i][2]-=0.1
                if self.particles[i][0].y>self.surf.GET_WIN_HEIGHT() or self.particles[i][0].y<0 or self.particles[i][0].x<0 or self.particles[i][0].x>self.surf.GET_WIN_WIDTH():
                    del self.particles[i]
                    break
                if self.particles[i][2]<=0:
                    del self.particles[i]
                    break
        
        def Xclean(self):
            for i in range(len(self.particles)):
                if self.particles[i][3]<=0:
                    del self.particles[i]
                    break
                if random.randint(0,1)==1:
                    del self.particles[i]
                    break
            if len(self.particles)>self.max_particles:
                del self.particles[0:50]
                

        def PCount(self,pos):
            Text_(str(len(self.particles)),True,'black','arial',20,pos,SURF=self.surf.screen).RENDER()

            

        def Focus(self):
            for i in range(len(self.particles)):
                self.particles[i][1] = self.particles[i][1].SUM(self.gravity)
                self.particles[i][0] = self.particles[i][0].SUM(self.particles[i][1])
                if self.size_resize:
                    self.particles[i][3]-=self.size_deller
                
                


        def Render(self):
            for i in range(len(self.particles)):
                if self.shape == 'r':
                    if self.particles[i][2]>0:
                        self.surf.GL.Rect(self.color,self.particles[i][0].pos1,[self.particles[i][3],self.particles[i][3]],0,'s','D')
                
                elif self.shape == 'c':
                    if self.particles[i][2]>0:
                        self.surf.GL.Circle(self.color,self.particles[i][0].pos1,self.particles[i][3],0,'s','D')



        
        def Set_position(self,pos):
            self.point_pos = Vec2_(pos=pos)



        

            
        
            


                

            








































