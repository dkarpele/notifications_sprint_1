from datetime import datetime

from models.model import Model


class NotificationsHistoryModel(Model):
    user_email: str
    message_content: dict
    html_content: str
    last_notification_send: datetime
