import logging
import os

from jinja2 import Environment, FileSystemLoader
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from core.config import email_settings
from message_worker import AbstractMessage


class Email(AbstractMessage):
    current_path = os.path.dirname(__file__)
    loader = FileSystemLoader(current_path)
    env = Environment(loader=loader)

    async def send_registered(self, data: dict, correlation_id: str):
        sent = await self.message_already_sent(correlation_id)
        if sent:
            return self.id_exists_error(correlation_id)

        template = self.env.get_template('email_templates/'
                                         'email_registered.html')
        template_data = {
            "first_name": data['first_name'],
            "last_name": data['last_name']
        }
        output = template.render(**template_data)

        message = Mail(
            from_email=email_settings.from_email,
            to_emails=data['email'],
            subject='User registration confirmation',
            html_content=output)
        try:
            sg = SendGridAPIClient(email_settings.sg_api_key)
            response = sg.send(message)
            logging.info(f'Sendgrid status code: {response.status_code}')
            logging.info(f'Sendgrid message body: {response.body}')
            logging.info(f'Sendgrid headers:\n {response.headers}')
            await self.change_db_status(correlation_id)
            await self.add_notifications_history(data['id'],
                                                 data['email'],
                                                 template_data,
                                                 output)
        except Exception as e:
            logging.error(e)

    async def send_likes(self, data: dict, correlation_id: str):
        sent = await self.message_already_sent(correlation_id)
        if sent:
            return self.id_exists_error(correlation_id)

        template = self.env.get_template('email_templates/'
                                         'email_likes_for_review.html')
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
                await self.change_db_status(correlation_id)
                await self.add_notifications_history(user_id,
                                                     to_email,
                                                     template_data,
                                                     output)
            except Exception as e:
                logging.error(e)
