"""Обёртка над SQLAlchemy Async-engine + Session factory."""
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, \
    async_sessionmaker

engine: AsyncEngine | None = None
async_session: async_sessionmaker | None = None


async def init_db(dsn: str) -> None:
    global engine, async_session
    engine = create_async_engine(dsn, echo=False, pool_pre_ping=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
