import shlex
from argparse import ArgumentError, Namespace

import structlog
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from disnake.ext.commands import Context
from whenever import PlainDateTime

from bio_jardas.exceptions import ParserError
from bio_jardas.observability import bind_attempted_command, bind_error_cause
from bio_jardas.parser import DiscordArgumentParser
from bio_jardas.utils import shlex_command_has_help

logger = structlog.stdlib.get_logger()


def parse_cron_trigger(expr: str) -> CronTrigger:
    try:
        return CronTrigger.from_crontab(expr)
    except ValueError as exc:
        raise ParserError(f"Invalid cron: {exc}")


def parse_datetime_trigger(timestamp: str) -> DateTrigger:
    try:
        datetime = PlainDateTime.parse_iso(timestamp)
        zoned_dt = datetime.assume_system_tz(disambiguate="earlier")
        return DateTrigger(run_date=zoned_dt.py_datetime())
    except ValueError as exc:
        raise ParserError(f"Invalid iso timestamp: {exc}")


async def parse_shell_like_command(
    command: str, parser: DiscordArgumentParser, context: Context
) -> Namespace | None:
    # TODO: organize this somewhere else
    split_command = shlex.split(command)
    try:
        return parser.parse_args(split_command)
    except (ParserError, ArgumentError) as exc:
        bind_attempted_command(context)
        await context.reply(f"```{parser.format_usage()}\n{parser.format_help()}```")
        if shlex_command_has_help(split_command):
            await logger.ainfo("Helped with a command")
            return None
        bind_error_cause(str(exc))
        await logger.aerror("Exception parsing command")
        return None
