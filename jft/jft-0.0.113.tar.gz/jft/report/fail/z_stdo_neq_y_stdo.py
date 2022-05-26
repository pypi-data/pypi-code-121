from jft.text_colours.danger import f as danger
from jft.duration import f as duration
from jft.text_colours.primary import f as pri
from jft.text_colours.secondary import f as sec
from jft.report.summarise_file import f as summarise_file
from time import time

f = lambda name, x_args, x_stdi, y_stdo, z_stdo, time_started, max_filename_length: (
  False, '\n'.join([
    '|'.join([
      "\r",
      f"{danger('  FAIL  ')}",
      f" {name:{max_filename_length}} ",
      f" {duration(time_started, name)} ",
      ""
    ]),
    f"{danger('mode:')} y_stdo != z_stdo",
    f"{pri('Input       x_args: ')} {summarise_file(str(x_args))}",
    f"{sec('Input       x_stdi: ')} {summarise_file(str(x_stdi))}",
    f"{sec('Expectation y_stdo: ')} {summarise_file(str(y_stdo))}",
    f"{sec('Observation z_stdo: ')} {summarise_file(str(z_stdo))}",
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
    "\x1b[1;31mmode:\x1b[0;0m y_stdo != z_stdo",
    "\x1b[1;34mInput       x_args: \x1b[0;0m {'a': 0, 'b': 1}",
    "\x1b[0;35mInput       x_stdi: \x1b[0;0m []",
    "\x1b[0;35mExpectation y_stdo: \x1b[0;0m []",
    "\x1b[0;35mObservation z_stdo: \x1b[0;0m []"
  ])

  o_result, o_message = f(
    'fake_name',
    x_args={'a': 0, 'b': 1},
    x_stdi=[],
    y_stdo=[],
    z_stdo=[],
    time_started=time(),
    max_filename_length=9,
  )

  return all([
    e_result == o_result,
    e_message_l == o_message[:len(e_message_l)],
    e_message_r == o_message[len(o_message) - len(e_message_r):]
  ])
  