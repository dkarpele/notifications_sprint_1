import aiohttp
import asyncio

import pytest_asyncio

pytest_plugins = "tests.functional.fixtures.get_data"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def session_client():
    client = aiohttp.ClientSession()
    yield client
    await client.close()
