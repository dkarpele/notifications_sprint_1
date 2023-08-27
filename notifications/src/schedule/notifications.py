import aiohttp
import time

from aiohttp.web_exceptions import HTTPException
from fastapi import status as st

import core.config as conf
from services.connections import get_broker

routing_key = 'user-reporting.v1.likes-for-reviews'


async def likes_for_reviews():
    broker = await get_broker()
    data = await users_daily_likes()
    await broker.produce(routing_key=routing_key,
                         data=data,
                         correlation_id=round(time.time()))


async def users_daily_likes() -> dict:
    url = f'http://{conf.settings.host_ugc}:'\
          f'{conf.settings.port_ugc}'\
          f'/api/v1/reviews/users-daily-likes'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                body = await response.json()
                status_code = response.status
                if status_code != st.HTTP_200_OK:
                    raise HTTPException(
                        reason=body['detail'],
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return body
    except ConnectionRefusedError as err:
        raise HTTPException(reason=err.strerror)
    except aiohttp.ServerTimeoutError as err:
        raise HTTPException(reason=err.strerror)
    except aiohttp.TooManyRedirects as err:
        raise HTTPException(reason=err.strerror)
    except aiohttp.ClientError as err:
        raise HTTPException(reason=err.strerror)
