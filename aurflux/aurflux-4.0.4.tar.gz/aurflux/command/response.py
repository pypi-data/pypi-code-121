from __future__ import annotations

__package__ = "aurflux.command"

import typing as ty

if ty.TYPE_CHECKING:
   from ..context import MessageCtx, CommandCtx
   from ..flux import FluxEvent
import time
import aurcore as aur
import typing as ty
import asyncio as aio
import discord
from .. import utils
import datetime
from loguru import logger
import enum


class Status(enum.Enum):
   OK = utils.EMOJI.check
   ERROR = utils.EMOJI.x


class Response(aur.util.AutoRepr):
   __iter_done = False
   message: ty.Optional[discord.Message]
   delete_after: ty.Optional[float]

   def __init__(
         self,
         # ctx: Context,
         content: str = None,
         embed: discord.Embed = None,
         delete_after: ty.Union[float, datetime.timedelta] = None,
         status: ty.Literal["ok", "error"] = "ok",
         ping: bool = False,
         post_process: ty.Callable[[MessageCtx, ty.Optional[discord.Message], Status], ty.Coroutine] = None,
         trashable: bool = True,
   ):
      self.content = content
      self.embed = embed

      if isinstance(delete_after, datetime.timedelta):
         self.delete_after = delete_after.total_seconds()
      else:
         self.delete_after = delete_after

      self.message: ty.Optional[discord.Message] = None
      self.status = status
      self.ping = ping
      self.post_process = post_process or (lambda *_: aio.sleep(0))
      self.trashable = trashable

   async def execute(self, ctx: CommandCtx) -> None:
      try:
         if self.status == "ok":
            await ctx.msg_ctx.message.add_reaction(utils.EMOJI.check)
         if self.status == "error":
            await ctx.msg_ctx.message.add_reaction(utils.EMOJI.x)
      except (discord.errors.NotFound, discord.errors.Forbidden):
         pass
      if not self.content and not self.embed:
         return

      content = self.content if self.content else "" + (f"\n{ctx.author_ctx.author.mention}" if self.ping else "")
      if len(content) > 1900:
         content = f"Output too long, see:\n{await utils.haste(ctx.flux.aiohttp_session, content)}"

      self.message = await ctx.msg_ctx.dest.send(
         content=content,
         embed=self.embed,
         delete_after=self.delete_after
      )

      async def handle_trash() -> None:
         try:
            await self.message.add_reaction(utils.EMOJI.trashcan)
            try:
               await ctx.msg_ctx.flux.router.wait_for(
                  ":reaction_add",
                  check=lambda ev: ev.args[0].message.id == self.message.id and ev.args[1] == ctx.msg_ctx.message.author and ev.args[0].emoji == utils.EMOJI.trashcan,
                  timeout=20
               )
               await self.message.delete()
            except aio.exceptions.TimeoutError:
               await self.message.remove_reaction(emoji=utils.EMOJI.trashcan, member=ctx.flux.user)

         except (discord.errors.NotFound, discord.errors.Forbidden):
            pass

      if self.trashable and self.message:
         aio.create_task(handle_trash())

      await self.post_process(ctx.msg_ctx, self.message, self.status)
