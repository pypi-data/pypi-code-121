from __future__ import annotations
import typing as ty
from ..errors import BotMissingPermissions

if ty.TYPE_CHECKING:
   import discord


def perm_check(c: discord.TextChannel, need: discord.Permissions):
   if not need <= (p := c.permissions_for(c.guild.me)):
      raise BotMissingPermissions(need, p, c)