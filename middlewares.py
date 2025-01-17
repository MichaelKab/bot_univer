from db_work import insert_log
import logging
import os
import time
import uuid
from typing import Any, Awaitable, Callable, Dict

import requests
from aiogram import BaseMiddleware
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import TelegramObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from db_work import is_user_registered

load_dotenv()
GigaChatKey = os.getenv("GigaChatKey")
logger = logging.getLogger(__name__)
TOKEN_UPDATE_INTERVAL = 3600


class Registration(StatesGroup):
    waiting_username = State()


class RegisterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if event.message:
            user_id = event.message.from_user.id
            # fsm_context = FSMContext(storage=event.message.bot.get('storage'), chat=event.message.chat.id,
            #                          user=user_id)
            reg = Registration.waiting_username
            st = await data['state'].get_state()
            if not is_user_registered(
                    user_id) and event.message.text != "Зарегистрироваться" and reg != st:
                builder = ReplyKeyboardBuilder()
                builder.button(text="Зарегистрироваться")
                await event.message.answer("Вы не зарегистрированы", reply_markup=builder.as_markup(resize_keyboard=True))
                return

        result = await handler(event, data)
        return result


class LoggingMiddleware(BaseMiddleware):
    """Middleware для обновления токена раз в час."""

    def __init__(self):
        super().__init__()
        self.token = None  # Хранится текущий токен
        self.last_updated = 0  # Время последнего обновления токена

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Обрабатывает входящие сообщения."""
        current_time = time.time()
        logger.debug(f'Прошло времени с обновления токена {current_time - self.last_updated}')
        if event.message:
            insert_log(user_id = event.message.from_user.id, text=event.message.text)
        result = await handler(event, data)
        return result

    @staticmethod
    async def update_token() -> str:
        """Обновление токена с помощью внешнего API."""
        logger.debug('Обновляем токен')
        rq_uid = str(uuid.uuid4())
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        payload = {'scope': 'GIGACHAT_API_PERS'}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': rq_uid,
            'Authorization': f'Basic {GigaChatKey}'
        }

        try:
            response = requests.post(url, headers=headers, data=payload, verify=False)
            response.raise_for_status()
            token_data = response.json()

            logger.debug(f"Новый токен:{token_data.get('access_token')}")
            return token_data.get("access_token")  # Предполагаем, что токен возвращается в этом поле
        except requests.RequestException as e:
            logger.debug('Ошибка при обновлении токена: ')
            return None
