# mypy: disable-error-code="no-untyped-def"
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.settings import Settings

# evita erro Missing named argument "DATABASE_URL" for "Settings"Mypycall-arg
# erro exigi  DATABASE_URL na inicialização da classe
# apesar de não ser necessário
engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
