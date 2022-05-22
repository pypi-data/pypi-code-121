import turtle
import random


class Pong:

    def Pong():
        print('''

         [1] Classic
         [2] Black and Greem
         [3] Black and Red
         [4] Black and blue
         [5] White and Black
         [6] Red and Black
         [7] Blue and Black
         [r] Random Theme
        ''')
        theme = input("Choose a Theme: ")
        if theme == "r":
            t = random.randrange(1, 7)
            theme = str(t)
    
        wn = turtle.Screen()
        wn.title("Pong")
        if theme == "5":
            wn.bgcolor("white")
        elif theme == "6":
            wn.bgcolor("red")
        elif theme == "7":
            wn.bgcolor("blue")
        else:
            wn.bgcolor("black")
        wn.setup(width=800, height=600)
        wn.tracer(0)

        score_a = 0
        score_b = 0



        paddle_a = turtle.Turtle()
        paddle_a.speed(0)
        paddle_a.shape("square")

        paddle_a.penup()
        paddle_a.goto(-350, 0)
        paddle_a.shapesize(stretch_wid=5, stretch_len=1)

        paddle_b = turtle.Turtle()
        paddle_b.speed(0)
        paddle_b.shape("square")

        paddle_b.penup()
        paddle_b.goto(350, 0)
        paddle_b.shapesize(stretch_wid=5, stretch_len=1)

        ball = turtle.Turtle()
        ball.speed(0)
        ball.shape("square")

        ball.penup()
        ball.goto(0, 0)
        ball.dx = 0.2
        ball.dy = 0.2

        pen = turtle.Turtle()
        pen.speed(0)
        if theme == "1":
            pen.color("white")
        elif theme == "2":
            pen.color("green")
        elif theme == "3":
            pen.color("red")
        elif theme == "4":
            pen.color("blue")
        elif theme == "5":
            pen.color("black")
        else:
            pen.color("black")
        pen.penup()
        pen.hideturtle()
        pen.goto(0, 260)
        pen.write("Player A: 0  Player B: 0", align="center", font=("Courier", 24, "normal"))

        if theme == "1":
            paddle_a.color("white")
            paddle_b.color("white")
            ball.color("white")

        elif theme == "2":
            paddle_a.color("green")
            paddle_b.color("green")
            ball.color("green")

        elif theme == "3":
            paddle_a.color("red")
            paddle_b.color("red")
            ball.color("red")

        elif theme == "4":
            paddle_a.color("blue")
            paddle_b.color("blue")
            ball.color("blue")
        elif theme == "5":
            paddle_a.color("black")
            paddle_b.color("black")
            ball.color("black")
        else:
            paddle_a.color("black")
            paddle_b.color("black")
            ball.color("black")

        def paddle_a_up():
            y = paddle_a.ycor()
            y += 24
            paddle_a.sety(y)
        def paddle_a_down():
            y = paddle_a.ycor()
            y -= 24
            paddle_a.sety(y)
    
        def paddle_b_up():
            y = paddle_b.ycor()
            y += 24
            paddle_b.sety(y)
        def paddle_b_down():
            y = paddle_b.ycor()
            y -= 24
            paddle_b.sety(y)
    
        wn.listen()
        wn.onkeypress(paddle_a_up, "w")
        wn.onkeypress(paddle_a_down, "s")
        wn.onkeypress(paddle_b_up, "Up")
        wn.onkeypress(paddle_b_down, "Down")

        while True:
            wn.update()
            ball.setx(ball.xcor() + ball.dx)
            ball.sety(ball.ycor() + ball.dy)
    
        if ball.ycor() > 290:
            ball.sety(290)
            ball.dy *= -1
        

        if ball.ycor() < -290:
            ball.sety(-290)
            ball.dy *= -1
    
        if ball.xcor() > 390:
            ball.goto(0, 0)
            ball.dx *= -1
            score_a += 1
            pen.clear()
            pen.write("Player A: {}  Player B: {}".format(score_a, score_b), align="center", font=("Courier", 24, "normal"))
            speed = 0
            speed += 1
            ball.speed(speed)
        if ball.xcor() < -390:
            ball.goto(0, 0)
            ball.dx *= -1
            score_b += 1
            pen.clear()
            pen.write("Player A: {}  Player B: {}".format(score_a, score_b), align="center", font=("Courier", 24, "normal"))
            speed = 0
            speed += 1
            ball.speed(speed)
        
    
        if (ball.xcor() > 340 and ball.xcor() < 350) and (ball.ycor() < paddle_b.ycor() + 40 and ball.ycor() > paddle_b.ycor() -40):
            ball.setx(340)
            ball.dx *= -1
        
        if (ball.xcor() < -340 and ball.xcor() > -350) and (ball.ycor()< paddle_a.ycor() + 40 and ball.ycor() > paddle_a.ycor() -40):
            ball.setx(-340)
            ball.dx *= -1
    
 