from pydantic.schema import UUID

from models.model import Model


class RequestUserModel(Model):
    user_id: UUID
