from models.model import Model


class NotificationsHistoryModel(Model):
    user_email: str
    message: dict
