import threading
import tkinter as tk
from tkinter import ttk
from tkinter import *

import time
import ctypes
def notify(text, link, duration, button_text):
    def download_file_worker():
        time.sleep(duration)
        root.destroy()


    def schedule_check(t):
        
        root.after(1000, check_if_done, t)


    def check_if_done(t):
        if not t.is_alive():
            pass
        else:
            schedule_check(t)

    def openweb():
        import webbrowser
        webbrowser.open(link, new=2)
        root.destroy()
    def download_file():
        textlength = len(text)

    
        Grid.columnconfigure(root, index = 0,
                             weight = 1)
         
        Grid.rowconfigure(root, 0,
                          weight = 1)
        button_1 = Label(root, text = text[0:26], font="bold" )
        if textlength > 26:

            button_extra = Label(root, text = text[26:50] + "..", font="bold" )
            button_extra.grid(row = 1,
                  column = 1, sticky = "NSEW") 
        button_1.grid(row = 0,
                  column = 1, sticky = "NSEW") 

        button_2 = Button(root, text = button_text,font="bold", command = openweb)

        button_2.grid(row = 2,
                  column = 1, sticky = "NSEW")    
        
        t = threading.Thread(target=download_file_worker)
        t.start()
        schedule_check(t)

    user32 = ctypes.windll.user32

    screensizex = user32.GetSystemMetrics(0)
    screensizey = user32.GetSystemMetrics(1)
    screensizex = str(screensizex - 200)
    screensizey = str(screensizey - 100)
    root = tk.Tk()
    root.geometry("200x100+"+screensizex +"+"+screensizey )
    root.overrideredirect(1)
    root.title("Download file with Tcl/Tk")
     



    download_file()
    root.mainloop()