"""Discord Bot."""
import logging
import os

import hikari
import krcg.vtes

from .commands import (
    APPLICATION,
    COMMANDS,
    COMMANDS_TO_REGISTER,
    COMPONENTS,
    CommandFailed,
    build_command_tree,
)

from . import db
from .tournament import Tournament


# ####################################################################### Logging config
logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="[%(levelname)7s] %(message)s",
)

# ####################################################################### Discord client
bot = hikari.GatewayBot(os.getenv("DISCORD_TOKEN") or "")
UPDATE = os.getenv("UPDATE")
RESET = os.getenv("RESET")

# ####################################################################### Init KRCG
krcg.vtes.VTES.load()


# ########################################################################### Bot events
@bot.listen()
async def on_ready(event: hikari.StartedEvent) -> None:
    """Login success informative log."""
    logger.info("Ready as %s", bot.get_me().username)
    await db.init()
    if not APPLICATION:
        APPLICATION.append(await bot.rest.fetch_application())
    application = APPLICATION[-1]
    commands = build_command_tree(bot.rest)
    try:
        registered_commands = await bot.rest.fetch_application_commands(
            application=application,
        )
        if UPDATE or set(c.name for c in commands) ^ set(
            c.name for c in registered_commands
        ):
            logger.info("Updating commands: %s", commands)
            registered_commands = await bot.rest.set_application_commands(
                application=application,
                commands=commands,
            )
    except hikari.ForbiddenError:
        logger.exception("Bot does not have commands permission")
        return
    except hikari.BadRequestError:
        logger.exception("Bot did not manage to update commands")
        return
    for command in registered_commands:
        try:
            COMMANDS[command.id] = COMMANDS_TO_REGISTER[command.name]
        except KeyError:
            logger.exception("Received unknow command %s", command)


@bot.listen()
async def on_connected(event: hikari.GuildAvailableEvent) -> None:
    """Connected to a guild."""
    logger.info("Logged in %s as %s", event.guild.name, bot.get_me().username)
    if not APPLICATION:
        APPLICATION.append(await bot.rest.fetch_application())
    if not RESET:
        return
    application = APPLICATION[-1]
    guild = event.guild
    if RESET:
        try:
            await bot.rest.set_application_commands(
                application=application,
                guild=guild,
                commands=[],
            )
        except hikari.ForbiddenError:
            logger.error("Bot does not have commands scope in guild %s", guild)
            return
        except hikari.BadRequestError:
            logger.error("Bot did not manage to update commands for guild %s", guild)
            return


async def _interaction_response(instance, interaction, content):
    """Default response to interaction (in case of error)"""
    if instance:
        await instance.create_or_edit_response(
            content, flags=hikari.MessageFlag.EPHEMERAL, embeds=[], components=[]
        )
    else:
        await interaction.create_initial_response(
            hikari.interactions.base_interactions.ResponseType.MESSAGE_CREATE,
            content,
            flags=hikari.MessageFlag.EPHEMERAL,
            embeds=[],
            components=[],
        )


@bot.listen()
async def on_interaction(event: hikari.InteractionCreateEvent) -> None:
    """Handle interactions (slash commands)."""
    logger.info("Interaction %s", event.interaction)
    if not event.interaction.guild_id:
        await _interaction_response(
            event.interaction,
            "Archon cannot be used in a private channel",
        )
        return
    if event.interaction.type == hikari.InteractionType.APPLICATION_COMMAND:
        try:
            instance = None
            command = COMMANDS[event.interaction.command_id]
            channel = event.interaction.get_channel()
            if not channel:
                channel = event.interaction.fetch_channel()
            async with db.tournament(
                event.interaction.guild_id,
                channel.parent_id,
                command.UPDATE,
            ) as (
                connection,
                tournament_data,
            ):
                instance = command(
                    bot,
                    connection,
                    Tournament(**tournament_data) if tournament_data else None,
                    event.interaction,
                    channel.id,
                    channel.parent_id,
                )
                await instance(
                    **{
                        option.name: option.value
                        for option in event.interaction.options or []
                    }
                )
        except CommandFailed as exc:
            logger.info("Command failed: %s - %s", event.interaction, exc.args)
            if exc.args:
                await _interaction_response(instance, event.interaction, exc.args[0])
        except Exception:
            logger.exception("Command failed: %s", event.interaction)
            await _interaction_response(instance, event.interaction, "Command error.")

    elif event.interaction.type == hikari.InteractionType.MESSAGE_COMPONENT:
        try:
            instance = None
            component_function = COMPONENTS[event.interaction.custom_id]
            channel = event.interaction.get_channel()
            if not channel:
                channel = event.interaction.fetch_channel()
            async with db.tournament(
                event.interaction.guild_id,
                channel.parent_id,
                component_function.UPDATE,
            ) as (
                connection,
                tournament_data,
            ):
                instance = component_function(
                    bot,
                    connection,
                    Tournament(**tournament_data) if tournament_data else None,
                    event.interaction,
                    channel.id,
                    channel.parent_id,
                )
                await instance()
        except CommandFailed as exc:
            logger.info("Command failed: %s - %s", event.interaction, exc.args)
            if exc.args:
                await _interaction_response(instance, event.interaction, exc.args[0])
        except Exception:
            logger.exception("Command failed: %s", event.interaction)
            await _interaction_response(instance, event.interaction, "Command error.")


def main():
    """Entrypoint for the Discord Bot."""
    bot.run()
