from sqlmodel import SQLModel


class FilterPage(SQLModel):
    offset: int = 0
    limit: int = 100
