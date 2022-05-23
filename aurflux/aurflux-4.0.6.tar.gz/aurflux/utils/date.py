from __future__ import annotations

DATETIME_FMT_L = "%I:%M:%S %p %Z on %a, %b %d, %Y"
DATETIME_FMT_S = "%Y-%m-%d %H:%M %Z"

TIME_DURATION_UNITS = (
   ('week', 60 * 60 * 24 * 7),
   ('day', 60 * 60 * 24),
   ('hour', 60 * 60),
   ('min', 60),
   ('sec', 1)
)


def human_time(seconds: int) -> str:
   if seconds == 0:
      return 'No time at all!'
   parts = []
   for unit, div in TIME_DURATION_UNITS:
      amount, seconds = divmod(int(seconds), div)
      if amount > 0:
         parts.append('{} {}{}'.format(amount, unit, "" if amount == 1 else "s"))
   return ', '.join(parts)
