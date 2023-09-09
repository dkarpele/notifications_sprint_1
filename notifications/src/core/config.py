import logging
import os
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
    host_ugc: str = Field(..., env='HOST_UGC')
    port_ugc: int = Field(..., env='PORT_UGC')
    host_auth: str = Field(..., env='HOST_AUTH')
    port_auth: int = Field(..., env='PORT_AUTH')
    host_content: str = Field(..., env='HOST_CONTENT')
    port_content: int = Field(..., env='PORT_CONTENT')


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
        url = f"amqp://{self.rabbit_user}"\
                f":{self.rabbit_pass}"\
                f"@{self.rabbit_host}"\
                f":{self.rabbit_port}/"
        logging.info(f'Trying to connect to {url}')
        return url


amqp_settings = RabbitCreds()


class DBCreds(MainConf):
    dbname: str = Field(..., env="DB_NAME")
    user: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    host: str = Field(env="DB_HOST", default='127.0.0.1')
    port: int = Field(env="DB_PORT", default=5432)
    echo: bool = os.getenv('ENGINE_ECHO', 'False') == 'True'


db_settings = DBCreds()


class CronSettings:
    likes_for_reviews: dict = {
        'hour': 14,
        'minute': 39,
        'second': 55,
        'timezone': 'UTC'
    }
    process_initiated_notifications: dict = {
        'minute': 10,
    }
    process_produced_notifications: dict = {
        'minute': 5,
    }
    process_consumed_notifications: dict = {
        'minute': 5,
    }


cron_settings = CronSettings()


class EmailSettings(MainConf):
    sg_api_key: str = Field(..., env="SENDGRID_API_KEY")
    from_email: str = Field(..., env="FROM_EMAIL")


email_settings = EmailSettings()
