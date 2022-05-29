import thales as th 
import pygame 
import math 
from pygame.locals import * 

class SlopeField: 
    def __init__(self, surface, g, f, color=(0,0,255), gradient=False, vector=False):
        self.surface, self.g, self.f, self.color = surface, g, f, color 
        self.gradient, self.vector = gradient, vector

    def get_color(self, slope): 
        maxSlope = 10 
        i = min(abs(slope),maxSlope)*(765/maxSlope) 
        if i <= 255: 
            return (0,i,255-i) 
        elif i <= 510: 
            return (i-255,255,0) 
        elif i <= 765: 
            return (255,765-i,0)
        else: 
            return (255,0,0) 
        
    def get_field(self): 
        field = [] 
        for r in range (round(self.g.gy(self.g.sDims[1])), round(self.g.gy(0))): 
            row = [] 
            for c in range (round(self.g.gx(0)), round(self.g.gx(self.g.sDims[0]))+1): 
                mag = min(0.2 + abs(self.f(c,r))/10, 0.8) if self.vector else 0.6 
                theta = math.atan(self.f(c,r)) 
                dx, dy = mag * math.cos(theta), mag * math.sin(theta) 
                v = th.Vector(self.surface, self.g, (c-0.5,r), (c-0.5+dx,r+dy), color=(60,60,255))
                if self.gradient: v.color = self.get_color(self.f(c,r)) 
                row.append(v) 
            field.append(row) 
        return field 

    def draw(self): 
        field = self.get_field() 
        for y in field: 
            for v in y: 
                v.draw()  

if __name__ == '__main__':
    def f(x, y): 
        return x**2 + y 

    SW, SH = 800, 600 
    surface = pygame.display.set_mode((SW,SH)) 
    pygame.display.set_caption('Slope Field Example') 

    g = th.Grid(surface, (SW/2, SH/2), (40,40), (SW,SH), cColor=(100,100,100))
    
    s = SlopeField(surface, g, f)

    while True: 
        for event in pygame.event.get(): 
            if event.type == QUIT: 
                pygame.quit() 
                exit(0) 
            if event.type == KEYDOWN:  
                if event.key == pygame.K_g: 
                    s.gradient = not s.gradient 
                if event.key == pygame.K_v: 
                    s.vector = not s.vector 
            g.pan(event, resetButton = pygame.K_r) 
            g.zoom(event) 

        surface.fill((255,255,255)) 

        g.draw() 
        s.draw() 

        pygame.display.update() 
            