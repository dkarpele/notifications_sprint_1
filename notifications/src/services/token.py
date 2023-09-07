import http

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        """
        Returns access token for request taken from header Authorization
        :param request:
        :return:
        """
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        if not creds:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                                detail='Invalid authorization code.')
        if not creds.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED,
                                detail='Only Bearer token might be accepted')
        return creds.credentials


security_jwt = JWTBearer()
