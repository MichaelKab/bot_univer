import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


# Команда /notify для создания уведомления
async def notify(message: Message, notify_time, bot: Bot):
    chat_id = message.chat.id
    one_hour_earlier = notify_time - timedelta(hours=1)

    if datetime.now() > notify_time:
        notify_time = datetime.now() + timedelta(seconds=5)
        scheduler.add_job(already_start, 'date', run_date=notify_time, args=[chat_id, bot])
    elif datetime.now() <= one_hour_earlier:
        scheduler.add_job(send_notification, 'date', run_date=one_hour_earlier, args=[chat_id, bot])
        scheduler.add_job(now_start, 'date', run_date=notify_time, args=[chat_id, bot])
        await message.answer(f"Напоминание о соревновании запланировано на {notify_time.strftime('%H:%M:%S')}!")
    else:
        await message.answer(f"Cоревнование начнётся меньше чем через час")


# Функция отправки уведомления
async def send_notification(chat_id: int, bot: Bot):
    try:
        await bot.send_message(chat_id, "Скоро начнётся соревнование, на которое вы зарегистрированы")
    except Exception as e:
        logger.debug(f"Ошибка при отправке уведомления: {e}")


async def already_start(chat_id: int, bot: Bot):
    try:
        await bot.send_message(chat_id, "Соревнование уже началось")
    except Exception as e:
        logger.debug(f"Ошибка при отправке уведомления: {e}")


async def now_start(chat_id: int, bot: Bot):
    try:
        await bot.send_message(chat_id, "Соревнование, на которое вы зарегистрированы, началось")
    except Exception as e:
        logger.debug(f"Ошибка при отправке уведомления: {e}")
