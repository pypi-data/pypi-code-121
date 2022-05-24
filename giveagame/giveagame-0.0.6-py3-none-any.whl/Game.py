from tkinter import *
from giveagame.Coords import *
from giveagame.sprites.DoorSprite import *
from giveagame.sprites.MovingPlatformSprite import *
from giveagame.sprites.PlatformSprite import *
from giveagame.sprites.Sprite import *
from giveagame.sprites.StickFigureSprite import * 

class Game:
	def __init__(self, title, cw, ch, bg_img):
		self.tk = Tk()
		self.tk.title(title)
		self.tk.resizable(0, 0)
		self.tk.wm_attributes("-topmost", 1)
		self.canvas = Canvas(self.tk, width=cw, height=ch, \
			highlightthickness=0)
		self.canvas.pack()
		self.tk.update()
		self.canvas_height = ch
		self.canvas_width = cw
		self.bg = PhotoImage(file=bg_img)
		self.icon = PhotoImage(file="imgs/icon.gif")
		self.tk.iconphoto(False, self.icon)
		w = self.bg.width()
		h = self.bg.height()
		for x in range(0, 5):
			for y in range(0, 5):
				self.canvas.create_image(x * w, y * h, \
					image=self.bg, anchor='nw')
		self.sprites = []
		self.running = True

	def mainloop(self):
		while 1:
			if self.running == True:
				for sprite in self.sprites:
					sprite.move()
			self.tk.update_idletasks()
			self.tk.update()
			time.sleep(0.01)
