'''
Inputs:
    cover (path or https)
    audio (path or https)
    artists ("main_artist" or "main_artist, feature1, feature2...")
    song (name)
    reverb (level 0 to 10)
    speed (level -10 to 10)
    upload (yes/no)
    compress (yes/no)
    toptext (yes/no)

Example code:

client_secrets='/home/user/secrets/client_secrets.json'
cover = 'https://www.rollingstone.com/wp-content/uploads/2020/08/100gecs.jpg'
audio = 'https://youtu.be/2PWMiy4RysI'
artists = '100 gecs'
song = 'Doritos & Fritos'
reverb = '10'
speed = '-10'

video = BuildVideo(song=song, artists=artists, audio=audio,
            cover=cover, speed=speed, reverb=reverb)
# (can use video.custom_toptext('text') to change the top text)
video.export_audio()
video.export_images()
video.export_video()
video.upload_youtube(client_secrets=client_secrets)
video.finish() # (could use compress=False to disable compression)
'''

from musicvideos import images, audio_mod, video
from musicvideos_extras import tools, youtube

import shutil
import os

class BuildVideo:
    def __init__(self,
                song='',
                artists='',
                cover=None,
                audio=None,
                speed=0,
                reverb=0,
                remove_toptext=False):
        '''
        This function will setup everything
        for the video images, audio and export to
        work properly :)
        '''

        if cover is None or audio is None:
            return print('\033[91m✘ Build necessary variables missing (cover or audio)\033[0m')

        # Speed, reverb and song variables
        self.speed = int(speed)
        self.reverb = int(float(reverb) * 10)
        self.song = song.strip()

        self.files = {
            'download_cover' : f'cover {song}.png',
            'download_audio' : f'original {song}.wav',
            'main_image' : f'image {song}.png',
            'thumb_image' : f'thumb {song}.png',
            'video_file' : f'video {song}.mp4',
            'folder' : '',
            'full_folder' : '',
            'mod_audio' : ''
        }

        # Save original directory
        self.orig_dir = os.getcwd()

        # Artists separation
        if ',' in artists:
            self.artists = artists.split(',')
            for i, j in enumerate(self.artists):
                self.artists[i] = j.strip()
                if self.artists[i] == '':
                    self.artists.pop(i)
        else:
            self.artists = [artists]

        # Speed Messages
        if self.speed > 0:
            speed_text = 'Nightcore'
        elif self.speed < 0:
            speed_text = 'Slowed'
        else:
            speed_text = ''

        self.speed_text = speed_text

        # Reverb Messages
        if self.reverb > 0:
            reverb_text = 'Reverb'
        else:
            reverb_text = ''

        self.reverb_text = reverb_text

        # Modified audio filename and folder name
        if speed_text != '':
            self.files['mod_audio'] = f'{speed_text.lower()} {song}.wav'
            self.files['folder'] = f'{speed_text.lower()} {song}'
        elif reverb_text != '':
            self.files['mod_audio'] = f'{reverb_text.lower()} {song}.wav'
            self.files['folder'] = f'{reverb_text.lower()} {song}'
        else:
            self.files['mod_audio'] = f'monkaS?? {song}.wav'
            self.files['folder'] = f'monkaS?? {song}'

        # Setup the full path folder directory variable (for the youtube upload)
        self.files['full_folder'] = f'{self.orig_dir}/{self.files["folder"]}'

        # Top Text
        toptext_components = []
        try:
            if speed_text != '':
                toptext_components.append(speed_text)
            if reverb_text != '':
                toptext_components.append(reverb_text)
            if len(toptext_components) > 0:
                toptext_plus = ' + '.join(toptext_components)
                self.toptext_plus = f'({toptext_plus})'
                toptext_and = ' and '.join(toptext_components)
                self.toptext_and = f'({toptext_and})'
            else:
                self.toptext_plus = ''
                self.toptext_and = ''
            if remove_toptext:
                self.toptext_plus = ''
                self.toptext_and = ''
        except:
            self.toptext_plus = ''
            self.toptext_and = ''

        # This will try to create the folder, but if it already
        # exists it will create one inside that one
        inside = False
        while not inside:
            try:
                os.mkdir(self.files['folder'])
                os.chdir(self.files['folder'])
                inside = True
            except Exception as e:
                print(f'Folder already exists, creating a new one inside...')
                os.chdir(self.files['folder'])
                self.files['full_folder'] += f'/{self.files["folder"]}'

        # Download cover if it is a link otherwise copy it to the folder
        if tools.check_if_url(cover):
            tools.download_image(cover, output=self.files['download_cover'])
            self.cover = self.files['download_cover']
        else:
            os.chdir(self.orig_dir)
            shutil.copyfile(cover,
                        f'{self.files["full_folder"]}/{self.files["download_cover"]}')

            os.chdir(self.files['full_folder'])

        self.cover = self.files['download_cover']

        # Download audio if it is a link otherwise copy it to the folder
        if tools.check_if_url(audio):
            self.url = audio + '\n'
            tools.download_audio(audio, output=self.files['download_audio'])
            self.audio = self.files['download_audio']
        else:
            self.url = ''
            os.chdir(self.orig_dir)
            dot_location = audio.rfind('.')
            audio_extension = audio[dot_location:]
            audio_file_in_folder = f'{self.files["full_folder"]}/{self.files["download_audio"]}'
            if audio_extension != '.wav':
                tools.convert(audio, audio_file_in_folder)
            else:
                shutil.copyfile(audio, audio_file_in_folder)
            os.chdir(self.files['full_folder'])
            self.audio = self.files['download_audio']


    def custom_toptext(self, text):
        self.toptext_and = f'({text})'
        self.toptext_plus = f'({text})'

    def export_images(self):
        video_images = images.VideoImages(cover=self.cover)
        video_images.main(toptext=self.toptext_plus, song=self.song,
                    artist=self.artists[0], output=self.files['main_image'])
        video_images.thumbnail(output=self.files['thumb_image'])
        print('\033[92m✔ Finished export_images process\033[0m')

    def export_audio(self):
        audio = audio_mod.Audio(self.audio)
        if self.speed != 0:
            audio.speed(self.speed)
        if self.reverb != 0:
            audio.reverb(wet=self.reverb)
        audio.export(self.files['mod_audio'])
        print('\033[92m✔ Finished export_audio process\033[0m')

    def export_video(self):
        video.exportvideo(image=self.files['main_image'], audio=self.files['mod_audio'],
                    output=self.files['video_file'])
        print('\033[92m✔ Finished export_video process\033[0m')

    def upload_youtube(self, channel='justcow', client_secrets='client_secrets.json'):
        os.chdir(self.orig_dir)
        tags = [channel, self.song,
                f'{self.speed_text.lower()} {self.song}',
                f'{self.reverb_text.lower()} {self.song}',
                f'{self.speed_text.lower()} {self.reverb_text} {self.song}']
        title = f'{self.artists[0]} - {self.song} {self.toptext_plus}'
        description = f'{self.song} {self.toptext_and} \n{self.url}\n'
        for i in self.artists:
            tags.append(i)
            description += f'{i}\n'
        os.chdir(os.path.dirname(client_secrets))
        youtube.upload(
            client_secrets=client_secrets,
            video_file=f'{self.files["full_folder"]}/{self.files["video_file"]}',
            thumbnail=f'{self.files["full_folder"]}/{self.files["thumb_image"]}',
            category='10',
            title=title,
            description=description,
            tags=tags
            )
        os.chdir(self.orig_dir)
        print('\033[92m✔ Finished upload process\033[0m')

    def finish(self, compress=True):
        if compress:
            tools.compress_file(f'{self.files["full_folder"]}/{self.files["mod_audio"]}')
            tools.compress_file(f'{self.files["full_folder"]}/{self.files["download_audio"]}')
        os.chdir(self.orig_dir)
        print('\033[92m✔ Finished\033[0m')
