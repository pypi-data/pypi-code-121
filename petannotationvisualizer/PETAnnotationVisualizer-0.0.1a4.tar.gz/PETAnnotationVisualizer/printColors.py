from Colors import Annotator_Colors
import tkinter as tk

class PrintColors(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        for color in list(Annotator_Colors.values())[210:]:
            tk.Label(self.parent, text=color, bg=color,  anchor='w').pack(fill='x')

window = tk.Tk()

program = PrintColors(window)
# Start the GUI event loop
program.mainloop()
