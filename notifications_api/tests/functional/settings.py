from pydantic import BaseSettings, Field
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    service_url: str = Field('http://127.0.0.1:81', env='SERVICE_URL')
    auth_url: str = Field('http://127.0.0.1:80', env='AUTH_URL')

    class Config:
        env_file = '.env'


settings = Settings()
