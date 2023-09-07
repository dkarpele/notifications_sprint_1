import logging
from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from models.schemas import Notification, NotificationsHistory
from services.connections import get_db, DbHelpers
from services.exceptions import db_bad_request


class AbstractMessage(ABC):
    """
    Абстрактный класс для отправки сообщений.
    Описывает какие методы должны быть у подобных классов.
    """

    @abstractmethod
    async def send_registered(self,
                              data: dict,
                              correlation_id: str):
        pass

    @abstractmethod
    async def send_likes(self,
                         data: dict,
                         correlation_id: str):
        pass

    @staticmethod
    async def message_already_sent(correlation_id: str) -> bool | None:
        """
        Idempotency check. If the message with correlation_id is already in
        `Sent` status - ignore sending.
        :param correlation_id:
        :return:
        """
        db = await get_db()
        conn = DbHelpers(db)
        try:
            message = await conn.select(
                model=Notification,
                filter_=Notification.content_id == correlation_id)
            message = message.scalar_one()
            if message.status == 'Sent':
                return True
            return None
        except SQLAlchemyError as err:
            raise db_bad_request(err)

    @staticmethod
    async def change_db_status(correlation_id: str):
        db = await get_db()
        conn = DbHelpers(db)
        try:
            await conn.update(
                model=Notification,
                model_column=Notification.content_id,
                column_value=correlation_id,
                update_values={
                    'status': 'Sent',
                    'failures': 0,
                    'modified': datetime.utcnow(),
                    'last_notification_send': datetime.utcnow()})
        except SQLAlchemyError as err:
            raise db_bad_request(err)

    @staticmethod
    async def add_notifications_history(user_id: str,
                                        user_email: str,
                                        message_content: dict,
                                        html_content: str = '') -> None:
        db = await get_db()
        conn = DbHelpers(db)
        try:
            await conn.insert(
                NotificationsHistory(user_id,
                                     user_email,
                                     str(message_content),
                                     html_content,
                                     datetime.utcnow()
                                     )
            )

        except SQLAlchemyError as err:
            raise db_bad_request(err)

    @staticmethod
    def id_exists_error(correlation_id: str):
        return logging.error(f'Message with correlation_id {correlation_id} '
                             f'has already been sent. Skipping sending.')
