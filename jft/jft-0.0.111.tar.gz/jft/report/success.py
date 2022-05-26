from jft.text_colours.success import f as success
from jft.duration import f as duration
from time import time

f = lambda name, time_started, max_filename_length: (
  True, '|'.join([
    "\r",
    f"{success('  PASS  ')}",
    f" {name:{max_filename_length}} ",
    f" {duration(time_started, name)} ",
    "",
  ])
)

def t():
  e_result = True
  e_message_l = '|'.join([
    '\r|\x1b[1;32m  PASS  \x1b[0;0m',
    ' fake_name ',
    ' \x1b[1;32m                           '
  ])
  e_message_r = '\x1b[0;0m |'

  o_result, o_message = f('fake_name', time(), 9)

  return all([
    e_result == o_result,
    e_message_l == o_message[0:len(e_message_l)],
    e_message_r == o_message[len(o_message) - len(e_message_r):]
  ])
