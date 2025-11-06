from sqlalchemy import URL

from insperion_api.settings.config import settings


class DatabaseConfig:
    def __init__(self) -> None:
        self.db_username = settings.db_username
        self.db_password = settings.db_password
        self.db_host = settings.db_host
        self.db_port = settings.db_port
        self.db_name = settings.db_name

    def build_db_url(self, async_driver: bool = False) -> URL:
        driver: str
        if not async_driver:
            driver = "postgresql"
        else:
            driver = "postgresql+asyncpg"
        url_object = URL.create(
            drivername=driver,
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )
        return url_object

    def build_url_as_string(self) -> str:
        return self.build_db_url().render_as_string(hide_password=False)
