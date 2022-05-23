from __future__ import annotations

import time


class Timer:
   def __enter__(self):
      self.elapsed = time.perf_counter()
      return self

   def __exit__(self, exc_type, exc_val, exc_tb):
      self.elapsed = time.perf_counter() - self.elapsed