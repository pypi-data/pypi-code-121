import tkinter as tit
from tkinter import simpledialog,messagebox,Canvas
from pygame import mixer
import time
from os.path import join

root = tit.Tk()
root.title('PHYSICAL CONDITION APPLET')
c = tit.Canvas(root,width=800,height=800,bg='black')
c.pack()
c.create_text(50,50,anchor='nw',fill='orange',\
              font='Arial 28 bold underline',text='Welcome to the physical condition applet')
mixer.init()
beep=mixer.Sound('200bpm%E6%AD%BB%E4%BA%A1%E4%B9%8B%E6%9B%B2 2.flac')
beep.play()
time.sleep(5)

def write():
        print('Creating a new file')
        path = input('What is you path(/User/you input(path)/Desktop) name?')
        name = 'APPLET'+'.txt'  # Name of text file coerced with +.txt
        try:
           file = open(name,'w')
           file.write('APPLET.txt","influenza/A good rest is all you need,and drink more water.\ncommon cold/Please drink more hot water,and wear more warm clothes.\nphysical fitness/Please drink more hot water to prevent cold.\nrun a fever/Please go to the hospital for treatment.')
           file.close()

        except Exception as e:
            print(e)
            print('Something went wrong! Cannot tell what?')
def get_name():
    name = tit.simpledialog.askstring('Visiting patients','What\'s your name: ')
    return name

def get_task():
    task = tit.simpledialog.askstring('Task','What\'s your physical condition?: ')
    return task

def get_physical_condition():
    gpc = tit.simpledialog.askstring('Task','Do you have any other discomfort? ')
    return gpc

def yes_text():
    Yes_text = tit.simpledialog.askstring('Task','Tell me about it,please! ')
    return Yes_text

def read_from_file():
    try:
        with open('APPLET.txt') as file:
            for line in file:
                line = line.rstrip('\n')
                condition,solution = line.split('/')
                the_physical_condition[condition] = solution
    except Exception as e:
        print(e)
        print("请下载源文件，并拖放到文件夹下")
def write_to_file(solution_name,condition_name):
    try:
        with open('APPLET.txt','a')as file:
            file.write('\n'+ solution_name + '/' + condition_name)
    except Exception as e:
        print(e)
        print("请下载源文件，并拖放到文件夹下")
            
    
write()
the_physical_condition={}
read_from_file()
name=get_name()
task=get_task()
gpc=get_physical_condition()
ytt=yes_text()

while True:
    name
    c.create_text(50,100,anchor='w',fill='Thistle',\
                  font='Arial 28 bold',text='hello, %s' % (name))
    task
    if task == 'run a fever':
        not_bad_message=('Please go to the hospital for treatment.')
        c.create_text(50,130,anchor='w',fill='lightblue',\
                      font='Arial 28 bold',text=not_bad_message)
        gpc
    elif task == 'common cold':
        good_message='Please drink more hot water,and wear more warm clothe\n-s,around the scarf.'
        c.create_text(50,130,anchor='w',fill='lightblue',\
                      font='Arial 28 bold',text=good_message)
        gpc
    else:
        display='Please drink more hot water to prevent cold.'
        c.create_text(50,130,anchor='w',fill='lightblue',\
                      font='Arial 28 bold',text=display)
        gpc
    if gpc =='yes':
        ytt
    else:
        break
    if ytt in the_physical_condition:
        result = the_physical_condition[ytt]
        c.create_text(50,160,anchor='w',fill='lightblue',\
                      font='Arial 28 bold',text=ytt+'ought to '+result+'!')
    else:
        new_solution = simpledialog.askstring('Teach me','I don\'t know!Wha\'s the solution of '+ytt+'?')
        the_physical_condition[ytt] = new_solution
        write_to_file(ytt,new_solution)
root.mainloop()

            
            

