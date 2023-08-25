import aiohttp
import pytest

from http import HTTPStatus
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/reviews'


@pytest.mark.xfail(reason="It fails if admin user doesn't exist in DB or "
                          "auth server isn't running.\n"
                          "The test suite passes only when executed as a class"
                          ", not as a separate test.")
class TestAddReview:
    postfix = '/add-review'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "review": "string"
                    },
                    {'status': HTTPStatus.CREATED,
                     'likes_amount': 0},
            ),
        ]
    )
    async def test_add_review(self,
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
                assert body['likes_amount'] == expected_answer['likes_amount']


class TestGetReview:
    postfix = ('/list-reviews'
               '?movie_id=3fa85f64-5717-4562-b3fc-2c963f66afa6')

    @pytest.mark.parametrize(
        'paginate, sort, expected_answer',
        [

            (
                    '',
                    '',
                    {'status': HTTPStatus.OK,
                     'likes_amount': 0},
            ),

            (
                    '&page_size=5&page_number=2',
                    '&sort=date',
                    {'status': HTTPStatus.OK,
                     'likes_amount': 0},
            ),

            (
                    '&page_size=5',
                    '&sort=-date',
                    {'status': HTTPStatus.OK,
                     'likes_amount': 0},
            ),
        ]
    )
    async def test_get_review(self,
                              session_client,
                              paginate,
                              sort,
                              expected_answer):
        url = settings.service_url + PREFIX + self.postfix + sort + paginate

        async with session_client.get(url) as response:
            assert response.status == expected_answer['status']
            body = await response.json()
            assert body[0]['likes_amount'] == expected_answer['likes_amount']


class TestLikeToReview:
    postfix = '/add-like-to-review'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "review_id": "14db81b9ef5d70ad9756d5cc"
                    },
                    {'status': HTTPStatus.BAD_REQUEST,
                     'detail': '14db81b9ef5d70ad9756d5cc review does not'
                               ' exist'},
            ),
        ]
    )
    async def test_add_like_to_review_negative(self,
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
                assert body['detail'] == expected_answer['detail']
