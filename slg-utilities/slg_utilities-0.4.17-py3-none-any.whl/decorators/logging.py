import traceback
import logging
import os


def log_error(filename, full_traceback=False):
  def outer(func):
    def inner(*args, **kwargs):
      try:
        return func(*args, **kwargs)
      except Exception as e:
        if not os.path.exists(f"/var/log/usr/{filename}"):
          with open(f"/var/log/usr/{filename}", 'w+'):
            pass

        logging.basicConfig(filename=f"/var/log/usr/{filename}", level=logging.INFO, format='%(asctime)s %(message)s')
        if full_traceback:
          tb = traceback.format_exc(limit=6).replace(",", "\n")
          logging.error(f'Full traceback: {tb}')
        else:
          logging.error(f'Error: {e}')
        print(e)
      return
    return inner
  return outer



