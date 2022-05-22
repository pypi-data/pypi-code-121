import math
import pygame 
import sympy as sym
from pygame.locals import * 

class Grid: 
    def __init__(self, surface, center, cDims, sDims, cColor=(0,0,0), aColor=(0,0,0), cWidth=2, aWidth=4): 
        """
        Params: 
        surface: the Pygame surface object on which the grid is displayed 
        center: an integer tuple, the pixel coordinates of the origin of the grid 
        cDims: an integer tuple, the pixel dimensions of each cell of the grid
        sDims: an integer tuple, The dimensions of the surface object 
        cColor: a pygame.Color object, the color of the lines of the grid cells 
        aColor: a pygame.Color object, the color of the axis lines 
        cWidth: an integer, the pixel width of the lines of the grid cells 
        aWidth: an integer, the pixel width of the axis lines 
        """

        self.surface, self.center, self.cDims, self.sDims = surface, center, cDims, sDims 
        self.cColor, self.aColor, self.cWidth, self.aWidth = cColor, aColor, cWidth, aWidth 
        self.panning, self.panX, self.panY, self.ogCDims = False, 0, 0, cDims

    def px(self, x): 
        return math.floor(x*self.cDims[0] + self.center[0])

    def py(self, y): 
        return math.floor(-y*self.cDims[1] + self.center[1]) 

    def pixel(self, x, y): 
        # input a tuple of grid coordinates, output a tuple of pixel coordinates 
        return self.px(x), self.py(y) 

    def gx(self, x): 
        return (x - self.center[0])/self.cDims[0]

    def gy(self, y) :
        return -(y - self.center[1])/self.cDims[1] 

    def grid(self, x, y): 
        # input a tuple of pixel coordinates, output a tuple of grid coordinates 
        return self.gx(x), self.gy(y) 

    def draw(self): 
        # cell lines 
        for cNeg in range (math.ceil(self.center[0] / self.cDims[0])): 
            pygame.draw.line(self.surface, self.cColor, (self.center[0] - cNeg * self.cDims[0], 0), 
                (self.center[0] - cNeg * self.cDims[0], self.sDims[1]), self.cWidth)  
        for cPos in range (math.ceil((self.sDims[0] - self.center[0])/self.cDims[0])): 
            pygame.draw.line(self.surface, self.cColor, (self.center[0] + cPos * self.cDims[0], 0), 
                (self.center[0] + cPos * self.cDims[0], self.sDims[1]), self.cWidth)
        for rNeg in range (math.ceil((self.sDims[1] - self.center[1])/self.cDims[1])): 
            pygame.draw.line(self.surface, self.cColor, (0, self.center[1] + rNeg * self.cDims[1]), 
                (self.sDims[0], self.center[1] + rNeg * self.cDims[1]), self.cWidth)
        for rPos in range (math.ceil(self.center[1] / self.cDims[1])): 
            pygame.draw.line(self.surface, self.cColor, (0, self.center[1] - rPos * self.cDims[1]), 
                (self.sDims[0], self.center[1] - rPos * self.cDims[1]), self.cWidth)  
        
        # axis lines 
        pygame.draw.line(self.surface, self.aColor, (self.center[0], 0), (self.center[0], self.sDims[1]), self.aWidth)
        pygame.draw.line(self.surface, self.aColor, (0, self.center[1]), (self.sDims[0], self.center[1]), self.aWidth) 
    
    def pan(self, event, button=3, resetButton=None):
        if event.type == MOUSEMOTION and self.panning: 
            sf=6
            dx, dy = (event.pos[0] - self.panX)/sf, (event.pos[1] - self.panY)/sf
            self.center = (self.center[0] + dx, self.center[1] + dy)
        if event.type == MOUSEBUTTONDOWN and event.button == button: 
            self.panX, self.panY = event.pos 
            self.panning = True 
        if event.type == MOUSEBUTTONUP and event.button == button: 
            self.panning = False; 
        if resetButton: 
            if event.type == KEYDOWN and event.key == resetButton: 
                self.center = (self.sDims[0] / 2, self.sDims[1] / 2)
                self.cDims = self.ogCDims 

    def zoom(self, event, inButton=4, outButton=5): 
        sf = 1.25 
        if event.type == MOUSEBUTTONDOWN: 
            centerDist = (event.pos[0] - self.center[0], event.pos[1] - self.center[1])
            if event.button == inButton: 
                self.cDims = (self.cDims[0]*sf, self.cDims[1]*sf)
                self.center = (event.pos[0] - centerDist[0] * sf, event.pos[1] - centerDist[1] * sf) 
            if event.button == outButton: 
                self.cDims = (self.cDims[0]/sf, self.cDims[1]/sf) 
                self.center = (event.pos[0] - centerDist[0] / sf, event.pos[1] - centerDist[1] / sf) 

class Point: 
    def __init__(self, surface, grid, coords, radius=10, fColor=(0,0,0), oColor=None, oWidth=4): 
        """
        surface: the Pygame surface object on which the grid is displayed 
        grid: the Grid object on which the point is plotted 
        coords: an integer tuple, the grid coordinates of the point    
        radius: an integer, the pixel radius of the point  
        oColor: a pygame.Color object, the (outline) color of the point 
        fColor: a pygame.Color object, the optional fill color of the point 
        outline: a boolean, whether or not to use the fill color 
        oWidth: an integer, the width of the outline if the fill color is used 
        """

        self.surface, self.grid, self.coords = surface, grid, coords 
        self.radius, self.oColor, self.fColor, self.oWidth = radius, oColor, fColor, oWidth 
        self.dragging = False 
        if (not self.oColor): self.oColor = self.fColor

    def move(self, x, y): 
        # change the center of the pixel to the grid coordinates provided
        self.coords = (self.coords[0] + x, self.coords[1] + y)  

    def pos(self, x, y): 
        self.coords = x, y 

    def draw(self): 
        pygame.draw.circle(self.surface, self.oColor, (self.grid.pixel(self.coords[0], self.coords[1])), self.radius)
        pygame.draw.circle(self.surface, self.fColor, (self.grid.pixel(self.coords[0], self.coords[1])), self.radius - self.oWidth) 

    def checkDrag(self, event, drag=False, button=1):
        if event.type == MOUSEMOTION and self.dragging: 
            self.coords = self.grid.grid(*event.pos)
            return True 
        if event.type == MOUSEBUTTONDOWN and event.button == button: 
            x, y = event.pos  
            if math.hypot(self.grid.px(self.coords[0]) - x, self.grid.py(self.coords[1]) - y) <= self.radius:
                if (drag): self.dragging = True 
                return True 
        if event.type == MOUSEBUTTONUP and event.button == button: 
            self.dragging = False 

    def getDist(self, p, tuple=False, useAbs=False):
        dx, dy = self.coords[0] - p.coords[0], self.coords[1] - p.coords[1]
        if tuple: 
            return (abs(dx), abs(dy)) if useAbs else (dx, dy) 
        else: 
            return math.sqrt(dx**2 + dy**2)
              

class Funct: 
    # add support for implicit relations 

    def __init__(self, surface, grid, f, inp=None, width=6, color=(255,0,0)): 
        """
        surface: the Pygame surface on which the function is plotted 
        grid: the Grid object on which the function is plotted 
        f: the lambda function describing the function relationship 
        inp: an array of input (x) values for the function 
        width: an integer, the width of the function 
        color: the color the function is drawn with 
        """

        self.surface, self.grid, self.f, self.inp, self.width, self.color = surface, grid, f, inp, width, color 

        self.points = [] 
        if (inp): 
            for x in inp: 
                self.points.append(Point(surface, self.grid, (x, self.get(x)), self.width/2, self.color))

    sx = sym.symbols('x') 

    def get(self, x): 
        # returns the value of the function at the grid input 
        # Switch to .subs(sx, x?)
        try: 
            return self.f(x).evalf() 
        except AttributeError: 
            return self.f(x) 

    # TODO: improve symbolic implementation (sympy functions, fast drawing errors) 

    def get_deriv(self, copy=True): 
        #new_f = copy.deepcopy(self) 
        new_f = sym.lambdify(self.sx, sym.diff(self.f(self.sx), self.sx)) 
        if copy: # switch around? 
            return Funct(self.surface, self.grid, new_f)
        return Funct(self.surface, self.grid, new_f, self.inp, self.width, self.color) 

    def get_int(self, copy=True): 
        #new_f = copy.deepcopy(self) 
        new_f = sym.lambdify(self.sx, sym.integrate(self.f(self.sx), self.sx))
        if copy: 
            return Funct(self.surface, self.grid, new_f)
        return Funct(self.surface, self.grid, new_f, self.inp, self.width, self.color)  

    # TODO: Add methods for tangents and zeroes 

    def get_zeroes(self): 
        # add complex number handling, determine if NM is faster
        return sym.solve(self.f(self.sx), self.sx)

    def get_extrema(self): 
        return self.get_deriv().get_zeroes()  

    def get_tangent(self, tx, color=(0,150,0)): 
        m = self.get_deriv().get(tx)
        tf = lambda x : m * (x - tx) + self.get(tx)
        tangent_f = Funct(self.surface, self.grid, tf, color=color)
        return tangent_f 
            
    def draw(self, inp=None, fast=False, acc=200):
        if (self.inp and not inp): 
            for p in self.points: 
                p.draw() 
        else: 
            for x in range (int(self.grid.gx(0)*acc), int(self.grid.gx(self.surface.get_width())*acc), 1): 
                if fast: 
                    pygame.draw.line(self.surface, self.color, (self.grid.px(x/acc), self.grid.py(self.get(x/acc)) + self.width/2), 
                                                               (self.grid.px(x/acc), self.grid.py(self.get(x/acc)) - self.width/2))
                else: 
                    Point(self.surface, self.grid, (x/acc, self.get(x/acc)), self.width/2, self.color).draw() 

class Vector:
    def __init__(self, surface, grid, c1, c2, width=5, color=(0,0,255)): 
        """
        surface: the Pygame surface object on which the grid is plotted 
        grid: the Grid object on which the vector is plotted 
        c1: an integer tuple, the grid coordinates of the starting point 
        c2: an integer tuple, the grid coordinates of the end point 
        width: an integer, the pixel width of the velocity arrow 
        color: a pygame.Color object, the color of the velocity arrow  
        """

        # TODO: Add an alternative implementation using c1, m (slope), and mag (magnitude) 

        self.surface, self.grid, self.c1, self.c2 = surface, grid, c1, c2 
        self.width, self.color = width, color 

    def move_start(self, x, y): 
        # change the center of the starting point of the vector to the grid coordinates provided
        self.c1 = (x,y) 

    def move_end(self, x, y): 
        # change the center of the end point of the vector to the grid coordinates provided 
        self.c2 = (x,y)  

    def draw(self): 
        pygame.draw.line(self.surface, self.color, self.grid.pixel(*self.c1), self.grid.pixel(*self.c2), self.width) 

# example program 

if __name__ == '__main__': 
    WHITE = (255, 255, 255) 
    BLACK = (0, 0, 0) 
    BLUE = (0, 0, 255) 

    SW, SH = 700, 500 
    surface = pygame.display.set_mode((SW, SH)) 
    pygame.display.set_caption('graph test') 

    g = Grid(surface, (350, 300), (30, 30), (SW, SH), cColor=BLUE)

    f1 = Funct(surface, g, lambda x : x ** 2, color=(0,175,0))
    pLam = lambda x, y : Point(surface, g, (x, y), oColor=BLACK, fColor=WHITE)
    points = [pLam(-3, f1.get(-3)), pLam(-2, f1.get(-2)), pLam(-1, f1.get(-1)), pLam(0, f1.get(0)), pLam(1, f1.get(1)), pLam(2, f1.get(2)), pLam(3, f1.get(3))]

    offset = 0  

    while True: 
        for event in pygame.event.get(): 
            if event.type == QUIT: 
                pygame.quit() 
                exit(0) 
            g.pan(event) 
            g.zoom(event) 

        offset += 0.4 
        f2 = Funct(surface, g, lambda x : math.sin(x**2 - offset) + x)
        f3 = Funct(surface, g, lambda x : math.sin(x**2 - offset) - x)

        surface.fill(WHITE)

        g.draw() 
        f1.draw() 
        f2.draw(fast=True) 
        f3.draw(fast=True) 
        for p in points: 
            p.draw() 

        pygame.display.update() 