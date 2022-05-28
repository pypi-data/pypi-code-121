"""
prettier & prettier logging
"""

import os
import re
import sys
import json
import math
import logging
import datetime
from typing import Tuple, List, Dict, Any, Union
from pygments import highlight, lexers, formatters
from collections import OrderedDict
from collections.abc import Sized

import pandas as pd
from transformers import TrainerCallback
import sty
import colorama
from tqdm.auto import tqdm

from stefutil.primitive import is_float


__all__ = [
    'fmt_num', 'fmt_sizeof', 'fmt_delta', 'sec2mmss', 'round_up_1digit', 'nth_sig_digit', 'now',
    'log', 'log_s', 'logi', 'log_dict', 'log_dict_nc', 'log_dict_id', 'log_dict_pg', 'log_dict_p',
    'hex2rgb', 'MyTheme', 'MyFormatter', 'get_logger',
    'MlPrettier', 'MyProgressCallback'
]


pd.set_option('expand_frame_repr', False)
pd.set_option('display.precision', 2)
pd.set_option('max_colwidth', 40)
pd.set_option('display.max_columns', None)


def fmt_num(num: Union[float, int], suffix: str = '') -> str:
    """
    Convert number to human-readable format, in e.g. Thousands, Millions
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1000.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1000.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def fmt_sizeof(num: int, suffix='B') -> str:
    """ Converts byte size to human-readable format """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def fmt_delta(secs: Union[int, float, datetime.timedelta]) -> str:
    if isinstance(secs, datetime.timedelta):
        secs = secs.seconds + (secs.microseconds/1e6)
    if secs >= 86400:
        d = secs // 86400  # // floor division
        return f'{round(d)}d{fmt_delta(secs - d * 86400)}'
    elif secs >= 3600:
        h = secs // 3600
        return f'{round(h)}h{fmt_delta(secs - h * 3600)}'
    elif secs >= 60:
        m = secs // 60
        return f'{round(m)}m{fmt_delta(secs - m * 60)}'
    else:
        return f'{round(secs)}s'


def sec2mmss(sec: int) -> str:
    return str(datetime.timedelta(seconds=sec))[2:]


def round_up_1digit(num: int):
    d = math.floor(math.log10(num))
    fact = 10**d
    return math.ceil(num/fact) * fact


def nth_sig_digit(flt: float, n: int = 1) -> float:
    """
    :return: first n-th significant digit of `sig_d`
    """
    return float('{:.{p}g}'.format(flt, p=n))


def now(as_str=True, for_path=False) -> Union[datetime.datetime, str]:
    """
    # Considering file output path
    :param as_str: If true, returns string; otherwise, returns datetime object
    :param for_path: If true, the string returned is formatted as intended for file system path
    """
    d = datetime.datetime.now()
    fmt = '%Y-%m-%d_%H-%M-%S' if for_path else '%Y-%m-%d %H:%M:%S'
    return d.strftime(fmt) if as_str else d


def log(s, c: str = 'log', c_time='green', as_str=False, bold: bool = False, pad: int = None):
    """
    Prints `s` to console with color `c`
    """
    if not hasattr(log, 'reset'):
        log.reset = colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL
    if not hasattr(log, 'd'):
        log.d = dict(
            log='',
            warn=colorama.Fore.YELLOW,
            error=colorama.Fore.RED,
            err=colorama.Fore.RED,
            success=colorama.Fore.GREEN,
            suc=colorama.Fore.GREEN,
            info=colorama.Fore.BLUE,
            i=colorama.Fore.BLUE,
            w=colorama.Fore.RED,

            y=colorama.Fore.YELLOW,
            yellow=colorama.Fore.YELLOW,
            red=colorama.Fore.RED,
            r=colorama.Fore.RED,
            green=colorama.Fore.GREEN,
            g=colorama.Fore.GREEN,
            blue=colorama.Fore.BLUE,
            b=colorama.Fore.BLUE,

            m=colorama.Fore.MAGENTA
        )
    if c in log.d:
        c = log.d[c]
    if bold:
        c += colorama.Style.BRIGHT
    if as_str:
        return f'{c}{s:>{pad}}{log.reset}' if pad is not None else f'{c}{s}{log.reset}'
    else:
        print(f'{c}{log(now(), c=c_time, as_str=True)}| {s}{log.reset}')


def log_s(s, c, bold: bool = False):
    return log(s, c=c, as_str=True, bold=bold)


def logi(s):
    """
    Syntactic sugar for logging `info` as string
    """
    return log_s(s, c='i')


def log_dict(d: Dict = None, with_color=True, pad_float: int = 5, sep=': ', **kwargs) -> str:
    """
    Syntactic sugar for logging dict with coloring for console output
    """
    def _log_val(v):
        if isinstance(v, dict):
            return log_dict(v, with_color=with_color)
        else:
            if is_float(v):  # Pad only normal, expected floats, intended for metric logging
                if is_float(v, no_int=True, no_sci=True):
                    v = float(v)
                    return log(v, c='i', as_str=True, pad=pad_float) if with_color else f'{v:>{pad_float}}'
                else:
                    return logi(v) if with_color else v
            else:
                return logi(v) if with_color else v
    d = d or kwargs or dict()
    pairs = (f'{k}{sep}{_log_val(v)}' for k, v in d.items())
    pref = log_s('{', c='m') if with_color else '{'
    post = log_s('}', c='m') if with_color else '}'
    return pref + ', '.join(pairs) + post


def log_dict_nc(d: Dict = None, **kwargs) -> str:
    """
    Syntactic sugar for no color
    """
    return log_dict(d, with_color=False, **kwargs)


def log_dict_id(d: Dict) -> str:
    """
    Indented dict
    """
    return json.dumps(d, indent=4)


def log_dict_pg(d: Dict) -> str:
    """
    prettier dict colored by `pygments` and with indent
    """
    return highlight(log_dict_id(d), lexers.JsonLexer(), formatters.TerminalFormatter())


def log_dict_p(d: Dict, **kwargs) -> str:
    """
    a compact, one-line str for dict

    Intended as part of filename
    """
    return log_dict(d, with_color=False, sep='=', **kwargs)


def hex2rgb(hx: str, normalize=False) -> Union[Tuple[int], Tuple[float]]:
    # Modified from https://stackoverflow.com/a/62083599/10732321
    if not hasattr(hex2rgb, 'regex'):
        hex2rgb.regex = re.compile(r'#[a-fA-F\d]{3}(?:[a-fA-F\d]{3})?$')
    m = hex2rgb.regex.match(hx)
    assert m is not None
    if len(hx) <= 4:
        ret = tuple(int(hx[i]*2, 16) for i in range(1, 4))
    else:
        ret = tuple(int(hx[i:i+2], 16) for i in range(1, 7, 2))
    return tuple(i/255 for i in ret) if normalize else ret


class MyTheme:
    """
    Theme based on `sty` and `Atom OneDark`
    """
    COLORS = OrderedDict([
        ('yellow', 'E5C07B'),
        ('green', '00BA8E'),
        ('blue', '61AFEF'),
        ('cyan', '2AA198'),
        ('red', 'E06C75'),
        ('purple', 'C678DD')
    ])
    yellow, green, blue, cyan, red, purple = (
        hex2rgb(f'#{h}') for h in ['E5C07B', '00BA8E', '61AFEF', '2AA198', 'E06C75', 'C678DD']
    )

    @staticmethod
    def set_color_type(t: str):
        """
        Sets the class attribute accordingly

        :param t: One of ['rgb`, `sty`]
            If `rgb`: 3-tuple of rgb values
            If `sty`: String for terminal styling prefix
        """
        for color, hex_ in MyTheme.COLORS.items():
            val = hex2rgb(f'#{hex_}')  # For `rgb`
            if t == 'sty':
                setattr(sty.fg, color, sty.Style(sty.RgbFg(*val)))
                val = getattr(sty.fg, color)
            setattr(MyTheme, color, val)


class MyFormatter(logging.Formatter):
    """
    Modified from https://stackoverflow.com/a/56944256/10732321

    Default styling: Time in green, metadata indicates severity, plain log message
    """
    RESET = sty.rs.fg + sty.rs.bg + sty.rs.ef

    MyTheme.set_color_type('sty')
    yellow, green, blue, cyan, red, purple = (
        MyTheme.yellow, MyTheme.green, MyTheme.blue, MyTheme.cyan, MyTheme.red, MyTheme.purple
    )

    KW_TIME = '%(asctime)s'
    KW_MSG = '%(message)s'
    KW_LINENO = '%(lineno)d'
    KW_FNM = '%(filename)s'
    KW_FUNC_NM = '%(funcName)s'
    KW_NAME = '%(name)s'

    DEBUG = INFO = BASE = RESET
    WARN, ERR, CRIT = yellow, red, purple
    CRIT += sty.Style(sty.ef.bold)

    LVL_MAP = {  # level => (abbreviation, style)
        logging.DEBUG: ('DBG', DEBUG),
        logging.INFO: ('INFO', INFO),
        logging.WARNING: ('WARN', WARN),
        logging.ERROR: ('ERR', ERR),
        logging.CRITICAL: ('CRIT', CRIT)
    }

    def __init__(self, with_color=True, color_time=green):
        super().__init__()
        self.with_color = with_color

        sty_kw, reset = MyFormatter.blue, MyFormatter.RESET
        color_time = f'{color_time}{MyFormatter.KW_TIME}{sty_kw}|{reset}'

        def args2fmt(args_):
            if self.with_color:
                return color_time + self.fmt_meta(*args_) + f'{sty_kw}: {reset}{MyFormatter.KW_MSG}' + reset
            else:
                return f'{MyFormatter.KW_TIME}| {self.fmt_meta(*args_)}: {MyFormatter.KW_MSG}'

        self.formats = {level: args2fmt(args) for level, args in MyFormatter.LVL_MAP.items()}
        self.formatter = {
            lv: logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S') for lv, fmt in self.formats.items()
        }

    def fmt_meta(self, meta_abv, meta_style=None):
        if self.with_color:
            return f'{MyFormatter.purple}[{MyFormatter.KW_NAME}]' \
               f'{MyFormatter.blue}::{MyFormatter.purple}{MyFormatter.KW_FUNC_NM}' \
               f'{MyFormatter.blue}::{MyFormatter.purple}{MyFormatter.KW_FNM}' \
               f'{MyFormatter.blue}:{MyFormatter.purple}{MyFormatter.KW_LINENO}' \
               f'{MyFormatter.blue}:{meta_style}{meta_abv}{MyFormatter.RESET}'
        else:
            return f'[{MyFormatter.KW_NAME}] {MyFormatter.KW_FUNC_NM}::{MyFormatter.KW_FNM}' \
                   f':{MyFormatter.KW_LINENO}, {meta_abv}'

    def format(self, entry):
        return self.formatter[entry.levelno].format(entry)


def get_logger(name: str, typ: str = 'stdout', file_path: str = None) -> logging.Logger:
    """
    :param name: Name of the logger
    :param typ: Logger type, one of [`stdout`, `file-write`]
    :param file_path: File path for file-write logging
    """
    assert typ in ['stdout', 'file-write']
    logger = logging.getLogger(f'{name} file write' if typ == 'file-write' else name)
    logger.handlers = []  # A crude way to remove prior handlers, ensure only 1 handler per logger
    logger.setLevel(logging.DEBUG)
    if typ == 'stdout':
        handler = logging.StreamHandler(stream=sys.stdout)  # stdout for my own coloring
    else:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        handler = logging.FileHandler(file_path)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(MyFormatter(with_color=typ == 'stdout'))
    logger.addHandler(handler)
    return logger


class MlPrettier:
    """
    My utilities for deep learning training logging
    """
    def __init__(self, ref: Dict[str, Any] = None, metric_keys: List[str] = None):
        """
        :param ref: Reference that are potentially needed
            i.e. for logging epoch/step, need the total #
        :param metric_keys: keys that are considered metric
            Will be logged in [0, 100]
        """
        self.ref = ref
        self.metric_keys = metric_keys or ['acc', 'recall', 'auc']

    def __call__(self, d: Union[str, Dict], val=None) -> Union[Any, Dict[str, Any]]:
        """
        :param d: If str, prettify a single value
            Otherwise, prettify a dict
        """
        is_dict = isinstance(d, dict)
        if not ((isinstance(d, str) and val is not None) or is_dict):
            raise ValueError('Either a key-value pair or a mapping is expected')
        if is_dict:
            d: Dict
            return {k: self._pretty_single(k, v) for k, v in d.items()}
        else:
            return self._pretty_single(d, val)

    def _pretty_single(self, key: str, val=None) -> Union[str, List[str], Dict[str, Any]]:
        """
        `val` processing is infered based on key
        """
        if key in ['step', 'epoch']:
            k = next(iter(k for k in self.ref.keys() if key in k))
            lim = self.ref[k]
            assert isinstance(val, (int, float))
            len_lim = len(str(lim))
            if isinstance(val, int):
                s_val = f'{val:>{len_lim}}'
            else:
                fmt = f'%{len_lim + 4}.3f'
                s_val = fmt % val
            return f'{s_val}/{lim}'  # Pad integer
        elif 'loss' in key:
            return f'{round(val, 4):7.4f}'
        elif any(k in key for k in self.metric_keys):  # custom in-key-ratio metric
            def _single(v):
                return f'{round(v * 100, 2):6.2f}' if v is not None else '-'

            if isinstance(val, list):
                return [_single(v) for v in val]
            elif isinstance(val, dict):
                return {k: _single(v) for k, v in val.items()}
            else:
                return _single(val)
        elif 'learning_rate' in key or 'lr' in key:
            return f'{round(val, 7):.3e}'
        else:
            return val


class MyProgressCallback(TrainerCallback):
    """
    My modification to the HF progress callback

    1. Effectively remove all logging, keep only the progress bar w.r.t. this callback
    2. Train tqdm for each epoch only
    3. Option to disable progress bar for evaluation

    Expects to start from whole epochs
    """
    def __init__(self, train_only: bool = False):
        """
        :param train_only: If true, disable progress bar for evaluation
        """
        self.training_bar = None
        self.prediction_bar = None
        self.train_only = train_only
        self.step_per_epoch = None
        self.current_step = None

    @staticmethod
    def _get_steps_per_epoch(state):
        assert state.max_steps % state.num_train_epochs == 0
        return state.max_steps // state.num_train_epochs

    @staticmethod
    def _get_curr_epoch(state) -> str:
        return MlPrettier(ref=dict(epoch=state.num_train_epochs))('epoch', int(state.epoch+1))

    def on_epoch_begin(self, args, state, control, **kwargs):
        if state.is_local_process_zero:
            if not self.step_per_epoch:
                self.step_per_epoch = MyProgressCallback._get_steps_per_epoch(state)
            ep = MyProgressCallback._get_curr_epoch(state)
            self.training_bar = tqdm(total=self.step_per_epoch, desc=f'Train Epoch {ep}')
        self.current_step = 0

    def on_train_begin(self, args, state, control, **kwargs):
        pass

    def on_epoch_end(self, args, state, control, **kwargs):
        if state.is_local_process_zero:
            self.training_bar.close()
            self.training_bar = None

    def on_step_end(self, args, state, control, **kwargs):
        if state.is_local_process_zero:
            self.training_bar.update(1)

    def on_prediction_step(self, args, state, control, eval_dataloader=None, **kwargs):
        if not self.train_only:
            if state.is_local_process_zero and isinstance(eval_dataloader.dataset, Sized):
                if self.prediction_bar is None:
                    ep = MyProgressCallback._get_curr_epoch(state)
                    desc = f'Eval Epoch {ep}'
                    self.prediction_bar = tqdm(desc=desc, total=len(eval_dataloader), leave=self.training_bar is None)
                self.prediction_bar.update(1)

    def on_evaluate(self, args, state, control, **kwargs):
        if not self.train_only:
            if state.is_local_process_zero:
                if self.prediction_bar is not None:
                    self.prediction_bar.close()
                self.prediction_bar = None

    def on_log(self, args, state, control, logs=None, **kwargs):
        if state.is_local_process_zero and self.training_bar is not None:
            _ = logs.pop("total_flos", None)

    def on_train_end(self, args, state, control, **kwargs):
        pass


if __name__ == '__main__':
    lg = get_logger('test')
    lg.info('test')
