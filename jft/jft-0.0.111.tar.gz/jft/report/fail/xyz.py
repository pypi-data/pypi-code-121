from jft.text_colours.danger import f as danger
from jft.duration import f as duration
from jft.text_colours.primary import f as pri
from jft.text_colours.secondary import f as sec
from jft.report.summarise_file import f as summarise_file
from time import time

f = lambda name, xyz, mode, time_started, max_filename_length: (
  False, '\n'.join([
    '|'.join([
      "\r",
      f"{danger('  FAIL  ')}",
      f" {name:{max_filename_length}} ",
      f" {duration(time_started, name)} ",
      ""
    ]),
    f"{danger('mode:')} {mode}",
    f"{pri('Input       x_args: ')} {summarise_file(str(xyz['x_args']))}",
    f"{pri('Expectation y_return: ')} {summarise_file(str(xyz['y_return']))}",
    f"{pri('Observation z_return: ')} {summarise_file(str(xyz['z_return']))}",
    f"{sec('Input       x_stdi: ')} {summarise_file(str(xyz['x_stdi']))}",
    f"{sec('Expectation y_stdo: ')} {summarise_file(str(xyz['y_stdo']))}",
    f"{sec('Observation z_stdo: ')} {summarise_file(str(xyz['z_stdo']))}",
  ])
)

def t():
  e_result = False
  e_message_l = '|'.join([
    "\r",
    "\x1b[1;31m  FAIL  \x1b[0;0m",
    " fake_name ",
    " \x1b[1;32m                           "
  ])
  e_message_r = '\n'.join([
    "\x1b[0;0m |",
    "\x1b[1;31mmode:\x1b[0;0m fake_mode",
    "\x1b[1;34mInput       x_args: \x1b[0;0m {'a': 0, 'b': 1}",
    "\x1b[1;34mExpectation y_return: \x1b[0;0m 0.5",
    "\x1b[1;34mObservation z_return: \x1b[0;0m 0.5",
    "\x1b[0;35mInput       x_stdi: \x1b[0;0m []",
    "\x1b[0;35mExpectation y_stdo: \x1b[0;0m []",
    "\x1b[0;35mObservation z_stdo: \x1b[0;0m []"
  ])

  o_result, o_message = f(
    'fake_name',
    {
      'x_args': {'a': 0, 'b': 1},
      'y_return': 0.5,
      'z_return': 0.5,
      'x_stdi': [],
      'y_stdo': [],
      'z_stdo': [],
    },
    'fake_mode',
    time(),
    9,
  )

  return all([
    e_result == o_result,
    e_message_l == o_message[:len(e_message_l)],
    e_message_r == o_message[len(o_message) - len(e_message_r):]
  ])
  