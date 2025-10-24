from .config import ConfigCog
from .game import GameCog
from .hug import HugCog
from .reply import ReplyCog
from .roast import RoastCog
from .vocabulary import VocabularyCog

ALL_COGS = [ConfigCog, GameCog, HugCog, ReplyCog, RoastCog, VocabularyCog]
__all__ = [
    "ALL_COGS",
    "ConfigCog",
    "GameCog",
    "HugCog",
    "ReplyCog",
    "RoastCog",
    "VocabularyCog",
]
