#!python3
import os
from tkinter import *
from tkinter import messagebox
import tkinter.filedialog
from math import floor, ceil

from .Singleton import Singleton
from .Controller import controll
from .Video import Video
from .SuperButton import SuperButton
from .Config import config


class GUI(Singleton):
    def __init__(self) -> None:
        #root/window config
        self.root = Tk()
        self.root.title('Arduino Control' + ' - ' + config.environment.user)

        self.topmost = IntVar(value=config.topmost)
        self.toggle_topmost()
        
        #bind resize routine
        self.root.bind('<Configure>', self.on_resize)
        #configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        
        #window dimensions
        self.default_window_width = config.buttons_per_row * 80 + (config.buttons_per_row + 1) * 2 # buttons + padding
        self.default_height_no_video = 100 + (20 + 80) * ceil(len(config.pins) / config.buttons_per_row) # poti + (label + button) * n_rows + magic
        self.default_height_with_video = self.default_height_no_video + int(self.default_window_width * 9/16)

        #Top frame config
        self.top_frame = Frame(self.root)
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_rowconfigure(1, weight=0)
        #top left/center video
        if (config.video_allowed):
            self.video_enabled = IntVar()
            self.video_enabled.set(config.video_on_by_default)
            self.video_frame = Frame(self.top_frame)
            self.video_frame.grid(row=0, column=0, sticky="nsew")
            self.video_frame.grid_columnconfigure(0, weight=1)
            self.video_frame.grid_rowconfigure(0, weight=1)
            self.video = Video(frame=self.video_frame, source=config.environment.cam)
            self.toggle_video()

        #bottom frame config
        self.bottom_frame = Frame(self.root)
        self.bottom_frame.grid(row=1, sticky="nsew")
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)
        
        #top right potentiometer
        self.poti_frame = Frame(self.bottom_frame)
        self.poti_frame.grid(row=0, column=0)
        self.draw_poti(self.poti_frame)

        #bottom buttons
        self.button_frame = Frame(self.bottom_frame)
        self.button_frame.grid(row=1, sticky="nsew")
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(1, weight=1)
        for i in range(config.buttons_per_row):
            self.button_frame.grid_columnconfigure(i, weight=1)


        self.buttons = []
        for i, pin in enumerate(config.pins):
            self.buttons.append(SuperButton(self.button_frame, index = i, pin = pin))
            xlabel = Label(self.button_frame, text="Pin " + str(pin.external))
            row = 1 + 2 * floor(i / config.buttons_per_row) # only in uneven rows
            column = i - floor(i / config.buttons_per_row) * config.buttons_per_row # zero to buttons_per_row
            xlabel.grid(row=row, column=column, sticky="nsew")
        
        self.preset = StringVar(value="default")
        #radiobuttons cant call functions with arguments
        self.button_modes = []
        for pin in config.pins:
            self.button_modes.append(StringVar())
        self.import_io_preset()

        #add menubar
        self.draw_menubar()
        self.root.config(menu = self.menubar)

        #window geometry
        if config.video_on_by_default and config.video_allowed:
            window_height = self.default_height_with_video
        else:
            window_height = self.default_height_no_video

        self.center_window(self.root, self.default_window_width, window_height)
        self.root.resizable(False, False)
        

    def center_window(self, window: Tk, width: int = -1, height: int = -1) -> None:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        center_x = int(screen_width/2 - width / 2)
        center_y = int(screen_height/2 - height / 2)
        if width <= 0 or height <= 0:
            window.geometry(f'+{center_x}+{center_y}')
        else:
            window.geometry(f'{width}x{height}+{center_x}+{center_y}')
        
    #called with Tk.after for regular tasks
    def on_timer(self) -> None:
        controll.poll_inputs()
        self.root.after(config.pollrate, self.on_timer)
        pass

    #called on every resize event
    def on_resize(self, event) -> None:
        new_width = self.top_frame.winfo_width() - self.poti_label.winfo_width() - 5 #-5 to ensure this doesnt trigger resize itself
        self.poti_scale.configure(length=new_width)
        pass

    #called from menubar
    def about(self) -> None:
        about_window = Toplevel()        
        about_window.attributes('-topmost', 1)
        Label(about_window, text=config.about_content).pack(pady = 20, padx = 20)
        self.center_window(about_window)

    #called once during init
    def draw_poti(self, frame: Frame) -> None:
        frame.grid(row=0, column=0, sticky="sew")
        
        self.poti_label = Label(frame, text="Potentio-\nmeter")
        self.poti_label.grid(row=0, column=0, sticky="nsew")

        self.poti_val = IntVar(0)
        self.poti_scale = Scale(frame,
                                from_ = config.poti_lowest,
                                to = config.poti_highest,
                                resolution = config.poti_resolution,
                                variable = self.poti_val,
                                sliderlength = 15,
                                width = 30,
                                orient = HORIZONTAL,
                                command = controll.set_poti)
        self.poti_scale.grid(row=0, column=1, sticky="nsew")
        
        self.poti_scale.bind("<Button-4>", self.poti_on_mouse_wheel) # Linux up
        self.poti_scale.bind("<Button-5>", self.poti_on_mouse_wheel) # Linux down
    
    def poti_on_mouse_wheel(self, event) -> None:
        value = self.poti_val.get()
        if event.num == 4: # Linux up
            value += config.poti_mouse_wheel_steps
        elif event.num == 5: # Linux down
            value -= config.poti_mouse_wheel_steps
            
        if value > config.poti_highest:
            value = config.poti_highest

        if value < config.poti_lowest:
            value = config.poti_lowest

        self.poti_scale.set(value)

    #start Tk()
    def run(self) -> None:
        #initialize input polling
        self.root.after(config.pollrate, self.on_timer)
        #let Tk do it's thing
        self.root.mainloop()

    # called on mode change from menubar
    def set_button_modes(self, from_preset: bool = False) -> None:
        if not from_preset:
            self.preset.set(None)
        for i, button in enumerate(self.buttons):
            mode = self.button_modes[i].get()
            button.set_mode(mode)
        pass

    #called once during init
    def draw_menubar(self) -> None:
        self.menubar = Menu(self.root)

        filemenu = Menu(self.menubar, tearoff=0)

        if (config.video_allowed):
            filemenu.add_checkbutton(label="Video", variable=self.video_enabled, onvalue=1, offvalue=0 , command=self.toggle_video)
        filemenu.add_checkbutton(label="Always on Top", variable=self.topmost, onvalue=1, offvalue=0 , command=self.toggle_topmost)
        
        filemenu.add_command(label="Exit", command=self.root.quit)

        configmenu = Menu(self.menubar, tearoff=0)

        buttonmenus = []
        for i, pin in enumerate(config.pins):
            buttonmenus.append(Menu(configmenu, tearoff=0))
            for mode in config.pin_modes:
                buttonmenus[i].add_radiobutton(label=mode,
                                                variable=self.button_modes[i],
                                                value=mode,
                                                command=self.set_button_modes)
            configmenu.add_cascade(label="Pin" + str(pin.external), menu=buttonmenus[i])

        presetmenu = Menu(self.menubar, tearoff=0)

        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)

        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Config", menu=configmenu)
        self.menubar.add_cascade(label="Presets", menu=presetmenu)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        

        self.importmenu = Menu(presetmenu, tearoff=0)
        presetmenu.add_cascade(label="Import", menu=self.importmenu)
        presetmenu.add_command(label="Export", command=self.export_io_preset)

        
        for entry in os.listdir(config.pin_config_path):
            self.importmenu.add_radiobutton(label=entry, variable=self.preset, value=entry, command=self.import_io_preset)

    def toggle_video(self, new_status: int = -1) -> None:
        if new_status != -1:
            self.video_enabled.set(new_status)
        if self.video_enabled.get():
            self.root.geometry(f'{self.root.winfo_width()}x{self.default_height_with_video}')
            self.video.play()
            if config.video_warning:
                #start timeout
                if config.video_auto_off_ms > 0:
                    self.root.after(config.video_auto_off_ms, self.toggle_video, 0)
                #message user
                messagebox.showinfo(config.video_message_title, config.video_message)
        else:
            self.video.stop_video()
            self.root.geometry(f'{self.root.winfo_width()}x{self.default_height_no_video}')
            
    def toggle_topmost(self) -> None:
        self.root.attributes('-topmost', self.topmost.get())

    def export_io_preset(self) -> None:
        path = tkinter.filedialog.asksaveasfile(initialdir=config.pin_config_path)
        if path == None:
            return
        else:
            with open(path.name, "w") as file:
                for pin in self.button_modes:
                    file.writelines(pin.get() + "\n")
            file_name = os.path.basename(str(path.name))
            self.preset.set(file_name)
            self.importmenu.add_radiobutton(label=file_name, variable=self.preset, value=file_name, command=self.import_io_preset)

    def import_io_preset(self) -> None:
        with open(os.path.join(config.pin_config_path, self.preset.get())) as preset_file:
            pin = []
            for line in preset_file:
                pin.append(line.strip())
            for i, mode in enumerate(pin):
                self.button_modes[i].set(mode)
        self.set_button_modes(from_preset=True)

    



if __name__ == "__main__":
    import sys as sys
    gui = GUI()
    gui.run()
    controll.on_exit()
    sys.exit(0)