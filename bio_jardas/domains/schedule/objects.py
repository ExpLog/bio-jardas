from dataclasses import dataclass


@dataclass(frozen=True)
class EventReminder:
    event_name: str | None
    event_link: str | None
    channel_id: int
    guild_id: int
    message_group_name: str | None
