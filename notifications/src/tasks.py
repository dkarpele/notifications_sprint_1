from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import cron_settings
from schedule.notifications import likes_for_reviews


async def jobs(job: AsyncIOScheduler) -> None:
    job.add_job(likes_for_reviews,
                trigger='cron',
                hour=cron_settings.likes_for_reviews['hour'],
                minute=cron_settings.likes_for_reviews['minute'],
                second=cron_settings.likes_for_reviews['second'],
                timezone=cron_settings.likes_for_reviews['timezone'])
