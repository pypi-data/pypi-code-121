# coding: utf8
# 

import os, requests, webbrowser, selenium, time
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

import sys
import pandas as pd

exit()

"""
def callback(icon):
    image = Image.new('RGBA', (128,128), (255,255,255,255)) # create new image
    percent = 100
    while True:
        img = image.copy()
        d = ImageDraw.Draw(img)
        d.rectangle([0, 128, 128, 128-(percent * 128) / 100], fill='blue')
        icon.icon = img
        time.sleep(1)
        percent -= 5
        if percent < 0:
            percent = 100

image = Image.open("src/alpha.png") #Battery Status Full
icon = Icon("Test Icon 1", image)

icon.visible = True
icon.run(setup=callback)
"""

#rep = stitch.Stitch.getWebsites()

state = True

def on_clicked(icon, item):
    global state
    state = not item.checked

    if item.checked:
        api.start()

def exitAlpha():
    icon.stop()
    
global icon
icon        = Icon('test name')
icon.icon   = Image.open("src/alpha.png")
icon.menu   = Menu(
        MenuItem('Alpha',None),
        MenuItem(
            'Running',
            on_clicked,
            checked=lambda item: state),
        MenuItem('Exit',exitAlpha),
    )
    
icon.run()