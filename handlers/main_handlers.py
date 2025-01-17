import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from db_work import *
from menu import *
from middlewares import Registration
from scheduler import *
from .competition_handlers import gen_leader_board
load_dotenv()

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "Зарегистрироваться")
async def register(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if is_user_registered(user_id):
        await message.answer("Вы уже зарегистрированы!")
        return
    await state.set_state(Registration.waiting_username)
    await message.answer("Введите желаемый юзернейм для регистрации:")


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_menu()
    )


@router.message(Command("info"))
async def cmd_start(message: Message):
    await message.answer(
        """данный бот предназначен для участия в соревнованиях по программированию на языке python
        Вы можете зарегистрироваться на соревнование и в момент его проведения засылать задачи. 
        Задачи оцениваются llm Gigachat. После оценки, можете обсудить с llm своё решение и оценку.
        Также существуют таблицы лидеров. В глобальной таблице суммируются баллы со всех соревнований, в которых вы приняли участие.
        В таблице соревнования суммируются только баллы с задач присутствующих в данном соревновании. 
        """,
        reply_markup=main_menu()
    )


@router.message(F.text == "Зарегистрироваться")
async def register(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if is_user_registered(user_id):
        await message.answer("Вы уже зарегистрированы!")
        return
    await state.set_state(Registration.waiting_username)
    await message.answer("Введите желаемый юзернейм для регистрации:")



@router.message(F.text == "Список соревнований")
async def competitions_list(message: Message):
    buttons = []
    keyboarad_info, string_answer = get_competitions()
    for index, button in enumerate(keyboarad_info):
        buttons.append([InlineKeyboardButton(
            text=button["name"],
            callback_data=f'competition {button["id"]}')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(string_answer, reply_markup=keyboard)


@router.message(F.text == "Общая таблица лидеров")
async def global_leader_board(message: Message):
    all_marks = select_all_marks()
    leaderboard = gen_leader_board(all_marks)
    await message.answer("\n".join(leaderboard), parse_mode="HTML")


@router.message(Registration.waiting_username)
async def get_username(message: Message, state: FSMContext):
    if len(message.text) == 0:
        await message.answer("Попробуйте другой username")
    username = message.text
    user_id = message.from_user.id
    save_user(user_id, username)
    await state.clear()
    await message.answer(
        f"Регистрация прошла успешно! Ваш юзернейм: {username}",
        reply_markup=main_menu()
    )


@router.message()
async def catch_all_handler(message: Message):
    await message.answer("Я не понимаю это сообщение. Попробуй использовать /info.")
