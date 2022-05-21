import turtle
import threading

turtle.ht()
turtle.title('pjer')

class sprite():
  def __init__(self, model, speed, size):
      turtle.pencolor('#000000')
      self.model = model
      turtle.speed(speed)
      self.speed=speed
      self.size=size
    
  class classic():
    def __init__(self, model, speed):
      turtle.pencolor('#000000')
      self.model = model
      turtle.speed(speed)
    def create(self, x, y):
        self.id = {
          "x":x,
          "y":y
        }

    def move(self,ox,oy,xc,yc,diffrence):
      self.undraw(ox,oy,diffrence)
      self.draw(ox+(xc*diffrence),oy+(yc*diffrence),diffrence)
  
    def draw(self,x,y, diffrence):
      turtle.pencolor('#000000')
      turtle.penup()
      turtle.goto(x,y)
      turtle.pensize(diffrence)
      turtle.ht()
      for i in range(len(self.model)):
        if i==4 or i==8 or i==12:
          turtle.penup()
          turtle.back(4*diffrence)
          turtle.right(90)
          turtle.forward(diffrence)
          turtle.left(90)
        
        if self.model[i]==1:
          turtle.pendown()
          turtle.forward(0)
          turtle.penup()
          turtle.forward(diffrence)
        elif self.model[i]==0:
          turtle.penup()
          turtle.forward(diffrence)
        
        turtle.ht()

    def undraw(self,x,y,diffrence):
      turtle.penup()
      turtle.goto(x,y)
      turtle.pencolor('#ffffff')
      for i in range(len(self.model)):
        if i==4 or i==8 or i==12:
          turtle.penup()
          turtle.back(4*diffrence)
          turtle.right(90)
          turtle.forward(diffrence)
          turtle.left(90)
        
        if self.model[i]==1:
          turtle.pendown()
          turtle.forward(0)
          turtle.penup()
          turtle.forward(diffrence)
        elif self.model[i]==0:
          turtle.penup()
          turtle.forward(diffrence)
        
        turtle.ht()

  
  def draw(self,x,y):
    self.x = x
    self.y = y
    t1t=[]
    t2t=[]
    t3t=[]
    t4t=[]
    for i in range(len(self.model)):
      if len(self.model) !=16:
        return print('Error Model has to many or not enough characters')
      if i <=3:
        t1t.append(self.model[i])
      elif i <= 7 and i > 3:
        t2t.append(self.model[i])
      elif i <= 11 and i > 7:
        t3t.append(self.model[i])
      elif i <= 15 and i > 11:
        t4t.append(self.model[i])
    t1=turtle.Turtle()
    t2=turtle.Turtle()
    t3=turtle.Turtle()
    t4=turtle.Turtle()
    tl=[t1,t2,t3,t4]
    for t in tl:
      t.penup()
      t.ht()
    t1.goto(x,y)
    t2.goto(x,y-(self.size))
    t3.goto(x,y-(self.size*2))
    t4.goto(x,y-(self.size*3))
    for t in tl:
      t.shape('square')
      t.pencolor('#000000')
      t.speed(self.speed)
      t.ht()
      t.pensize(self.size)
      if t==t1:
        wt = threading.Thread(target=turtleTask(t1t,t,self.size), args=(1,), daemon=True)
        wt.start()
      elif t==t2:
        xt = threading.Thread(target=turtleTask(t2t,t,self.size), args=(1,), daemon=True)
        xt.start()
      elif t==t3:
        yt = threading.Thread(target=turtleTask(t3t,t,self.size), args=(1,), daemon=True)
        yt.start()
      elif t==t4:
        zt = threading.Thread(target=turtleTask(t4t,t,self.size), args=(1,), daemon=True)
        zt.start()

  def undraw(self,x,y):
    t1t=[]
    t2t=[]
    t3t=[]
    t4t=[]
    for i in range(len(self.model)):
      if len(self.model) !=16:
        return print('Error Model has to many or not enough characters')
      if i <=3:
        t1t.append(self.model[i])
      elif i <= 7 and i > 3:
        t2t.append(self.model[i])
      elif i <= 11 and i > 7:
        t3t.append(self.model[i])
      elif i <= 15 and i > 11:
        t4t.append(self.model[i])
    t1=turtle.Turtle()
    t2=turtle.Turtle()
    t3=turtle.Turtle()
    t4=turtle.Turtle()
    tl=[t1,t2,t3,t4]
    for t in tl:
      t.penup()
      t.ht()
    t1.goto(x,y)
    t2.goto(x,y-(self.size))
    t3.goto(x,y-(self.size*2))
    t4.goto(x,y-(self.size*3))
    for t in tl:
      t.pencolor('#ffffff')
      t.speed(self.speed)
      t.ht()
      t.pensize(self.size+4)
      t.ht()
      if t==t1:
        wt = threading.Thread(target=turtleTask(t1t,t,self.size), args=(1,), daemon=True)
        wt.start()
      elif t==t2:
        xt = threading.Thread(target=turtleTask(t2t,t,self.size), args=(1,), daemon=True)
        xt.start()
      elif t==t3:
        yt = threading.Thread(target=turtleTask(t3t,t,self.size), args=(1,), daemon=True)
        yt.start()
      elif t==t4:
        zt = threading.Thread(target=turtleTask(t4t,t,self.size), args=(1,), daemon=True)
        zt.start()
  def move(self,newX,newY):
    self.undraw(self.x,self.y)
    self.draw(newX,newY)
    self.x = newX
    self.y = newY
class prefs():
  def setTitle(title):
    turtle.title(title)

  def setIcon(icoPath):
    root = turtle.Screen()._root
    root.iconbitmap(icoPath)

  class screen():
    def screenSize(height,width):
      turtle.screensize(canvwidth=width, canvheight=height)
    def BGcolor(color):
      turtle.bgcolor()
  
def turtleTask(task,t,size):
    taskCheck=[]
    if not len(task)==4:
      return print('Invalid task')
    for i in range(len(task)):
      taskRead=task[i]
      taskCheck.append(taskRead)
      if taskRead==0:
        t.penup()
      elif taskRead==1:
        t.pendown()
      else:
        return print('Invalid character in task')
      t.forward(0)
      t.penup()
      t.forward(size)
    if not taskCheck==task:
        return print('Something went wrong trying to generate task; Given task: '+str(task)+' resulted in: '+str(taskCheck))