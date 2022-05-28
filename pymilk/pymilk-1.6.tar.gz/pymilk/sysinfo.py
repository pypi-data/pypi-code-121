from sys import platform


system_type = platform.lower()
if   'win'   in system_type: system_type = 'win'
elif 'linux' in system_type: system_type = 'linux'
elif 'mac'   in system_type: system_type = 'mac'
