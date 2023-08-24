import aiohttp
import pytest

from http import HTTPStatus
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/bookmarks'


@pytest.mark.xfail(reason="It fails if admin user doesn't exist in DB or "
                          "auth server isn't running.\n"
                          "The test suite passes only when executed as a class"
                          ", not as a separate test.")
class TestBookmarks:
    postfix = '/bookmarks'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    },
                    {'status': HTTPStatus.CREATED},
            ),
        ]
    )
    async def test_set_bookmark(self,
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
                    },
                    {'status': HTTPStatus.UNAUTHORIZED,
                     'detail': 'Could not validate credentials'},
            ),
        ]
    )
    async def test_add_bookmark_expired_token(self,
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

    @pytest.mark.parametrize(
        'expected_answer',
        [
            {'status': HTTPStatus.OK,
             "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
        ]
    )
    async def test_get_bookmark(self,
                                get_token,
                                expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                assert body[0]['movie_id'] == expected_answer['movie_id']

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    },
                    {'status': HTTPStatus.NO_CONTENT},
            ),
        ]
    )
    async def test_delete_bookmark(self,
                                   get_token,
                                   payload,
                                   expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.delete(url, json=payload) as response:
                assert response.status == expected_answer['status']
