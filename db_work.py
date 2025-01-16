import sqlite3
import locale

DB_NAME = "bot.db"
from datetime import datetime

SPLITER_IN_PARTICIPANTS = ' '


# Функция для добавления тестовых данных


def is_user_registered(user_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# Сохраняем пользователя в базу данных
def save_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def pretty_date_start(date_start):
    date_start, time_start = date_start.split(" ")
    date_start_formatted = datetime.strptime(date_start, '%Y-%m-%d').strftime('%d %B %Y, %A')
    return date_start_formatted, time_start


def count_participants(parts):
    return len(parts.split(SPLITER_IN_PARTICIPANTS))


def get_competitions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, date_start, duration, participants FROM competitions")
    competitions = cursor.fetchall()
    formatted_competitions = []
    locale.setlocale(locale.LC_ALL, 'ru_RU')
    keyboard_info = []
    conn.close()
    for index, competition in enumerate(competitions):
        id_el, name, date_start, duration, participants = competition
        keyboard_info.append({"name": f"{index + 1}. {name}", "id": id_el})
        date_start_formatted, time_start = pretty_date_start(date_start)
        duration_info = f"{duration // 60} ч {duration % 60} мин"
        if duration == 0:
            duration_info = "неограниченно"
        formatted_competitions.append(
            f"📅 {date_start_formatted} | 👥 {count_participants(participants)} \n{index + 1}. {name} | {time_start} | {duration_info}\n")
    return (keyboard_info, "\n".join(formatted_competitions))


def get_competition_by_id(competition_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitions WHERE id = ?", (competition_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_participants_by_compid(competition_id: int) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT participants FROM competitions WHERE id = ?", (competition_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0]


def add_new_participant_by_compid(competitions, competition_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE competitions SET participants = ? WHERE id = ?", (competitions, competition_id))
    conn.commit()
    conn.close()


def get_all_tasks_in_competition(competition_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT task_id FROM tasks_and_competitions WHERE competition_id = ?", (competition_id,))
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def get_time_start_competition(competition_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date_start FROM competitions WHERE id = ?", (competition_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0]


def insert_solution(code_link: str, user_id: int, task_id: int, comp_id: int, mark: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO task_user_codes (user_id, task_id, competition_id, code_link, mark) VALUES (?, ?, ?, ?, ?)",
        (user_id, task_id, comp_id, code_link, mark))
    conn.commit()
    conn.close()


def delete_previous_solution(user_id: int, task_id: int, comp_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM task_user_codes WHERE user_id = ? AND task_id = ? AND competition_id = ?",
        (user_id, task_id, comp_id)
    )
    conn.commit()
    conn.close()


def get_user_by_id(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    # conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0]


def select_all_marks() -> list[dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, competition_id, mark FROM task_user_codes")
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def get_task_by_id(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    result = dict(cursor.fetchone())
    conn.close()
    return result
