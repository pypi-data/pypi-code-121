from __future__ import annotations

import datetime
import itertools as itt
import json
import re
import sys
import traceback
import typing as ty

import discord
import tabulate
from loguru import logger

import dateparser

import aurflux.utils
from . import FluxCog
from .. import CommandEvent, utils
from ..auth import Auth, AuthList, Record
from ..command import Response
from ..context import CommandCtx, GuildMessageCtx, ManualAuthCtx, ManualAuthorCtx
from ..errors import CommandError
from aurcore.util import flattener

flattener._DICT_FLATTEN_SEP = "."
if ty.TYPE_CHECKING:
   from ..context import GuildAwareCtx
   from ..command import Command
   from ..types_ import GuildCommandCtx


class Builtins(FluxCog):
   RULETYPES = {
      "p"          : "permissions",
      "r"          : "role",
      "m"          : "member",
      "permissions": "permissions",
      "role"       : "role",
      "member"     : "member",
   }
   name = "builtins"

   def load(self) -> None:
      async def parse_auth_id(ctx: GuildAwareCtx, type_: str, target_: str) -> int:
         if type_ == "member":
            ids_ = utils.find_mentions(target_)

            if not ids_:
               raise CommandError(f"No member ID found in {target_}")
            if not await self.flux.get_member_s(ctx.guild, ids_[0]):
               raise CommandError(f"No member found with ID {ids_[0]}")
            return ids_[0]
         if type_ == "role":
            ids_ = utils.find_mentions(target_)
            role = ids_ and ctx.guild.get_role(ids_[0])
            if not role:
               role = next((r for r in ctx.guild.roles if r.name.removeprefix("@") == target_), None)
               if role:
                  return role.id
               raise CommandError(f"No role found with ID {target_}")
            return role.id
         if type_ == "permissions":
            p_dict: ty.List[str] = json.loads(target_)
            return discord.Permissions(**{p: True for p in p_dict}).value
         else:
            raise ValueError

      async def parse_auth_context(ctx: GuildAwareCtx, type_: str, target_: str) -> ManualAuthCtx:
         if type_ == "user":
            ids_ = utils.find_mentions(target_)
            if not ids_:
               raise CommandError(f"No user ID found in {target_}")
            user = await self.flux.get_user_s(ids_[0])
            if not user:
               raise CommandError(f"No user found with ID: {ids_[0]}")
            return ManualAuthCtx(flux=self.flux, auth_list=AuthList(user=user.id), config_identifier=ids_[0])
         auth_id = await parse_auth_id(ctx, type_=type_, target_=target_)
         if type_ == "member":
            member = await self.flux.get_member_s(ctx.guild, auth_id)
            if not member:
               raise CommandError(f"No member found with id `{auth_id}`")
            return ManualAuthCtx(flux=self.flux,
                                 auth_list=AuthList(
                                    user=member.id, roles=[r.id for r in member.roles],
                                    permissions=member.guild_permissions),
                                 config_identifier=str(ctx.guild.id))
         if type_ == "role":
            role = ctx.guild.get_role(auth_id)
            if not role:
               raise CommandError(f"No role found with id `{auth_id}`")
            return ManualAuthCtx(
               flux=self.flux,
               auth_list=AuthList(roles=[auth_id], permissions=role.permissions),
               config_identifier=str(ctx.guild.id))

         if type_ == "permissions":
            try:
               return ManualAuthCtx(
                  flux=self.flux,
                  auth_list=AuthList(permissions=discord.Permissions(permissions=auth_id)),
                  config_identifier=str(ctx.guild.id))
            except TypeError as e:
               raise CommandError(f"Permissions `{auth_id}` could not be parsed. See:\n{e}")
         raise ValueError

      @self._commandeer(name="asif", default_auths=[Record.allow_all()])
      async def __asif(ctx: GuildCommandCtx, args: str, _=()):
         """
         asif [type] <target>/{target} command args*
         ==
         Runs `command` as if it was being run by a `target` user, member, role, or permission-haver
         ==
         [type]: [user/role/member/permissions/u/r/m/p] the type of `target`
         <target>: <user/member/role>. Simulates usage by a given caller, \\
         with a role, or a set of permissions. See [here](s.ze.ax/perm) for {perms} names
         {target}: JSON Array of permissions to simulate having
         command: Name of the Command to run as `target`
         args: command arguments to pass to the Command
         ==
         :param ctx:
         :param args:
         :return:
         """

         try:
            mock_type, mock_target, command, command_args = utils.regex_parse(
               re.compile(r"(\S+)\s+((\[[^\]]*\])|([^\s\[]+))\s+(\S+)\s*(.*)"),
               args,
               [x - 1 for x in [1, 2, 5, 6]]
            )
         except (ValueError, AttributeError) as e:
            logger.info(e)
            raise CommandError(f"See `help asif` for usage")

         # noinspection PyPep8Naming
         MOCK_TYPES = {
            "u"   : "user",
            "user": "user",
            **self.RULETYPES
         }
         try:
            mock_type = MOCK_TYPES[mock_type]
         except KeyError:
            raise CommandError(f"`{mock_type}` must be in [{', '.join(MOCK_TYPES.keys())}]")

         cmd_name, cmd_args, *_ = [*command.split(" ", 1), None]
         mock_auth_ctx = await parse_auth_context(ctx=ctx.msg_ctx, type_=mock_type, target_=mock_target)
         if mock_type == "user":
            mock_author_ctx = ManualAuthorCtx(author=await self.flux.fetch_user(int(mock_target)))
         elif mock_type == "member" and ctx.msg_ctx.message.guild:
            mock_author_ctx = ManualAuthorCtx(author=await self.flux.get_member_s(ctx.msg_ctx.guild, int(mock_target)))
         else:
            mock_author_ctx = ctx.author_ctx

         cmd = utils.find_cmd_or_cog(self.flux, cmd_name, only="command")

         if not cmd:
            raise CommandError(f"Command {cmd_name} not found")
         if Auth.accepts_all(ctx.auth_ctxs + [mock_auth_ctx], cmd):
            await self.flux.router.submit(
               event=CommandEvent(flux=self.flux,
                                  cmd_ctx=CommandCtx(
                                     self.flux,
                                     ctx.msg_ctx,
                                     mock_author_ctx,
                                     ctx.auth_ctxs + [mock_auth_ctx]
                                  ),
                                  cmd_name=cmd_name,
                                  cmd_args=cmd_args))
         else:
            raise CommandError(f"Can only mock commands that you have access to")

         return Response()

      @self._commandeer(name="setprefix", default_auths=[Record.allow_server_manager()])
      async def __set_prefix(ctx: GuildCommandCtx, prefix: str, _):
         """
         setprefix prefix
         ==
         Sets the bot prefix to `prefix`
         Ignores surrounding whitespace.
         ==
         prefix: The string to put before a command name. Strips leading and trailing spaces.
         ==
         :param ctx:
         :param prefix:
         :return:
         """
         async with self.flux.CONFIG.writeable_conf(ctx.msg_ctx) as cfg:
            cfg["prefix"] = prefix.strip()
         return Response()

      # noinspection PyUnresolvedReferences
      @self._commandeer(name="exec", override_auths=[Record.deny_all()])
      async def __exec(ctx: CommandCtx, script: str, _):
         """
         exec ute order 66
         ==
         Safe™
         ==
         :)
         ==
         :param ctx:
         :param script:
         :return:
         """
         from pprint import pformat

         exec_func = utils.sexec
         if "await " in script:
            exec_func = utils.aexec

         # Utils for exec
         from .. import context
         # ==
         _s = self
         _c = ctx.msg_ctx.dest
         _d = discord
         # noinspection PyTypeChecker
         _g: ty.Optional[discord.Guild] = ctx.msg_ctx.message.guild
         _b = _g.me
         with utils.Timer() as t:
            # noinspection PyBroadException
            try:
               res = str(await exec_func(script, globals(), locals()))
            except Exception as e:
               res = re.sub(r'File ".*[\\/]([^\\/]+.py)"', r'File "\1"', traceback.format_exc(limit=1))
            res = res.replace(r"/home/zenith/.cache/pypoetry/virtualenvs/pinbot-AoGbOYTv-py3.9/lib/python3.9/site-packages", "...")

         return Response((f"Ran in {t.elapsed * 1000:.2f} ms\n"
                          f"**IN**:\n"
                          f"```py\n{script}\n```"
                          f"**OUT**:\n"
                          f"```py\n{pformat(res)}\n```"), trashable=True)


      @self._commandeer(name="reboot", default_auths=[Record.deny_all()])
      async def __reboot(ctx: CommandCtx, _, __):
         """
         reboot
         ==
         Reboots...
         ==
         ==
         :param ctx:
         :param _:
         :param __:
         :return:
         """
         sys.exit()
      @self._commandeer(name="auth", default_auths=[Record.allow_server_manager()])
      async def __auth(ctx: GuildCommandCtx, auth_str, _):
         """
         auth name [rule] [id_type] <id>/{perm}
         ==
         Authorizes some group (a member, members that have a role, or have some permissions) to use a command or a cog
         ==
         name: Command name or Cog name;
         [rule]: [ALLOW/DENY];
         id_type: [member/role/permission/m/r/p] The type that `id` is
         <id>: <member/role> The target member or role to allow
         {perm}: A permission JSON array representing a set of permissions that a user must have ALL of. \\
         ex. ["manage_server","kick_members"]
         EXAMPLE: Want to allow the role @moderator to use `auth` (Note: This effectively gives full bot access): \\
         `auth auth ALLOW role @moderators`
         ==
         :param ctx:
         :param auth_str:
         :return:
         """
         try:
            rule_subject, rule, id_type, rule_target_id_raw, = utils.regex_parse(
               re.compile(r"(\S+)\s+(\S+)\s+(\S+)\s+((\[[^\]]*\])|([^\s\[]+))"),
               auth_str,
               [x - 1 for x in [1, 2, 3, 4]]
            )
         except (ValueError, AttributeError, TypeError):
            raise CommandError(f"See `help auth` for usage")

         rule_subject = rule_subject.lower()
         rule = rule.upper()
         id_type = id_type.lower()

         cmd_or_cog = utils.find_cmd_or_cog(self.flux, rule_subject)
         if not cmd_or_cog:
            raise CommandError(f"No cog or command found with name {rule_subject}")
         if rule not in ["ALLOW", "DENY"]:
            raise CommandError(f'rule {rule} not in ["ALLOW","DENY"]')
         try:
            target_id = await parse_auth_id(ctx.msg_ctx, type_=self.RULETYPES[id_type], target_=rule_target_id_raw)
         except KeyError:
            raise CommandError(f"Rule type {id_type} not in {self.RULETYPES.keys()}")

         record = Record(rule=rule, target_id=target_id, target_type=id_type.upper())
         await Auth.add_record(ctx.msg_ctx, auth_id=cmd_or_cog.auth_id, record=record)
         return Response(f"Added record {record}")

      # noinspection PyPep8Naming
      @self._commandeer(name="userinfo", default_auths=[Record.allow_server_manager()])
      async def __userinfo(ctx: GuildCommandCtx, target_raw, _):
         """
         userinfo (<user/member>)
         ==
         Authorizes some group (member, has a role, or has a permission) to use a command or a cog
         ==
         <user/member>: The target member/user to userinfo. Defaults to caller if not provided.
         ==
         :param ctx:
         :param target_raw:
         :return:
         """
         utils.perm_check(ctx.msg_ctx.channel, discord.Permissions(embed_links=True))

         if not target_raw:
            target = ctx.author_ctx.author
         else:
            if not (target := utils.find_mentions(target_raw)[0]):
               raise CommandError(f"Cannot find a user/member in `{target_raw}`. It should either be an ID or a mention")

            if isinstance(ctx.msg_ctx, GuildMessageCtx):
               target = await self.flux.get_member_s(ctx.msg_ctx.guild, target)
            else:
               target = await ctx.msg_ctx.flux.get_user(target)

         embed = discord.Embed(title=f"{utils.EMOJI.question}{target}'s Userinfo", color=target.color)
         embed.set_thumbnail(url=str(target.avatar_url))
         embed.add_field(name="Display Name", value=utils.copylink(target.display_name), inline=True)
         embed.add_field(name="ID", value=utils.copylink(str(target.id)), inline=False)
         embed.add_field(name="Latest Join", value=utils.copylink(target.joined_at.strftime(utils.DATETIME_FMT_L)), inline=False)
         embed.add_field(name="Creation Date", value=utils.copylink(target.created_at.strftime(utils.DATETIME_FMT_L)), inline=False)

         if isinstance(ctx.msg_ctx, GuildMessageCtx):
            if target.color != discord.Color.default():
               embed.add_field(name="Color", value=utils.copylink(hex(target.color.value).upper()), inline=False)
            if target.premium_since:
               delta = (datetime.datetime.utcnow() - target.premium_since).days
               D_IN_M = 29.53
               D_IN_Y = 365.25
               if delta < 7:
                  output = f"{delta} days"
               elif delta < D_IN_M:  # average month length
                  output = f"{delta // 7} weeks"
               elif delta < D_IN_Y * 2 + 1:
                  output = f"{delta // D_IN_M} months"
               else:
                  output = f"{delta // D_IN_Y} years"
               embed.add_field(name="Boosting for ", value=output)
            roles = ",".join(role.mention for role in (target.roles or ())[::-1])
            if len(roles) >= 2048:
               url = utils.haste(self.flux.aiohttp_session, "\n".join(f"{role.id}:{role.name}" for role in target.roles))
               roles = f"(roles)[{url}]"
            embed.add_field(name="Roles", value=roles)

            embed.add_field(
               name="Permissions in this channel",
               value=f"[Permissions](https://discordapi.com/permissions.html#{target.permissions_in(ctx.msg_ctx.channel).value})",
               inline=False
            )
            embed.add_field(
               name="Server Permissions",
               value=f"[Permissions](https://discordapi.com/permissions.html#{target.guild_permissions.value})",
               inline=False
            )
         return Response(embed=embed)

      @self._commandeer(name="serverinfo", default_auths=[Record.allow_server_manager()])
      async def __serverinfo(ctx: GuildCommandCtx, _, __):
         """
         serverinfo
         ==
         Gets information about the server
         ==
         ==
         :param ctx:
         :param _:
         :return:
         """
         utils.perm_check(ctx.msg_ctx.channel, discord.Permissions(embed_links=True))

         g = ctx.msg_ctx.guild
         embed = discord.Embed(title=f"{utils.EMOJI.question}{g} Server Info")
         embed.set_thumbnail(url=str(ctx.msg_ctx.guild.icon_url))
         # Info
         embed.add_field(name="Owner", value=f"<@!{g.owner_id}>", inline=True)
         embed.add_field(name="Region", value=f"{g.region}", inline=True)
         embed.add_field(name="Members", value=f"{g.member_count}")

         # Creation
         embed.add_field(name="Creation", value=g.created_at.strftime(utils.DATETIME_FMT_L), inline=False)

         # Extra Info
         embed.add_field(name="MFA Required", value=f"{bool(g.mfa_level)}", inline=True)
         embed.add_field(name="Verify Level", value=f"{g.verification_level}", inline=True)
         embed.add_field(name="Filter", value=f"{g.explicit_content_filter}", inline=True)

         # Boosters
         boosters_haste = await utils.haste(
            self.flux.aiohttp_session,
            tabulate.tabulate(
               headers=["Member", "Mention"],
               tabular_data=[[str(member), member.mention] for member in g.premium_subscribers])
         ) if g.premium_subscribers else ""
         embed.add_field(name="Nitro Boosters", value=f"[{g.premium_subscription_count} boosters]({boosters_haste})", inline=True)
         embed.add_field(name="Boost Level", value=f"{g.premium_tier}", inline=True)

         # Emoji
         emoji_haste = await utils.haste(
            self.flux.aiohttp_session,
            content=tabulate.tabulate(
               headers=["Emoji", "Animated", "URL"],
               tabular_data=[[str(emoji), emoji.animated, emoji.url] for emoji in g.emojis]
            )
         )
         embed.add_field(name="Emoji", value=f"[{len(g.emojis)}/{g.emoji_limit * 2} emojis]({emoji_haste})", inline=False)

         # Features
         features_haste = await utils.haste(
            self.flux.aiohttp_session,
            content="\n".join(feature for feature in g.features)
         ) if g.features else ""
         embed.add_field(name="Features", value=f"[{len(g.features)} features enabled]({features_haste})", inline=False)

         # Channels
         text_channels = [channel for channel in g.text_channels if channel.overwrites_for(g.default_role).read_messages is not False and g.default_role.permissions.read_messages]
         public_channels_haste = await utils.haste(
            self.flux.aiohttp_session,
            content=tabulate.tabulate(
               [[f"{channel}",
                 f"{channel.id}",
                 f"{channel.category}",
                 f"{channel.created_at.strftime(utils.DATETIME_FMT_S)}",
                 f"{channel.permissions_synced}",
                 f"{channel.slowmode_delay}s",
                 f"{channel.position}",
                 ]
                for channel in text_channels],
               headers=("Name", "ID", "Category", "Creation", "Perm Sync", "Slow", "Position")
            )
         ) if text_channels else ""
         embed.add_field(name="Public Text Channels", value=f"[{len(text_channels)} Channels]({public_channels_haste})", inline=True)

         voice_channels = [channel for channel in g.voice_channels if channel.overwrites_for(g.default_role).connect is not False and g.default_role.permissions.connect]
         public_vc_haste = await utils.haste(
            self.flux.aiohttp_session,
            content=tabulate.tabulate(
               [[f"{channel}",
                 f"{channel.id}",
                 f"{channel.category}",
                 f"{channel.created_at.strftime(utils.DATETIME_FMT_S)}",
                 f"{channel.permissions_synced}",
                 f"{channel.bitrate // 1000} kbps",
                 f"{channel.user_limit}"
                 ]
                for channel in voice_channels],
               headers=("Name", "ID", "Category", "Creation", "Perm Sync", "Bitrate", "User Limit")

            )
         ) if voice_channels else ""

         embed.add_field(name="Public Voice Channels", value=f"[{len(voice_channels)} Channels]({public_vc_haste})", inline=True)

         # Roles
         roles = [role for role in g.roles]
         public_roles_haste = await utils.haste(
            self.flux.aiohttp_session,
            content=tabulate.tabulate(
               [[f"{role}",
                 f"{role.id}",
                 f"{role.position}",
                 f"{role.color}",
                 f"{role.created_at.strftime(utils.DATETIME_FMT_S)}",
                 f"{len(role.members)}",
                 f"{role.mentionable}",
                 f"{role.hoist}",
                 f"{role.managed}",
                 ]
                for role in roles],
               headers=("Name", "ID", "Position", "Color Hex", "Creation Date", "# of visible members", "Mentionable", "Hoist", "Managed")

            )
         )
         embed.add_field(name="Roles", value=f"[{len(roles)} Roles]({public_roles_haste})", inline=True)

         return Response(embed=embed)
         pass

      @self._commandeer(name="help", default_auths=[Record.allow_all()])
      async def __get_help(ctx: GuildCommandCtx, help_target: ty.Optional[str], _):
         """
         help (command_name/section)
         ==
         My brother is dying! Get Help!
         ==
         command_name: The command to get help for. Command list if not provided. Gets help about reading help if you `help help`
         ==
         :param ctx:
         :param help_target: what to get help about
         :return:
         """
         utils.perm_check(ctx.msg_ctx.channel, discord.Permissions(embed_links=True))
         configs = self.flux.CONFIG.of(ctx.msg_ctx)
         authorized_cmds: ty.Dict[str, ty.Tuple[FluxCog, Command]] = {command.name: (cog, command) for cog in self.flux.cogs for command in cog.commands if
                                                                      Auth.accepts_all(ctx.auth_ctxs, command) and command.name != "help"}
         # Help
         if not help_target:
            help_embed = discord.Embed(title=f"{utils.EMOJI.question} Help", description=f"{configs['prefix']}help <command/section> for more info")
            cog_groups = itt.groupby(authorized_cmds.items(), lambda x: x[1][0])
            for cog, group in cog_groups:
               # noinspection Mypy
               cog: FluxCog  # https://youtrack.jetbrains.com/issue/PY-43664
               group: ty.Iterable[ty.Tuple[str, ty.Tuple[FluxCog, Command]]]
               usages = "\n".join(
                  ["\n".join([f"{configs['prefix']}{usage}" for usage in cmd_item[1][1].usage.split("\n")])
                   for cmd_item in group]
               )
               help_embed.add_field(name=cog.name, value=usages, inline=False)
            return Response(embed=help_embed)

         # Help for Cog

         if cog := next((c for c in self.flux.cogs if c.name.lower() == help_target.lower()), None):
            embed = discord.Embed(title=f"{utils.EMOJI.question} Section Help: {cog.name}")
            for cmd in cog.commands:
               if cmd.name in authorized_cmds:
                  embed.add_field(name=cmd.name, value=cmd.description, inline=False)
            return Response(embed=embed)

         # Help for Help
         if help_target == "help":
            embed = discord.Embed(title="\U00002754 Command Help", description="How to read help")
            embed.add_field(name="Usage", value='..commandname [lit] <user> {json} (optional) extra*', inline=False)
            embed.add_field(name="a/b", value="Either a or b. E.g. <user>/{userinfo} ", inline=False)
            embed.add_field(name="[lit]", value="Something with a limited set of choices. See `help commandname`", inline=False)
            embed.add_field(name="<user>", value="Either an ID or a Mention of something. E.g. a @user", inline=False)
            embed.add_field(name="(optional)", value="Can leave this out", inline=False)
            embed.add_field(name="{json}", value="Json. No spaces please ;w;", inline=False)
            embed.add_field(name="*extra", value="Can put multiple of these. Spaces okay.", inline=False)

            return Response(embed=embed)

         if help_target not in authorized_cmds:
            return Response(f"No command or section `{help_target}` to show help for", status="error")

         # Help for Command
         cog, cmd = authorized_cmds[help_target]
         embed = discord.Embed(
            title=f"\U00002754 Command Help: {help_target}",
            description=cmd.description)

         embed.add_field(name="Usage", value=cmd.usage, inline=False)
         for arg, detail in cmd.param_usage:
            embed.add_field(name=arg.strip(), value=detail.strip(), inline=False)

         return Response(embed=embed)
      @self._commandeer(name="purge", default_auths=[Record.allow_server_manager()])
      async def __purge(ctx: GuildCommandCtx, args: str, flags: ty.List[str]):
         """
         purge n
         ==
         Purges messages from channel
         ==
         n: number of messages to purge. ALL for all messages
         ==
         :param ctx:
         :param args:
         :param flags:
         :return:
         """

         if not args:
            raise CommandError(f"Need to provide a number of messages to purge")
         args = args.strip()
         if args == "ALL":
            num = None
         else:
            num = int(args.strip())

         if not "f" in flags:
            check_msg =  Response(f"Are you sure that you want to remove {num if num is not None else all} messages in this channel, {ctx.msg_ctx.channel.mention}?")
            yield check_msg
            await check_msg.message.add_reaction(aurflux.utils.EMOJI.check)

            await self.flux.router.wait_for(":reaction_add", check=lambda ev: ev.args[1].id == ctx.author_ctx.author.id and str(ev.args[0].emoji) == aurflux.utils.EMOJI.check, timeout=15)

         await ctx.msg_ctx.channel.purge(limit=num)



      @self._commandeer(name="config", default_auths=[Record.allow_server_manager()])
      async def __config(ctx: GuildCommandCtx, args: str, _):
         """
         config configpath (value)
         ==
         Configurate a setting
         ==
         configpath: config key
         value: Value to set. prints info if empty
         ==
         :param ctx:
         :param args:
         :return:
         """
         if not args:
            raise CommandError(f"Need to provide a config path. Available cogs: {','.join([cog.name for cog in self.flux.cogs])}")
         config, value, *_ = [*args.split(" ", 1), None]
         if (cfgroot := config.split(".", 1)[0]) not in [cog.name for cog in self.flux.cogs]:
            raise CommandError(f"Cog name `{cfgroot or ' '}` not found in cogs: {','.join([cog.name for cog in self.flux.cogs])}")

         ID_TYPES = ("user","channel","role","guild","member")

         async def parse_config_value(val:str, config_type: ty.Literal["int","float","datetime","str","user","channel","role","guild","member"]):
            val = val.strip()
            try:
               if config_type in ID_TYPES:
                  try:
                     obj = await ctx.msg_ctx.find_in_guild(t["type"], aurflux.utils.find_mentions(val)[0])
                  except IndexError:
                     return Response(f"Could not be parsed into a {t['type']}")
                  return obj.id
               else:
                  if config_type == "str":
                     return val
                  if config_type == "int":
                     return int(val)
                  if config_type == "float":
                     return float(val)
                  if config_type == "datetime":
                     return dateparser.parse(val).isoformat()
            except (TypeError, ValueError, AttributeError) as e:
               raise CommandError(f"{val} not recognizable or locatable as a {t['type']}\n{e}")



         if value is not None:
            value : str = value.strip()
            async with self.flux.CONFIG.writeable_conf(ctx.msg_ctx) as cfg:
               print(ctx.msg_ctx)
               print(cfg)

               t = cfg
               try:
                  for part in config.split("."):
                     t = t[part]
               except KeyError:
                  return Response(f"Not recognized as a config path!")
               if t["type"] == "category":
                  raise CommandError(f"`{config}` is a category, not a setting!")
               elif t["type"].startswith("list:"):
                  raw_val_list = value.removeprefix("[").removesuffix("]").split(",")
                  t["value"] = [await parse_config_value(raw_val, t["type"].removeprefix("list:")) for raw_val in raw_val_list]
               else:
                  t["value"] = await parse_config_value(value, t["type"])

               return Response(f'Set {config} to `{t["value"]}`')
         else:
            cfg = self.flux.CONFIG.of(ctx.msg_ctx)
            print(ctx.msg_ctx.config_identifier)
            t = cfg
            try:
               for part in config.split("."):
                  t = t[part]
            except KeyError:
               return Response(f"Not a setting, or no settings for this cog.")
            cfg_msg = [[f"{config}", f"({(t['type'].title())}) {t['__meta']}"]]
            cfg_msg.append(["-", "-"])

            for key in [k for k in t.keys() if k not in ('__meta', 'value', 'type')]:
               cfg_msg.append([f"\n{config}.{key}", f"({t[key]['type'].title()}) {t[key]['__meta']}", t[key]["value"] if "value" in t[key] else ""])
            return Response(f"```{tabulate.tabulate(cfg_msg, headers=('Config Key', 'Info', 'Value'))}```")

      @self._commandeer(name="reload", allow_dm=True, default_auths=[Record.deny_all()])
      async def __reload(ctx: CommandCtx, cog_name: str):
         """
         reload cogname
         ==
         ==
         ==
         :param ctx:
         :param cog_name:
         :return:
         """
         return Response(await self.flux.reload_cog(cog_name))

   @property
   def default_auths(self) -> ty.List[Record]:
      return []
