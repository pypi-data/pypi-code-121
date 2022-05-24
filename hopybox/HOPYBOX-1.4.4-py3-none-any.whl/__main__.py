#Copyright owned by HOStudio123 author
#-*- coding:utf-8 -*-
from rich.console import Console
console = Console()
#Loading library
with console.status("\033[96mLoading library …\033[0m"):
  import rlcompleter # Prevent keyboard errors, but also have negative effects
  import importlib
  from  getpass import getuser
  from .version import version
  from .download import download
  from .hopter import (
      Error_pta,
      Tip_pta
)
  from .system import (
      systems,
      runpy,
      python,
      install,
      uninstall,
      debug,
      all_help,
      module_help,
      license,
      pip_list,
      clear_text
)
  from .qqget import (
      qqname,
      qqhead
)
  from .urlget import (
      hoget,
      browser_get
)
  from .sdemail import sd_email
  from .check import check_version
  from .caculate import (
      caculate,
      root_caculate,
      triangle_caculate,
      pi
)
  from .translate import translate_print
  from .findipway import way_four
  from .filetoolbox import (
      read_file,
      del_file
)
  from .weather import city
  from .fps import (
      fps,
      fps_print
)
  from .timetoolbox import (
      timestamp_print,
      format_time_a
)
  #Main program header
  print('\033[96mWELCOME TO HOPYBOX\n\033[0m\033[92m[USER:{}] [FPS:{}] [RUN:{}]\033[0m\n{}'.format(getuser().upper(),fps(),format_time_a(),version))
#Main program variables
pattern = 'Command'
#The main block of code
while True:
  answer = input('\033[0m\033[93mHOPYBOX/{}:\033[0m'.format(pattern))
  if answer == 'exit':
    exit()
  elif answer == 'clear':
    clear_text()
  elif answer == 'take command':
    pattern = 'Command'
    Tip_pta('Program mode switched successfully')
  elif answer == 'take system':
    pattern = 'System'
    Tip_pta('Program mode switched successfully')
  elif answer == 'take python':
    pattern = 'Python'
    Tip_pta('Program mode switched successfully')
  #Command
  elif pattern == 'Command':
    if answer == 'help':
      all_help()
    elif answer[:5] == 'help ':
      module_help(answer[5:])
    elif answer == 'license':
      license()
    elif answer == 'version':
      print(version)
    elif answer[:4] == 'run ':
      runpy(answer[4:])
    elif answer[:9] == 'download ':
      download(answer[9:])
    elif answer[:6] == 'hoget ':
      hoget(answer[6:])
    elif answer[:7] == 'bowget ':
      browser_get(answer[7:])
    elif answer[:5] == 'open ':
      read_file(answer[5:])
    elif answer[:10] == 'translate ':
      translate_print(answer[10:])
    elif answer[:3] == 'id ':
      print('\033[32m'+str(id(answer[3:])))
    elif answer[:7] == 'qqname ':
      qqname(answer[7:])
    elif answer[:7] == 'qqhead ':
      qqhead(answer[7:])
    elif answer[:6] == 'email ':
      sd_email(answer[6:])
    elif answer == 'check version':
      check_version()
    elif answer[:10] == 'caculate √':
      root_caculate(answer[10:])
    elif answer[:10] == 'caculate |':
      abs_caculate(answer[10:])
    elif answer[:9] == 'triangle ':
      triangle_caculate(answer[9:])
    elif answer[:9] == 'caculate ':
      caculate(answer[9:])
    elif answer[:8] == 'install ':
      install(answer[8:])
    elif answer[:10] == 'uninstall ':
      uninstall(answer[10:])
    elif answer[:8] == 'fwayget ':
      way_four(answer[8:])
    elif answer[:8] == 'weather ':
      city(answer[8:])
    elif answer == 'pack list':
      pip_list()
    elif answer[:4] == 'del ':
      del_file(answer[4:])
    elif answer == 'fps':
      fps_print()
    elif answer == 'timestamp':
      timestamp_print()
    elif answer == 'pi':
      pi()
    elif not answer:
      Error_pta('NotFindOrderError',pattern,'Please enter a command',answer)
    else:
      Error_pta('OrderError',pattern,'Unrecognized instruction',answer)
  #System
  elif pattern == 'System':
    if answer:
      systems(answer)
    else:
      Error_pta('NotFindOrderError',pattern,'Please enter a command',answer)
  #Python
  elif pattern == 'Python':
    if answer == 'interpreter':
      python()
    elif answer[:6] == 'debug ':
      debug(answer[6:])
    else:
      Error_pta('OrderError',pattern,'Unrecognized instruction',answer)