import turtle as t
from pygame import mixer
import time

def rectangle(horizontal,vertical,color):
    t.pendown()
    t.pensize(1)
    t.color(color)
    t.begin_fill()
    for counter in range(1,3):
        t.forward(horizontal)
        t.right(90)
        t.forward(vertical)
        t.right(90)
    t.end_fill()
    t.penup()

t.penup()
t.speed(0)
t.bgcolor('Dodger blue')
t.shape('turtle')

#feet
t.goto(-100,-150)
rectangle(50,20,'hot pink')
t.goto(-30,-150)
rectangle(50,20,'hot pink')

#legs
t.goto(-25,-50)
rectangle(15,100,'skyblue1')
t.goto(-55,-50)
rectangle(-15,100,'skyblue1')

#body
t.goto(-90,100)
rectangle(100,150,'hot pink')

#arms
t.goto(-150,70)
rectangle(60,15,'pink')
t.goto(-150,110)
rectangle(15,40,'white')

t.goto(10,70)
rectangle(60,15,'pink')
t.goto(55,110)
rectangle(15,40,'white')

#neck
t.goto(-50,120)
rectangle(15,20,'white')

#head
t.goto(-85,170)
rectangle(80,50,'pink')

#eyes
t.goto(-60,160)
rectangle(30,10,'white')
t.goto(-58,160)
rectangle(5,5,'goldenrod')
t.goto(-41,160)
rectangle(5,5,'goldenrod')

#mouth
t.goto(-65,135)
t.left(6)
rectangle(40,5,'red')

#middle finger
t.goto(-145,120)
rectangle(3,10,'white')

t.write("你过来呀！",align='right',font=('Arial',40,'bold'))
t.hideturtle()
