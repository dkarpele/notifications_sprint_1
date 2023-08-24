from pydantic import Field, EmailStr
from pydantic.schema import UUID

from models.model import Model


class RequestUserModel(Model):
    user_id: UUID
    user_email: EmailStr
    first_name: str = Field(...,
                            min_length=3,
                            max_length=50
                            )
    last_name: str = Field(...,
                           min_length=3,
                           max_length=50)
