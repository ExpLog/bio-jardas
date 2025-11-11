import shlex
from argparse import ArgumentError

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import FromDishka
from disnake.ext.commands import Context, check, group
from structlog.contextvars import get_merged_contextvars

from bio_jardas import emojis
from bio_jardas.cogs import BaseCog
from bio_jardas.command_checks import is_bot_owner
from bio_jardas.dependency_injection import cog_inject
from bio_jardas.domains.game.jobs import REMOVE_SHADOW_BAN_JOB_PREFIX
from bio_jardas.domains.message.services import MessageService
from bio_jardas.domains.schedule.jobs import random_scheduled_message
from bio_jardas.domains.schedule.parsers import schedule_message_parser
from bio_jardas.exceptions import ParserError
from bio_jardas.observability import bind_attempted_command, bind_error_cause
from bio_jardas.shortcuts import channel_id
from bio_jardas.utils import command_string, shlex_command_has_help

logger = structlog.stdlib.get_logger()


class ScheduleCog(BaseCog):
    @group(name="schedule", invoke_without_command=True, case_insensitive=True)
    @check(is_bot_owner)
    async def schedule(self, context: Context) -> None:
        # TODO: add some help text
        await context.reply("WIP help")

    @schedule.command("message")
    @check(is_bot_owner)
    @cog_inject
    async def schedule_message(
        self,
        context: Context,
        *,
        command: str,
        message_service: FromDishka[MessageService],
        scheduler: FromDishka[AsyncIOScheduler],
    ) -> None:
        parser = schedule_message_parser(command_string(context))
        split_command = shlex.split(command)
        try:
            args = parser.parse_args(split_command)
        except (ParserError, ArgumentError) as exc:
            bind_attempted_command(context)
            if shlex_command_has_help(split_command):
                await logger.ainfo("Helped with a command")
                return
            bind_error_cause(str(exc))
            await logger.aerror("Exception parsing command")
            await context.reply(f"{parser.format_usage()}\n{parser.format_help()}")
            return

        message_group_name = args.message_group
        message_group_exists = await message_service.message_group_exists(
            message_group_name=message_group_name
        )
        if not message_group_exists:
            await logger.aerror(
                "Message group doesn't exist", message_group_name=message_group_name
            )
            await context.message.add_reaction(emojis.FAILURE)
            await context.reply(f"Message group {message_group_name} doesn't exist.")
            return

        job = scheduler.add_job(
            random_scheduled_message,
            trigger=args.cron,
            args=[
                message_group_name,
                channel_id(context),
                get_merged_contextvars(logger),
            ],
            id=args.id,
            misfire_grace_time=60 * 5,
            coalesce=True,
            replace_existing=True,
        )
        await context.reply(f"Job scheduled: {job}")

    @schedule.command("list")
    @check(is_bot_owner)
    @cog_inject
    async def schedule_list(
        self,
        context: Context,
        *,
        scheduler: FromDishka[AsyncIOScheduler],
    ) -> None:
        jobs = scheduler.get_jobs()
        if not jobs:
            await context.send("No scheduled jobs")
            return

        message_parts = []
        for job in jobs:
            if REMOVE_SHADOW_BAN_JOB_PREFIX in job.id:
                continue
            part = f"id={job.id}, next_run_time={job.next_run_time}"
            message_parts.append(part)

        message = "\n".join(message_parts)
        await context.reply(message)

    @schedule.command("remove")
    @check(is_bot_owner)
    @cog_inject
    async def schedule_remove(
        self,
        context: Context,
        *,
        job_id: str,
        scheduler: FromDishka[AsyncIOScheduler],
    ) -> None:
        job = scheduler.get_job(job_id)
        if not job or REMOVE_SHADOW_BAN_JOB_PREFIX in job.id:
            await logger.ainfo("Failed to remove scheduled job")
            await context.message.add_reaction(emojis.FAILURE)
            await context.reply("This job doesn't exist", job_id=job_id)

        await logger.ainfo("Removed scheduled job", job_id=job_id)
        job.remove()
        await context.message.add_reaction(emojis.SUCCESS)
