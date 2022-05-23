from __future__ import annotations
import typing as ty
import discord


class CommandException(BaseException):
   def __init__(self, message=None, *args):
      if message is not None:
         # clean-up @everyone and @here mentions
         m = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
         super().__init__(m, *args)
      else:
         super().__init__(*args)


class CommandInfo(CommandException):
   pass


class CommandError(CommandException):
   pass


class CommandSyntaxError(CommandError):
   def __init__(self, command_name: str, prefix: str, *args: ty.Any):
      message = f"Syntax not recognized... see {prefix}{command_name}"
      super().__init__(message, *args)


class UserMissingPermissions(CommandError):
   def __init__(self, missing_perms, *args: ty.Any):
      self.missing_perms = missing_perms

      missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in missing_perms]

      if len(missing) > 2:
         fmt = '{}, and {}'.format(", ".join(missing[:-1]), missing[-1])
      else:
         fmt = ' and '.join(missing)
      message = 'You are missing {} permission{} to run this command.'.format(fmt, "s" if len(missing) > 2 else "")
      super().__init__(message, *args)


class BotMissingPermissions(CommandError):
   def __init__(self, need: discord.Permissions, have: discord.Permissions, channel: discord.TextChannel = None, *args: ty.Any):
      missing_perms = discord.Permissions(permissions=(need.value ^ have.value) & need.value)

      missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm, v in missing_perms if v]

      if len(missing) > 2:
         fmt = '{}, and {}'.format(", ".join(missing[:-1]), missing[-1])
      else:
         fmt = ' and '.join(missing)
      message = f"I am missing {fmt} permission{'s' if len(missing) > 2 else ''} {f' in {channel.mention} ' if channel else ''}."
      super().__init__(message, *args)
