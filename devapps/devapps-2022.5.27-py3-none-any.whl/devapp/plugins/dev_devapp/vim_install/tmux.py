from utils import dbg, logger, L, RESET, C
from utils import read_file, write_file, cur_test, env, now, wait, vi
from utils import session_name, OS, os, sys, utf, p, pycond, strip_ansi, term_cols
from rich.console import Console
from dataclasses import dataclass

prompt = '$'
tmux_symb = '💻'
tmux_cols = term_cols
tmux_exe = env.get('tmux', 'tmux')


def tmux(cmd, *args, no_t=False, enc=False, symb=tmux_symb):
    if cmd == 'snapshot':
        cmd, args, symb = 'capture-pane', ('-epJS', '-1000000'), '📷'
    dbg(symb + cmd, **({} if not args else {'args': ' '.join(args)}))
    if not no_t:
        args = ('-t', session_name() + ':1') + args
    breakpoint()  # FIXME BREAKPOINT
    r = OS.call(tmux_exe, '-S', C.d_tmp + '/tmux', cmd, *args, enc=enc)
    if symb == '📷':
        r = utf(r).rstrip()
        if r.strip():
            d = term_cols - tmux_cols
            if d:
                r = '\n'.join([i[:-d] for i in r.splitlines()])
        print((r + RESET + '\n') if not term_cols < tmux_cols else '')
    return r


def kill_sessions():
    if not env.get('keep_sessions'):
        os.system('pkill tmux')


def create_session():
    env['SHELL'] = '/bin/bash'
    env['p'] = env['PATH']
    tmux('new', '-s', session_name(), '-d', no_t=True)


def ensure_session():
    if not session_name() in '\n' + utf(tmux('ls', no_t=True)):
        create_session()


def kill_session():
    tmux('kill-session')


class TmuxTest:
    def setup_method(self, _):
        ensure_session()

    def teardown_method(self, _):

        if not env.get('keep_sessions'):
            kill_session()
        # tear down self.attribute


class run:
    shell_cmds = lambda cmds, **kw: [run.shell_cmd(c, **kw) for c in cmds]

    def shell_cmd(cmd, **kw):
        """Either dict or string"""
        if isinstance(cmd, dict):
            cmd.update(kw)
        else:
            kw['cmd'] = cmd
            cmd = kw
        try:
            return run.tmux(**cmd)
        except Exception as ex:
            logger.error('Tmux Run Error', exc=ex)
            raise

    def tmux(
        cmd,
        expect=None,
        silent=None,
        wait_after=None,
        prompt=prompt,
        timeout=5,
        asserts=None,
        **kw,
    ):
        """
        - expect: Presence of this and we have the result. May be callable.
        """
        breakpoint()  # FIXME BREAKPOINT
        if isinstance(cmd, list):
            l = dict(locals())
            l.pop('cmd')
            return [run.tmux(c, **l) for c in cmd]
        sn = session_name()
        if cmd.startswith('wait '):
            wait(float(cmd.split()[1]))
            return 'silent'

        sk = 'send-keys:'
        if cmd.startswith(sk):
            cmd = cmd.split('#', 1)[0].strip()
            tmux('send-keys', cmd[len(sk) :], enc='unicode-escape')
            # at ci seen delays after C-c:
            wait(0.1)
            return 'silent'

        expect_echo_out_cmd = ''
        is_multiline = '\n' in cmd
        if expect is None:
            # we do NOT fail on exit codes, just want to know if the command completed,
            # by scraping the tmux output for a string:
            # if you want the first send set -e
            sep = '\n' if (is_multiline or ' # ' in cmd) else ';'
            # here docs can't have ';echo -n... at last line:
            # not match on the issuing cmd
            expect_echo_out_cmd = sep + 'echo -n ax_; echo -n done'
            cmd += expect_echo_out_cmd
            expect = 'ax_done'

        if cmd:
            init_prompt(prompt)
            # send the sequence as hex (-H):
            seq = ' '.join([hex(ord(b))[2:] for b in cmd])
            seq += ' a'
            _ = expect_echo_out_cmd
            _ = cmd if not _ else cmd.split(_, 1)[0] + L(_)
            tmux('send-keys', '-H', seq)

        t0 = now()
        wait_dt = 0.1
        last_msg = now()
        max_wait = 2

        while True:
            res = tmux('snapshot')
            print('.', end='', file=sys.stderr)
            if callable(expect):
                er = expect(res)
                if er == True:
                    break
                elif isinstance(er, float):
                    # allow deliver new timeout based on result so far:
                    timeout = er

            elif expect is not False and expect in res:
                break
            dt = now() - t0
            if dt > timeout:
                if expect is False:
                    # wanted then:
                    break

                tom = 'Command %s: Timeout (> %s sec) expecting "%s"'
                raise Exception(tom % (cmd, timeout, expect))

            if now() - last_msg > 5:
                dbg('%ss[%s] Hint: tmux att -t %s' % (round(dt, 1), timeout, sn))
            wait(wait_dt)  # fast first
            wait_dt = min(timeout / 10.0, max_wait)
            max_wait = min(5, max_wait + 2)

        if expect_echo_out_cmd:
            # when expect was given we include it (expect="Ready to accept Connections")
            # expect_echo_out_cmd is empty then
            res = res.split(expect, 1)[0].strip()
            a = expect_echo_out_cmd
            a = a[1:] if a.startswith('\n') else a  # when \n is the sep we won't see it
            res = res.replace(a, '')
        else:
            # the tmux window contains a lot of white space after the last output when
            # short cmd
            res = res.strip()
        if wait_after:
            wait(float(wait_after))
        check_asserts(asserts, res)
        dbg('Have tmux result:', res='\n' + res)
        return res if not silent else 'silent'


def check_asserts(ass, res):
    if ass is None:
        return
    s = str(res)
    is_pycond = False
    if isinstance(ass, str) and ' and ' in ass or ' or ' in ass or 'not ' in ass:
        is_pycond = True
    elif isinstance(ass, list) and ass[1] in {'and', 'or'}:
        is_pycond = True
    if is_pycond:

        def f(k, v, state, **kw):
            return (k in state['res'], v)

        r = pycond.pycond(ass, f)
        a = r(state={'res': s})
        if not a:
            raise Exception('Assertion error: ' + str(ass))
        return

    if not isinstance(ass, (list, tuple)):
        ass = [ass]

    for a in ass:
        if not a in s:
            raise Exception('Assertion error: ' + str(a))


def init_prompt(prompt=prompt):
    """run before each command"""
    tmux('send-keys', '-R')
    tmux('resize-window', '-x', str(tmux_cols))
    tmux('clear-history')
    tmux('send-keys', '', 'Enter')
    t0 = now()
    p = prompt
    while now() - t0 < 2:
        r = tmux('snapshot')
        # prompt can be more chars:
        if r and (r.endswith(p) or r[-1] in {'#', '$'}):
            return
        print(r)
        dbg('waiting for content...', want=p)
        wait(0.1)
    raise Exception('No Prompt; Have so far: %s' % r)


@dataclass
class nvim_result:
    pane: str
    clear: str
    file: str
    dt: float

    def __repr__(r):
        cr = Console().rule
        f = ' '.join(cur_test())
        t = f'Result State: {f}'
        cr(t, style='white on magenta')
        cr = p(cr, style='black on white')
        cr('Pane (clear)')
        print(r.clear)
        cr('File')
        print(r.file)
        cr('Pane')
        print(r.pane)
        return ''


class expect:
    def vim_up_fully_loaded(res, content='', last=[0]):
        if vi() in res:
            return
        if not content in res:
            return
        if last[0] and last[0] == res:
            return True
        last[0] = res


class nvim:
    def new(fn, content='', keys=[]):
        """
        - Creates the file with content
        - Opens nvim in tmux on the file
        - Waits until no change in output
        - Sends the given keys
        - Sends ESC + :wq + Enter

        Returns a nvim_result object
        """
        t0 = now()
        if not fn:
            fn = 'test_file'
        ffn = write_file(fn, content)
        init_prompt()  # we need to be on the shell, not in nvim
        r = run.tmux
        r(vi() + f' "{ffn}"', expect=expect.vim_up_fully_loaded, timeout=10)
        [r('send-keys: %s' % k) for k in keys]
        pane = tmux('snapshot')
        r('send-keys: Escape')
        r('send-keys: :wq')
        r('send-keys: Enter')
        file = read_file(ffn, dflt='n.a.')
        return nvim_result(pane=pane, clear=strip_ansi(pane), file=file, dt=now() - t0)
