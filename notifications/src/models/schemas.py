import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    content_id = Column(String,
                        ForeignKey('content.id',
                                   ondelete='CASCADE'),
                        nullable=False)
    routing_key = Column(String, nullable=False)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)
    failures = Column(Integer, default=0)
    last_notification_send = Column(DateTime, default=None)

    contents = relationship('NotificationContent',
                            back_populates='notifications')

    def __init__(self,
                 content_id: str,
                 routing_key: str,
                 status: str,
                 failures: int = 0,
                 last_notification_send: datetime | None = None) -> None:
        self.content_id = content_id
        self.status = status
        self.routing_key = routing_key
        self.failures = failures
        self.modified = datetime.utcnow()
        self.last_notification_send = last_notification_send

    def __repr__(self):
        return f'<Notification {self.content_id}>'


class NotificationContent(Base):
    __tablename__ = 'content'

    id = Column(String, primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    content = Column(String, nullable=True)

    notifications = relationship('Notification',
                                 back_populates='contents')

    def __init__(self,
                 _id: str,
                 content: str):
        self.id = _id
        self.content = content

    def __repr__(self):
        return f'<Content {self.content}>'


class NotificationsHistory(Base):
    __tablename__ = 'notifications_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID, nullable=True)
    user_email = Column(String, nullable=True)
    message_content = Column(String, nullable=True)
    html_content = Column(String, nullable=True)
    last_notification_send = Column(DateTime, default=None)

    def __init__(self,
                 user_id: str,
                 user_email: str,
                 message_content: str,
                 html_content: str,
                 last_notification_send: datetime | None = None) -> None:
        self.user_id = user_id
        self.user_email = user_email
        self.message_content = message_content
        self.html_content = html_content
        self.last_notification_send = last_notification_send

    def __repr__(self):
        return f'<History {self.user_id}>'
