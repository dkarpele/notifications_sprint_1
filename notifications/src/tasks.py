from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import cron_settings
from schedule.notifications import likes_for_reviews, \
    process_initiated_notifications, process_produced_notifications, \
    process_consumed_notifications


async def jobs(job: AsyncIOScheduler) -> None:
    """
    List of jobs to schedule
    :param job: job name as a function
    :return:
    """
    # await likes_for_reviews()
    # job.add_job(likes_for_reviews,
    #             trigger='cron',
    #             hour=cron_settings.likes_for_reviews['hour'],
    #             minute=cron_settings.likes_for_reviews['minute'],
    #             second=cron_settings.likes_for_reviews['second'],
    #             timezone=cron_settings.likes_for_reviews['timezone'])
    #
    # job.add_job(process_initiated_notifications,
    #             trigger='interval',
    #             minutes=cron_settings.process_initiated_notifications['minute']
    #             )
    #
    # job.add_job(process_produced_notifications,
    #             trigger='interval',
    #             minutes=cron_settings.process_produced_notifications['minute'])
    #
    # job.add_job(process_consumed_notifications,
    #             trigger='interval',
    #             minutes=cron_settings.process_consumed_notifications['minute'])
