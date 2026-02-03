from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lovely_bot"
    ids_passwords_path: str = "ids_passwords.txt"

    class Config:
        env_file = ".env"


settings = Settings()
