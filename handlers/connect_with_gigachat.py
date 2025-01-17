import os
import os
import string

from PyPDF2 import PdfReader
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

from db_work import *
from menu import *
from scheduler import *

gigachat_router = Router()
GigaChatKey = os.getenv("GigaChatKey")


class UploadSolution(StatesGroup):
    waiting_for_Solution = State()
    chat_with_llm = State()


@gigachat_router.callback_query(lambda c: "prepare_send" in c.data)
async def prepare_to_solution(callback_query: CallbackQuery, state: FSMContext):
    trash, id_comp, task_id = callback_query.data.split(' ')
    await state.set_state(UploadSolution.waiting_for_Solution)
    await state.update_data(pressed_button={"comp_id": id_comp, "task_id": task_id})
    await callback_query.message.answer("Прикрепите файл решения формата .py")


@gigachat_router.message(UploadSolution.waiting_for_Solution)
async def process_file(message: Message, state: FSMContext, bot: Bot):
    # Получаем данные о нажатой кнопке из состояния FSM
    data = await state.get_data()
    mp = data.get("pressed_button")
    task_id = mp["task_id"]
    comp_od = mp["comp_id"]
    # Проверяем, что файл имеет расширение .py
    if not message.document:
        await message.answer("Ошибка: отправьте файл с расширением .py")
        return
    file_name = message.document.file_name

    if not file_name.endswith(".py"):
        await message.answer("Ошибка: отправьте файл с расширением .py")
        return

    file_id = message.document.file_id
    file_path = f"files/user_codes/{file_id}.py"
    await bot.download(message.document, destination=file_path)
    for_user = """
    Решение отправлено. Ожидайте оценки
    Критерии:
    1)Правильные ответы на каждом из тестов Оценка от 0 до 5
    2) Корректная асимптотика. Оценка от 0 до 5
    3) Лаконичность. Оценка от 0 до 2
    """
    await message.answer(for_user)
    try:
        with open(file_path, "r", encoding="utf-8") as code_file:
            user_code = code_file.read()
    except Exception as e:
        logger.debug(f'Ошибка чтения файла с кодом:{e}')
        return
    #
    task_txt_path: str = get_task_by_id(task_id)['text_task']
    # task_pdf_path = f"/files/task1/A Это топсорт.pdf"
    now_dir: str = os.path.abspath(os.curdir).replace("\\", "/")
    # task_pdf_path:str = now_dir + task_pdf_path,
    # потом подрузку из бд сделать
    task_condition = ""
    try:
        file_open = open(task_txt_path, "r")
        task_condition = file_open.read()
    except Exception as e:
        await message.reply(f"Ошибка чтения файла с условием задачи: {e}")
        return

    # gigachat_token = data.get("gigachat_token")
    # logger.debug(f'токен:{gigachat_token}')
    llm = GigaChat(
        credentials=GigaChatKey,
        scope="GIGACHAT_API_PERS",
        model="GigaChat",
        verify_ssl_certs=False,
        streaming=False,
    )
    messages = [
        SystemMessage(
            content="Ты программист хорошо разбирающийся в PYTHON"
        )
    ]
    mark_prompt = f"""
    Оцени решение данной задачи на языке Python. Не нужно приводить свой код. Оцени только отправленный.
    Критерии:
    1)Правильные ответы на каждом из тестов, также придумай свои корректные тесты и протестируй на них. Оценка от 0 до 5
    2) Корректная асимптотика. Оцени асимптотическую сложность алгоритма по времени и по памяти, если она соответствует ограничением задачи, то поставь хороший балл. Оценка от 0 до 5
    3) Лаконичность. Оцени, насколько данный код соответствует стандартам написания кода. Оценка от 0 до 2
    В итоге выведи только суммарную оценку, которая считается как сумма всех оценок по критериям. Cообщение должно состоять только из одного числа
    Условие:
    {task_condition}
    Код:
    {user_code}
    """
    messages.append(HumanMessage(content=mark_prompt))
    await state.set_state(UploadSolution.chat_with_llm)
    try:
        res = llm.invoke(messages)
        messages.append(res)
        result = res.content
        await message.answer(f"Оценка модели GigaChat:\n{result}")
        mark = ''
        for char in result:
            if char in string.digits:
                mark += char
        logger.debug(f"Оценка:{mark}")
        if mark == '':
            mark = 0
        mark = int(mark)
    except Exception as e:
        await message.answer(f"Ошибка при работе с GigaChat: {e}")
        return
    delete_previous_solution(user_id=message.from_user.id, task_id=task_id, comp_id=comp_od)
    insert_solution(code_link=file_path, user_id=message.from_user.id, task_id=task_id, comp_id=comp_od, mark=mark)
    await state.update_data(messages=messages)
    builder = ReplyKeyboardBuilder()
    builder.button(text="Закончить общение", callback_data='stop')
    await message.answer("Вы можете продолжить обсуждение своего решения",
                         reply_markup=builder.as_markup(resize_keyboard=True))


@gigachat_router.message(UploadSolution.chat_with_llm)
async def continue_dialog(message: Message, state: FSMContext):
    # Получаем память пользователя
    if message.text == "Закончить общение":
        await state.clear()
        await message.answer("Общение прекращено", reply_markup=main_menu())
        return
    llm = GigaChat(
        credentials=GigaChatKey,
        scope="GIGACHAT_API_PERS",
        model="GigaChat",
        verify_ssl_certs=False,
        streaming=False,
    )
    data = await state.get_data()
    messages = data.get("messages")
    messages.append(HumanMessage(message.text))
    try:
        res = llm.invoke(messages)
        messages.append(res)
        await message.answer(res.content)
    except Exception as e:
        await message.answer(f"Ошибка при работе с GigaChat: {e}")
        return
    await state.update_data(messages=messages)
