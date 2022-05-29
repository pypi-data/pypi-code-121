import sys
import os
import subprocess
import inspect
# noinspection PyPackageRequirements
import pyttsx3  # pip install pyttsx3


# @staticmethod
# def onStart(name):
#     print('starting', name)
#
# @staticmethod
# def onWord(name, location, length):
#     print('word', name, location, length)
#
# @staticmethod
# def onEnd(name, completed):
#     print('finishing', name, completed)

# self.buddy = pyttsx3.init()
# self.buddy.connect('started-utterance', self.onStart)
# self.buddy.connect('started-word', self.onWord)
# self.buddy.connect('finished-utterance', self.onEnd)

def get_file_name() -> str:
    ret_val = ''
    try:
        scope_1_back = inspect.stack()[1]  # stack()[0] is this function
        ret_val = '{}'.format(scope_1_back.filename)
    except IndexError as e:
        print(e)
    return ret_val


class MachineBuddy:
    """
    text to speech
    https://pypi.org/project/pyttsx3/
    """

    def __init__(self, voice_ind: int = 0, rate: int = 200, vol: float = 1.0) -> None:
        """
        :param voice_ind: default voice - num 0 in self.buddy.getProperty('voices')
        :param rate: default rate 200
        :param vol: default vol 1.0 (from 0.0 to 1.0)
        """
        self.buddy = pyttsx3.init()
        # noinspection PyTypeChecker
        self.voices_num = len(self.buddy.getProperty('voices'))
        if 0 < voice_ind <= self.voices_num - 1:  # 0 by default
            self.change_voice(voice_ind)
        if 0 < rate != 200:
            self.change_rate(rate)
        if 0 <= vol < 1.0:
            self.change_volume(vol)
        return

    def __del__(self) -> None:
        # if self.buddy is not None:
        #     self.buddy.stop()
        return

    def __str__(self) -> str:
        string = 'MachineBuddy:\n'
        # noinspection PyTypeChecker
        voice_name = os.path.basename(self.buddy.getProperty('voice'))
        string += '\tvoice:{}\n'.format(voice_name)
        string += '\tvol:{}\n'.format(self.buddy.getProperty('volume'))
        string += '\trate:{}'.format(self.buddy.getProperty('rate'))
        return string

    def get_all_voices(self, ack: bool = True, tabs: int = 1):
        """
        :param ack:
        :param tabs:
        :return:
        TO add more speakers on Windows10:
        based on https://www.youtube.com/watch?v=KMtLqPi2wiU&ab_channel=MuruganS
        step 1(download):
            ctrl+winKey+n - open narrator
            add more voices
            add voice
            select, install and wait for it to finish
            # the new voice available only to Microsoft
            i will refer to this language as _NEW_LANGUAGE
        step 2(make the installed voice available to all tts programs):
            start, regedit, open as administrator:
                goto: Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens
                click export on any language and save to desktop(we just need a path) -> i will call it f1
                goto: Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\_NEW_LANGUAGE
                select the _NEW_LANGUAGE installed on step 1. export to desktop -> i will call it f2
                open both saved files on notepad++
                from f1 - copy the paths
                e.g.
                path1: [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0]
                path2: [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0\Attributes]
                we care only for the dir name:
                so path1: [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\SOME_LANGUAGE]
                so path2: [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\SOME_LANGUAGE\Attributes]

                open f2
                duplicate the first 2 paragraphs (first is the actual language and second is the attributes)
                paragraph 1:
                    [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\_NEW_LANGUAGE]
                paragraph 2:
                    [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\_NEW_LANGUAGE\Attributes]
                now you have 4 paragraphs instead of 2:
                p1 [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\_NEW_LANGUAGE]
                p2 [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\_NEW_LANGUAGE\Attributes]
                p3 [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\_NEW_LANGUAGE]
                p4 [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\_NEW_LANGUAGE\Attributes]
                change p3 to path1 and change SOME_LANGUAGE to _NEW_LANGUAGE
                change p4 to path2 and change SOME_LANGUAGE to _NEW_LANGUAGE
                e.g.
                from
                [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\MSTTS_V110_heIL_Asaf]
                to
                [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_heIL_Asaf]
                and from
                [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\MSTTS_V110_heIL_Asaf\Attributes]
                to
                [HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_heIL_Asaf\Attributes]
                save and exit notepad++
                run the saved file and _NEW_LANGUAGE should appear in any tts program
        """

        all_voice = self.buddy.getProperty('voices')
        if ack:
            # noinspection PyTypeChecker
            for v in all_voice:
                print('{}{}'.format(tabs * '\t', v))
        return all_voice

    def change_voice(self, new_voice_ind: int) -> None:
        """
        :param new_voice_ind:
        voices differ between computers
        :return:
        """
        if 0 <= new_voice_ind <= self.voices_num - 1:
            voices = self.buddy.getProperty('voices')
            # noinspection PyUnresolvedReferences
            self.buddy.setProperty(name='voice', value=voices[new_voice_ind].id)
        return

    def change_rate(self, new_rate: int) -> None:
        """
        default rate 200
        :param new_rate:
        :return:
        """
        if new_rate > 0:
            # rate = self.buddy.getProperty('rate')  # getting details of current speaking rate
            # print(rate)  # printing current voice rate
            self.buddy.setProperty('rate', new_rate)  # setting up new voice rate
        return

    def change_volume(self, new_vol: float) -> None:
        """
        default 1.0
        :param new_vol:
        :return:
        setting up volume level between 0 and 1
        """
        if 0.0 <= new_vol <= 1.0:  # 1 by default
            # volume = self.buddy.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
            # print(volume)  # printing current volume level
            self.buddy.setProperty('volume', new_vol)
        return

    def say(self, text: str) -> None:
        """
        :param text:
        :return:
        """
        self.buddy.say(text)
        self.buddy.runAndWait()
        return

    @staticmethod
    def speak(text: str, block: bool = True) -> None:
        """
        :param text:
        :param block: if True - program waits till speaking is over
            if False - run the speak function with another process
        :return:
        static use with default params
        """
        if block:
            pyttsx3.speak(text)
        else:
            tts_path = get_file_name()
            # print(tts_path)
            # print(os.path.exists(tts_path))
            # subprocess.call([r"C:\Users\GiladEiniKbyLake\.conda\envs\wu\python.exe", "tts.py", phrase])
            # subprocess.run([r"C:\Users\GiladEiniKbyLake\.conda\envs\wu\python.exe", "tts.py", phrase])
            subprocess.Popen([sys.executable, tts_path, text])  # Call subprocess
            # args = [tts_path, '--text', text]
            # p = subprocess.Popen([sys.executable or 'python'] + args)
            # p.wait()
        return


def main(argv: list) -> None:
    # print('argv', argv, len(argv))
    if len(argv) == 2:  # just text - say static
        MachineBuddy.speak(text=argv[1])
    return


if __name__ == '__main__':
    main(sys.argv)
