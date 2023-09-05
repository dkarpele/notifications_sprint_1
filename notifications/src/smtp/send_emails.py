import logging
import os
from datetime import datetime

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from core.config import email_settings
from models.schemas import Notification
from services.connections import get_db, DbHelpers
from services.exceptions import db_bad_request

load_dotenv()

current_path = os.path.dirname(__file__)
loader = FileSystemLoader(current_path)
env = Environment(loader=loader)


def id_exists_error(correlation_id: str):
    return logging.error(f'Message with correlation_id {correlation_id} '
                         f'has already been sent. Skipping sending.')


async def message_already_sent(correlation_id: str) -> bool | None:
    """
    Idempotency check. If the message with correlation_id is already in `Sent`
    status - ignore sending.
    :param correlation_id:
    :return:
    """
    db = await get_db()
    conn = DbHelpers(db)
    try:
        message = await conn.select(
            model=Notification,
            filter_=Notification.content_id.like(correlation_id))
        message = message.scalar_one()
        if message.status == 'Sent':
            return True
        return None
    except SQLAlchemyError as err:
        raise db_bad_request(err)


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


async def send_email_registered(data: dict, correlation_id: str):
    sent = await message_already_sent(correlation_id)
    if sent:
        return id_exists_error(correlation_id)

    template = env.get_template('registered.html')
    template_data = {
        "first_name": data['first_name'],
        "last_name": data['last_name']
    }
    output = template.render(**template_data)

    message = Mail(
        from_email=email_settings.from_email,
        to_emails=data['user_email'],
        subject='User registration confirmation',
        html_content=output)
    try:
        sg = SendGridAPIClient(email_settings.sg_api_key)
        response = sg.send(message)
        logging.info(f'Sendgrid status code: {response.status_code}')
        logging.info(f'Sendgrid message body: {response.body}')
        logging.info(f'Sendgrid headers:\n {response.headers}')
        await change_db_status(correlation_id)
    except Exception as e:
        logging.error(e)


async def send_email_likes(data: dict, correlation_id: str):
    sent = await message_already_sent(correlation_id)
    if sent:
        return id_exists_error(correlation_id)

    template = env.get_template('likes_for_review.html')
    for user_id in data:
        to_email = data[user_id][-1][0]
        template_data = {
            "first_name": data[user_id][-1][1],
            "last_name": data[user_id][-1][1],
            "reviews": data[user_id][:-1]
        }
        output = template.render(**template_data)

        message = Mail(
            from_email=email_settings.from_email,
            to_emails=to_email,
            subject='Your best comments today! ',
            html_content=output)
        try:
            sg = SendGridAPIClient(email_settings.sg_api_key)
            response = sg.send(message)
            logging.info(f'Sendgrid status code: {response.status_code}')
            logging.info(f'Sendgrid message body: {response.body}')
            logging.info(f'Sendgrid headers:\n {response.headers}')
            await change_db_status(correlation_id)
        except Exception as e:
            logging.error(e)
