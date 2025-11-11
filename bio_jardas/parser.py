from argparse import ArgumentParser, HelpFormatter

from bio_jardas.exceptions import ParserError


class DiscordArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs["exit_on_error"] = False
        super().__init__(*args, formatter_class=NoWrapFormatter, **kwargs)

    def exit(self, status: int = 0, message: str | None = None) -> None:
        pass

    def error(self, message: str) -> None:
        raise ParserError(message.strip())

    def format_help(self):
        lines = []
        for action in self._actions:
            if action.option_strings:
                opts = ", ".join(action.option_strings)
            else:
                opts = action.metavar or action.dest
            if action.help:
                lines.append(f"{opts}: {action.help}")
            else:
                lines.append(opts)
        return "\n".join(lines)

    def print_help(self, file=None):
        pass


class NoWrapFormatter(HelpFormatter):
    def __init__(self, prog: str):
        super().__init__(prog, max_help_position=10**6, width=10**6)
