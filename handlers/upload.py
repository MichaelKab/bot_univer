from aiogram import F, Router
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db_work import *
from menu import *
from scheduler import *

router_upload = Router()
class UploadTask(StatesGroup):
    waiting_for_pdf = State()
    waiting_for_input_tests = State()
    waiting_for_output_tests = State()

@router_upload.message(F.text == "Загрузить задачу")
async def upload_task(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте PDF файл с условием задачи.", reply_markup=cancel_menu())
    await state.set_state(UploadTask.waiting_for_pdf)


class IsPdfDocument(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.document and message.document.mime_type == 'application/pdf'


@router_upload.message(UploadTask.waiting_for_pdf)
async def handle_pdf_file(message: Message, state: FSMContext, bot: Bot):
    if message.document and message.document.mime_type == 'application/pdf':
        pdf_file = message.document
        file_path = f"files/{pdf_file.file_id}.pdf"
        await bot.download(pdf_file, destination=file_path)
        await state.update_data(pdf_file_path=file_path)
        await message.answer("Теперь отправьте текстовый файл с входными тестами.", reply_markup=cancel_menu())
        await state.set_state(UploadTask.waiting_for_input_tests)
    elif message.text == "Вернуться на главную":
        await return_to_main_menu(message, state)
    else:
        await message.answer("Пожалуйста, загрузите PDF файл.")


@router_upload.message(UploadTask.waiting_for_input_tests)
async def handle_input_tests_file(message: Message, state: FSMContext, bot: Bot):
    if message.document and message.document.mime_type == 'text/plain':
        input_file = message.document
        file_path = f"files/{input_file.file_id}_input.txt"
        await bot.download(input_file, destination=file_path)
        await state.update_data(input_file_path=file_path)
        await message.answer("Теперь отправьте текстовый файл с выходными тестами.", reply_markup=cancel_menu())
        await state.set_state(UploadTask.waiting_for_output_tests)
    elif message.text == "Вернуться на главную":
        await return_to_main_menu(message, state)
    else:
        await message.answer("Пожалуйста, загрузите текстовый файл с входными тестами.")


@router_upload.message(UploadTask.waiting_for_output_tests)
async def handle_output_tests_file(message: Message, state: FSMContext, bot: Bot):
    if message.document and message.document.mime_type == 'text/plain':
        output_file = message.document
        file_path = f"files/{output_file.file_id}_output.txt"
        await bot.download(output_file, destination=file_path)

        data = await state.get_data()
        pdf_file_path = data['pdf_file_path']
        input_file_path = data['input_file_path']

        author = message.from_user.username or "Unknown"

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (pdf_file, author, tests) VALUES (?, ?, ?)",
            (pdf_file_path, author, f"{input_file_path},{file_path}")
        )
        conn.commit()
        conn.close()

        await message.answer("Задача успешно загружена!", reply_markup=main_menu())
        await state.clear()
    elif message.text == "Вернуться на главную":
        await return_to_main_menu(message, state)
    else:
        await message.answer("Пожалуйста, загрузите текстовый файл с выходными тестами.")

@router_upload.message(F.text == "Вернуться на главную")
async def return_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись на главный экран.", reply_markup=main_menu())