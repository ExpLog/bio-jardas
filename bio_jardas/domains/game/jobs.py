import structlog

from bio_jardas.bot import BioJardas
from bio_jardas.dependency_injection import di_container
from bio_jardas.observability import restore_context_to_logs

REMOVE_SHADOW_BAN_JOB_PREFIX = "remove_shadow_ban"

logger = structlog.stdlib.get_logger()


async def remove_shadow_ban(
    player_snowflake_id: int,
    guild_snowflake_id: int,
    shadow_role_snowflake_id: int,
    member_role_snowflake_id: int,
    logger_context: dict,
) -> None:
    restore_context_to_logs(logger_context)

    jardas = await di_container.get(BioJardas)

    await logger.ainfo("Initiating shadow ban reversal")
    try:
        guild = jardas.get_guild(guild_snowflake_id)
        player = guild.get_member(player_snowflake_id)
        shadow_role = guild.get_role(shadow_role_snowflake_id)
        member_role = guild.get_role(member_role_snowflake_id)
    except Exception:
        await logger.aexception("Failed to fetch data when removing shadow ban")
        return

    await player.add_roles(member_role)
    await player.remove_roles(shadow_role)
    await player.send("Your punishment has ended weakling!")
    await logger.ainfo("User shadow ban reversed")
