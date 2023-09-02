from fastapi import HTTPException, status

credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
)

relogin_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your credentials expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
)

access_token_invalid_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired. Create new token with /refresh",
            headers={"WWW-Authenticate": "Bearer"},
)


wrong_username_or_password = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
)


def db_bad_request(err: Exception):
    return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err.__dict__['orig']),
            headers={"WWW-Authenticate": "Bearer"},
        )


def entity_doesnt_exist(err: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{err}",
        headers={"WWW-Authenticate": "Bearer"},
    )


too_many_requests = HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers={"WWW-Authenticate": "Bearer"},
)
