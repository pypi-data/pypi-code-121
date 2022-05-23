from __future__ import annotations
import abc
import typing as ty
from abc import ABCMeta
from builtins import property
import dataclasses as dtcs
import re
import aurcore as aur

from ..auth import AuthList
from ..utils import parsers

if ty.TYPE_CHECKING:
   import discord
   from .. import FluxClient


@dtcs.dataclass
class CommandCtx(aur.util.AutoRepr):
   flux: FluxClient
   msg_ctx: MessageCtx
   author_ctx: AuthorAwareCtx
   auth_ctxs: ty.List[AuthAwareCtx]


# @dtcs.dataclass
# class GuildCommandCtx(CommandCtx):
#    msg_ctx: GuildMessageCtx
#    author_ctx: AuthorAwareCtx
#    auth_ctxs: ty.List[AuthAwareCtx]


class ConfigCtx(aur.util.AutoRepr):
   def __init__(self, flux: FluxClient, **kwargs):
      self.flux = flux

   @property
   @abc.abstractmethod
   def config_identifier(self) -> str: ...

   @property
   def config(self) -> ty.Dict[str, ty.Any]:
      return self.flux.CONFIG.of(self)

   @property
   def me(self) -> discord.abc.User:
      return self.flux.user


class GuildAwareCtx(ConfigCtx):
   def __init__(self, flux: FluxClient, **kwargs):
      super().__init__(flux=flux, **kwargs)

   @property
   @abc.abstractmethod
   def guild(self) -> discord.Guild:
      ...

   @property
   def config_identifier(self) -> str:
      return str(self.guild.id)

   async def find_in_guild(self, _type: ty.Literal["member", "channel", "role"], id_: str):
      if _type == "member":
         return self.guild.get_member(int(id_))
      if _type == "channel":
         return self.guild.get_channel(int(id_))
      if _type == "role":
         return self.guild.get_role(int(id_))

      return None


# class GuildCommandCtx(CommandCtx, GuildAwareCtx):
#    def __init__(self, guild: discord.Guild, **kwargs):
#       super().__init__(**kwargs)
#       self.guild_ = guild
#
#    @property
#    def guild(self) -> discord.Guild:
#       return self.guild_


class AuthorAwareCtx:
   @property
   @abc.abstractmethod
   def author(self) -> ty.Union[discord.User, discord.Member]: ...


class _MessageableCtx(ConfigCtx):
   def __init__(self, flux: FluxClient, **kwargs):
      super().__init__(flux=flux, **kwargs)

   @property
   @abc.abstractmethod
   def dest(self) -> discord.abc.Messageable: ...


class AuthAwareCtx(ConfigCtx):
   def __init__(self, flux: FluxClient, **kwargs):
      super().__init__(flux=flux, **kwargs)

   @property
   @abc.abstractmethod
   def auth_list(self) -> AuthList: ...


class ManualAuthCtx(AuthAwareCtx):

   def __init__(self, flux: FluxClient, auth_list: AuthList, config_identifier: str, **kwargs):
      super().__init__(flux=flux, **kwargs)
      self.auth_list_ = auth_list
      self.config_identifier_ = config_identifier

   @property
   def auth_list(self) -> AuthList:
      return self.auth_list_

   @property
   def config_identifier(self) -> str:
      return self.config_identifier_


class ManualAuthorCtx(AuthorAwareCtx):
   def __init__(self, author: ty.Union[discord.User, discord.Member]):
      super().__init__()
      self.author_ = author

   @property
   def author(self) -> ty.Union[discord.User, discord.Member]:
      return self.author_


class ManualGuildCtx(GuildAwareCtx):
   def __init__(self, flux: FluxClient, guild: discord.Guild, **kwargs):
      super().__init__(flux=flux, **kwargs)
      self.guild_ = guild

   @property
   def guild(self) -> discord.Guild:
      return self.guild_


class GuildMemberCtx(AuthAwareCtx, GuildAwareCtx):

   def __init__(self, flux: FluxClient, member: discord.Member, **kwargs):
      super().__init__(flux=flux, **kwargs)
      self.member = member

   @property
   def auth_list(self) -> AuthList:
      return AuthList(
         user=self.member.id,
         roles=[role.id for role in self.member.roles],
         permissions=self.member.guild_permissions
      )

   def guild(self) -> discord.Guild:
      return self.member.guild


class MessageCtx(AuthAwareCtx, AuthorAwareCtx, metaclass=ABCMeta):
   def __init__(self, flux: FluxClient, message: discord.Message, **kwargs: ty.Any):
      super().__init__(flux=flux, **kwargs)
      self.message: discord.Message = message

   @property
   def author(self) -> ty.Union[discord.Member, discord.User]:
      return self.message.author

   @property
   def dest(self) -> discord.abc.Messageable:
      return self.message.channel


class GuildTextChannelCtx(GuildAwareCtx, _MessageableCtx):

   def __init__(self, flux: FluxClient, channel: discord.TextChannel, **kwargs: ty.Any):
      super().__init__(flux=flux, **kwargs)
      self.channel = channel

   @property
   def guild(self) -> discord.Guild:
      return self.channel.guild

   @property
   def me(self) -> discord.abc.User:
      return self.guild.me

   @property
   def dest(self) -> discord.abc.Messageable:
      return self.channel


class DMChannelCtx(_MessageableCtx, AuthAwareCtx):
   def __init__(self, flux: FluxClient, channel: discord.DMChannel, **kwargs):
      super().__init__(flux=flux, **kwargs)
      self.channel = channel

   @property
   def recipient(self) -> discord.User:
      return self.channel.recipient

   @property
   def me(self) -> discord.ClientUser:
      return self.channel.me

   @property
   def config_identifier(self) -> str:
      return str(self.channel.recipient.id)

   @property
   def dest(self) -> discord.abc.Messageable:
      return self.recipient.dm_channel

   @property
   def auth_list(self) -> AuthList:
      return AuthList(
         user=self.recipient.id,
      )


class GuildMessageCtx(GuildTextChannelCtx, MessageCtx, GuildMemberCtx):
   def __init__(self, flux: FluxClient, message: discord.Message, **kwargs):
      super().__init__(flux=flux, message=message, channel=message.channel, member=message.author, **kwargs)

   @property
   def author(self) -> discord.Member:
      return self.member

   async def find_in_guild(self, _type: ty.Literal["member", "channel", "role", "message"], raw_id: str):
      if _type == "member":
         return self.guild.get_member(int(raw_id))
      if _type == "channel":
         return self.guild.get_channel(int(raw_id))
      if _type == "role":
         return self.guild.get_role(int(raw_id))
      if _type == "message":
         return await self.channel.fetch_message(int(raw_id))
      return None


class DMMessageCtx(DMChannelCtx, MessageCtx):
   def __init__(self, **kwargs):
      super().__init__(**kwargs)