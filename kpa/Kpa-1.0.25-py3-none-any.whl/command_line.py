#!/usr/bin/env python3

def main():
    import sys, pathlib
    from .func_utils import assign

    if sys.argv[1:] == ['status-code-server']:
        from .http_server import serve, status_code_server
        serve(status_code_server)

    elif sys.argv[1:] == ['dir-server']:
        from .http_server import serve, magic_dir_server
        serve(magic_dir_server)

    elif sys.argv[1:] and sys.argv[1] == 'redirect-server':
        from .http_server import serve, make_redirect_server
        port = int(sys.argv[2])
        target_base_url = sys.argv[3]
        serve(make_redirect_server(target_base_url), port=port)

    elif sys.argv[1:] == ['termcolor']:
        from .terminal_utils import termcolor
        def r(num): return '#' if num is None else str(num%10)
        print('    # ' + ' '.join('{bg:2}'.format(bg=bg) for bg in range(50)))
        for fg in [None]+list(range(0,25)):
            print('{fg:<2} '.format(fg=(fg if fg is not None else '#')) +
                  ' '.join(termcolor(r(fg)+r(bg), fg, bg) for bg in [None]+list(range(50))))

    elif sys.argv[1:] and sys.argv[1] == "pip-find-updates":
        from .pip_utils import check_file
        @assign
        def filepath():
            if sys.argv[2:]:
                p = pathlib.Path(sys.argv[2])
                return p.as_posix() if p.exists() else None
            p = pathlib.Path().absolute()
            for directory in [p] + list(p.parents):
                for filename in ['setup.py', 'requirements.txt']:
                    p = directory / filename
                    if p.exists(): return p.as_posix()
            return None
        if not filepath: print('argv[2] not found and failed to find setup.py or requirements.txt in parent dirs')
        else:
            print('Looking at {filepath}'.format(filepath=filepath))
            check_file(filepath)

    else:
        if sys.argv[1:]: print('unknown command:', sys.argv[1:])
        from kpa.version import version
        print(f'kpa version {version}\n')
        print('available commands:\n  kpa termcolor\n  kpa status-code-server\n  kpa redirect-server\n  kpa pip-find-updates')
