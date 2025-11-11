from bio_jardas.domains.schedule.utils import parse_cron
from bio_jardas.parser import DiscordArgumentParser


def schedule_message_parser(command_string: str) -> DiscordArgumentParser:
    parser = DiscordArgumentParser(prog=command_string)
    parser.add_argument(
        "--cron",
        type=parse_cron,
        required=True,
        help="cron expression (5-6 fields)",
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
