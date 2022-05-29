import turtle as t
from random import randint,random

def draw_star(points,size,col,x,y):
    t.penup()
    t.goto(x,y)
    t.pendown()
    angle = 180 - (180/points)
    t.color(col)
    t.begin_fill()
    for i in range(points):
        t.forward(size)
        t.right(angle)
    t.end_fill()

def draw_star_here(x,y):
    ranPts = randint(2,5)*2 + 1
    ranSize = randint(10,50)
    rancol = (random(),random(),random())
    draw_star(ranPts,ranSize,rancol,x,y)


#Main code
t.Screen().bgcolor('dark blue')
t.hideturtle()
t.speed('fastest')

'''
while True:
    ranPts = randint(2,5)*2 + 1
    ranSize = randint(10,50)
    rancol = (random(),random(),random())
    ranX = randint(-350,300)
    ranY = randint(-250,250)
    draw_star(ranPts,ranSize,rancol,ranX,ranY)
'''
t.onscreenclick(draw_star_here)
