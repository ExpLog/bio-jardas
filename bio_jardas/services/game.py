from collections import defaultdict

from disnake.ext.commands import Bot

from bio_jardas.db.game import Score
from bio_jardas.db.repositories.game import ScoreRepository
from bio_jardas.domain_objects.game import GameName, Leaderboard


class GameService:
    def __init__(
        self,
        bot: Bot,
        score_repo: ScoreRepository,
    ):
        self.bot = bot
        self.score_repo = score_repo

    async def increase_score_by(
        self, user_snowflake_id: int, score_name: str, amount: int = 1
    ) -> Score:
        score = await self.score_repo.get_or_create(
            user_snowflake_id, score_name, for_update=True
        )
        score.increase_by(amount)
        return score

    async def reset_current_score(
        self, user_snowflake_id: int, score_name: str
    ) -> Score:
        score = await self.score_repo.get_or_create(
            user_snowflake_id, score_name, for_update=True
        )
        score.reset()
        return score

    async def leaderboard(self, score_names: list[GameName], places: int = 3):
        high_scores = await self.score_repo.get_high_scores(score_names, places)

        scores_by_name = defaultdict(list)
        for score in high_scores:
            scores_by_name[score.name].append(score)

        for name in scores_by_name:
            scores_by_name[name] = sorted(
                scores_by_name[name], key=lambda s: s.highest, reverse=True
            )

        return [
            Leaderboard(name, scores)
            for name in score_names
            if (scores := scores_by_name[name])
        ]
