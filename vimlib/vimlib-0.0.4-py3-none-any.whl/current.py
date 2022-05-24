from pathlib import Path
from types import SimpleNamespace

import vim
from pyvim.job import Job


class Current:
    """Python interface to Vim's current (vim.current)."""

    def __init__(self):

        pass

    @property
    def filetype(self):
        return vim.eval('&filetype')

    @property
    def cursor(self):
        cursor = vim.current.window.cursor
        return SimpleNamespace(row=cursor[0], column=cursor[-1])

    @property
    def view(self):

        # {'lnum': '25', 'leftcol': '0', 'col': '15', 'topfill': '0', 'topline': '1', 'coladd': '0', 'skipcol': '0', 'curswant': '15'}
        view = vim.eval('winsaveview()')

        # Can use the following to set the current view
        # call winrestview(view)
        # vim.command('call winrestview(py3eval("view"))')

        return view

    # see `help expand()`
    @property
    def file(self):
        # .name
        # .parent
        return Path(vim.eval('expand("%")'))

    @property
    def word(self):
        # word under cursor
        return vim.eval('expand("<cword>")')

    @property
    def WORD(self):
        # WORD under cursor
        return vim.eval('expand("<cWORD>")')

    @property
    def line(self):
        return vim.current.line

    @property
    def paragraph(self):
        # FIX: Adds surrounding lines
        vim.command("'{,'}y")
        return vim.eval('@"')
        """ This works, but will shift the window... and is clunky
        # cursor = vim.current.window.cursor
        # vim.command('normal yip')
        # vim.current.window.cursor = cursor
        # return str(cursor)
        """

    @property
    def buffer(self):
        return vim.current.buffer

    @property
    def selection(self):
        """prototype
        >>> pyvim.current.selection

        [bufnum, lnum, col, off]
        v - Visual (Character) - characterwise-visual
        V - Visual line - linewise-visual
         (A <CTRL-V> Character) - Visual blockwise - blockwise-visual
        """

        mode = vim.eval('visualmode()')
        start = [int(i) for i in vim.eval("""getpos("'<")""")]
        # start_buf = start[0]
        start_buf = vim.current.buffer.number
        start_line = start[1]
        start_pos = start[2]
        end = [int(i) for i in vim.eval("""getpos("'>")""")]
        # end_buf = end[0]
        end_buf = vim.current.buffer.number
        end_line = end[1]
        end_pos = end[2]
        end_pos = min(end[2], 80)

        # buf = vim.buffers[int(start_buf)+1]
        buf = vim.current.buffer
        rows = range(start_line - 1, end_line)
        columns = range(start_pos - 1, end_pos)
        lines = buf[start_line - 1 : end_line]

        if mode == '':
            # visual-blockwise
            text = []
            # text = [buf[row][col] for row in rows for col in columns]
            for row in rows:
                for col in columns:
                    text.append(buf[row][col])
                text.append('\n')
            text = ''.join(text[:-1])
        elif mode == 'V':
            text = '\n'.join(lines)
        elif mode == 'v':
            text = []
            # start
            first_line = lines[0]
            if len(lines) == 1:
                text.append(first_line[start_pos - 1 : end_pos])
            else:
                text.append(first_line[start_pos - 1 :])
            # middle
            if len(lines) > 2:
                middle_lines = buf[start_line : end_line - 1]
                for line in middle_lines:
                    text.append(line)
            # end
            if len(lines) > 1:
                last_line = lines[-1]
                text.append(last_line[:end_pos])
            text = '\n'.join(text)
        else:
            vim.command('echohl WarningMsg')
            vim.command("echom 'No selection detected.'")
            vim.command('echohl None')

            return ''

        return text

    @property
    def visual(self):

        mode = vim.eval('visualmode()')
        # Start
        start = [int(i) for i in vim.eval("""getpos("'<")""")]
        start_buf = vim.current.buffer.number
        start_line = start[1]
        start_pos = start[2]
        # End
        end = [int(i) for i in vim.eval("""getpos("'>")""")]
        end_buf = vim.current.buffer.number
        end_line = end[1]
        end_pos = end[2]
        # Why is this here?
        end_pos = min(end[2], 80)

        visual = dict(
            lines=dict(
                start=start_line,
                end=end_line,
            ),
            columns=dict(
                start=start_pos,
                end=end_pos,
            ),
        )

        return visual

    @property
    def jobs(self):
        """Get all running Jobs.

        To-do
        -----
        - [ ] Return a list of Job objects instead (see job.py).

        Returns
        -------
        List of job objects from Vim.
        Currently cannot process it... So it only gives a list of None...
        """
        jobs = []
        for i in range(len(vim.eval('job_info()'))):
            try:
                job = Job(**vim.eval(f'job_info(job_info()[{i}])'))
                jobs.append(job)
            except vim.error:
                # Sometimes gives extra jobs that for some reason can't be
                # evaluated.
                pass
        return jobs


current: Current = Current()
