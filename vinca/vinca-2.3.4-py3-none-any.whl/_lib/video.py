import tkinter as Tk
from subprocess import run

TERMINAL_BACKGROUND = '#000000'

class ActiveWindow:
        def __init__(self):
                # use xdotool to query basic info about the terminal's geometry
                out = run(['xdotool','getactivewindow','getwindowgeometry'], capture_output=True)
                # TODO warn user if they do not have xdotool installed
                # parse output and calculate references
                out = str(out.stdout, encoding='utf-8')
                window_id, abs_pos, geometry = out.splitlines()
                self.left, self.top = abs_pos.split()[1].split(',')
                self.left, self.top = int(self.left), int(self.top)
                self.width, self.height = geometry.split()[1].split('x')
                self.width, self.height = int(self.width), int(self.height)
                self.right = self.left + self.width
                self.bottom = self.top + self.height
                self.center_x = self.left + self.width // 2
                self.center_y = self.top + self.height // 2

class DisplayImage:
        """A simple class to draw an image to the screen.
        MUST BE PNG
        There are two methods: show and close.
        It can also be invoked as a context manager."""

        def __init__(self, *, image_path=None, data_bytes=None):
                self.image_path = image_path
                self.data_bytes = data_bytes

        def show(self):
        # get geometry information about the active terminal
                aw = ActiveWindow()

                self.root = Tk.Tk()

                if self.image_path:
                        self.image = Tk.PhotoImage(file=self.image_path)
                elif self.data_bytes:
                        self.image = Tk.PhotoImage(data=self.data_bytes)
                # warning: images cannot be stored as local variables
                # of a function or else there is risk of them being
                # destroyed by premature garbage collection.

                # we want to center the image at the bottom of the terminal
                # with a 40 pixel margin on all sides
                # if the image is too big we will only see part of it
                # but the window will fit inside the active terminal
                img_height = self.image.height()
                img_width = self.image.width()
                margin = 40
                left = max(aw.left + margin, aw.center_x - img_width // 2)
                right = min(aw.right - margin, aw.center_x + img_width // 2)
                width = right - left
                bottom = aw.bottom - margin
                top = max(aw.top + margin, bottom - img_height)
                height = bottom - top
                self.root.geometry(f'{width}x{height}+{left}+{top}')

                # we do not want to let the window manager make decisions
                self.root.overrideredirect(True)

                # draw the image on a canvas
                # place our canvas to occupy the whole window
                self.canvas = Tk.Canvas(self.root, width=width, height=height)
                self.canvas.config(bg=TERMINAL_BACKGROUND)
                self.canvas.create_image(0,0, anchor=Tk.NW, image=self.image)
                self.canvas.place(x=-1,y=-1, height=height+2, width=width+2)

                # manually draw our window to the screen
                # it is common to see root.mainloop(), but
                # that is unneeded as there is not UX here.
                self.root.update()

        def close(self):
                assert self.root
                self.root.destroy()

        def __enter__(self):
                if self.data_bytes or (self.image_path and self.image_path.exists()):
                        self.show()

        def __exit__(self, *exception_args):
                if self.data_bytes or (self.image_path and self.image_path.exists()):
                        self.close()
