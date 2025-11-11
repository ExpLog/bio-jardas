from apscheduler.triggers.cron import CronTrigger

from bio_jardas.exceptions import ParserError


def parse_cron(expr: str) -> CronTrigger:
    try:
        return CronTrigger.from_crontab(expr)
    except ValueError as exc:
        raise ParserError(f"Invalid cron: {exc}")
