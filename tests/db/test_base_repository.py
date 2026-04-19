import pytest
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.domains.game.models import Score
from bio_jardas.domains.game.repositories import ScoreRepository


# We chose Score for these base CRUD tests because we had to choose one model
# to verify the generic repository behavior, and Score is one of the simplest
# models in the codebase (no audit fields).
@pytest.fixture
async def score_repo(session: AsyncSession) -> ScoreRepository:
    return ScoreRepository(session)


async def test_crud_add(score_repo: ScoreRepository) -> None:
    score = Score(user_snowflake_id=1, name="game1", highest=10)
    added = await score_repo.add(score)

    assert added.id is not None
    assert added.user_snowflake_id == 1

    # Verify persistence
    fetched = await score_repo.get_by_id(added.id)
    assert fetched.name == "game1"
    assert fetched.highest == 10


async def test_crud_add_many(score_repo: ScoreRepository) -> None:
    scores = [
        Score(user_snowflake_id=1, name="game1", highest=10),
        Score(user_snowflake_id=2, name="game1", highest=20),
    ]
    added = await score_repo.add_many(scores)

    assert len(added) == 2
    assert added[0].id is not None
    assert added[1].id is not None

    # Verify persistence
    fetched = await score_repo.get_many(Score.user_snowflake_id.in_([1, 2]))
    assert len(fetched) == 2
    assert {s.highest for s in fetched} == {10, 20}


async def test_crud_get_one(score_repo: ScoreRepository) -> None:
    score = Score(user_snowflake_id=1, name="game1")
    await score_repo.add(score)

    fetched = await score_repo.get_one(Score.user_snowflake_id == 1)
    assert fetched.id == score.id

    with pytest.raises(EntityNotFoundError):
        await score_repo.get_one(Score.user_snowflake_id == 2)


async def test_crud_get_one_or_none(score_repo: ScoreRepository) -> None:
    score = Score(user_snowflake_id=1, name="game1")
    await score_repo.add(score)

    assert (await score_repo.get_one_or_none(Score.user_snowflake_id == 1)) is not None
    assert (await score_repo.get_one_or_none(Score.user_snowflake_id == 2)) is None


async def test_crud_delete(score_repo: ScoreRepository) -> None:
    score = Score(user_snowflake_id=1, name="game1")
    await score_repo.add(score)

    success = await score_repo.delete(score.id)
    assert success is True

    fetched = await score_repo.get_one_or_none(Score.id == score.id)
    assert fetched is None


async def test_crud_delete_many(score_repo: ScoreRepository) -> None:
    scores = [
        Score(user_snowflake_id=1, name="game1"),
        Score(user_snowflake_id=2, name="game1"),
        Score(user_snowflake_id=3, name="game1"),
    ]
    await score_repo.add_many(scores)
    ids = [s.id for s in scores]

    deleted_count = await score_repo.delete_many(ids[:2])
    assert deleted_count == 2

    remaining = await score_repo.get_many(Score.id.in_(ids))
    assert len(remaining) == 1
    assert remaining[0].id == ids[2]


async def test_crud_delete_where(score_repo: ScoreRepository) -> None:
    scores = [
        Score(user_snowflake_id=1, name="game1"),
        Score(user_snowflake_id=2, name="game1"),
        Score(user_snowflake_id=1, name="game2"),
    ]
    await score_repo.add_many(scores)

    deleted_count = await score_repo.delete_where(Score.user_snowflake_id == 1)
    assert deleted_count == 2

    remaining = await score_repo.get_many()
    assert len(remaining) == 1
    assert remaining[0].name == "game1"
    assert remaining[0].user_snowflake_id == 2


async def test_crud_exists(score_repo: ScoreRepository) -> None:
    score = Score(user_snowflake_id=1, name="game1")
    await score_repo.add(score)

    assert await score_repo.exists(Score.user_snowflake_id == 1) is True
    assert await score_repo.exists(Score.user_snowflake_id == 2) is False


async def test_crud_get_many_pagination(score_repo: ScoreRepository) -> None:
    scores = [Score(user_snowflake_id=i, name="game") for i in range(10)]
    await score_repo.add_many(scores)

    page1 = await score_repo.get_many(
        limit=3, offset=0, order_by=[Score.user_snowflake_id]
    )
    assert len(page1) == 3
    assert [s.user_snowflake_id for s in page1] == [0, 1, 2]

    page2 = await score_repo.get_many(
        limit=3, offset=3, order_by=[Score.user_snowflake_id]
    )
    assert len(page2) == 3
    assert [s.user_snowflake_id for s in page2] == [3, 4, 5]


async def test_crud_get_many_order_by(score_repo: ScoreRepository) -> None:
    scores = [
        Score(user_snowflake_id=1, name="game", highest=100),
        Score(user_snowflake_id=2, name="game", highest=50),
        Score(user_snowflake_id=3, name="game", highest=150),
    ]
    await score_repo.add_many(scores)

    asc = await score_repo.get_many(order_by=[Score.highest.asc()])
    assert [s.highest for s in asc] == [50, 100, 150]

    desc = await score_repo.get_many(order_by=[Score.highest.desc()])
    assert [s.highest for s in desc] == [150, 100, 50]


async def test_crud_get_by_id_not_found(score_repo: ScoreRepository) -> None:
    with pytest.raises(EntityNotFoundError):
        await score_repo.get_by_id(999999)


async def test_crud_get_one_multiple_results(score_repo: ScoreRepository) -> None:
    scores = [
        Score(user_snowflake_id=1, name="game1"),
        Score(user_snowflake_id=1, name="game2"),
    ]
    await score_repo.add_many(scores)

    with pytest.raises(MultipleResultsFound):
        await score_repo.get_one(Score.user_snowflake_id == 1)


async def test_crud_get_one_or_none_multiple_results(
    score_repo: ScoreRepository,
) -> None:
    scores = [
        Score(user_snowflake_id=1, name="game1"),
        Score(user_snowflake_id=1, name="game2"),
    ]
    await score_repo.add_many(scores)

    with pytest.raises(MultipleResultsFound):
        await score_repo.get_one_or_none(Score.user_snowflake_id == 1)
