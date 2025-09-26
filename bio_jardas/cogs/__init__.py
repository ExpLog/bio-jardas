from .config import ConfigCog
from .hug import HugCog
from .reply import ReplyCog
from .vocabulary import VocabularyCog

ALL_COGS = [ConfigCog, HugCog, ReplyCog, VocabularyCog]
__all__ = ["ALL_COGS", "ConfigCog", "HugCog", "ReplyCog", "VocabularyCog"]
