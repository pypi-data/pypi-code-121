import threading
import tkinter as tk
from tkinter import ttk
from tkinter import *

import time
import ctypes
rootdestroyed = False
try:
    def notify(text, link, duration, button_text):
        def download_file_worker():
            time.sleep(duration)
            if rootdestroyed == False:
                try:
                    root.destroy()
                except Exception as e:
                    pass

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
            rootdestroyed = True
        def download_file():
            textlength = len(text)

        
            Grid.columnconfigure(root, index = 0,
                                 weight = 1)
             
            Grid.rowconfigure(root, 0,
                              weight = 1)
            button_1 = Label(root, text = text[0:42] + "..", font="bold" )
           
            button_1.grid(row = 0,
                      column = 0) 

            button_2 = Button(root, text = button_text,font="bold", command = openweb)

            button_2.grid(row = 2,
                      column = 0, sticky = "NSEW")    
            
            t = threading.Thread(target=download_file_worker)
            t.start()
            schedule_check(t)

        user32 = ctypes.windll.user32

        screensizex = user32.GetSystemMetrics(0)
        screensizey = user32.GetSystemMetrics(1)
        screensizex = str(screensizex - 300)
        screensizey = str(screensizey - 100)
        root = tk.Tk()
        root.geometry("300x100+"+screensizex +"+"+screensizey )

        root.overrideredirect(1)
        root.title("Download file with Tcl/Tk")
         



        download_file()
        root.mainloop()
 
except Exception as e:
    print("error occured contact us at - https://progbits.xyz for support")