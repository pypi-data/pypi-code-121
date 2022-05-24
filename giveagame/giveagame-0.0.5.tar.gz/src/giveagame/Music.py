from threading import Thread
from playsound import playsound

class Music:
    def __init__(self, music_file, loop_music):
        self.music_file = music_file
        self.loop_music = loop_music

    def music(self):
        if self.loop_music == True:
            while self.loop_music:
                playsound(self.music_file, block=False)
        else:
            playsound(self.music_file, block=True)

    def start(self):
        self.Thread(target=music, daemon=True, name="musicClassThread").start()
