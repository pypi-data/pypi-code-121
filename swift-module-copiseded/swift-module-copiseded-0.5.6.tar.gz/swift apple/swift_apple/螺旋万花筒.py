import turtle as t
from random import randint,random
def draw_squriel(steps,size,col,x,y):
    t.penup()
    t.goto(x,y)
    t.pendown()
    t.color(col)
    t.begin_fill()
    angle = 90 - (90/steps)
    for i in range(steps):
        t.forward(size)
        t.left(angle)
    t.end_fill()
t.Screen().bgcolor('dark blue')
t.hideturtle()
t.speed('fastest')
def draw_squriel_here(x,y):
    ranSps = randint(4,10)*4 + 2
    ranSize = randint(10,50)
    rancol = (random(),random(),random())
    draw_squriel(ranSps,ranSize,rancol,x,y)
t.onscreenclick(draw_squriel_here,1,False)
