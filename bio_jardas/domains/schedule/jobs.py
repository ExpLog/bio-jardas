import structlog
from dishka import FromDishka
from structlog.contextvars import bind_contextvars

from bio_jardas.bot import BioJardas
from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.dependency_injection import job_inject
from bio_jardas.domains.message.services import MessageService
from bio_jardas.domains.schedule.objects import EventReminder
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


async def event_reminder(reminder: EventReminder, structlog_context: dict) -> None:
    restore_context_to_logs(structlog_context)
    bind_contextvars(job="event_reminder")
    await _event_reminder(reminder)


@job_inject
async def _event_reminder(
    reminder: EventReminder,
    bot: FromDishka[BioJardas],
    message_service: FromDishka[MessageService],
) -> None:
    channel = bot.get_channel(reminder.channel_id)
    guild = bot.get_guild(reminder.guild_id)

    message = None
    if reminder.message_group_name:
        try:
            message = await message_service.random_message_from_group(
                reminder.message_group_name
            )
            bind_contextvars(message_group_id=message.group_id, message_id=message.id)
        except EntityNotFoundError as exc:
            bind_error_cause(str(exc.__cause__))
            await logger.aerror("Scheduled message failed")
            return

    link = reminder.event_link
    if not link:
        events = await guild.fetch_scheduled_events()
        matches = [e for e in events if e.name == reminder.event_name]
        matches = sorted(matches, key=lambda m: m.scheduled_start_time)
        if not matches:
            await logger.aerror(
                "No matching events found", event_name=reminder.event_name
            )
            return
        link = matches[0].url

    await logger.ainfo(
        "Sending event reminder", event_link=link, event_name=reminder.event_name
    )
    if message:
        await channel.send(message.text)
    await channel.send(link)
