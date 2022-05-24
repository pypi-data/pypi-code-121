from giveagame.sprites.Sprite import *
from giveagame.Coords import *
from tkinter import PhotoImage

class DoorSprite(Sprite):
    def __init__(self, game,  x, y, width, height):
        Sprite.__init__(self, game)
        self.closed_door = PhotoImage(file="imgs/door1.gif")
        self.open_door = PhotoImage(file="imgs/door2.gif")
        self.image = game.canvas.create_image(x, y, \
                                              image=self.closed_door, anchor='nw')
        self.coordinates = Coords(x, y, x + (width / 2), y + height)
        self.endgame = True

    def opendoor(self):
        self.game.canvas.itemconfig(self.image, image=self.open_door)
        self.game.tk.update_idletasks()
        
    def closedoor(self):
        self.game.canvas.itemconfig(self.image, image=self.closed_door)
        self.game.tk.update_idletasks()
