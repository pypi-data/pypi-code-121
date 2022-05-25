import sys
import os
import stat
import time
from colorama import Fore, Style, init, deinit


class Ls:
    '''This is a simple Python class for listing the content of a directory.
    The sole purpose is giving portability to the common ls command to Windows systems'''

    just = 7

    def __init__(self, opt='', path='.') -> None:

        if not opt or opt.startswith('-'):
            self.opt, self.path = opt, path
        else:
            self.opt, self.path = '', opt

    def echo(self, signal: int) -> None:
        try:
            with os.scandir(self.path) as dir:
                dir = sorted(dir, key=lambda x: (x.stat().st_mode, x.name))

                if 'l' in self.opt:
                    for i in dir:
                        if i.name.startswith('.') and 'a' not in self.opt:
                            continue
                        
                        # print() by 'column item' for better performance
                        print(self._colorful_permissions(stat.filemode(i.stat().st_mode), 'c' in self.opt), end='   ')
                        print(time.strftime('%d %b %y %H:%M', time.localtime(i.stat().st_ctime)), end='   ')
                        print(self._human_color(self._humanize(i), 'c' in self.opt).rjust(self.just), end='   ')
                        print(self._type_color(i, 'c' in self.opt))

                else:
                    print(*[self._type_color(i, 'c' in self.opt) for i in dir \
                        if not i.name.startswith('.') or 'a' in self.opt], sep='   ') 

        except PermissionError as err:
            if signal: # not going recursively on echo()
                print(f'{str(err)[:12]} {err.strerror}: {err.filename}')
                deinit()
                quit()

            try:
                self.path = os.path.realpath(self.path)
                self.echo(1)
                print(Style.RESET_ALL +
                    f"\nYou can't access files from here because CD doesn't follow symlinks. Do first: cd {os.path.realpath('.')}"
                    )

            except PermissionError:
                pass
        
        except FileNotFoundError as err:
            print(err)

    def _type_color(self, i: os.DirEntry, colors: bool) -> str:
        if not colors:
            return i.name

        #if i.is_symlink(): doesn't work
            
        if i.is_dir():                
            if os.path.realpath(i.path) != os.path.join(os.path.realpath(self.path), i.name): # workaround
                return Fore.CYAN + i.name + Fore.LIGHTBLACK_EX + ' --> ' + os.path.realpath(i.path)

            return Fore.LIGHTBLUE_EX + i.name

        else:
            if i.name.endswith(('.zip', '.exe', '.msi', '.dll', '.bat', '.sys', '.log', '.ini')):
                return Fore.YELLOW + i.name
            if i.name.endswith(('.py', '.pyx', '.pyd', '.pyw')):
                return Fore.GREEN + i.name
            if i.name.endswith(('.tmp')):
                return Fore.LIGHTBLACK_EX + i.name
            if i.name.endswith(('.pdf')):
                return Fore.LIGHTRED_EX + i.name
            return i.name

    def _humanize(self, i: os.DirEntry):
        if i.is_dir():
            return '-'

        entry = i.stat().st_size 
        units = ('k', 'M', 'G')
        final = ''

        for unit in units:
            if entry >= 1024:
                entry /= 1024
                final = unit
            else:
                break

        if entry:
            if final:
                return f'{entry:.1f}{final}'
            return str(entry)
        return '-'

    def _human_color(self, data: str, colors: bool) -> str:
        if not colors:
            return data

        self.just = 16

        if 'G' in data:
            return Fore.RED + data + Style.RESET_ALL
        elif 'M' in data:
            return Fore.LIGHTRED_EX + data + Style.RESET_ALL
        elif 'k' in data:
            return Fore.LIGHTYELLOW_EX + data + Style.RESET_ALL
        else:
            return Fore.WHITE + data + Style.RESET_ALL


    def _colorful_permissions(self, data: os.stat_result.st_mode, colors: bool) -> str:
        if not colors:
            return data

        lis = list(data)
        lis.insert(-3, Fore.LIGHTRED_EX)
        lis.insert(4, Fore.LIGHTYELLOW_EX)
        lis.insert(1, Fore.LIGHTGREEN_EX)
        if lis[0] == 'd': lis.insert(0, Fore.LIGHTBLUE_EX)
        lis.append(Style.RESET_ALL)

        return ''.join(lis)


def main():
    init()

    args = sys.argv[1:]

    #For Powershell and Unix compatibility
    if len(args) > 2:
        print(f'Ignored {sys.argv[3:]} parameter(s)')
        args = args[:2]

    Ls(*args).echo(0)
    deinit()


if __name__ == '__main__':
    main()