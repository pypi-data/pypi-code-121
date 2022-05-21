import hikari


SPECTATE_TEXT = (
    hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.READ_MESSAGE_HISTORY
)
TEXT = (
    hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.SEND_MESSAGES_IN_THREADS
    | hikari.Permissions.ADD_REACTIONS
)
SPECTATE_VOICE = hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.CONNECT
VOICE = (
    hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
JUDGE_VOICE = (
    hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
    | hikari.Permissions.PRIORITY_SPEAKER
    | hikari.Permissions.MUTE_MEMBERS
    | hikari.Permissions.DEAFEN_MEMBERS
)
