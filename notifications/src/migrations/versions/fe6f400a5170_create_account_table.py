"""create account table

Revision ID: fe6f400a5170
Revises:
Create Date: 2023-08-28 20:55:50.676334

"""
from typing import Sequence, Union

from alembic import op

from models.schemas import Notification, NotificationContent, \
    NotificationsHistory

# revision identifiers, used by Alembic.
revision: str = 'fe6f400a5170'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notifications',
        Notification.id.expression,
        Notification.content_id.expression,
        Notification.routing_key.expression,
        Notification.status.expression,
        Notification.last_notification_send.expression,
        Notification.failures.expression,
        Notification.created_at.expression,
        Notification.modified.expression,
    )

    op.create_table(
        'content',
        NotificationContent.id.expression,
        NotificationContent.content.expression
    )

    op.create_table(
        'notifications-history',
        NotificationsHistory.id.expression,
        NotificationsHistory.user_id.expression,
        NotificationsHistory.user_email.expression,
        NotificationsHistory.message.expression
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('content')
    op.drop_table('notifications-history')
