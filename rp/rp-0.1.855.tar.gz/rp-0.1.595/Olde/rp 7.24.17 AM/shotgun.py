#A dependency shotgun
packages=['HTMLParser','Pyperclip','colorama','drawille','exofrills','gtts_token','lazyasd','matplotlib','more_itertools','pandas','pyaudio','pygame','pymatbridge','requests','rtmidi','scipy','serial','setproctitle','sklearn','sounddevice','suplemon','urwid','win_unicode_console','youtube_dl','opencv-python','scikit-learn','pillow','playsound','numpngw','psutil','xonsh']
for package in packages:
    bar='――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――'
    print(bar)
    print("ATTEMPTING TO INSTALL PACKAGE:".center(len(bar)))
    print(package.center(len(bar)))
    print(bar)
    from subprocess import run
    from os import name
    if name=='nt':# We're on windows
        run('pip3 install '+package,shell=True)# Might be prompted for a password
    else:
        run('sudo pip3 install '+package,shell=True)# Might be prompted for a password
