import uuid
from http import HTTPStatus
from logging import config as logging_config

import pytest
from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
pytestmark = pytest.mark.asyncio

PREFIX = '/api/v1/notify-email'


class TestNotifications:
    postfix = '/user-sign-up'
    user_id = str(uuid.uuid4())

    @pytest.mark.parametrize(
        'payload, expected_answer',
        [
            (
                    {
                        "user_id": user_id,
                        "user_email": "user@example.com",
                        "first_name": "string",
                        "last_name": "string"
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
                        "user_email": "user@example.com",
                        "first_name": "string",
                        "last_name": "string"
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
