import os
from io import BytesIO
import pickle
from pydub import AudioSegment
'''
ESI file is Easy Sampler Instrument, an ESI file combines a folder of audio files (samples)
and a settings file (not necessary) into one file, and can be loaded in Easy Sampler or to
unzip as a folder of sound files.
It can also be loaded as a python object, which is an instance of class esi.
'''


class esi:

    def __init__(self, samples, settings=None, name_mappings=None):
        self.samples = samples
        self.settings = settings
        self.name_mappings = name_mappings
        self.file_names = {os.path.splitext(i)[0]: i for i in self.samples}

    def __getitem__(self, ind):
        if self.name_mappings:
            if ind in self.name_mappings:
                return self.samples[self.name_mappings[ind]]
        if ind in self.samples:
            return self.samples[ind]
        if ind in self.file_names:
            return self.samples[self.file_names[ind]]

    def export(self, note_name, name=None, format='wav', **export_args):
        current = self[note_name]
        if not current:
            return
        if name is None:
            if self.name_mappings and note_name in self.name_mappings:
                name = self.name_mappings[note_name]
            elif note_name in self.samples:
                name = note_name
            elif note_name in self.file_names:
                name = self.file_names[note_name]
        if type(current) == AudioSegment:
            current.export(name, **export_args)
        else:
            with open(name, 'wb') as f:
                f.write(current)

    def export_all(self, folder_name='Untitled'):
        abs_path = os.getcwd()
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        os.chdir(folder_name)
        for i, j in self.samples.items():
            if type(j) == AudioSegment:
                j.export(i, format=os.path.splitext(i)[1][1:])
            else:
                with open(i, 'wb') as f:
                    f.write(j)
        os.chdir(abs_path)


def make_esi(file_path,
             name='untitled.esi',
             settings=None,
             asfile=True,
             name_mappings=None,
             show_msg=True):
    abs_path = os.getcwd()
    filenames = os.listdir(file_path)
    current_samples = {}
    current_settings = None
    if settings is not None:
        if asfile:
            with open(settings, encoding='utf-8') as f:
                current_settings = f.read()
        else:
            current_settings = settings

    if not filenames:
        if show_msg:
            print('There are no sound files to make ESI files')
        return
    os.chdir(file_path)
    for t in filenames:
        with open(t, 'rb') as f:
            current_samples[t] = f.read()
    current_esi = esi(current_samples, current_settings, name_mappings)
    os.chdir(abs_path)
    with open(name, 'wb') as f:
        pickle.dump(current_esi, f)
    if show_msg:
        print(f'Successfully made ESI file: {name}')


def unzip_esi(file_path, folder_name=None, show_msg=True):
    if folder_name is None:
        folder_name = os.path.basename(file_path)
        folder_name = folder_name[:folder_name.rfind('.')]
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    current_esi = load_esi(file_path, convert=False)
    abs_path = os.getcwd()
    os.chdir(folder_name)
    for each in current_esi.samples:
        if show_msg:
            print(f'Currently unzip file {each}')
        with open(each, 'wb') as f:
            f.write(current_esi.samples[each])
    if show_msg:
        print(f'Unzip {os.path.basename(file_path)} successfully')
    os.chdir(abs_path)


def load_esi(file_path, convert=True):
    with open(file_path, 'rb') as file:
        current_esi = pickle.load(file)
    current_samples = current_esi.samples
    if convert:
        current_esi.samples = {
            i:
            AudioSegment.from_file(BytesIO(current_samples[i]),
                                   format=os.path.splitext(i)[1]
                                   [1:]).set_frame_rate(44100).set_channels(2)
            for i in current_samples
        }
    return current_esi
