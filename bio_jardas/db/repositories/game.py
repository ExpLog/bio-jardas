from sqlalchemy import desc, func, select
from sqlalchemy.orm import aliased

from bio_jardas.db.game import Score
from bio_jardas.db.repositories.base import CRUDRepository


class ScoreRepository(CRUDRepository[Score]):
    model_type = Score

    async def get_or_create(
        self,
        user_snowflake_id: int,
        score_name: str,
        for_update: bool = False,
    ) -> Score:
        score = await self.get_one_or_none(
            Score.user_snowflake_id == user_snowflake_id,
            Score.name == score_name,
            for_update=for_update,
        )
        if not score:
            score = Score(
                user_snowflake_id=user_snowflake_id,
                name=score_name,
            )
            await self.add(score)
        return score

    async def get_high_scores(self, names: list[str], places: int) -> list[Score]:
        rank_column = (
            func.rank()
            .over(partition_by=Score.name, order_by=desc(Score.highest))
            .label("rank")
        )

        ranked_scores_subquery = (
            select(Score, rank_column).where(Score.name.in_(names)).subquery()
        )

        score_ranked = aliased(Score, ranked_scores_subquery)
        query = select(score_ranked).where(ranked_scores_subquery.c.rank <= places)

        result = await self.session.execute(query)
        return list(result.scalars().all())
