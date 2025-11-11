import structlog
from dishka import FromDishka
from structlog.contextvars import bind_contextvars

from bio_jardas.bot import BioJardas
from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.dependency_injection import job_inject
from bio_jardas.domains.message.services import MessageService
from bio_jardas.observability import bind_error_cause, restore_context_to_logs

logger = structlog.stdlib.get_logger()


async def random_scheduled_message(
    message_group_name: str, channel_snowflake_id: int, structlog_context: dict
) -> None:
    restore_context_to_logs(structlog_context)
    bind_contextvars(job="random_scheduled_message")
    await _random_scheduled_message(message_group_name, channel_snowflake_id)


@job_inject
async def _random_scheduled_message(
    message_group_name: str,
    channel_snowflake_id: int,
    bot: FromDishka[BioJardas],
    message_service: FromDishka[MessageService],
) -> None:
    channel = bot.get_channel(channel_snowflake_id)
    try:
        message = await message_service.random_message_from_group(message_group_name)
    except EntityNotFoundError as exc:
        bind_error_cause(str(exc.__cause__))
        await logger.aerror("Scheduled message failed")
        return

    await logger.ainfo(
        "Sending scheduled message",
        message_group_id=message.group_id,
        message_id=message.id,
    )
    await channel.send(message.text)
