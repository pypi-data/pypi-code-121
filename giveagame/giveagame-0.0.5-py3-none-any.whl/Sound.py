from giveagame import Music
from threading import Thread
from playsound import playsound

class Sound(Music):
    def __init__(self, music_file):
        self.music_file = music_file
        self.loop_music = False

    def start(self):
        self.Thread(target=music, daemon=True, name="soundClassThread").start()
