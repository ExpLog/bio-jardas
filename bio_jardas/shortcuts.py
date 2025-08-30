from disnake import Message as DiscordMessage
from disnake.ext.commands import Context


def author_id(obj: Context | DiscordMessage) -> int:
    return obj.author.id


def channel_id(obj: Context | DiscordMessage) -> int:
    return obj.channel.id


def command_qualified_name(obj: Context) -> str:
    return obj.command.qualified_name
