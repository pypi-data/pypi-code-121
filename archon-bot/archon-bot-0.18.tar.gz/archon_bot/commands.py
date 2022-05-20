import asyncio

import csv
import enum
import functools
import itertools
import io
import logging
import random
from typing import Iterable, List, Optional, Union

import hikari
from hikari.interactions.base_interactions import ResponseType
from hikari.interactions.command_interactions import CommandInteraction
from hikari.interactions.component_interactions import ComponentInteraction
import krcg.deck

import stringcase


from . import db
from . import tournament
from . import permissions as perm

logger = logging.getLogger()
CommandFailed = tournament.CommandFailed

APPLICATION = []
COMMANDS = {}
SUB_COMMANDS = {}
COMMANDS_TO_REGISTER = {}
COMPONENTS = {}

VDB_URL = "https://vdb.im"
AMARANTH_URL = "https://amaranth.vtes.co.nz"


def build_command_tree(rest_api):
    """Hikari commands to submit to the Discord server on boot."""
    commands = {}
    for name, klass in COMMANDS_TO_REGISTER.items():
        command = rest_api.slash_command_builder(
            name, klass.DESCRIPTION
        ).set_default_permission(True)
        for option in klass.OPTIONS:
            command = command.add_option(option)
        commands[klass] = command

    for klass, sub_commands in SUB_COMMANDS.items():
        for name, sub_klass in sub_commands.items():
            if any(
                opt.type == hikari.OptionType.SUB_COMMAND for opt in sub_klass.OPTIONS
            ):
                assert all(
                    opt.type == hikari.OptionType.SUB_COMMAND
                    for opt in sub_klass.OPTIONS
                ), "if one option is a subcommand, they all should be"
                option_type = hikari.OptionType.SUB_COMMAND_GROUP
            else:
                option_type = hikari.OptionType.SUB_COMMAND

            option = hikari.CommandOption(
                type=option_type,
                name=name,
                description=sub_klass.DESCRIPTION,
                options=sub_klass.OPTIONS,
            )
            commands[klass] = commands[klass].add_option(option)

    return list(commands.values())


class MetaCommand(type):
    """Metaclass to register commands."""

    def __new__(cls, name, bases, dict_):
        command_name = stringcase.spinalcase(name)
        if command_name in COMMANDS_TO_REGISTER:
            raise ValueError(f"Command {name} is already registered")
        klass = super().__new__(cls, name, bases, dict_)
        if command_name == "base-command":
            return klass
        if klass.GROUP:
            SUB_COMMANDS.setdefault(klass.GROUP, {})
            SUB_COMMANDS[klass.GROUP][command_name] = klass
        else:
            COMMANDS_TO_REGISTER[command_name] = klass
        return klass


class CommandAccess(str, enum.Enum):
    """For now, only the Judge access is controlled."""

    PUBLIC = "PUBLIC"
    ADMIN = "ADMIN"
    PLAYER = "PLAYER"
    JUDGE = "JUDGE"


def _split_text(s, limit):
    """Utility function to split a text at a convenient spot."""
    if len(s) < limit:
        return s, ""
    index = s.rfind("\n", 0, limit)
    rindex = index + 1
    if index < 0:
        index = s.rfind(" ", 0, limit)
        rindex = index + 1
        if index < 0:
            index = limit
            rindex = index
    return s[:index], s[rindex:]


def _paginate_embed(embed: hikari.Embed) -> List[hikari.Embed]:
    """Utility function to paginate a Discord Embed"""
    embeds = []
    fields = []
    base_title = embed.title
    description = ""
    page = 1
    logger.debug("embed: %s", embed)
    while embed:
        if embed.description:
            embed.description, description = _split_text(embed.description, 2048)
        while embed.fields and (len(embed.fields) > 15 or description):
            fields.append(embed.fields[-1])
            embed.remove_field(-1)
        embeds.append(embed)
        if description or fields:
            page += 1
            embed = hikari.Embed(
                title=base_title + f" ({page})",
                description=description,
            )
            for field in fields:
                embed.add_field(name=field.name, value=field.value, inline=field.inline)
            description = ""
            fields = []
        else:
            embed = None
    if len(embeds) > 10:
        raise RuntimeError("Too many embeds")
    return embeds


class InteractionContext:
    """In case of interaction chaining, this context is passed unchanged.

    Track if we have an initial response already, to know if we should create or edit
    """

    def __init__(self):
        self.has_response = False


class BaseInteraction:
    """Base class for all interactions (commands and components)"""

    #: The interaction does not update tournament data. Override in children as needed.
    UPDATE = False
    #: The interaction requires an open tournament (most of them except open)
    REQUIRES_TOURNAMENT = True
    ACCESS = CommandAccess.PUBLIC

    def __init__(
        self,
        bot: hikari.GatewayBot,
        connection,
        tournament_: tournament.Tournament,
        interaction: Union[CommandInteraction, ComponentInteraction],
        channel_id: hikari.Snowflake,
        category_id: Optional[hikari.Snowflake] = None,
        interaction_context: Optional[InteractionContext] = None,
    ):
        self.bot: hikari.GatewayBot = bot
        self.connection = connection
        self.interaction: Union[CommandInteraction, ComponentInteraction] = interaction
        self.channel_id: hikari.Snowflake = channel_id
        self.author: hikari.InteractionMember = self.interaction.member
        self.guild_id: hikari.Snowflake = self.interaction.guild_id
        self.category_id: hikari.Snowflake = category_id
        self.tournament: tournament.Tournament = tournament_
        self.interaction_context = interaction_context or InteractionContext()
        if self.REQUIRES_TOURNAMENT and not self.tournament:
            raise CommandFailed(
                "No tournament running. Please use the `/open-tournament` command."
            )
        if self.ACCESS == CommandAccess.JUDGE and not self._is_judge():
            raise CommandFailed("Only a Judge can call this command")

    @classmethod
    def copy_from_interaction(cls, rhs, *args, **kwargs):
        """Can be used to "chain" interactions.

        For example you might have commands A, B and C as different steps
        for a given process, but a
        """
        return cls(
            *args,
            bot=rhs.bot,
            connection=rhs.connection,
            interaction=rhs.interaction,
            channel_id=rhs.channel_id,
            category_id=rhs.category_id,
            tournament_=rhs.tournament,
            interaction_context=rhs.interaction_context,
            **kwargs,
        )

    def update(self) -> None:
        """Update tournament data."""
        if not self.UPDATE:
            raise RuntimeError("Command is not marked as UPDATE")
        data = self.tournament.to_json()
        db.update_tournament(
            self.connection,
            self.guild_id,
            self.category_id,
            data,
        )

    def _is_judge(self) -> bool:
        """Check whether the author is a judge."""
        judge_role_id = self.tournament.roles[self.tournament.JUDGE]
        return judge_role_id in self.author.role_ids

    def _is_judge_channel(self) -> bool:
        """Check wether the command was issued in the Judges private channel."""
        return (
            self.channel_id
            == self.tournament.channels[tournament.Tournament.JUDGE_TEXT]
        )

    def _player_display(self, player_id: tournament.PlayerID) -> str:
        """How to display a player."""
        player = self.tournament.players[player_id]
        return (
            ("**[D]** " if player.vekn in self.tournament.dropped else "")
            + (f"{player.name} #{player.vekn} " if player.name else f"#{player.vekn} ")
            + (f"<@{player.discord}>" if player.discord else "")
        )

    def _deck_display(self, data: dict) -> str:
        deck = krcg.deck.Deck()
        deck.from_json(data)
        return f"[{deck.name}]({deck.to_vdb()})"

    @property
    def reason(self) -> str:
        """Reason given for Discord logs on channel/role creations."""
        return f"{self.tournament.name} Tournament"

    async def __call__(self) -> None:
        """To implement in children classes"""
        raise NotImplementedError()


class BaseCommand(BaseInteraction, metaclass=MetaCommand):
    """Base class for all commands"""

    #: Command description. Override in children.
    DESCRIPTION = ""
    #: Define command options. Override in children as needed.
    OPTIONS = []
    #: Main command this sub command is attached to, if any
    GROUP = None

    async def deferred(self, flags: Optional[hikari.MessageFlag] = None) -> None:
        """Let Discord know we're working (displays the '...' on Discord).

        It's useful especially for commands that have a bit of compute time,
        where we cannot be certain we will answer fast enough for Discord to
        not drop the command altogether.

        Note the flags (None or EPHEMERAL) passed should match the ones used in
        subsequent calls to create_or_edit_response.
        """
        await self.interaction.create_initial_response(
            ResponseType.DEFERRED_MESSAGE_CREATE, flags=flags
        )
        self.interaction_context.has_response = True

    async def create_or_edit_response(self, *args, **kwargs) -> None:
        """Create or edit the interaction response.

        The flags (None or EPHEMERAL) are used on creation to display the answer
        to the author only (EPHEMERAL) or everyone.
        You can pass empty list for embeds and components if you want to reset them.
        """
        flags = kwargs.pop("flags", None)
        if self.interaction_context.has_response:
            func = self.interaction.edit_initial_response
        else:
            func = functools.partial(
                self.interaction.create_initial_response,
                ResponseType.MESSAGE_CREATE,
                flags=flags,
            )
        await func(*args, **kwargs)
        self.interaction_context.has_response = True


class BaseComponent(BaseInteraction):
    """Base class for all components"""

    async def deferred(self, flags: Optional[hikari.MessageFlag] = None) -> None:
        """Let Discord know we're working (displays the '...' on Discord)."""
        await self.interaction.create_initial_response(
            ResponseType.DEFERRED_MESSAGE_UPDATE, flags=flags
        )
        self.interaction_context.has_response = True

    async def create_or_edit_response(self, *args, **kwargs) -> None:
        """Create or edit the interaction response."""
        flags = kwargs.pop("flags", None)
        if self.interaction_context.has_response:
            func = self.interaction.edit_initial_response
        else:
            func = functools.partial(
                self.interaction.create_initial_response,
                ResponseType.MESSAGE_UPDATE,
                flags=flags,
            )
        await func(*args, **kwargs)
        self.interaction_context.has_response = True


class OpenTournament(BaseCommand):
    """Open the tournament"""

    UPDATE = True
    ACCESS = CommandAccess.ADMIN  # For now, the admin access is public
    REQUIRES_TOURNAMENT = False
    DESCRIPTION = "ADMIN: Open a new event or tournament"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="name",
            description="The tournament name",
            is_required=True,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.INTEGER,
            name="rounds",
            description=(
                "The maximum number of rounds a player can play (not counting finals)"
            ),
            is_required=False,
            min_value=1,
        ),
    ]

    async def __call__(self, name: str, rounds: Optional[int] = 0) -> None:
        """Open the tournament, create channels and roles, then configure (chain)"""
        if self.tournament:
            raise CommandFailed("A tournament is already open here")
        await self.deferred()
        self.tournament = tournament.Tournament(name=name)
        if rounds:
            self.tournament.max_rounds = rounds
        logger.debug("Creating roles...")
        judge_role, spectator_role, player_role = await asyncio.gather(
            self.bot.rest.create_role(
                self.guild_id,
                name=f"{self.tournament.prefix}Judge",
                mentionable=True,
                reason=self.reason,
            ),
            self.bot.rest.create_role(
                self.guild_id,
                name=f"{self.tournament.prefix}Spectator",
                mentionable=True,
                reason=self.reason,
            ),
            self.bot.rest.create_role(
                self.guild_id,
                name=f"{self.tournament.prefix}Player",
                mentionable=True,
                reason=self.reason,
            ),
        )
        self.tournament.roles[self.tournament.JUDGE] = judge_role.id
        self.tournament.roles[self.tournament.SPECTATOR] = spectator_role.id
        self.tournament.roles[self.tournament.PLAYER] = player_role.id
        logger.debug("Register tournament in DB...")
        db.create_tournament(
            self.connection,
            self.tournament.prefix,
            self.guild_id,
            self.category_id,
            self.tournament.to_json(),
        )
        logger.debug("Add roles and create channels...")
        results = await asyncio.gather(
            self.author.add_role(judge_role, reason=self.reason),
            self.bot.rest.add_role_to_member(
                self.guild_id, self.bot.get_me(), judge_role, reason=self.reason
            ),
            self.bot.rest.create_guild_text_channel(
                self.guild_id,
                "Judges",
                category=self.category_id or hikari.UNDEFINED,
                reason=self.reason,
                permission_overwrites=[
                    hikari.PermissionOverwrite(
                        id=self.guild_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        deny=perm.TEXT,
                    ),
                    hikari.PermissionOverwrite(
                        id=judge_role.id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.TEXT,
                    ),
                ],
            ),
            self.bot.rest.create_guild_voice_channel(
                self.guild_id,
                "Judges",
                category=self.category_id or hikari.UNDEFINED,
                bitrate=96000,
                reason=self.reason,
                permission_overwrites=[
                    hikari.PermissionOverwrite(
                        id=self.guild_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        deny=perm.VOICE,
                    ),
                    hikari.PermissionOverwrite(
                        id=judge_role.id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.VOICE,
                    ),
                ],
            ),
        )
        # author is now a judge, he can configure (next step)
        self.author.role_ids.append(judge_role.id)
        self.tournament.channels[tournament.Tournament.JUDGE_TEXT] = results[2].id
        self.tournament.channels[tournament.Tournament.JUDGE_VOICE] = results[3].id
        logger.debug("Update tournament data")
        self.update()
        # await set_judge_permissions(self.connection, self.bot, self.guild_id)
        next_step = ConfigureTournament.copy_from_interaction(self)
        await next_step()


class ConfigureTournament(BaseCommand):
    """Configure. Chained from OpenTournament, can also be called on its own.

    VEKN_REQUIRED: Requires VEKN ID# for registration, check against VEKN website
    DECKLIST_REQUIRED: Requires decklist (VDB or Amaranth), check legqlity
    CHECKIN_EACH_ROUND: Players must check in beafore each round
    LEAGUE: Players can still register and change deck once the tournament is running
    STAGGERED: 6, 7, 11 players round-robin
    """

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Configure the tournament"
    OPTIONS = []

    async def __call__(self) -> None:
        # has been acknowledged/deferred already
        if hasattr(self.interaction, "custom_id"):
            if self.interaction.custom_id == "vekn-required":
                self.tournament.flags ^= tournament.TournamentFlag.VEKN_REQUIRED
            elif self.interaction.custom_id == "decklist-required":
                self.tournament.flags ^= tournament.TournamentFlag.DECKLIST_REQUIRED
            elif self.interaction.custom_id == "checkin-each-round":
                self.tournament.flags ^= tournament.TournamentFlag.CHECKIN_EACH_ROUND
            elif self.interaction.custom_id == "league":
                self.tournament.flags ^= tournament.TournamentFlag.LEAGUE
            elif self.interaction.custom_id == "staggered":
                if self.tournament.flags & tournament.TournamentFlag.STAGGERED:
                    self.tournament.rounds = []
                    self.tournament.flags ^= tournament.TournamentFlag.STAGGERED
                else:
                    self.tournament.make_staggered()
        self.update()
        vekn_required = self.tournament.flags & tournament.TournamentFlag.VEKN_REQUIRED
        decklist_required = (
            self.tournament.flags & tournament.TournamentFlag.DECKLIST_REQUIRED
        )
        checkin_each_round = (
            self.tournament.flags & tournament.TournamentFlag.CHECKIN_EACH_ROUND
        )
        league = self.tournament.flags & tournament.TournamentFlag.LEAGUE
        staggered = self.tournament.flags & tournament.TournamentFlag.STAGGERED
        if getattr(self.interaction, "custom_id", None) == "validate":
            components = []
            COMPONENTS.pop("vekn-required", None)
            COMPONENTS.pop("decklist-required", None)
            COMPONENTS.pop("checkin-each-round", None)
            COMPONENTS.pop("league", None)
            COMPONENTS.pop("staggered", None)
            COMPONENTS.pop("validate", None)
        else:
            components = [
                self.bot.rest.build_action_row()
                .add_button(
                    hikari.ButtonStyle.SECONDARY
                    if vekn_required
                    else hikari.ButtonStyle.PRIMARY,
                    "vekn-required",
                )
                .set_label("No VEKN" if vekn_required else "Require VEKN")
                .add_to_container()
                .add_button(
                    hikari.ButtonStyle.SECONDARY
                    if decklist_required
                    else hikari.ButtonStyle.PRIMARY,
                    "decklist-required",
                )
                .set_label("No Decklist" if decklist_required else "Require Decklist")
                .add_to_container()
                .add_button(
                    hikari.ButtonStyle.SECONDARY
                    if checkin_each_round
                    else hikari.ButtonStyle.PRIMARY,
                    "checkin-each-round",
                )
                .set_label(
                    "Checkin once" if checkin_each_round else "Checkin each round"
                )
                .add_to_container()
                .add_button(
                    hikari.ButtonStyle.SECONDARY
                    if league
                    else hikari.ButtonStyle.PRIMARY,
                    "league",
                )
                .set_label("Tournament" if league else "League")
                .add_to_container()
                .add_button(
                    hikari.ButtonStyle.SECONDARY
                    if staggered
                    else hikari.ButtonStyle.PRIMARY,
                    "staggered",
                )
                .set_label("Normal" if staggered else "Staggered")
                .add_to_container(),
                self.bot.rest.build_action_row()
                .add_button(hikari.ButtonStyle.SUCCESS, "validate")
                .set_label("OK")
                .add_to_container(),
            ]
            COMPONENTS["vekn-required"] = ConfigureTournament
            COMPONENTS["decklist-required"] = ConfigureTournament
            COMPONENTS["checkin-each-round"] = ConfigureTournament
            COMPONENTS["league"] = ConfigureTournament
            COMPONENTS["staggered"] = ConfigureTournament
            COMPONENTS["validate"] = ConfigureTournament

        embed = hikari.Embed(
            title=f"Configuration - {self.tournament.name}",
            description=(
                f"- VEKN ID# is {'' if vekn_required else 'not '}required\n"
                f"- Decklist is {'' if decklist_required else 'not '}required\n"
                f"- Check-in {'each round' if checkin_each_round else 'once'}\n"
                + (
                    "- League format (multi-deck, join while in progress)\n"
                    if league
                    else "- Standard tournament\n"
                )
                + ("- Tournament is staggered\n" if staggered else "")
            ),
        )
        if not components:
            embed.description += (
                "\nRegistrations are now open.\n"
                "Use the `/appoint` command to appoint judges, bots and spectators.\n"
            )
        # different API response when a component is clicked,
        if getattr(self.interaction, "custom_id", None):
            await self.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                embed=embed,
                components=components,
            )
        # when called directly or just after the `open` command
        else:
            await self.create_or_edit_response(
                embed=embed,
                flags=hikari.MessageFlag.EPHEMERAL,
                components=components,
            )


class CloseTournament(BaseCommand):
    """Delete all roles and channels, mark as closed in DB (confirmation required)"""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Close the tournament"
    OPTIONS = []

    async def __call__(self) -> None:
        """Ask for confirmation, display confirm and cancel buttons"""
        if not self.tournament:
            raise CommandFailed("No tournament going on here")
        confirmation = (
            self.bot.rest.build_action_row()
            .add_button(hikari.ButtonStyle.DANGER, "confirm-close")
            .set_label("Close tournament")
            .add_to_container()
            .add_button(hikari.ButtonStyle.SECONDARY, "cancel-close")
            .set_label("Cancel")
            .add_to_container()
        )

        COMPONENTS["confirm-close"] = CloseTournament.Confirmed
        COMPONENTS["cancel-close"] = CloseTournament.Cancel
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Are you sure?",
                description=(
                    "This will definitely close all tournament channels.\n"
                    "Make sure you downloaded the tournament reports "
                    "(`/download-reports`)"
                ),
            ),
            components=[confirmation],
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    class Confirmed(BaseComponent):
        """When the confirm button is hit"""

        UPDATE = True

        async def __call__(self) -> None:
            await self.deferred()
            results = await asyncio.gather(
                *(
                    self.bot.rest.delete_channel(channel)
                    for channel in self.tournament.channels.values()
                ),
                return_exceptions=True,
            )
            results.extend(
                await asyncio.gather(
                    *(
                        self.bot.rest.delete_role(self.guild_id, role_id)
                        for role_id in self.tournament.roles.values()
                    ),
                    return_exceptions=True,
                )
            )
            self.tournament.channels = []
            self.tournament.roles = []
            self.update()
            db.close_tournament(self.connection, self.guild_id, self.category_id)
            COMPONENTS.pop("confirm-close", None)
            if any(isinstance(r, (hikari.ClientHTTPResponseError)) for r in results):
                logger.error("Errors closing tournament: %s", results)
                await self.create_or_edit_response(
                    embed=hikari.Embed(
                        title="Cleanup required",
                        description="Some tournament channels or roles have not been "
                        "deleted, make sure you clean up the server appropriately.",
                    ),
                    components=[],
                )
            else:
                await self.create_or_edit_response(
                    embed=hikari.Embed(
                        title="Tournament closed",
                        description="Thanks for using the Archon Bot.",
                    ),
                    components=[],
                )

    class Cancel(BaseComponent):
        """When the cancel button is hit"""

        UPDATE = False

        async def __call__(self):
            COMPONENTS.pop("cancel-close", None)
            await self.create_or_edit_response(
                "Cancelled",
                flags=hikari.MessageFlag.EPHEMERAL,
                components=[],
                embeds=[],
            )


class Register(BaseCommand):
    """Registration (auto-check-in if the check-in is open).

    The same class and code is used for CheckIn.
    """

    UPDATE = True
    DESCRIPTION = "Register for this tournament"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="vekn",
            description="Your VEKN ID#",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="name",
            description="Your name",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="decklist",
            description="Your decklist (Amaranth or VDB URL)",
            is_required=False,
        ),
    ]

    async def __call__(
        self,
        vekn: Optional[str] = None,
        name: Optional[str] = None,
        decklist: Optional[str] = None,
    ) -> None:
        if not self.tournament:
            raise CommandFailed("No tournament in progress")
        await self.deferred(flags=hikari.MessageFlag.EPHEMERAL)
        deck = None
        if decklist:
            deck = krcg.deck.Deck.from_url(decklist)
        discord_id = self.author.id
        try:
            player = await self.tournament.add_player(
                vekn, name, discord=discord_id, deck=deck, judge=False
            )
        except tournament.ErrorDecklistRequired:
            await self.create_or_edit_response(
                embed=hikari.Embed(
                    title="Decklist required",
                    description=(
                        "You need to provide a decklist with the `/register` command. "
                        "You do not need to provide the other parameters (eg. `vekn`) "
                        "if you have done so already: only your decklist will update."
                    ),
                )
            )
            return
        await self.bot.rest.add_role_to_member(
            self.guild_id,
            discord_id,
            self.tournament.roles[self.tournament.PLAYER],
            reason=self.reason,
        )
        description = "You are successfully registered for the tournament."
        if player.playing:
            description = "You are ready to play."
        elif (
            self.tournament.flags & tournament.TournamentFlag.DECKLIST_REQUIRED
            and not player.deck
        ):
            description += (
                "\nA decklist is required to participate, please use this command "
                "again to provide one before the tournament begins."
            )
        else:
            description += (
                "\nPlease note you will need to confirm your presence by "
                "using the `checkin` command before the next round begins."
            )
        self.update()
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Registered",
                description=description,
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
            components=[],
        )


class RegisterPlayer(BaseCommand):
    """Register another player (for judges). Also useful for offline tournaments."""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Register a player for this tournament"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="vekn",
            description="Your VEKN ID#",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="name",
            description="Your name",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="decklist",
            description="Your decklist (Amaranth or VDB URL)",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.USER,
            name="user",
            description="user to register (if any)",
            is_required=False,
        ),
    ]

    async def __call__(
        self,
        vekn: Optional[str] = None,
        name: Optional[str] = None,
        decklist: Optional[str] = None,
        user: Optional[hikari.Snowflake] = None,
    ) -> None:
        await self.deferred()
        deck = None
        if decklist:
            deck = krcg.deck.Deck.from_url(decklist)
        try:
            player = await self.tournament.add_player(
                vekn, name, discord=user, deck=deck, judge=True
            )
        except tournament.ErrorDecklistRequired:
            await self.create_or_edit_response(
                embed=hikari.Embed(
                    title="Decklist required",
                    description="Check-in is open: you need to provide a decklist.",
                )
            )
            return
        if user:
            await self.bot.rest.add_role_to_member(
                self.guild_id,
                user,
                self.tournament.roles[self.tournament.PLAYER],
                reason=self.reason,
            )
        self.update()
        player_display = self._player_display(player.vekn)
        description = f"{player_display} is successfully registered for the tournament."
        if player.playing:
            description = f"{player_display} is ready to play."
        elif (
            self.tournament.flags & tournament.TournamentFlag.DECKLIST_REQUIRED
            and not player.deck
        ):
            description += (
                "\nA decklist is required to participate, please use this command "
                "again to provide one before the tournament begins."
            )
        else:
            if self.tournament.state == tournament.TournamentState.PLAYING:
                description += (
                    "\nYou can add the player to the current round if you find a spot "
                    "for them on a table that has not yet begun to play by using the "
                    "`/round add` command"
                )
            else:
                description += (
                    "\nThe user will need to confirm their presence "
                    "by using the `checkin` command before next round begins.\n"
                )
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Player registered",
                description=description,
            ),
        )


class CheckIn(Register):
    """Just an alias."""

    UPDATE = True
    ACCESS = CommandAccess.PLAYER
    DESCRIPTION = "Check-in to play the next round"
    OPTIONS = []


class OpenCheckIn(BaseCommand):
    """Open the check-in so players can join the incoming round."""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Open check-in to players for next round"
    OPTIONS = []

    async def __call__(self) -> None:
        self.tournament.open_checkin()
        self.update()
        await self.create_or_edit_response("Check-in is open")


class Drop(BaseCommand):
    """Drop from the tournament."""

    UPDATE = True
    ACCESS = CommandAccess.PLAYER
    DESCRIPTION = "Drop from the tournament"
    OPTIONS = []

    async def __call__(self) -> None:
        self.tournament.drop(self.author.id)
        self.update()
        await self.create_or_edit_response(
            "Dropped",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


class DropPlayer(BaseCommand):
    """Drop a player. Remove him from the list if the tournament has not started."""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Remove a player from tournament (not a disqualification)"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.USER,
            name="user",
            description="user to drop",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="vekn",
            description="user to drop",
            is_required=False,
        ),
    ]

    async def __call__(
        self, user: Optional[hikari.Snowflake] = None, vekn: Optional[str] = None
    ) -> None:
        self.tournament.drop(user or vekn)
        self.update()
        await self.create_or_edit_response(
            f"Dropped {self._player_display(user or vekn)}"
        )


class Disqualify(BaseCommand):
    """Disqualify a player. Only a Judge can re-register them."""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Disqualify a player from the tournament"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.USER,
            name="user",
            description="user to disqualify",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="vekn",
            description="user to disqualify",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="note",
            description=(
                "Judge note stating the reason for disqualification "
                "(ignore if a warning was already issued)"
            ),
            is_required=False,
        ),
    ]

    async def __call__(
        self,
        user: Optional[hikari.Snowflake] = None,
        vekn: Optional[str] = None,
        note: Optional[str] = None,
    ) -> None:
        self.tournament.drop(user or vekn, reason=tournament.DropReason.DISQUALIFIED)
        if note:
            self.tournament.note(
                user or vekn, self.author.id, tournament.NoteLevel.WARNING, note
            )
        self.update()
        await self.create_or_edit_response(
            f"<@{user}> Disqualified",
            user_mentions=[user],
        )


class Appoint(BaseCommand):
    """Appoint Judges, bots and spectators for channels access.

    Judges might not have role management permissions on a server.
    """

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Appoint judges, bots and spectators"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="role",
            description="The role to give",
            is_required=True,
            choices=[
                hikari.CommandChoice(name="Judge", value="JUDGE"),
                hikari.CommandChoice(name="Spectator", value="SPECTATOR"),
                hikari.CommandChoice(name="Bot", value="BOT"),
            ],
        ),
        hikari.CommandOption(
            type=hikari.OptionType.USER,
            name="user",
            description="The user to give the tole to",
            is_required=True,
        ),
    ]

    async def __call__(
        self,
        role: str,
        user: hikari.Snowflake = None,
    ) -> None:
        await self.deferred(flags=hikari.MessageFlag.EPHEMERAL)
        if role in ["JUDGE", "BOT"]:
            await self.bot.rest.add_role_to_member(
                self.guild_id,
                user,
                self.tournament.roles[self.tournament.JUDGE],
                reason=self.reason,
            )
        else:
            await self.bot.rest.add_role_to_member(
                self.guild_id,
                user,
                self.tournament.roles[self.tournament.SPECTATOR],
                reason=self.reason,
            )
        await self.create_or_edit_response(
            f"Appointed <@{user}> as {role}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


class Round(BaseCommand):
    """Handle rounds.

    start: start a round with checked-in players
    finish: finish a round (checks for VPs consistency)
    reset: cancel the round and seating
    add: add a player on a table where the game has not started yet
    remove: remove a player from a table where the game has not started yet
    """

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Handle rounds"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND,
            name="start",
            description="Start the next round",
        ),
        hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND,
            name="finish",
            description="Finish the current round",
            options=[
                hikari.CommandOption(
                    type=hikari.OptionType.BOOLEAN,
                    name="keep_checkin",
                    description="Keep current check-in state despite configuration",
                    is_required=False,
                )
            ],
        ),
        hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND,
            name="reset",
            description="Reset the current round",
        ),
        hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND,
            name="add",
            description="Add a player to the current round",
            options=[
                hikari.CommandOption(
                    type=hikari.OptionType.INTEGER,
                    name="table",
                    description="Table number to add the user to",
                    is_required=True,
                    min_value=1,
                ),
                hikari.CommandOption(
                    type=hikari.OptionType.USER,
                    name="user",
                    description="The user to add to the round",
                    is_required=False,
                ),
                hikari.CommandOption(
                    type=hikari.OptionType.STRING,
                    name="vekn",
                    description="The user ID to add to the round",
                    is_required=False,
                ),
            ],
        ),
        hikari.CommandOption(
            type=hikari.OptionType.SUB_COMMAND,
            name="remove",
            description="Remove a player from the current round",
            options=[
                hikari.CommandOption(
                    type=hikari.OptionType.USER,
                    name="user",
                    description="The user to remove from the round",
                    is_required=False,
                ),
                hikari.CommandOption(
                    type=hikari.OptionType.STRING,
                    name="vekn",
                    description="The user ID to remove from the round",
                    is_required=False,
                ),
            ],
        ),
    ]

    async def __call__(self, *args, **kwargs) -> None:
        """Call subcommand (start, finish, reset, add, remove)"""
        logger.debug("%s | %s", args, kwargs)
        for option in self.interaction.options or []:
            await getattr(self, option.name)(
                **{subopt.name: subopt.value for subopt in (option.options or [])}
            )

    async def _progress(self, step, **kwargs) -> None:
        """Progress bar for the start subcommand"""
        chunk = tournament.ITERATIONS // 20
        if step % chunk:
            return
        progress = step // chunk
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Seating players...",
                description="▇" * progress + "▁" * (20 - progress),
            )
        )

    async def _display_seating(self, table_num) -> None:
        """Display the seating in the table channel."""
        table = self.tournament.rounds[-1].seating[table_num - 1]
        channel_id = self.tournament.channels[
            f"TEXT-{self.tournament.table_name(table_num)}".lower()
        ]
        voice_channel = self.tournament.channels.get(
            f"VOICE-{self.tournament.table_name(table_num)}".lower(), None
        )
        embed = hikari.Embed(
            title=f"Table {table_num} seating",
            description="\n".join(
                f"{j}. {self._player_display(p)}" for j, p in enumerate(table, 1)
            )
            + "\n\nThe first player should create the table.",
        )
        if voice_channel:
            embed.add_field(name="Join vocal", value=f"<#{voice_channel}>", inline=True)
        embed.add_field(name="Start the timer", value="`timer 2.5`", inline=True)
        embed.set_thumbnail(hikari.UnicodeEmoji("🪑"))
        await self.bot.rest.create_message(channel_id, embed=embed)

    async def start(self) -> None:
        """Start a round. Dynamically optimise seating to follow official VEKN rules.

        Assign roles and create text and voice channels for players.
        """
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Seating players...",
                description="_" * 20,
            )
        )
        round = await self.tournament.start_round(self._progress)
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Assigning tables...",
                description="Table channels are being opened and roles assigned",
            )
        )
        table_roles = await asyncio.gather(
            *(
                self.bot.rest.create_role(
                    guild=self.guild_id,
                    name=self.tournament.table_name(i + 1),
                    mentionable=True,
                    reason=self.reason,
                )
                for i in range(round.seating.tables_count())
            )
        )
        for role in table_roles:
            self.tournament.roles[role.name] = role.id
        player_roles = []
        for role, table in zip(table_roles, round.seating.iter_tables()):
            for number in table:
                if number not in self.tournament.players:
                    continue
                discord_id = self.tournament.players[number].discord
                if not discord_id:
                    continue
                player_roles.append([discord_id, role.id])
        await asyncio.gather(
            *(
                self.bot.rest.add_role_to_member(
                    guild=self.guild_id, user=user, role=role
                )
                for user, role in player_roles
            )
        )
        judge_role_id = self.tournament.roles[self.tournament.JUDGE]
        spectator_role_id = self.tournament.roles[self.tournament.SPECTATOR]
        channels = []
        channels.extend(
            self.bot.rest.create_guild_text_channel(
                guild=self.guild_id,
                name=self.tournament.table_name(i),
                reason=self.reason,
                permission_overwrites=[
                    hikari.PermissionOverwrite(
                        id=self.guild_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        deny=perm.TEXT,
                    ),
                    hikari.PermissionOverwrite(
                        id=role.id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.TEXT,
                    ),
                    hikari.PermissionOverwrite(
                        id=judge_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.TEXT,
                    ),
                    hikari.PermissionOverwrite(
                        id=spectator_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.SPECTATE_TEXT,
                    ),
                ],
            )
            for i, role in enumerate(table_roles, 1)
        )
        channels.extend(
            self.bot.rest.create_guild_voice_channel(
                guild=self.guild_id,
                name=self.tournament.table_name(i),
                reason=self.reason,
                bitrate=96000,
                permission_overwrites=[
                    hikari.PermissionOverwrite(
                        id=self.guild_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        deny=perm.VOICE,
                    ),
                    hikari.PermissionOverwrite(
                        id=role.id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.VOICE,
                    ),
                    hikari.PermissionOverwrite(
                        id=judge_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.JUDGE_VOICE,
                    ),
                    hikari.PermissionOverwrite(
                        id=spectator_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.SPECTATE_VOICE,
                    ),
                ],
            )
            for i, role in enumerate(table_roles, 1)
        )
        channels = await asyncio.gather(*channels)
        for channel in channels:
            if isinstance(channel, hikari.GuildTextChannel):
                self.tournament.channels[f"text-{channel.name}".lower()] = channel.id
            elif isinstance(channel, hikari.GuildVoiceChannel):
                self.tournament.channels[f"voice-{channel.name}".lower()] = channel.id
        await asyncio.gather(
            *(self._display_seating(i + 1) for i in range(round.seating.tables_count()))
        )
        self.update()
        embed = hikari.Embed(
            title=f"Round {self.tournament.current_round} Seating",
        )
        for i, table in enumerate(round.seating.iter_tables(), 1):
            embed.add_field(
                name=f"Table {i}",
                value="\n".join(
                    f"{j}. {self._player_display(vekn)}"
                    for j, vekn in enumerate(table, 1)
                ),
                inline=True,
            )
        embed.set_thumbnail(hikari.UnicodeEmoji("🪑"))
        await self.create_or_edit_response(
            embeds=_paginate_embed(embed),
            user_mentions=True,
        )

    async def _delete_round_tables(self, finals: bool = False) -> None:
        """Delete table channels and roles used for the round."""
        # TODO: tables roles and channels retrieval should be coded in tournament
        if finals:
            table_names = [f"{self.tournament.prefix}Finals"]
        else:
            table_names = [
                self.tournament.table_name(i + 1)
                for i in range(self.tournament.rounds[-1].seating.tables_count())
            ]
        roles = [self.tournament.roles.pop(t, None) for t in table_names]
        roles = [r for r in roles if r]
        text_channels = [
            self.tournament.channels.pop(f"TEXT-{t}".lower(), None) for t in table_names
        ]
        voice_channels = [
            self.tournament.channels.pop(f"VOICE-{t}".lower(), None)
            for t in table_names
        ]
        text_channels = [c for c in text_channels if c]
        voice_channels = [c for c in voice_channels if c]
        await asyncio.gather(
            *(
                [
                    self.bot.rest.delete_channel(channel)
                    for channel in text_channels + voice_channels
                ]
                + [
                    self.bot.rest.delete_role(
                        self.guild_id,
                        role,
                    )
                    for role in roles
                ]
            ),
            return_exceptions=True,
        )

    async def finish(self, keep_checkin: bool = False) -> None:
        """Finish round (checks scores consistency)"""
        await self.deferred()
        round = self.tournament.finish_round(keep_checkin)
        await self._delete_round_tables(round.finals)
        self.update()
        await self.create_or_edit_response("Round finished")

    async def reset(self) -> None:
        """Rollback round"""
        await self.deferred()
        round = self.tournament.reset_round()
        await self._delete_round_tables(round.finals)
        self.update()
        await self.create_or_edit_response("Round reset")

    async def add(
        self,
        table: int,
        user: Optional[hikari.Snowflake] = None,
        vekn: Optional[str] = None,
    ) -> None:
        """Add player to a 4-players table"""
        await self.deferred()
        self.tournament.round_add(user or vekn, table)
        await self._display_seating(table)
        self.update()
        await self.create_or_edit_response(f"Player added to table {table}")

    async def remove(
        self, user: Optional[hikari.Snowflake] = None, vekn: Optional[str] = None
    ) -> None:
        """Remove player from a 5-players table"""
        await self.deferred()
        table = self.tournament.round_remove(user or vekn)
        await self._display_seating(table)
        self.update()
        await self.create_or_edit_response(f"Player removed from table {table}")


class Finals(BaseCommand):
    """Start finals (auto toss for a spot in case of points draw)."""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Start the finals"
    OPTIONS = []

    async def __call__(self) -> None:
        round = self.tournament.start_finals()
        table = round.seating[0]
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Creating channels...",
                description="Finals channels are being opened and roles assigned",
            )
        )
        self.update()
        table_role = await self.bot.rest.create_role(
            guild=self.guild_id,
            name=f"{self.tournament.prefix}Finals",
            mentionable=True,
            reason=self.reason,
        )
        self.tournament.roles[table_role.name] = table_role.id
        finalists = []
        for number in round.seating[0]:
            if number not in self.tournament.players:
                continue
            discord_id = self.tournament.players[number].discord
            if not discord_id:
                continue
            finalists.append(discord_id)
        await asyncio.gather(
            *(
                self.bot.rest.add_role_to_member(
                    guild=self.guild_id,
                    user=discord_id,
                    role=table_role,
                    reason=self.reason,
                )
                for discord_id in finalists
            )
        )
        judge_role_id = self.tournament.roles[self.tournament.JUDGE]
        spectator_role_id = self.tournament.roles[self.tournament.SPECTATOR]
        channels = [
            self.bot.rest.create_guild_text_channel(
                guild=self.guild_id,
                name=f"{self.tournament.prefix}Finals",
                reason=self.reason,
                permission_overwrites=[
                    hikari.PermissionOverwrite(
                        id=self.guild_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        deny=perm.TEXT,
                    ),
                    hikari.PermissionOverwrite(
                        id=table_role.id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.TEXT,
                    ),
                    hikari.PermissionOverwrite(
                        id=judge_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.TEXT,
                    ),
                    hikari.PermissionOverwrite(
                        id=spectator_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.SPECTATE_TEXT,
                    ),
                ],
            ),
            self.bot.rest.create_guild_voice_channel(
                guild=self.guild_id,
                name=f"{self.tournament.prefix}Finals",
                reason=self.reason,
                permission_overwrites=[
                    hikari.PermissionOverwrite(
                        id=self.guild_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        deny=perm.VOICE,
                    ),
                    hikari.PermissionOverwrite(
                        id=table_role.id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.VOICE,
                    ),
                    hikari.PermissionOverwrite(
                        id=judge_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.JUDGE_VOICE,
                    ),
                    hikari.PermissionOverwrite(
                        id=spectator_role_id,
                        type=hikari.PermissionOverwriteType.ROLE,
                        allow=perm.SPECTATE_VOICE,
                    ),
                ],
            ),
        ]
        channels = await asyncio.gather(*channels)
        for channel in channels:
            if isinstance(channel, hikari.GuildTextChannel):
                name = channel.name.lower()
                self.tournament.channels[f"text-{name}"] = channels[0].id
            elif isinstance(channel, hikari.GuildVoiceChannel):
                self.tournament.channels[f"voice-{name}"] = channels[1].id
        seeding_embed = hikari.Embed(
            title="Finals seeding",
            description="\n".join(
                f"{j}. {self._player_display(p)}" for j, p in enumerate(table, 1)
            ),
        )
        await self.bot.rest.create_message(
            channels[0].id,
            embed=seeding_embed,
        )
        self.update()
        await self.create_or_edit_response(
            embed=seeding_embed,
            user_mentions=True,
        )


class Report(BaseCommand):
    """Report number of VPs scored"""

    UPDATE = True
    ACCESS = CommandAccess.PLAYER
    DESCRIPTION = "Report the number of VPs you got in the round"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.FLOAT,
            name="vp",
            description="Number of VPs won",
            is_required=True,
            min_value=0,
            max_value=5,
        ),
    ]

    async def __call__(self, vp: float) -> None:
        self.tournament.report(self.author.id, vp)
        self.update()
        await self.create_or_edit_response(
            content="Result registered", flags=hikari.MessageFlag.EPHEMERAL
        )


class FixReport(BaseCommand):
    """Fix a VP score on any table, any round."""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Fix a VP score"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.FLOAT,
            name="vp",
            description="Number of VPs won",
            is_required=True,
            min_value=0,
            max_value=5,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.USER,
            name="user",
            description="User whose result should be changed",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="vekn",
            description="User ID whose result should be changed",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.INTEGER,
            name="round",
            description=(
                "Round for which to change the result (defaults to current round)"
            ),
            is_required=False,
            min_value=1,
        ),
    ]

    async def __call__(
        self,
        vp: float,
        round: Optional[int] = None,
        user: Optional[hikari.Snowflake] = None,
        vekn: Optional[str] = None,
    ) -> None:
        self.tournament.report(user or vekn, vp, round)
        self.update()
        await self.create_or_edit_response(
            content=(
                f"Result registered: {vp} VPs for {self._player_display(user or vekn)}"
            ),
            flags=hikari.UNDEFINED
            if self._is_judge_channel()
            else hikari.MessageFlag.EPHEMERAL,
        )


class ValidateScore(BaseCommand):
    """Validate an odd VP situation (inconsistent score due to a judge ruling)"""

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "Validate an odd VP situation"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.INTEGER,
            name="table",
            description=("Table for which to validate the score"),
            is_required=True,
            min_value=1,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="note",
            description=("The reason for the odd VP situation"),
            is_required=True,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.INTEGER,
            name="round",
            description=(
                "Round for which to change the result (defaults to current round)"
            ),
            is_required=False,
            min_value=1,
        ),
    ]

    async def __call__(
        self, table: int, note: str, round: Optional[int] = None
    ) -> None:
        self.tournament.validate_score(table, self.author.id, note, round)
        self.update()
        await self.create_or_edit_response(
            content=f"Score validated for table {table}",
            flags=hikari.UNDEFINED
            if self._is_judge_channel()
            else hikari.MessageFlag.EPHEMERAL,
        )


def note_level_int(level: tournament.NoteLevel) -> int:
    """Note level as int. The higher the penalty, the higher the int."""
    return list(tournament.NoteLevel.__members__.values()).index(level)


def note_level_str(level: tournament.NoteLevel) -> str:
    """Note level label"""
    return {
        tournament.NoteLevel.OVERRIDE: "Override",
        tournament.NoteLevel.NOTE: "Note",
        tournament.NoteLevel.CAUTION: "Caution",
        tournament.NoteLevel.WARNING: "Warning",
    }[level]


def notes_by_level(notes: Iterable[tournament.Note]) -> List[List[tournament.Note]]:
    """Group notes by level"""
    ret = []
    notes = sorted(notes, key=lambda n: note_level_int(n.level))
    for _, level_notes in itertools.groupby(
        notes, key=lambda n: note_level_int(n.level)
    ):
        level_notes = list(level_notes)
        ret.append(list(level_notes))
    return ret


def partialclass(cls, *args, **kwds):
    """Useful util to pass some attributes to a subclass."""

    class NewCls(cls):
        __init__ = functools.partialmethod(cls.__init__, *args, **kwds)

    return NewCls


class Note(BaseCommand):
    """Allow a Judge to take a note on or deliver a caution or warning to a player.

    If previous notes have been taken on this player,
    ask the judge to review them and potentially adapt their note level
    (upgrade to caution, warning or disqualification).
    """

    UPDATE = True
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Take a note on a player, or deliver a caution or warning"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="level",
            description="Level of the remark",
            is_required=True,
            choices=[
                hikari.CommandChoice(name="Note", value=tournament.NoteLevel.NOTE),
                hikari.CommandChoice(
                    name="Caution", value=tournament.NoteLevel.CAUTION
                ),
                hikari.CommandChoice(
                    name="Warning", value=tournament.NoteLevel.WARNING
                ),
            ],
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="note",
            description="The comment",
            is_required=True,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.USER,
            name="user",
            description="User whose result should be changed",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="vekn",
            description="User ID whose result should be changed",
            is_required=False,
        ),
    ]

    async def __call__(
        self,
        level: tournament.NoteLevel,
        note: str,
        user: Optional[hikari.Snowflake] = None,
        vekn: Optional[str] = None,
    ) -> None:
        await self.deferred(hikari.MessageFlag.EPHEMERAL)
        vekn = self.tournament._check_player_id(user or vekn)
        previous_level, previous_notes = None, None
        if vekn in self.tournament.notes:
            previous_notes = notes_by_level(self.tournament.notes[vekn])[-1]
            previous_level = previous_notes[0].level
            if note_level_int(previous_level) < note_level_int(level):
                previous_level = previous_notes = None

        if previous_notes and previous_level == tournament.NoteLevel.WARNING:
            upgrade_component = (
                "note-upgrade",
                "Disqualification",
                partialclass(
                    Note.ApplyNote, vekn, note, tournament.NoteLevel.WARNING, True
                ),
            )
        elif previous_notes and previous_level == tournament.NoteLevel.CAUTION:
            upgrade_component = (
                "note-upgrade",
                "Warning",
                partialclass(
                    Note.ApplyNote, vekn, note, tournament.NoteLevel.WARNING, False
                ),
            )
        elif previous_notes and previous_level == tournament.NoteLevel.NOTE:
            upgrade_component = (
                "note-upgrade",
                "Caution",
                partialclass(
                    Note.ApplyNote, vekn, note, tournament.NoteLevel.CAUTION, False
                ),
            )

        confirmation = self.bot.rest.build_action_row()
        if previous_notes:
            confirmation = (
                confirmation.add_button(
                    hikari.ButtonStyle.DANGER, f"note-upgrade-{self.author.id}"
                )
                .set_label(f"Upgrade to {upgrade_component[1]}")
                .add_to_container()
            )
            COMPONENTS[f"note-upgrade-{self.author.id}"] = upgrade_component[2]
        confirmation = (
            confirmation.add_button(
                hikari.ButtonStyle.PRIMARY, f"note-continue-{self.author.id}"
            )
            .set_label("Continue")
            .add_to_container()
            .add_button(hikari.ButtonStyle.SECONDARY, "note-cancel")
            .set_label("Cancel")
            .add_to_container()
        )
        COMPONENTS[f"note-continue-{self.author.id}"] = partialclass(
            Note.ApplyNote, vekn, note, level, False
        )
        COMPONENTS["note-cancel"] = Note.Cancel
        if previous_notes:
            embed = hikari.Embed(
                title="Review note level",
                description=(
                    "There are already some notes for this player, "
                    "you might want to upgrade your note level."
                ),
            )
            embed.add_field(
                name=f"Previous {previous_level}",
                value="\n".join(f"- <@{p.judge}> {p.text}" for p in previous_notes),
            )
        else:
            embed = hikari.Embed(
                title="Confirmation",
                description="",
            )
        embed.add_field(
            name=f"Your {level}",
            value=note,
        )
        await self.create_or_edit_response(
            embed=embed,
            components=[confirmation],
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    class ApplyNote(BaseComponent):
        """Apply the note. Post a message on table channel for cautions and warnings."""

        UPDATE = True

        def __init__(
            self,
            vekn: str,
            note: str,
            level: tournament.NoteLevel,
            disqualify: bool,
            *args,
            **kwargs,
        ):
            self.vekn = vekn
            self.note = note
            self.level = level
            self.disqualify = disqualify
            super().__init__(*args, **kwargs)

        async def __call__(self):
            self.tournament.note(self.vekn, self.author.id, self.level, self.note)
            if self.disqualify:
                self.tournament.drop(self.vekn, tournament.DropReason.DISQUALIFIED)
            self.update()
            if self.level == tournament.NoteLevel.NOTE:
                await self.create_or_edit_response(
                    embed=hikari.Embed(title="Note taken", description=self.note),
                    flags=hikari.MessageFlag.EPHEMERAL,
                    components=[],
                )
            else:
                embed = hikari.Embed(
                    title=f"{self.level} delivered",
                    description=f"{self._player_display(self.vekn)}: {self.note}",
                )
                table_text = None
                info = self.tournament.player_info(self.vekn)
                if info.table:
                    if self.tournament.rounds[-1].finals:
                        table_name = f"{self.tournament.prefix}Finals"
                    else:
                        table_name = self.tournament.table_name(info.table)
                    table_text = self.tournament.channels.get(
                        f"text-{table_name}".lower(), None
                    )
                coroutines = [
                    self.create_or_edit_response(
                        embed=embed,
                        components=[],
                    )
                ]
                if table_text:
                    coroutines.append(
                        self.bot.rest.create_message(table_text, embed=embed)
                    )
                await asyncio.gather(*coroutines)

    class Cancel(BaseComponent):
        UPDATE = False

        async def __call__(self):
            await self.create_or_edit_response(
                "Cancelled",
                flags=hikari.MessageFlag.EPHEMERAL,
                components=[],
                embeds=[],
            )


class Announce(BaseCommand):
    """Standard announcement - depends on the tournament state / step.

    It's the core helper. It provides instructions and guidance for judges and players.
    """

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "Make the standard announcement (depends on the tournament state)"
    OPTIONS = []

    async def __call__(self) -> None:
        await self.deferred()
        judges_channel = self.tournament.channels[self.tournament.JUDGE_TEXT]
        current_round = self.tournament.current_round
        if self.tournament.state == tournament.TournamentState.CHECKIN:
            current_round += 1
        if self.tournament.rounds and self.tournament.rounds[-1].finals:
            current_round = "Finals"
        else:
            current_round = f"Round {current_round}"
        if self.tournament.state == tournament.TournamentState.REGISTRATION:
            embed = hikari.Embed(
                title=f"{self.tournament.name} — Registrations open",
                description=(
                    f"{self.tournament.players.count} players registered\n"
                    "**Use the `/register` command to register.**"
                ),
            )
            if self.tournament.flags & tournament.TournamentFlag.VEKN_REQUIRED:
                embed.add_field(
                    name="VEKN ID# required",
                    value=(
                        "A VEKN ID is required to register to this tournament. "
                        "You can find yours on the "
                        "[VEKN website](https://www.vekn.net/player-registry). "
                        "If you do not have one, ask the Judges or your Prince."
                    ),
                )
            if self.tournament.flags & tournament.TournamentFlag.DECKLIST_REQUIRED:
                embed.add_field(
                    name="Decklist required",
                    value=(
                        "A decklist is required for this tournament. "
                        "You can register without one, but you need to provide "
                        "it before the first round. "
                        "Use the `/register` command again to add your decklist."
                    ),
                )
            if self.tournament.flags & tournament.TournamentFlag.CHECKIN_EACH_ROUND:
                checkin_time = "each round"
            else:
                checkin_time = "the first round"
            embed.add_field(
                name="Check-in",
                value=(
                    "Once registered, you will need to check in before "
                    f"{checkin_time} using the `/check-in` command."
                ),
            )
            judges_embed = hikari.Embed(
                title=embed.title,
                description=(
                    "- `/players-list` to check progression\n"
                    "- `/register-player` to register players who struggles\n"
                    "- `/drop-player` to remove a player\n"
                    "- `/open-check-in` to allow check-in for the first round. "
                    "Registration will still be possible once you open check-in.\n"
                ),
            )
            judges_embed.add_field(
                name="Player Registration",
                value=(
                    "When you use the `/register-player` command, you need to provide "
                    "either the user or their VEKN ID#. With a *single command*, "
                    "you can provide both, and also the decklist. If the player is "
                    "listed already, the command will update the information "
                    "(VEKN ID# and/or deck). If not, the command will register them "
                    "as a new player."
                ),
            )
            judges_embed.add_field(
                name="No VEKN ID#",
                value=(
                    "If the tournament requires a VEKN ID# and the player does not "
                    "have one yet, they cannot register. As judge, you can register "
                    "them with the `/register-player` command. If you do not provide "
                    "a VEKN ID#, the bot will issue a temporary ID to use as VEKN ID#, "
                    "a short number prefixed with `P-`."
                ),
            )
            await asyncio.gather(
                *(
                    self.create_or_edit_response(embed=embed),
                    self.bot.rest.create_message(judges_channel, embed=judges_embed),
                )
            )

        elif self.tournament.state == tournament.TournamentState.CHECKIN:
            players_role = self.tournament.roles[self.tournament.PLAYER]
            embed = hikari.Embed(
                title=(f"{self.tournament.name} — CHECK-IN — {current_round}"),
                description=(
                    "⚠️ **Check-in is required to play** ⚠️\n"
                    "Please confirm your participation with the `/check-in` command.\n"
                    "You can use the `/status` command to verify your status."
                ),
            )
            if (
                self.tournament.current_round == 0
                or self.tournament.flags & tournament.TournamentFlag.LEAGUE
            ):
                embed.add_field(
                    name="Registration",
                    value=(
                        "If you are not registered yet, you can still do so "
                        "by using the `/register` command. You will be checked "
                        "in automatically."
                    ),
                )
            judges_embed = hikari.Embed(
                title=embed.title,
                description=(
                    "- `/players-list` to check progression\n"
                    "- `/register-player` to check players who struggle in\n"
                    "- `/round start` when you're ready\n"
                ),
            )
            await asyncio.gather(
                *(
                    self.create_or_edit_response(
                        embed=embed,
                        content=f"<@&{players_role}>",
                        role_mentions=[players_role],
                    ),
                    self.bot.rest.create_message(judges_channel, embed=judges_embed),
                )
            )

        elif self.tournament.state == tournament.TournamentState.WAITING:
            embed = hikari.Embed(
                title=(f"{self.tournament.name} — {current_round} finished"),
                description=(
                    "Waiting for next round to begin.\n"
                    "You can use the `/status` command to verify your status."
                ),
            )
            if self.tournament.flags & tournament.TournamentFlag.CHECKIN_EACH_ROUND:
                embed.add_field(
                    name="Check-in required",
                    value=(
                        "Players will need to **check in again** for next round "
                        "(unless it is the finals)."
                    ),
                )
            judges_embed = hikari.Embed(
                title=embed.title,
                description=(
                    "- `/open-check-in` to open the check-in for next round\n"
                    "- `/standings` to get current standings\n"
                    "- `/finals` to start the finals\n"
                ),
            )
            await asyncio.gather(
                *(
                    self.create_or_edit_response(embed=embed),
                    self.bot.rest.create_message(judges_channel, embed=judges_embed),
                )
            )
        elif self.tournament.state == tournament.TournamentState.FINISHED:
            description = f"The {self.tournament.name} is finished.\n"
            winner = self.tournament.players.get(self.tournament.winner, None)
            if winner:
                description += (
                    f"Congratulations {self._player_display(winner.vekn)} "
                    "for your victory!"
                )
            embed = hikari.Embed(
                title=(f"{self.tournament.name} — {current_round} finished"),
                description=description,
            )
            if winner.deck:
                embed.add_field(name="Decklist", value=self._deck_display(winner.deck))
            judges_embed = hikari.Embed(
                title=embed.title,
                description=(
                    "- `/download-reports` to get the tournament report files\n"
                    "- `/close-tournament` to close this tournament\n"
                ),
            )
            await asyncio.gather(
                *(
                    self.create_or_edit_response(embed=embed),
                    self.bot.rest.create_message(judges_channel, embed=judges_embed),
                )
            )
        elif self.tournament.state == tournament.TournamentState.PLAYING:
            embed = hikari.Embed(
                title=(f"{self.tournament.name} — {current_round} in progress"),
                description=(
                    "Join your assigned table channels and enjoy your game.\n"
                    "Use the `/status` command to **find your table** if you're lost."
                ),
            )
            embed.add_field(
                name="Report your results",
                value=(
                    "Use the `/report` command to report "
                    "your Victory Points.\n"
                    "No need to report scores of zero."
                ),
            )
            if self.tournament.rounds[-1].finals:
                judges_embed = hikari.Embed(
                    title=embed.title,
                    description=(
                        "- `/round reset` to cancel (the toss stays the same)\n"
                        "- `/fix-report` to register the score\n"
                        "- `/round finish` when all is good\n"
                        "\n"
                        "Once this is done, you can get the reports with "
                        "`/download-reports` and close the tournament with "
                        "`/close-tournament`."
                    ),
                )
            else:
                judges_embed = hikari.Embed(
                    title=embed.title,
                    description=(
                        "- `/round remove` to remove a player before the game begins\n"
                        "- `/round reset` to cancel the round and seating\n"
                        "- `/results` to see the results\n"
                        "- `/fix-report` to correct them if needed\n"
                        "- `/validate-score` to confirm odd situations\n"
                        "- `/round finish` when all is good\n"
                        "\n"
                        "You can still register a late arrival with `/register-player` "
                        "then add them to a 4-players table that has not yet started "
                        "(if any) with `/round add`."
                    ),
                )
            await asyncio.gather(
                *(
                    self.create_or_edit_response(embed=embed),
                    self.bot.rest.create_message(judges_channel, embed=judges_embed),
                )
            )


class Status(BaseCommand):
    """Player status. Provides guidance for lost souls."""

    UPDATE = False
    DESCRIPTION = "Check your current status"
    OPTIONS = []

    async def __call__(self) -> None:
        await self.deferred(hikari.MessageFlag.EPHEMERAL)
        if not self.tournament:
            raise CommandFailed("No tournament in progress")
        judge_role_id = self.tournament.roles[self.tournament.JUDGE]
        embed = hikari.Embed(
            title=f"{self.tournament.name} — {self.tournament.players.count} players"
        )
        if self.author.id not in self.tournament.players:
            if self.tournament.rounds and not (
                self.tournament.flags & tournament.TournamentFlag.LEAGUE
            ):
                embed.description = "Tournament in progress. You're not participating."
            elif self.tournament.state == tournament.TournamentState.WAITING:
                embed.description = "Waiting for registrations to open."
            else:
                embed.description = (
                    f"{self.tournament.players.count} players registered.\n"
                    "Register using the `/register` command."
                )
                if self.tournament.flags & tournament.TournamentFlag.VEKN_REQUIRED:
                    embed.description += (
                        "\nThis tournament requires a **VEKN ID#**. "
                        f"If you do not have one, ask a <@&{judge_role_id}> to help "
                        "with your registration."
                    )
        else:
            info = self.tournament.player_info(self.author.id)
            logger.debug("Player info: %s", info)
            embed.description = ""
            if info.drop and info.drop == tournament.DropReason.DROP:
                embed.description = "**DROPPED**\n"
            elif info.drop and info.drop == tournament.DropReason.DISQUALIFIED:
                embed.description = "**DISQUALIFIED**\n"
            penalties = [
                note
                for note in info.notes
                if note.level
                in [tournament.NoteLevel.CAUTION, tournament.NoteLevel.WARNING]
            ]
            if penalties:
                embed.add_field(
                    name="Penalties",
                    value="\n".join(
                        f"- **{note_level_str(note.level)}:** {note.text}"
                        for note in penalties
                    ),
                )
            if info.status == tournament.PlayerStatus.PLAYING:
                if self.tournament.rounds[-1].finals:
                    seat = "seed"
                    text_channel = f"text-{self.tournament.prefix}finals".lower()
                    voice_channel = f"voice-{self.tournament.prefix}finals".lower()
                else:
                    seat = "seat"
                    table_name = self.tournament.table_name(info.table)
                    text_channel = f"text-{table_name}".lower()
                    voice_channel = f"voice-{table_name}".lower()
                text_channel = self.tournament.channels.get(text_channel, None)
                voice_channel = self.tournament.channels.get(voice_channel, None)
                if text_channel:
                    embed.description = (
                        f"You are {seat} {info.position} on <#{text_channel}>\n"
                    )
                else:
                    embed.description = (
                        f"You are {seat} {info.position} on table {info.table}\n"
                    )
                if voice_channel:
                    embed.description += f"\n**Join vocal:** <#{voice_channel}>"
                embed.description += "\nUse the `/report` command to register your VPs"
            elif info.status == tournament.PlayerStatus.CHECKED_IN:
                embed.description = (
                    "You are ready to play. You will be assigned a table and a seat "
                    "when the round starts."
                )
            elif info.status == tournament.PlayerStatus.CHECKIN_REQUIRED:
                embed.description = (
                    "⚠️ **You need to check-in** ⚠️\n"
                    "Use the `/check-in` command to check in for the next round."
                )
            elif info.status == tournament.PlayerStatus.MISSING_DECK:
                embed.description = (
                    "⚠️ **You need to provide your decklist** ⚠️\n"
                    "Please use the `/register` command to provide your decklist.\n"
                    f"You need to provide a [VDB]({VDB_URL}) "
                    f"or [Amaranth]({AMARANTH_URL}) link (URL)."
                )
            elif info.status == tournament.PlayerStatus.WAITING:
                if self.tournament.current_round == 0:
                    embed.description = (
                        "You are registered. Waiting for check-in to open."
                    )
                elif self.tournament.rounds[-1].finals:
                    embed.description = (
                        "You are done. Thanks for participating in this event!"
                    )
                elif (
                    self.tournament.flags & tournament.TournamentFlag.CHECKIN_EACH_ROUND
                ):
                    embed.description = (
                        "You will need to **check-in again** for next round, if any."
                    )
                else:
                    embed.description = (
                        "You are ready to play. Waiting for next round to start."
                    )
            elif info.status == tournament.PlayerStatus.CHECKED_OUT:
                embed.description = "You are not checked in. Check-in is closed, sorry."
            else:
                raise RuntimeError("Unexpected tournament state")
            if self.tournament.rounds:
                if (
                    self.tournament.state == tournament.TournamentState.PLAYING
                    and info.player.playing
                ):
                    if self.tournament.rounds[-1].finals:
                        embed.description = (
                            f"**You are playing in the finals** {info.score}\n"
                            + embed.description
                        )
                    else:
                        ORDINAL = {
                            1: "st",
                            2: "nd",
                            3: "rd",
                        }
                        embed.description = (
                            f"**You are playing your {info.rounds}"
                            f"{ORDINAL.get(info.rounds, 'th')} round {info.score}**\n"
                            + embed.description
                        )
                else:
                    embed.description = (
                        f"You played {info.rounds} rounds {info.score}\n"
                        + embed.description
                    )
        await self.create_or_edit_response(
            embed=embed, flags=hikari.MessageFlag.EPHEMERAL
        )


class Standings(BaseCommand):
    """Standings of all players. Private (ephemeral) answer by default."""

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Display current standings"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.BOOLEAN,
            name="public",
            description="Display the standings publicly (default is private)",
            is_required=False,
        ),
    ]

    async def __call__(self, public: bool = False) -> None:
        winner, ranking = self.tournament.standings()
        embed = hikari.Embed(
            title="Standings",
            description="\n".join(
                ("*WINNER* " if winner == vekn else f"{rank}. ")
                + f"{self._player_display(vekn)} {score}"
                for rank, vekn, score in ranking
            ),
        )
        embed.set_thumbnail(hikari.UnicodeEmoji("📋"))
        await self.create_or_edit_response(
            embeds=_paginate_embed(embed),
            flags=(
                hikari.UNDEFINED
                if public or self._is_judge_channel()
                else hikari.MessageFlag.EPHEMERAL
            ),
        )


class PlayerInfo(BaseCommand):
    """Player information. Includes notes."""

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "Displayer a player's info (private)"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.STRING,
            name="vekn",
            description="Player VEKN ID#",
            is_required=False,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.USER,
            name="user",
            description="Player",
            is_required=False,
        ),
    ]

    async def __call__(
        self,
        vekn: Optional[str] = None,
        user: Optional[hikari.Snowflake] = None,
    ) -> None:
        info = self.tournament.player_info(vekn or user)
        description = self._player_display(info.player.vekn)
        description += (
            f"\n{info.rounds} round{'s' if info.rounds > 1 else ''} played {info.score}"
        )
        if info.drop and info.drop == tournament.DropReason.DROP:
            description += "\n**DROPPED**"
        elif info.drop and info.drop == tournament.DropReason.DISQUALIFIED:
            description += "\n**DISQUALIFIED**"
        embed = hikari.Embed(
            title="Player Info",
            description=description,
        )
        if info.player.deck:
            if self.tournament.rounds:
                embed.add_field(
                    name="Decklist", value=self._deck_display(info.player.deck)
                )
            else:
                embed.add_field(
                    name="Decklist registered",
                    value=(
                        "You will have access to the list "
                        "after the first round begins."
                    ),
                )
        if info.player.playing:
            if self.tournament.state in [
                tournament.TournamentState.CHECKIN,
                tournament.TournamentState.WAITING,
            ]:
                embed.add_field(
                    name="Checked-in",
                    value=("Player is checked-in and ready to play."),
                )
            elif self.tournament.state == tournament.TournamentState.PLAYING:
                # TODO factorize this part
                if self.tournament.rounds[-1].finals:
                    seat = "seed"
                    text_channel = f"text-{self.tournament.prefix}finals".lower()
                    voice_channel = f"voice-{self.tournament.prefix}finals".lower()
                else:
                    seat = "seat"
                    table_name = self.tournament.table_name(info.table)
                    text_channel = f"text-{table_name}".lower()
                    voice_channel = f"voice-{table_name}".lower()
                text_channel = self.tournament.channels.get(text_channel, None)
                voice_channel = self.tournament.channels.get(voice_channel, None)
                if text_channel:
                    description = (
                        f"Player is {seat} {info.position} on <#{text_channel}>\n"
                    )
                else:
                    description = (
                        f"Player is {seat} {info.position} on table {info.table}\n"
                    )
                if voice_channel:
                    description += f"\n**Vocal:** <#{voice_channel}>"
                embed.add_field(
                    name="Playing",
                    value=description,
                )
        for notes in notes_by_level(info.notes):
            embed.add_field(
                name=note_level_str(notes[0].level),
                value="\n".join(f"- <@{n.judge}> {n.text}" for n in notes),
            )
        await self.create_or_edit_response(
            embeds=_paginate_embed(embed),
            flags=(
                hikari.UNDEFINED
                if self._is_judge_channel()
                else hikari.MessageFlag.EPHEMERAL
            ),
        )


class Results(BaseCommand):
    """Round results. Defaults to current round."""

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Display current round results"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.INTEGER,
            name="round",
            description=(
                "Round for which to see the result (defaults to current round)"
            ),
            is_required=False,
            min_value=1,
        ),
        hikari.CommandOption(
            type=hikari.OptionType.BOOLEAN,
            name="public",
            description="Display the results publicly (default is private)",
            is_required=False,
        ),
    ]

    async def __call__(
        self, round: Optional[int] = None, public: Optional[bool] = False
    ) -> None:
        round_number = round or self.tournament.current_round
        try:
            round = self.tournament.rounds[round_number - 1]
        except IndexError:
            raise CommandFailed(f"Round {round_number} has not been played")
        if public or self._is_judge_channel():
            flag = hikari.UNDEFINED
        else:
            flag = hikari.MessageFlag.EPHEMERAL
        await self.deferred(flag)
        embed = hikari.Embed(
            title="Finals" if round.finals else f"Round {round_number}"
        )
        round.score()
        incorrect = set(round.incorrect)
        for i, table in enumerate(round.seating.iter_tables(), 1):
            scores = []
            for j, player_number in enumerate(table, 1):
                vekn = self.tournament._check_player_id(player_number)
                score = round.results.get(player_number, None) or tournament.Score()
                scores.append(f"{j}. {self._player_display(vekn)} {score}")
            embed.add_field(
                name=f"Table {i} " + ("⚠️" if i in incorrect else "☑️"),
                value="\n".join(scores),
                inline=True,
            )
        embeds = _paginate_embed(embed)
        await self.create_or_edit_response(embeds=embeds, flags=flag)


def status_icon(status: tournament.PlayerStatus) -> str:
    return {
        tournament.PlayerStatus.CHECKED_IN: "✅",
        tournament.PlayerStatus.DISQUALIFIED: "⛔️",
        tournament.PlayerStatus.PLAYING: "▶️",
        tournament.PlayerStatus.MISSING_DECK: "📄",
        tournament.PlayerStatus.CHECKIN_REQUIRED: "⌛️",
        tournament.PlayerStatus.WAITING: "",
        tournament.PlayerStatus.CHECKED_OUT: "❌",
    }[status]


class PlayersList(BaseCommand):
    """Players list with status icon - useful to sheperd the flock."""

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Display the list of players"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.BOOLEAN,
            name="public",
            description="Display the list publicly (default is private)",
            is_required=False,
        ),
    ]

    async def __call__(self, public: bool = False) -> None:
        if public or self._is_judge_channel():
            flag = hikari.UNDEFINED
        else:
            flag = hikari.MessageFlag.EPHEMERAL
        players = sorted(self.tournament.players.iter_players(), key=lambda p: p.number)
        embed = hikari.Embed(title=f"Players ({self.tournament.players.count})")
        player_lines = []
        for p in players:
            info = self.tournament.player_info(p.vekn)
            player_lines.append(
                f"- {status_icon(info.status)} {self._player_display(p.vekn)}"
            )
        embed.description = "\n".join(player_lines)
        embeds = _paginate_embed(embed)
        await self.create_or_edit_response(embeds=embeds, flags=flag)


class DownloadReports(BaseCommand):
    """Download reports. Archon-compatible reports if VEKN ID# were required."""

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Get CSV reports for the tournament"

    async def __call__(self) -> None:
        if self.tournament.state == tournament.TournamentState.PLAYING:
            raise CommandFailed("Finish the current round before exporting results")
        self.deferred(hikari.MessageFlag.EPHEMERAL)
        reports = [self._build_results_csv()]
        if self.tournament.flags & tournament.TournamentFlag.VEKN_REQUIRED:
            reports.append(self._build_methuselahs_csv())
            reports.extend(f for f in self._build_rounds_csvs())
            if self.tournament.state == tournament.TournamentState.FINISHED:
                reports.append(self._build_finals_csv())
        await self.create_or_edit_response(
            embed=hikari.Embed(
                title="Reports",
                description=(
                    "Download those file and store them safely before you close "
                    "the tournament."
                ),
            ),
            attachments=reports,
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    def _build_csv(self, filename: str, it: Iterable[str], columns=None):
        data = io.StringIO()
        writer = csv.writer(data)
        if columns:
            writer.writerow(columns)
        writer.writerows(it)
        data = io.BytesIO(data.getvalue().encode("utf-8"))
        return hikari.Bytes(data, filename, mimetype="text/csv")

    def _build_results_csv(self):
        winner, ranking = self.tournament.standings()
        data = []
        for rank, vekn, score in ranking:
            if vekn in self.tournament.dropped:
                rank = "DQ"
            info = self.tournament.player_info(vekn)
            data.append(
                [
                    info.player.number,
                    info.player.vekn,
                    info.player.name,
                    info.rounds,
                    score.gw,
                    score.vp,
                    info.player.seed or "",
                    rank,
                ]
            )
        return self._build_csv(
            "Report.csv",
            data,
            columns=[
                "Player Num",
                "V:EKN Num",
                "Name",
                "Games Played",
                "Games Won",
                "Total VPs",
                "Finals Position",
                "Rank",
            ],
        )

    def _player_first_last_name(self, player):
        name = player.name.split(" ", 1)
        if len(name) < 2:
            name.append("")
        return name

    def _build_methuselahs_csv(self):
        data = []
        for player in sorted(
            self.tournament.players.iter_players(), key=lambda p: p.number
        ):
            name = self._player_first_last_name(player)
            info = self.tournament.player_info(player.vekn)
            data.append(
                [
                    player.number,
                    name[0],
                    name[1],
                    "",  # country
                    player.vekn,
                    info.rounds,
                    "DQ" if info.drop else "",
                ]
            )
        return self._build_csv("Methuselahs.csv", data)

    def _build_rounds_csvs(self):
        for i, round in enumerate(self.tournament.rounds, 1):
            if not round.results:
                break
            if round.finals:
                break
            data = []
            for j, table in enumerate(round.seating, 1):
                for number in table:
                    player = self.tournament.players[number]
                    name = self._player_first_last_name(player)
                    data.append(
                        [
                            number,
                            name[0],
                            name[1],
                            j,
                            round.results.get(player.number, tournament.Score()).vp,
                        ]
                    )
                if len(table) < 5:
                    data.append(["", "", "", "", ""])
            yield self._build_csv(f"Round-{i}.csv", data)

    def _build_finals_csv(self):
        data = []
        round = self.tournament.rounds[-1]
        if not round.finals:
            raise RuntimeError("No finals")
        players = sorted(
            [self.tournament.players[n] for n in round.seating[0]], key=lambda p: p.seed
        )
        for player in players:
            name = self._player_first_last_name(player)
            data.append(
                [
                    player.number,
                    name[0],
                    name[1],
                    1,  # table
                    player.seed,  # seat
                    round.results.get(player.vekn, tournament.Score()).vp,
                ]
            )
        return self._build_csv("Finals.csv", data)


class Raffle(BaseCommand):
    """Could come in handy: select a count of players randomly."""

    UPDATE = False
    ACCESS = CommandAccess.JUDGE
    DESCRIPTION = "JUDGE: Select random players"
    OPTIONS = [
        hikari.CommandOption(
            type=hikari.OptionType.INTEGER,
            name="count",
            description="JUDGE: Number of players to select (defaults to one)",
            is_required=False,
        ),
    ]

    async def __call__(self, count: Optional[int] = None) -> None:
        await self.deferred()
        count = count or 1
        if count < 1 or count > self.tournament.players.count:
            raise CommandFailed(
                "Invalid count: choose a number between 1 and "
                f"{self.tournament.players.count}"
            )
        players = random.sample(
            [
                p.vekn
                for p in self.tournament.players.iter_players()
                if p.vekn and p.vekn not in self.tournament.dropped
            ],
            k=count,
        )
        embed = hikari.Embed(
            title="Raffle Winners",
            description="\n".join(f"- {self._player_display(p)}" for p in players),
        )
        await asyncio.sleep(3)
        await self.create_or_edit_response(embed=embed)
