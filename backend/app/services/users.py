from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.repositories import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)
        self.session = session

    async def ensure(self, tg_id: int, username: str | None = None) -> None:
        await self.repo.ensure(tg_id, username=username)
        await self.session.commit()
