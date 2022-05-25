from dataclasses import dataclass, field

from discord import Client as DiscordClient, Guild, PermissionOverwrite

from discord_coworking.command.api import Result
from discord_coworking.command.category import CreateCategory
from discord_coworking.command.decorator import async_batch
from discord_coworking.command.guild import GuildCommand
from discord_coworking.command.role import CreateRole, DEFAULT_ROLE
from discord_coworking.command.text_channel import CreateTextChannel
from discord_coworking.command.voice_channel import CreateVoiceChannel

NO_PERMISSIONS = PermissionOverwrite(
    create_instant_invite=False,
    kick_members=False,
    ban_members=False,
    administrator=False,
    manage_channels=False,
    manage_guild=False,
    add_reactions=False,
    view_audit_log=False,
    priority_speaker=False,
    stream=False,
    read_messages=False,
    view_channel=False,
    send_messages=False,
    send_tts_messages=False,
    manage_messages=False,
    embed_links=False,
    attach_files=False,
    read_message_history=False,
    mention_everyone=False,
    external_emojis=False,
    use_external_emojis=False,
    view_guild_insights=False,
    connect=False,
    speak=False,
    mute_members=False,
    deafen_members=False,
    move_members=False,
    use_voice_activation=False,
    change_nickname=False,
    manage_nicknames=False,
    manage_roles=False,
    manage_permissions=False,
    manage_webhooks=False,
    manage_emojis=False,
)


class OpenOrganization:
    DEFAULT_OTHERS_PERMISSIONS = PermissionOverwrite(
        create_instant_invite=False,
        kick_members=False,
        ban_members=False,
        administrator=False,
        manage_channels=False,
        manage_guild=False,
        add_reactions=False,
        view_audit_log=False,
        priority_speaker=False,
        stream=True,
        read_messages=True,
        view_channel=True,
        send_messages=True,
        send_tts_messages=False,
        manage_messages=False,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        mention_everyone=False,
        external_emojis=False,
        use_external_emojis=False,
        view_guild_insights=False,
        connect=True,
        speak=True,
        mute_members=False,
        deafen_members=False,
        move_members=False,
        use_voice_activation=True,
        change_nickname=True,
        manage_nicknames=False,
        manage_roles=False,
        manage_permissions=False,
        manage_webhooks=False,
        manage_emojis=False,
    )

    DEFAULT_FORMER_PERMISSIONS = DEFAULT_OTHERS_PERMISSIONS

    DEFAULT_ADMIN_PERMISSIONS = PermissionOverwrite(
        create_instant_invite=True,
        kick_members=True,
        ban_members=False,
        administrator=False,
        manage_channels=True,
        manage_guild=False,
        add_reactions=True,
        view_audit_log=True,
        priority_speaker=True,
        stream=True,
        read_messages=True,
        view_channel=True,
        send_messages=True,
        send_tts_messages=True,
        manage_messages=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        mention_everyone=True,
        external_emojis=True,
        use_external_emojis=True,
        view_guild_insights=False,
        connect=True,
        speak=True,
        mute_members=True,
        deafen_members=True,
        move_members=True,
        use_voice_activation=True,
        change_nickname=True,
        manage_nicknames=False,
        manage_roles=False,
        manage_permissions=False,
        manage_webhooks=False,
        manage_emojis=False,
    )

    DEFAULT_ASSOCIATE_PERMISSIONS = PermissionOverwrite(
        create_instant_invite=True,
        kick_members=False,
        ban_members=False,
        administrator=False,
        manage_channels=False,
        manage_guild=False,
        add_reactions=True,
        view_audit_log=True,
        priority_speaker=False,
        stream=True,
        read_messages=True,
        view_channel=True,
        send_messages=True,
        send_tts_messages=True,
        manage_messages=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        mention_everyone=True,
        external_emojis=True,
        use_external_emojis=True,
        view_guild_insights=False,
        connect=True,
        speak=True,
        mute_members=True,
        deafen_members=False,
        move_members=False,
        use_voice_activation=True,
        change_nickname=True,
        manage_nicknames=False,
        manage_roles=False,
        manage_permissions=False,
        manage_webhooks=False,
        manage_emojis=False,
    )


class PrivateOrganization:
    DEFAULT_OTHERS_PERMISSIONS = PermissionOverwrite(
        create_instant_invite=False,
        kick_members=False,
        ban_members=False,
        administrator=False,
        manage_channels=False,
        manage_guild=False,
        add_reactions=False,
        view_audit_log=False,
        priority_speaker=False,
        stream=False,
        read_messages=False,
        view_channel=False,
        send_messages=False,
        send_tts_messages=False,
        manage_messages=False,
        embed_links=False,
        attach_files=False,
        read_message_history=False,
        mention_everyone=False,
        external_emojis=False,
        use_external_emojis=False,
        view_guild_insights=False,
        connect=False,
        speak=False,
        mute_members=False,
        deafen_members=False,
        move_members=False,
        use_voice_activation=False,
        change_nickname=False,
        manage_nicknames=False,
        manage_roles=False,
        manage_permissions=False,
        manage_webhooks=False,
        manage_emojis=False,
    )

    DEFAULT_ADMIN_PERMISSIONS = PermissionOverwrite(
        create_instant_invite=True,
        kick_members=True,
        ban_members=False,
        administrator=False,
        manage_channels=True,
        manage_guild=False,
        add_reactions=True,
        view_audit_log=True,
        priority_speaker=True,
        stream=True,
        read_messages=True,
        view_channel=True,
        send_messages=True,
        send_tts_messages=True,
        manage_messages=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        mention_everyone=True,
        external_emojis=True,
        use_external_emojis=True,
        view_guild_insights=False,
        connect=True,
        speak=True,
        mute_members=True,
        deafen_members=True,
        move_members=True,
        use_voice_activation=True,
        change_nickname=True,
        manage_nicknames=False,
        manage_roles=False,
        manage_permissions=False,
        manage_webhooks=False,
        manage_emojis=False,
    )

    DEFAULT_ASSOCIATE_PERMISSIONS = PermissionOverwrite(
        create_instant_invite=True,
        kick_members=False,
        ban_members=False,
        administrator=False,
        manage_channels=False,
        manage_guild=False,
        add_reactions=True,
        view_audit_log=True,
        priority_speaker=False,
        stream=True,
        read_messages=True,
        view_channel=True,
        send_messages=True,
        send_tts_messages=True,
        manage_messages=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        mention_everyone=True,
        external_emojis=True,
        use_external_emojis=True,
        view_guild_insights=False,
        connect=True,
        speak=True,
        mute_members=True,
        deafen_members=False,
        move_members=False,
        use_voice_activation=True,
        change_nickname=True,
        manage_nicknames=False,
        manage_roles=False,
        manage_permissions=False,
        manage_webhooks=False,
        manage_emojis=False,
    )

    DEFAULT_FORMER_PERMISSIONS = DEFAULT_OTHERS_PERMISSIONS


@dataclass()
class CreateOrganization(GuildCommand):
    name: str = None
    admin_text_rooms = ['management', ]
    admin_voice_rooms = ['Dome', ]
    private_text_rooms = ['general', ]
    private_voice_rooms = ['Main Room', ]
    friend_text_rooms = ['coffee', ]
    friend_voice_rooms = ['Coffee', 'Rest Room', ]
    open_text_rooms = []
    open_voice_rooms = ['Living Room', ]

    default_admin_permissions: PermissionOverwrite = field(default_factory=PermissionOverwrite)
    default_associate_permissions: PermissionOverwrite = field(default_factory=PermissionOverwrite)
    default_others_permissions: PermissionOverwrite = field(default_factory=PermissionOverwrite)
    default_former_permissions: PermissionOverwrite = field(default_factory=PermissionOverwrite)

    @async_batch
    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> Result:
        admin_role = await CreateRole(
            name=f'{self.name}\'s Admin',
        ).do_on_guild(client, guild)
        yield admin_role
        associate_role = await CreateRole(
            name=f'{self.name}\'s Associate',
            hoist=True,
        ).do_on_guild(client, guild)
        yield associate_role
        former_role = await CreateRole(
            name=f'{self.name}\'s Former Associate',
        ).do_on_guild(client, guild)
        yield former_role
        created_category = await CreateCategory(
            name=self.name,
            overwrites={
                admin_role.role: self.default_admin_permissions,
                associate_role.role: self.default_associate_permissions,
                former_role.role: self.default_former_permissions,
                DEFAULT_ROLE: self.default_others_permissions,
            }
        ).do_on_guild(client, guild)
        yield created_category

        for room_name in self.admin_voice_rooms:
            yield await CreateVoiceChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    associate_role.role: self.default_others_permissions,
                    former_role.role: NO_PERMISSIONS,
                    DEFAULT_ROLE: NO_PERMISSIONS,
                }
            ).do_on_guild(client, guild)
        for room_name in self.admin_text_rooms:
            yield await CreateTextChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    associate_role.role: self.default_others_permissions,
                    former_role.role: NO_PERMISSIONS,
                    DEFAULT_ROLE: NO_PERMISSIONS,
                }
            ).do_on_guild(client, guild)

        for room_name in self.private_voice_rooms:
            yield await CreateVoiceChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    associate_role.role: self.default_associate_permissions,
                    former_role.role: self.default_former_permissions,
                    DEFAULT_ROLE: self.default_others_permissions,
                }
            ).do_on_guild(client, guild)
        for room_name in self.private_text_rooms:
            yield await CreateTextChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    associate_role.role: self.default_associate_permissions,
                    former_role.role: self.default_former_permissions,
                    DEFAULT_ROLE: self.default_others_permissions,
                }
            ).do_on_guild(client, guild)

        for room_name in self.friend_voice_rooms:
            yield await CreateVoiceChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    associate_role.role: self.default_associate_permissions,
                    former_role.role: self.default_associate_permissions,
                    DEFAULT_ROLE: self.default_others_permissions,
                }
            ).do_on_guild(client, guild)
        for room_name in self.friend_text_rooms:
            yield await CreateTextChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    associate_role.role: self.default_associate_permissions,
                    former_role.role: self.default_associate_permissions,
                    DEFAULT_ROLE: self.default_others_permissions,
                }
            ).do_on_guild(client, guild)

        for room_name in self.open_voice_rooms:
            yield await CreateVoiceChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    DEFAULT_ROLE: self.default_associate_permissions,
                }
            ).do_on_guild(client, guild)
        for room_name in self.open_text_rooms:
            yield await CreateTextChannel(
                name=room_name,
                category=created_category.category,
                overwrites={
                    admin_role.role: self.default_admin_permissions,
                    DEFAULT_ROLE: self.default_associate_permissions,
                }
            ).do_on_guild(client, guild)

    @classmethod
    def open_organization(cls, name: str, **kwargs) -> 'CreateOrganization':
        return cls(
            name=name,
            **kwargs,
            default_admin_permissions=OpenOrganization.DEFAULT_ADMIN_PERMISSIONS,
            default_associate_permissions=OpenOrganization.DEFAULT_ASSOCIATE_PERMISSIONS,
            default_former_permissions=OpenOrganization.DEFAULT_FORMER_PERMISSIONS,
            default_others_permissions=OpenOrganization.DEFAULT_OTHERS_PERMISSIONS,
        )

    @classmethod
    def private_organization(cls, name: str, **kwargs) -> 'CreateOrganization':
        return cls(
            name=name,
            **kwargs,
            default_admin_permissions=PrivateOrganization.DEFAULT_ADMIN_PERMISSIONS,
            default_associate_permissions=PrivateOrganization.DEFAULT_ASSOCIATE_PERMISSIONS,
            default_former_permissions=PrivateOrganization.DEFAULT_FORMER_PERMISSIONS,
            default_others_permissions=PrivateOrganization.DEFAULT_OTHERS_PERMISSIONS,
        )
