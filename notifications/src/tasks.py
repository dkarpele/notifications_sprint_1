from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import cron_settings
from schedule.notifications import (likes_for_reviews,
                                    process_initiated_notifications)


async def jobs(job: AsyncIOScheduler) -> None:
    """
    List of jobs to schedule
    :param job: job name as a function
    :return:
    """
    job.add_job(likes_for_reviews,
                trigger='cron',
                hour=cron_settings.likes_for_reviews['hour'],
                minute=cron_settings.likes_for_reviews['minute'],
                second=cron_settings.likes_for_reviews['second'],
                timezone=cron_settings.likes_for_reviews['timezone'])

    job.add_job(process_initiated_notifications,
                trigger='interval',
                minute=cron_settings.process_notifications['minute'],)
