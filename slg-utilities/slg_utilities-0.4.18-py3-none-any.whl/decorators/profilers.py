from ..helpers import *
import cProfile




def cProfile_dec(sort_by='tottime'):

  def outer(func):

    def inner(*args, **kwargs):

      profile = cProfile.Profile()
      profile.enable()

      output = func(*args, **kwargs)

      profile.print_stats(sort=sort_by)
      # sorting methods here:
      # https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats

      profile.disable()

      return output

    return inner

  return outer


def timeit(func):
  #decorator that wraps function with simple time log

  def inner(*args, **kwargs):

    t0 = time.time()
    prnt(args, 'args')
    prnt(kwargs, 'kwargs')

    output = func(*args, **kwargs)

    prnt(time.time() - t0, f"Time taken for {func.__name__}")

    return output

  return inner


@cProfile_dec()
def prof_test():
  j=1
  for i in range(10000000):
    j*=1.00000001

  return j