from disnake import Message as DiscordMessage
from disnake.ext.commands import Context


def author_id(obj: Context | DiscordMessage) -> int:
    return obj.author.id


def author_name(obj: Context | DiscordMessage) -> str:
    return obj.author.name


def channel_id(obj: Context | DiscordMessage) -> int:
    return obj.channel.id


def channel_name(obj: Context | DiscordMessage) -> str:
    return obj.channel.name


def guild_id(obj: Context | DiscordMessage) -> int:
    return obj.guild.id


def guild_name(obj: Context | DiscordMessage) -> str:
    return obj.guild.name


def command_qualified_name(obj: Context) -> str:
    return obj.command.qualified_name
