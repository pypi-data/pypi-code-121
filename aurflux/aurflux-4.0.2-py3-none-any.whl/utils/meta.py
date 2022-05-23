from __future__ import annotations

import inspect
import typing as ty

if ty.TYPE_CHECKING:
   from ..flux import FluxClient
   from ..command import Command
   from ..cog import FluxCog


def find_cmd_or_cog(flux: FluxClient, name: str, only=ty.Optional[ty.Literal["cog", "command"]]) -> ty.Optional[ty.Union[Command, FluxCog]]:
   for cog in flux.cogs:
      if only != "command" and cog.name.lower() == name.lower():
         return cog
      for command in cog.commands:
         if only != "cog" and command.name.lower() == name.lower():
            return command
   return None


def ms(key):
   try:
      return dict(inspect.getmembers(
         inspect.stack()[-1][0]))["f_globals"][key]
   except KeyError:
      for i in inspect.stack()[::-1]:
         try:
            return dict(inspect.getmembers(i[0]))["f_locals"][key]
         except KeyError:
            pass
         try:
            return dict(inspect.getmembers(i[0]))["f_globals"][key]
         except KeyError:
            pass
   raise KeyError("Could not find key " + key)
