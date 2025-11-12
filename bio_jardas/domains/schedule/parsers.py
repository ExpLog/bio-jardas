from bio_jardas.domains.schedule.utils import parse_cron_trigger, parse_datetime_trigger
from bio_jardas.parser import DiscordArgumentParser


def schedule_message_parser(command_string: str) -> DiscordArgumentParser:
    parser = DiscordArgumentParser(prog=command_string)
    parser.add_argument(
        "--cron",
        type=parse_cron_trigger,
        required=True,
        help="Cron expression (5-6 fields)",
    )
    parser.add_argument(
        "--message-group",
        "--mg",
        required=True,
        help="Name of the message group ($reply groups)",
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Unique schedule id. Will override schedules with same id.",
    )
    return parser


def schedule_event_reminder_parser(command_string: str) -> DiscordArgumentParser:
    parser = DiscordArgumentParser(prog=command_string)
    parser.add_argument(
        "--message-group",
        "--mg",
        required=False,
        help="Name of the message group ($reply groups). If given, a random message "
        "from this group will be included in the reminder.",
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Unique schedule id. Will override schedules with same id.",
    )
    time_group = parser.add_mutually_exclusive_group(required=True)
    time_group.add_argument(
        "--cron",
        type=parse_cron_trigger,
        help="Cron expression (5-6 fields). Use for recurring events.",
    )
    time_group.add_argument(
        "--timestamp",
        type=parse_datetime_trigger,
        help="Single timestamp. Use for one time events.",
    )
    event_group = parser.add_mutually_exclusive_group(required=True)
    event_group.add_argument(
        "--event-name",
        help="Event name. Use name for recurring events.",
    )
    event_group.add_argument(
        "--event-link", help="Event link. Use link for one time events."
    )
    return parser
