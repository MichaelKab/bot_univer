import os
from collections import defaultdict

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import timedelta
from db_work import *
from menu import *
from scheduler import *

router_competition = Router()


@router_competition.callback_query(lambda c: "competition" in c.data)
async def competition_info(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    id_comp = int(callback_query.data.split(' ')[1])
    competition = get_competition_by_id(id_comp)
    now_id, description, name, participants, admins, date_start, duration, tasks = competition
    date_start_formatted, time_start = pretty_date_start(date_start)
    all_info = f"📅 {date_start_formatted}, 👥 {len(participants.split(SPLITER_IN_PARTICIPANTS))} \n{name} | {time_start}"
    duration_info = f"{duration // 60} часов {duration % 60} минут"
    if duration == 0:
        duration_info = "неограниченно"
    all_info += f"\n Продолжительность: {duration_info}\nОписание:\n {description} \n"
    username_participants = []
    for participant in participants.split(SPLITER_IN_PARTICIPANTS):
        username_participants.append(get_user_by_id(int(participant)))
    all_participants = '\n'.join(username_participants)
    all_info += f"Участники: \n{all_participants}"
    buttons = []

    buttons.append([InlineKeyboardButton(text="Показать задачи",
                                         callback_data=f'tasks {now_id}')])
    buttons.append([InlineKeyboardButton(text="Показать таблицу лидеров",
                                         callback_data=f'leader_board {now_id}')])
    tasks: list[dict] = get_all_tasks_in_competition(id_comp)
    tm_datetime = datetime.strptime(get_time_start_competition(competition_id=id_comp), '%Y-%m-%d %H:%M:%S')
    if duration == 0 or (datetime.now() < tm_datetime and datetime.now() <= tm_datetime + timedelta(minutes=duration)):
        if is_registered_on_comp_by_id(user_id=user_id, participants=get_participants_by_compid(id_comp)):
            for index, task in enumerate(tasks):
                buttons.append([InlineKeyboardButton(text=f"Отправить решение на задачу {index + 1}",
                                                     callback_data=f'prepare_send {now_id} {task["task_id"]}')])
        else:
            buttons.append([InlineKeyboardButton(text="Учавствовать",
                                                 callback_data=f'participate {now_id}')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.answer(all_info, reply_markup=keyboard)


@router_competition.callback_query(lambda c: "participate" in c.data)
async def register_on_competition(callback_query: CallbackQuery, bot: Bot):
    id_comp = int(callback_query.data.split(' ')[1])
    participants = get_participants_by_compid(id_comp)
    user_id = callback_query.from_user.id
    if is_registered_on_comp_by_id(user_id=user_id, participants=participants):
        await callback_query.message.answer("Вы уже зарегистрированы на соревнование", reply_markup=main_menu())
        return
    date_time = get_time_start_competition(competition_id=id_comp)
    await notify(message=callback_query.message, notify_time=datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S'), bot=bot)
    add_new_participant_by_compid(participants + SPLITER_IN_PARTICIPANTS + str(user_id), id_comp)
    await callback_query.message.answer("Вы успешно зарегистрированы на соревнование", reply_markup=main_menu())
    return await competition_info(callback_query)


@router_competition.callback_query(lambda c: "tasks" in c.data)
async def show_tasks(callback_query: CallbackQuery, bot: Bot):
    trash, id_comp = callback_query.data.split(' ')
    tasks_id = get_all_tasks_in_competition(int(id_comp))
    if len(tasks_id) == 0:
        await callback_query.message.answer("Задач нет")
    for index, task_map in enumerate(tasks_id):
        task_id = task_map['task_id']
        task_info = get_task_by_id(task_id)
        pdf_file = task_info['pdf_file']
        name = task_info['name_task']
        now_dir = os.path.abspath(os.curdir).replace("\\", "/")
        load_file = FSInputFile(pdf_file)
        await bot.send_document(
            chat_id=callback_query.message.chat.id,
            document=load_file,
            caption=f"Условие задачи {index + 1} {name}"
        )


@router_competition.callback_query(lambda c: "leader_board" in c.data)
async def show_leaderboard(callback_query: CallbackQuery):
    trash, id_comp = callback_query.data.split(' ')
    id_comp = int(id_comp)
    solutions = select_all_marks()
    all_marks = []
    for solution in solutions:
        competition_id = solution['competition_id']
        if competition_id == id_comp:
            all_marks.append(solution)
    leaderboard = gen_leader_board(all_marks)
    await callback_query.message.answer("\n".join(leaderboard), parse_mode="HTML")


def is_registered_on_comp_by_id(user_id: int, participants: str) -> bool:
    participants_split = participants.split(SPLITER_IN_PARTICIPANTS)
    return str(user_id) in participants_split


def gen_leader_board(all_marks: list[dict]):
    marks_dict = defaultdict(int)
    for element in all_marks:
        user_id = element['user_id']
        mark = element['mark']
        username: str = get_user_by_id(user_id)
        marks_dict[username] += mark
    sorted_leaders = sorted(marks_dict.items(), key=lambda x: x[1], reverse=True)
    leaderboard = ["🏆 <b>Таблица лидеров</b> 🏆\n"]
    for rank, (username, score) in enumerate(sorted_leaders, start=1):
        leaderboard.append(f"{rank}. {username}: <b>{score}</b>")
    return leaderboard
