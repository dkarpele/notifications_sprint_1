from logging import config as logging_config

from core.logger import LOGGING
from dotenv import load_dotenv
from pydantic import Field, BaseSettings

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
load_dotenv()


class MainConf(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class Settings(MainConf):
    host: str = Field(..., env='HOST_NOTIFICATION_API')
    port: int = Field(..., env='PORT_NOTIFICATION_API')
    host_auth: str = Field(..., env='HOST_AUTH')
    port_auth: int = Field(..., env='PORT_AUTH')


settings = Settings()


class MongoCreds(MainConf):
    host: str = Field(..., env="MONGO_HOST")
    port: str = Field(..., env="MONGO_PORT")
    user: str = Field(default=None, env="MONGO_INITDB_ROOT_USERNAME")
    password: str = Field(default=None, env="MONGO_INITDB_ROOT_PASSWORD")
    db: str = Field(..., env="MONGO_INITDB_DATABASE")


mongo_settings = MongoCreds()


class RabbitCreds(MainConf):
    rabbit_host: str = Field(..., env="RABBIT_HOST")
    rabbit_port: str = Field(..., env="RABBIT_PORT")
    rabbit_user: str = Field(..., env="RABBIT_USER")
    rabbit_pass: str = Field(..., env="RABBIT_PASS")

    def get_amqp_uri(self):
        return f"amqp://{self.rabbit_user}"\
                f":{self.rabbit_pass}"\
                f"@{self.rabbit_host}"\
                f":{self.rabbit_port}/"


rabbit_settings = RabbitCreds()


class CronSettings:
    likes_for_reviews: dict = {
        'hour': 19,
        'minute': 45,
        'second': 20,
        'timezone': 'UTC'
    }


cron_settings = CronSettings()
