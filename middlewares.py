from aiogram.types import TelegramObject, Message
import requests
import uuid
import requests
import json
import time
from typing import Any, Awaitable, Callable, Dict
import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from db_work import is_user_registered
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
import os
load_dotenv()
GigaChatKey = os.getenv("GigaChatKey")
logger = logging.getLogger(__name__)
TOKEN_UPDATE_INTERVAL = 3600


class Registration(StatesGroup):
    waiting_username = State()


class SomeMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # ...
        # Здесь выполняется код на входе в middleware
        # ...
        # logger.debug(
        #     'Вошли в миддлварь %s, тип события %s',
        #     __class__.__name__,
        #     event.__class__.__name__
        # )
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
        # logger.debug('Выходим из миддлвари  %s', __class__.__name__)
        # ...
        # Здесь выполняется код на выходе из middleware
        # ...

        return result


class GigachatTokenMiddleware(BaseMiddleware):
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
        # Проверяем, нужно ли обновлять токен
        if self.token is None or current_time - self.last_updated > TOKEN_UPDATE_INTERVAL:
            self.token = await self.update_token()
            self.last_updated = current_time
        # Передаем токен в контекст данных
        data["gigachat_token"] = self.token
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
