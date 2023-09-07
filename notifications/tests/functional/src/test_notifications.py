from http import HTTPStatus
from logging import config as logging_config

import aiohttp
import pytest
from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/notify-email'


class TestNotifications:
    postfix = '/user-sign-up'
    user_id = '6c0dd299-63ad-4fd0-89de-790b0789fb50'

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "user_id": user_id,
                    },
                    {'status': HTTPStatus.CREATED},
            ),
        ]
    )
    async def test_user_sign_up(self,
                                session_client,
                                payload,
                                expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        async with session_client.post(url, json=payload) as response:
            assert response.status == expected_answer['status']

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "user_id": user_id,
                    },
                    {'status': HTTPStatus.OK,
                     'user_email': 'admin@example.com'},
            ),
        ]
    )
    async def test_notifications_history(self,
                                         get_token,
                                         session_client,
                                         payload,
                                         expected_answer):
        access_data = {"username": "admin@example.com",
                       "password": "Secret123"}
        access_token = await get_token(access_data)
        header = {'Authorization': f'Bearer {access_token}'}

        url = settings.service_url + PREFIX + '/get-notifications-history'
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as response:
                assert response.status == expected_answer['status']
                body = await response.json()
                assert body[0]['user_email'] == expected_answer['user_email']

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "user_id": user_id,
                    },
                    {'status': HTTPStatus.BAD_REQUEST},
            ),
        ]
    )
    async def test_user_sign_up_duplicate(self,
                                          session_client,
                                          payload,
                                          expected_answer):
        url = settings.service_url + PREFIX + self.postfix
        async with session_client.post(url, json=payload) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert f'DETAIL:  Key (id)=({self.user_id}) already exists.' \
                   in body['detail']
