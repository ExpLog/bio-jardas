import pytest
from dishka import AsyncContainer

from bio_jardas.db.exceptions import EntityNotFoundError
from bio_jardas.domains.message.services import MessageService


@pytest.fixture
async def message_service(di_container: AsyncContainer) -> MessageService:
    return await di_container.get(MessageService)


async def test_add_vocabulary_group_not_found(message_service: MessageService) -> None:
    with pytest.raises(EntityNotFoundError):
        await message_service.add_vocabulary(
            text="some text",
            message_group_name="non_existent_group",
            user_id=123,
        )
