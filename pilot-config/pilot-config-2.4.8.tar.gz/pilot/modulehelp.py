from asyncore import file_dispatcher
from pathlib import Path
from .pilotdriver import PilotDriver
from .pilotserver import PilotServer
from .sbc import Sbc

import re

import lazy_import
Compiler = lazy_import.lazy_callable("pybars.Compiler")

from rich.console import Console
from rich.markdown import Markdown
from rich import print as rich_print
from rich.table import Table, Column

from colorama import Fore
from colorama import Style
from colorama import init

init(autoreset=True)  # colorama color autoreset

# finds the largest string in an array
def largest_str(arr):
    # Initialize maximum element
    n = len(arr)
    max = len(arr[0])
    # Traverse array elements from second
    # and compare every element with 
    # current max
    for i in range(1, n):
        cur = len(arr[i])
        if cur > max:
            max = cur
    return max

class ModuleHelp():
    sbc = None
    module = None
    
    def gpiochip_base(self, _, offset):
        p = re.compile('^gpiochip([0-9]+)$', re.MULTILINE)
        l = re.compile('^pilot.*?_([0-9]+)$')
        matches = p.findall(self.sbc.cmd('ls /sys/class/gpio'))
        for gc_str in matches:
            gpio_start = int(gc_str)
            if gpio_start >= 60 and gpio_start < 500: #min gpio number of pilot GPIOs
                label = self.sbc.cmd('cat /sys/class/gpio/gpiochip{}/label'.format(gpio_start))
                num_match = l.match(label)
                if num_match and int(num_match.group(1)) == self.number: 
                    if offset != None:
                        gpio_start += offset
                    return gpio_start
        return -1
    
    def tty(self, _, block, offset=0):
        return "/dev/ttyP{}".format((self.number)*2+offset)


    def help(self, args):
        with Sbc(args) as sbc:
            self.sbc = sbc
            pilotserver = PilotServer(sbc)
            if 'server' in args and args.server != None:
                pilotserver.pilot_server = args.server
            
            #PilotDriver
            pilotdriver = PilotDriver(pilotserver, sbc)
    
            modules, success = pilotdriver.load_pilot_defs()
            if success:
                for mod in modules:
                    if mod['module'] == args.module:
                        self.number = args.module-1
                        self.printhelp(args, mod)
    
    def loop(self, _, block, start, to, incr):
        accum = '' 
        for i in range(start, to, incr):
            accum += "".join(block['fn'](i))
        return accum
    
    def printformatted(self, line):
        splitchars=["#", "//"]
        splitchar=""
        for sp in splitchars:
            splitchar = sp
            parts=line.split(splitchar, 1)
            if (len(parts) > 1):
                break
        if len(parts) > 1:
            print(Style.RESET_ALL + parts[0] + Fore.GREEN + splitchar + parts[1])
        else:
            print(parts[0])

    def printhelp(self, args, module):
            helpers = {'gpio_base': self.gpiochip_base, 'for': self.loop }

            print("")
            print(Fore.GREEN + 'Module [{}]: {}'.format(args.module, module['currentfid_nicename']))
            print("")
    
            if module != None:
                compiler = Compiler()

                if args.pinout:
                    if 'pinout' in module and 'default' in module['pinout'] and 'pins' in module['pinout']['default']:
                        pins = module['pinout']['default']['pins'] 
                        width = largest_str([item for sublist in pins for item in sublist]) + 2 # add a space on each side of the string

                        grid = Table(show_header=False, expand=False)
                        grid.add_column(justify="center")
                        for row in pins:
                            table = Table(show_header=False, expand=False)
                            i = 0
                            for col in row:
                                # color special pins
                                if col == "GND":
                                    row[i] = "[green]" + col
                                elif col == "VCC" or col == "24V" or col == "5V":
                                    row[i] = "[red]" + col
                                table.add_column(justify="center", width=width)
                                i = i + 1
                            table.add_row(*row)
                            grid.add_row(table)
                        rich_print(grid)
                    else:
                        print("No pinout available for this module")
                elif args.usage:
                    if 'usage' in module and module['usage'] != None:
                        template = compiler.compile(module['usage'])
                        text = template({
                            'module': module['module']-1, 
                            'slot': module['module'], 
                            'tty': "/dev/ttyP{}".format((module['module']-1)*2),
                            'tty1': "/dev/ttyP{}".format((module['module']-1)*2),
                            'tty2': "/dev/ttyP{}".format((module['module']-1)*2+1),
                            }, helpers)
                        console = Console()
                        md = Markdown(text)
                        console.print(md)
                    else:
                        print("No usage description available for this module")
                else:
                    if 'description' in module and module['description'] != None:
                        console = Console()
                        md = Markdown(module['description'])
                        console.print(md)
                    else:
                        print("No description available for this module")

                    print("")
                    print("Run with --pinout to see pinout")
                    print("Run with --usage to get usage examples")
            else:
                print("Module not found")



