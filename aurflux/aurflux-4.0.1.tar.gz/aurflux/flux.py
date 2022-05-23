from __future__ import annotations

import asyncio as aio
import importlib
import typing as ty

import aiohttp
import aurcore
import aurcore as aur
import discord.errors
import discord.ext
from aurcore import EventRouter
from loguru import logger

import sys
import inspect

from .config import Config
from .context import CommandCtx, GuildMessageCtx, MessageCtx
from .errors import CommandError

if ty.TYPE_CHECKING:
   import discord
   from .cog import FluxCog
   from aurcore import EventRouterHost

aur.log.setup()


class FluxEvent(aur.Event):
   def __init__(self, flux: FluxClient, __event_name: str, *args, **kwargs):
      super().__init__(__event_name, *args, **kwargs)
      self.flux: FluxClient = flux


class CommandEvent(FluxEvent):
   def __init__(self, flux: FluxClient, cmd_ctx: CommandCtx, cmd_args: ty.Optional[str], cmd_name: str, cmd_flags:ty.List[str] = ()):
      super().__init__(flux, f"flux:command:{cmd_name}")
      self.cmd_name = cmd_name
      self.cmd_ctx = cmd_ctx
      self.cmd_args = cmd_args
      self.cmd_flags = cmd_flags


class FluxClient(discord.Client):

   def __init__(
         self,
         name: str,
         admin_id: int,
         parent_router: EventRouterHost,
         builtins: bool = True,
         status: ty.Optional[str] = None,
         host: aurcore.AurCore = None,
         *args, **kwargs
   ):
      if status:
         # noinspection PyArgumentList
         self._activity = discord.Game(name=status)
         kwargs |= {"activity": self._activity}

      super(FluxClient, self).__init__(*args, **kwargs)

      self.router = EventRouter(name="flux", host=parent_router)
      self.CONFIG: Config = Config(admin_id=admin_id, name=name)
      self.admin_id = admin_id
      self.cogs: ty.List[FluxCog] = []

      self.aiohttp_session = aiohttp.ClientSession()

      self.register_listeners()

      if builtins:
         from .cog.builtins import Builtins
         self.register_cog(Builtins)

   def dispatch(self, event, *args, **kwargs) -> None:
      super(FluxClient, self).dispatch(event, *args, **kwargs)
      aio.create_task(self.router.submit(
         FluxEvent(self, f":{event}", *args, **kwargs)))

   def register_cog(self, cog: ty.Type[FluxCog]) -> FluxCog:
      c = cog(flux=self)
      logger.success(f"Registered {c}")
      self.cogs.append(c)
      return c

   async def debug_message(self, msg: str):
      await (await self.get_user_s(self.admin_id)).send(msg)

   async def reload_cog(self, cog_name: str) -> None:

      cog = next((cog for cog in self.cogs if cog.name == cog_name), None)
      if not cog:
         raise CommandError(f"`{cog_name}` not recognized in list of cogs")
      cog.teardown()
      self.cogs.remove(cog)

      cog_module = importlib.reload(sys.modules[cog.__module__])

      # logger.info(str(cog_module))
      # logger.info(str(cog.__class__.__name__))
      # logger.info(str(inspect.getmembers(cog_module)))

      cog = self.register_cog(getattr(cog_module, cog.__class__.__name__))
      await cog.startup()

   async def startup(self, token, *args, **kwargs) -> None:
      for cog in self.cogs:
         logger.info(f"Starting up cog: {cog}")
         aio.create_task(cog.startup(), name=str(cog)).add_done_callback(lambda t: logger.success(f"Successfully started up cog: {t.get_name()}"))
      # async def x():
      #    await aio.gather(*[cog.startup() for cog in self.cogs])

      # aio.create_task(x())
      logger.info("Starting discord!")
      await self.start(token, *args, **kwargs)

   async def shutdown(self, *args, **kwargs) -> None:
      await self.close()

   def register_listeners(self) -> None:
      @self.router.listen_for(":message")
      @aur.Eventful.decompose
      async def _(message: discord.Message) -> None:
         if not message.content or message.author is self.user:
            return
         if message.guild:
            ctx = GuildMessageCtx(flux=self, message=message)
         else:
            ctx = MessageCtx(flux=self, message=message)

         prefix = self.CONFIG.of(ctx)["prefix"]

         if not message.content.startswith(prefix):
            return
         raw_cmd, args, *_ = [*message.content.split(" ", 1), None]

         raw_cmd_name, raw_cmd_flags, *_ = [*raw_cmd.split(":"), None]

         cmd_name = raw_cmd_name[len(prefix):]

         await self.router.submit(event=CommandEvent(flux=self, cmd_ctx=CommandCtx(self, ctx, ctx, [ctx]), cmd_name=cmd_name, cmd_args=args.strip() if args else None, cmd_flags=raw_cmd_flags.split(",") if raw_cmd_flags else []))

      @self.router.listen_for(":resume")
      async def _(_):
         logger.info("Resuming...")
         await self.change_presence(activity=self._activity)

      @self.router.listen_for(":guild_join")
      async def _(ev: FluxEvent):
         logger.info(f"Joined guild: {ev.args[0]}")

      @self.router.listen_for(":guild_remove")
      async def _(ev: FluxEvent):
         logger.info(f"Removed from guild: {ev.args[0]}")

   async def get_user_s(self, user_id: int) -> ty.Optional[discord.User]:
      try:
         return self.get_user(user_id) or await self.fetch_user(user_id)
      except discord.errors.NotFound:
         return None

   async def get_member_s(self, g: discord.Guild, member_id: int) -> ty.Optional[discord.Member]:
      try:
         return g.get_member(member_id) or await g.fetch_member(member_id)
      except discord.errors.NotFound:
         return None

   async def get_channel_s(
         self, id_: int
   ) -> ty.Optional[ty.Union[discord.abc.GuildChannel, discord.abc.PrivateChannel]]:
      try:
         return self.get_channel(id_) or await self.fetch_channel(id_)
      except (discord.NotFound, discord.Forbidden, discord.HTTPException):
         return None


class FluxCore(aur.AurCore):
   def __init__(self, name: str, admin_id: int, status: str = None, intents: discord.Intents = None):
      super(FluxCore, self).__init__(name)
      self.flux = FluxClient(name=name, admin_id=admin_id, parent_router=self.router, status=status, intents=intents)

   async def startup(self, token: str, *args: ty.Any, **kwargs: ty.Any) -> None:
      await super(FluxCore, self).startup(*args, **kwargs)
      await self.flux.start(token)

   async def shutdown(self, *args: ty.Any, **kwargs: ty.Any) -> None:
      await super(FluxCore, self).shutdown(*args, **kwargs)
      await self.flux.logout()
      await self.flux.aiohttp_session.close()
