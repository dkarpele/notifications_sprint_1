import aiohttp
import pytest

from http import HTTPStatus
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/views'


@pytest.mark.xfail(reason="It fails if admin user doesn't exist in DB or "
                          "auth server isn't running")
class TestSendTimeframe:
    postfix = '/send-movie-time'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "begin_time": "2023-08-03T10:51:23.431Z",
                        "end_time": "2023-08-03T10:51:23.431Z"
                    },
                    {'status': HTTPStatus.CREATED},
            ),
        ]
    )
    async def test_send_time_frame(self,
                                   get_token,
                                   payload,
                                   expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.post(url, json=payload) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                assert 'user_id' in body.keys()

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "begin_time": "2023-08-03T10:51:23.431Z",
                        "end_time": "2023-08-03T10:51:23.431Z"
                    },
                    {'status': HTTPStatus.UNAUTHORIZED,
                     'detail': 'Could not validate credentials'},
            ),
        ]
    )
    async def test_send_time_frame_expired_token(self,
                                                 payload,
                                                 expected_answer):
        url = settings.service_url + PREFIX + self.postfix

        access_token = 'bad-token'
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.post(url, json=payload) as response:
                body = await response.json()
                assert response.status == expected_answer['status']
                assert body['detail'] == expected_answer['detail']
