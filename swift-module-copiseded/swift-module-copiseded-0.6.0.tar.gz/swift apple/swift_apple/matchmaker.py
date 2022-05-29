import random
import time
from tkinter import Tk,Button,DISABLED,messagebox
from pygame import mixer

mixer.init()
beep=mixer.Sound('200bpm%E6%AD%BB%E4%BA%A1%E4%B9%8B%E6%9B%B2 2.flac')
beep.play()
time.sleep(5)

def show_symbol(x,y):
    global first
    global previousX,previousY
    global moves
    global pairs
    buttons[x,y]['text'] = button_symbols[x,y]
    buttons[x,y].update_idletasks()

    if first:
        previousX = x
        previousX = y
        first = False
        moves = moves+1
    elif previousX != x or previousY != y:
        if buttons[previousX,previousY]['text'] != buttons[x,y]['text']:
            time.sleep(0.5)
            buttons[previousX,previousY]['text'] = ''
            buttons[x,y]['text']=''
        else:
            buttons[previousX,previousY]['command']=DISABLED
            buttons[x,y]['command']=DISABLED
            pairs = pairs+1
            if pairs == len(buttons)/2:
                messagebox.showinfo('Matching','number of moves: '+
                                    str(moves),command=close_window)
        first = True

def close_window(self):
    root.destroy()

root=Tk()
root.title('Matchmaker')
root.resizable(width=False,height=False)

buttons = {}
first = True
previousX = 0
previousY = 0
moves = 0
pairs = 0
button_symbols = {}
symbols = [u'\u2702',u'\u2702',u'\u2705',u'\u2705',u'\u2708',u'\u2708',\
        u'\u2709',u'\u2709',u'\u270A',u'\u270A',u'\u270B',u'\u270B',\
        u'\u270C',u'\u270C',u'\u270F',u'\u270F',u'\u2712',u'\u2712',\
        u'\u2714',u'\u2714',u'\u2716',u'\u2716',u'\u2728',u'\u2728',\
        u'\u2733',u'\u2733',u'\u2734',u'\u2734',u'\u2744',u'\u2744']
random.shuffle(symbols)

for x in range(6):
    for y in range(5):
        button = Button(command=lambda x=x,y=y: show_symbol(x,y),width=3,height=3)
        button.grid(column=x,row=y)
        buttons[x,y] = button
        button_symbols[x,y] = symbols.pop()

root.mainloop()
