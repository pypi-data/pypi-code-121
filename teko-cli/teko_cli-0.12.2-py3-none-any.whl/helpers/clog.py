import typer


class CLog:
    @staticmethod
    def _log(msg, level=None, fg=None, bg=None, bold=None, dim=None, underline=None, blink=None, reverse=None):
        if level:
            msg = f'[TEKO TOOL][{level}]:\t  {msg}'
        typer.echo(typer.style(msg, fg=fg, bg=bg, bold=bold, dim=dim,
                               underline=underline, blink=blink, reverse=reverse))

    @staticmethod
    def trivial(msg, **kwargs):
        if 'dim' not in kwargs:
            kwargs['dim'] = True
        CLog._log(msg, **kwargs)

    @staticmethod
    def echo(msg, **kwargs):
        CLog._log(msg, **kwargs)

    @staticmethod
    def info(msg, **kwargs):
        if 'fg' not in kwargs:
            kwargs['fg'] = 'bright_blue'
        CLog._log(msg, 'INFO', **kwargs)

    @staticmethod
    def important(msg, **kwargs):
        if 'fg' not in kwargs:
            kwargs['fg'] = 'green'
        if 'bold' not in kwargs:
            kwargs['bold'] = True
        CLog._log(msg, 'IMPORTANT', **kwargs)

    @staticmethod
    def warn(msg, **kwargs):
        if 'fg' not in kwargs:
            kwargs['fg'] = 'yellow'
        CLog._log(msg, 'WARN', **kwargs)

    @staticmethod
    def error(msg, **kwargs):
        if 'fg' not in kwargs:
            kwargs['fg'] = 'bright_red'
        CLog._log(msg, 'ERROR', **kwargs)

    @staticmethod
    def fatal(msg, **kwargs):
        if 'fg' not in kwargs:
            kwargs['fg'] = 'bright_red'
        if 'bold' not in kwargs:
            kwargs['bold'] = True
        if 'reverse' not in kwargs:
            kwargs['reverse'] = True
        CLog._log(msg, 'FATAL', **kwargs)


if __name__ == '__main__':
    CLog._log('log')
    CLog.trivial('trivial')
    CLog.echo('echo')
    CLog.info('info')
    CLog.info('info', bold=True)
    CLog.important('important')
    CLog.warn('warn')
    CLog.error('error')
    CLog.fatal('fatal')

