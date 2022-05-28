import turtle
import random
#main code
turtle.speed("fastest")
while True:
    turtle.goto(random.random(),random.random())
    turtle.penup()
    turtle.pendown()
    turtle.color(random.random(),random.random(),random.random())
    turtle.begin_fill()
    turtle.forward(90)
    turtle.shape("turtle")
    turtle.color(random.random(),random.random(),random.random())
    turtle.pencolor(random.random(),random.random(),random.random())
    turtle.left(random.random())
    turtle.forward(90)
    turtle.left(random.random())
    turtle.pencolor(random.random(),random.random(),random.random())
    turtle.forward(random.random())
    turtle.left(random.random())
    turtle.pencolor(random.random(),random.random(),random.random())
    turtle.forward(90)
    turtle.end_fill()
    turtle.color(random.random(),random.random(),random.random())
