import aiohttp
import pytest

from http import HTTPStatus
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/likes'


@pytest.mark.xfail(reason="It fails if admin user doesn't exist in DB or "
                          "auth server isn't running.\n"
                          "The test suite passes only when executed as a class"
                          ", not as a separate test.")
class TestAddLike:
    @pytest.mark.parametrize(
        'postfix, payload, expected_answer',
        [
            (
                    '/dislike',
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    },
                    {'status': HTTPStatus.CREATED,
                     'rating': 0},
            ),
            (
                    '/like',
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    },
                    {'status': HTTPStatus.CREATED,
                     'rating': 10},
            ),

        ]
    )
    async def test_set_like(self,
                            get_token,
                            postfix,
                            payload,
                            expected_answer):
        url = settings.service_url + PREFIX + postfix
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.post(url, json=payload) as response:
                assert response.status == expected_answer['status']

                body = await response.json()
                assert 'user_id' in body.keys()
                assert body['rating'] == expected_answer['rating']


class TestGetAvgMovieRating:
    @pytest.mark.parametrize(
        'postfix, expected_answer',
        [
            (
                    '/avg-movie-rating'
                    '?movie_id=3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    {'status': HTTPStatus.OK,
                     'avg_rating': 10},
            ),
        ]
    )
    async def test_get_rating(self,
                              session_client,
                              postfix,
                              expected_answer):
        url = settings.service_url + PREFIX + postfix

        async with session_client.get(url) as response:
            assert response.status == expected_answer['status']
            body = await response.json()
            assert body['avg_rating'] == expected_answer['avg_rating']


class TestCountLikesDislikesMovie:
    @pytest.mark.parametrize(
        'postfix, expected_answer',
        [
            (
                    '/likes-dislikes-count-movie'
                    '?movie_id=3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    {'status': HTTPStatus.OK,
                     'likes_count': 1},
            ),
        ]
    )
    async def test_get_likes_count(self,
                                   session_client,
                                   postfix,
                                   expected_answer):
        url = settings.service_url + PREFIX + postfix

        async with session_client.get(url) as response:
            assert response.status == expected_answer['status']
            body = await response.json()
            assert body['likes_count'] == expected_answer['likes_count']


@pytest.mark.xfail(reason="It fails if admin user doesn't exist in DB or "
                          "auth server isn't running.\n"
                          "The test suite passes only when executed as a class"
                          ", not as a separate test.")
class TestDeleteLike:
    @pytest.mark.parametrize(
        'postfix, payload, expected_answer',
        [
            (
                    '/like',
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    },
                    {'status': HTTPStatus.NO_CONTENT},
            ),
        ]
    )
    async def test_delete_like(self,
                               get_token,
                               postfix,
                               payload,
                               expected_answer):
        url = settings.service_url + PREFIX + postfix
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        async with aiohttp.ClientSession(headers=header) as session:
            async with session.delete(url, json=payload) as response:
                assert response.status == expected_answer['status']
