# mypy: disable-error-code="no-untyped-def"

from sqlmodel import Session, create_engine

from src.settings import Settings

# evita erro Missing named argument "DATABASE_URL" for "Settings"Mypycall-arg
# erro exigi  DATABASE_URL na inicialização da classe
# apesar de não ser necessário
engine = create_engine(Settings().DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session
