from jft.text_colours.danger import f as danger
from jft.duration import f as duration
from time import time

f = lambda name, mode, time_started, max_filename_length: (
  False,
  '\n'.join([
    '|'.join([
      "\r",
      f"{danger('  FAIL  ')}",
      f" {name:{max_filename_length}} ",
      f" {duration(time_started, name)} ",
      ""
    ]),
    f"{danger('mode:')} {mode}",
  ])
)

def t():
  e_result = False
  e_message_l = '|'.join([
    '\r',
    '\x1b[1;31m  FAIL  \x1b[0;0m',
    ' fake_name ',
    ' \x1b[1;32m                           '
  ])
  e_message_r = '|'.join([
    '\x1b[0;0m ',
    '\n\x1b[1;31mmode:\x1b[0;0m fake_mode'
  ])
  
  o_result, o_message = f('fake_name', 'fake_mode', time(), 9)

  return all([
    e_message_l == o_message[:len(e_message_l)],
    e_message_r == o_message[len(o_message) - len(e_message_r):],
    e_result == o_result
  ])