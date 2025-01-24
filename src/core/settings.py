from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    NAME: str

    def make_url(self, driver: str) -> str:
        return f"{driver}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def asyncpg_url(self) -> str:
        return self.make_url(driver="postgresql+asyncpg")

    @property
    def postgresql_url(self) -> str:
        return self.make_url(driver="postgresql")


class Settings(BaseSettings):
    DB: DatabaseConfig

    class Config:
        case_sensitive = True
        env_nested_delimiter = "__"
        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
