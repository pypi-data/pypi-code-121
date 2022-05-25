import os
import sys

def main():
    if len(sys.argv) != 2:
        print('This script do the setup for cmd.exe', 'Run:', '> win-basic-tools setup', 'Then refresh your cmd.exe', sep='\n')
        quit(0)
    
    if sys.argv[1] == 'uninstall':
        uninstall()
        quit(0)

    if sys.argv[1] != 'setup':
        print('This script do the setup for cmd.exe', 'Run:', '> win-basic-tools setup', sep='\n')
        quit(0)

    assert sys.platform == 'win32'
    
    sources_path = f'{sys.exec_prefix}/Lib/site-packages/win_basic_tools/sources'
    home_path = os.path.expanduser('~')

    with open(f'{home_path}\\.macros.doskey', 'w') as f:
        print(
            f'ls=python {sources_path}\\ls.py $*',
            f'll=python {sources_path}\\ls.py -lac $*',
            f'which=python {sources_path}\\which.py $1',
            f'touch=python {sources_path}\\touch.py $*',
            'cat=type $1',
            'pwd=cd',
            'mv=move $1 $2',
            'rm=del $*',
            sep='\n',
            file=f)
        
        
    os.system(f'reg add "HKCU\\Software\\Microsoft\\Command Processor" /v Autorun /d "doskey /macrofile=\\"{home_path}\\.macros.doskey\"" /f')

def uninstall():
    home_path = os.path.expanduser('~')

    os.system(f'reg delete "HKCU\\Software\\Microsoft\\Command Processor" /v Autorun')
    os.system(f'del {home_path}\\.macros.doskey')
    print('Refresh you cmd.exe for complete uninstall')

if __name__ == '__main__':
    main()