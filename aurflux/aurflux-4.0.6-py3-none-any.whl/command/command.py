from __future__ import annotations

import asyncio.exceptions
import functools as fnt
import traceback
import typing as ty

import aurcore as aur
from loguru import logger

from .response import Response
from .. import errors
from ..auth import Auth, AuthAware
from ..context import GuildMessageCtx

if ty.TYPE_CHECKING:
   from ..types_ import *
   from .. import FluxClient
   from ..cog import FluxCog
   from ..auth import Record
   from ..flux import CommandEvent
import typing as ty
import inspect


class Command(aur.util.AutoRepr, AuthAware):

   def __init__(
         self,
         flux: FluxClient,
         cog: FluxCog,
         func: CommandFunc,
         name: str,
         decompose: bool,
         allow_dm: bool,
         default_auths: ty.List[Record],
         override_auths: ty.List[Record],
   ):
      self.func = func
      self.flux = flux
      self.cog = cog
      self.name = name
      self.doc = inspect.getdoc(func)
      self.decompose = decompose
      self.allow_dm = allow_dm

      self.default_auths_: ty.List[Record] = default_auths
      self.override_auths_: ty.List[Record] = override_auths

      func_doc = inspect.getdoc(self.func)
      if not func_doc:
         raise RuntimeError(f"{self.func} lacks a docstring!")
      if self.func.__code__.co_argcount == 2:
         logger.warning(f"Deprecation Warning: {self.func} missing argument for flags")
      try:
         usage, description, params, *_ = func_doc.split("==")
      except ValueError as e:
         raise ValueError(f"{e} : {self.name}")

      self.usage = usage.strip()
      self.description = description.strip()

      def combine_params(acc: ty.List[ty.Tuple[str, str]], x: str):
         if acc and acc[-1][1].endswith("\\"):
            param_name, detail = acc.pop()
            # noinspection PyUnresolvedReferences,Mypy
            acc.append((param_name, detail.removesuffix("\\").strip() + "\n" + x))
         else:
            try:
               param_name, detail = x.split(":", 1)
            except ValueError as e:
               raise ValueError(f"Command {self.cog}:{self.name} is missing a ':' in param: {x}")
            acc.append((param_name, detail))
         return acc

      try:
         self.param_usage: ty.List[ty.Tuple[str, str]] = fnt.reduce(combine_params, [x for x in params.strip().split("\n") if x], [])
      except ValueError as e:
         raise ValueError(f"Param Parse error {e} in {self.name}")

   async def execute(self, ev: CommandEvent) -> None:
      cmd_ctx = ev.cmd_ctx

      if not isinstance(cmd_ctx.msg_ctx, GuildMessageCtx) and not self.allow_dm:
         return await Response(content="Cannot be used in DMs", status="error").execute(cmd_ctx)

      logger.trace(f"Command {self} executing in {cmd_ctx.msg_ctx}")

      if not Auth.accepts_all(cmd_ctx.auth_ctxs, self):
         return await Response(content="Forbidden", status="error").execute(cmd_ctx)

      try:
         with cmd_ctx.msg_ctx.dest.typing():
            if self.decompose:
               res = self.func(cmd_ctx, *ev.args, **ev.kwargs)
            else:
               if ev.cmd_flags or self.func.__code__.co_argcount == 3: #Todo: breaking release to remove this hack
                  res = self.func(cmd_ctx, ev.cmd_args, ev.cmd_flags)
               else:
                  res = self.func(cmd_ctx, ev.cmd_args)

         if res:
            async for resp in aur.util.AwaitableAiter(res):
               await resp.execute(cmd_ctx) if resp else None
      except errors.CommandError as e:
         info_message = f"{e}"
         await Response(content=info_message, status="error").execute(cmd_ctx)
      except errors.CommandInfo as e:
         info_message = f"{e}"
         await Response(content=info_message).execute(cmd_ctx)
      except asyncio.exceptions.TimeoutError:
         await Response(content="Timed out! Try again :(").execute(cmd_ctx)
      except Exception as e:
         print(traceback.format_exc())
         await Response(content=f"```Unexpected Exception:\n{str(e)}\n```", status="error", trashable=True).execute(cmd_ctx)
         logger.exception(f"Unexpected Command Exception from {self}:")

   @property
   def auth_id(self) -> str:
      return f"{self.cog.name}:{self.name}"

   @property
   def default_auths(self) -> ty.List[Record]:
      return self.default_auths_

   @property
   def override_auths(self) -> ty.List[Record]:
      return self.override_auths_

   def __str__(self):
      return f"<Command {self.name} in {self.cog}: {self.func.__name__}>"