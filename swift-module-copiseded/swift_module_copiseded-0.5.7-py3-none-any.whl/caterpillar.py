import random
import turtle as t

t.bgcolor('yellow')

caterpillar=t.Turtle()
caterpillar.shape('square')
caterpillar.color('red')
caterpillar.speed(0)
caterpillar.penup()
caterpillar.hideturtle()

caterpillar2=t.Turtle()
caterpillar2.shape('square')
caterpillar2.color('sea green')
caterpillar2.speed(0)
caterpillar2.penup()
caterpillar2.hideturtle()

leaf=t.Turtle()
leaf_shape=((0,0),(14,2),(18,6),(20,20),(6,18),(2,14))
t.register_shape('leaf',leaf_shape)
leaf.shape('leaf')
leaf.color('green')
leaf.speed(0)
leaf.penup()
leaf.hideturtle()

game_started=False
text_turtle=t.Turtle()
text_turtle.write('Press SPACE to start',align='center',font=('Arial',16,'bold'))
text_turtle.hideturtle()

score_turtle=t.Turtle()
score_turtle.hideturtle()
score_turtle.speed(0)

def outside_window(caterpillar):
    left_wall=-t.window_width()/2
    right_wall=t.window_width()/2
    top_wall=t.window_height()/2
    bottom_wall=-t.window_height()/2
    (x,y)=caterpillar.pos()
    outside=x<left_wall or x>right_wall or \
            y<bottom_wall or y>top_wall
    return outside

def game_over():
    caterpillar.color('yellow')
    caterpillar2.color('yellow')
    leaf.color('yellow')
    t.penup()
    t.hideturtle()
    t.write('GAME OVER!',align='center',font=('Arial',30,'normal'))
    

def display_score(current_score):
    score_turtle.clear()
    score_turtle.penup()
    x=(t.window_width()/2)-50
    y=(t.window_height()/2)-50
    score_turtle.setpos(x,y)
    score_turtle.write(str(current_score),align='right',font=('Arial',40,'bold'))

def place_leaf():
    leaf.ht()
    leaf.setx(random.randint(-200,200))
    leaf.sety(random.randint(-200,200))
    leaf.st()

def start_game():
    global game_started
    if game_started:
        return
    game_started=True

    score=0
    text_turtle.clear()

    caterpillar_speed=2
    caterpillar_length=3
    caterpillar.shapesize(1,caterpillar_length,1)
    caterpillar.showturtle()
    caterpillar2.shapesize(1,caterpillar_length,1)
    caterpillar.setheading(180)
    caterpillar2.showturtle()
    display_score(score)
    place_leaf()

    while True:
        caterpillar.forward(caterpillar_speed)
        caterpillar2.forward(caterpillar_speed)
        if caterpillar.distance(leaf)<20 or caterpillar2.distance(leaf)<20:
            place_leaf()
            caterpillar_length=caterpillar_length+1
            caterpillar.shapesize(1,caterpillar_length,1)
            caterpillar2.shapesize(1,caterpillar_length,1)
            caterpillar_speed=caterpillar_speed+1
            score=score+10
            display_score(score)
        if outside_window(caterpillar) or outside_window(caterpillar2):
            game_over()
            break
def move_up():
    if caterpillar.heading()==0 or caterpillar.heading()==180:
        caterpillar.setheading(90)
        
def move_down():
    if caterpillar.heading()==0 or caterpillar.heading()==180:
        caterpillar.setheading(270)
        
def move_left():
    if caterpillar.heading()==90 or caterpillar.heading()==270:
        caterpillar.setheading(180)
        
def move_right():
    if caterpillar.heading()==90 or caterpillar.heading()==270:
        caterpillar.setheading(0)

def caterpillar2_move_up():
    if caterpillar2.heading()==0 or caterpillar2.heading()==180:
        caterpillar2.setheading(90)
        
def caterpillar2_move_down():
    if caterpillar2.heading()==0 or caterpillar2.heading()==180:
        caterpillar2.setheading(270)
        
def caterpillar2_move_left():
    if caterpillar2.heading()==90 or caterpillar2.heading()==270:
        caterpillar2.setheading(180)
        
def caterpillar2_move_right():
    if caterpillar2.heading()==90 or caterpillar2.heading()==270:
        caterpillar2.setheading(0)
        
t.onkey(start_game,'space')
t.onkey(move_up,'Up')
t.onkey(move_right,'Right')
t.onkey(move_down,'Down')
t.onkey(move_left,'Left')

t.onkey(caterpillar2_move_up,'1')
t.onkey(caterpillar2_move_right,'4')
t.onkey(caterpillar2_move_down,'2')
t.onkey(caterpillar2_move_left,'3')
t.listen()
t.listen()
t.mainloop()
