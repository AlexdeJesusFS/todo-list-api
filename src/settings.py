from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )
    # valores default definidos para evitar erro [call-arg] do mypy
    # como valored de .env são definidos em tempo de execução são
    # invisíveis para o mypy
    DATABASE_URL: str = ''
    SECRET_KEY: str = ''
    ALGORITHM: str = ''
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
