import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

load_dotenv()

current_path = os.path.dirname(__file__)
loader = FileSystemLoader(current_path)
env = Environment(loader=loader)


def send_email_registered(data: dict):
    template = env.get_template('registered.html')
    template_data = {
        "first_name": data['first_name'],
        "last_name": data['last_name']
    }
    output = template.render(**template_data)

    message = Mail(
        from_email=f'{os.environ.get("FROM_EMAIL")}',
        to_emails=data['user_email'],
        subject='User registration confirmation',
        html_content=output)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logging.info(f'Sendgrid status code: {response.status_code}')
        logging.info(f'Sendgrid message body: {response.body}')
        logging.info(f'Sendgrid headers:\n {response.headers}')
    except Exception as e:
        logging.error(e)


def send_email_likes(data: dict):
    template = env.get_template('likes_for_review.html')
    for user_id in data:
        to_email = data[user_id][0]
        template_data = {
            "first_name": data[user_id][1],
            "last_name": data[user_id][2],
            "reviews": data[user_id][3:]
        }
        output = template.render(**template_data)

        message = Mail(
            from_email=f'{os.environ.get("FROM_EMAIL")}',
            to_emails=to_email,
            subject='Your best comments today! ',
            html_content=output)
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            logging.info(f'Sendgrid status code: {response.status_code}')
            logging.info(f'Sendgrid message body: {response.body}')
            logging.info(f'Sendgrid headers:\n {response.headers}')
        except Exception as e:
            logging.error(e)
