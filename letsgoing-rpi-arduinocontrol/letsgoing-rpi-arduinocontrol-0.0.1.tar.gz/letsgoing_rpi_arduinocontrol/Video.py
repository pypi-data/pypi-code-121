from tkinter import Frame
import vlc

class Video():
    def __init__(self, frame, source: str) -> None:
        self.frame = frame
        self.source = source
        pass

    def draw_video(self) -> None:
        self.videoFrame = Frame(self.frame)
        self.videoFrame.grid_columnconfigure(0, weight=1)
        self.videoFrame.grid_rowconfigure(0, weight=1)
        self.videoFrame.grid(row=0, column=0, sticky="nsew")

        self.vlc = vlc.Instance("--no-xlib")
        self.player = self.vlc.media_player_new()
        self.Media = self.vlc.media_new(self.source)
        self.player.set_media(self.Media)
        self.player.set_xwindow(self.videoFrame.winfo_id())
        if not self.player.get_media():
            self.videoFrame.config(bg="red")
        pass

    def stop_video(self) -> None:
        try:
            self.player.stop()
            self.vlc.release()
        except:
            #self.player not defined -> no video
            pass
        pass

    def play(self) -> None:
        self.draw_video()
        self.player.play()
        pass            



if __name__ == "__main__":
    from tkinter import Tk
    def centerWindow(window, width = -1, height = -1):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        center_x = int(screen_width/2 - width / 2)
        center_y = int(screen_height/2 - height / 2)
        if width <= 0 or height <= 0:
            window.geometry(f'+{center_x}+{center_y}')
        else:
            window.geometry(f'{width}x{height}+{center_x}+{center_y}')

    root = Tk()
    root.attributes('-topmost', 1)
    centerWindow(root, 960, 540)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    #video = VIDEO(root, "example.mp4")
    #video = VIDEO(root, "v4l2:///dev/video0")
    video = Video(root, "http://localhost:8080/?action=stream")

    video.play()
    root.mainloop()
    video.stop_video()