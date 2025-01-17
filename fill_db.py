import sqlite3

DB_NAME = "bot.db"

SPLITER_IN_PARTICIPANTS = ' '


def seed_competitions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM competitions")
    descriptions = [
        "Это первое соревнование. Оно показывает, в каком формате хочется видеть условия задач и знакомит пользователей",
        "Это сорвенование, которое закончилось. Задача задачь в него невозможна, но можно посмотреть условия и итоговый рейтинг",
        "Это сорвенование бесконечное. Задачи можно сдавать в любой момент, соответсвенно таблица лидеров также меняется"
    ]
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO competitions (description, name, participants, date_start, duration) VALUES (?,?, ?, ?, ?)",
            (descriptions[0], "Тестовое соревнование", "999999999", '2025-01-19 12:00:00', '480')
        )
        cursor.execute(
            "INSERT INTO competitions (description, name, participants, date_start, duration) VALUES (?, ?, ?, ?, ?)",
            (descriptions[1], "Закончившееся соревнование", "222222222 666666666 999999999", '2025-01-15 15:31:00',
             '240')
        )
        cursor.execute(
            "INSERT INTO competitions (description, name, participants, date_start, duration) VALUES (?,?, ?, ?, ?)",
            (descriptions[2], "Бесконечное соревнование", "222222222 111111111 666666666 999999999",
             '2025-01-16 10:00:00', '0')
        )
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (111111111, 'chill gay')
        )
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (999999999, 'crutoy perets')
        )
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (666666666, 'mega xexe')
        )
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (222222222, 'not xexe')
        )
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO tasks (name_task, pdf_file, text_task, author) VALUES (?, ?, ?, ?)",
            ("Это топсорт?", "files/task1/A Это топсорт.pdf", "files/task1/text_task.txt", "me")
        )
        cursor.execute(
            "INSERT INTO tasks (name_task, pdf_file, text_task, author) VALUES (?, ?, ?, ?)",
            ("Кто тут король", "files/task2/Кто тут король.pdf", "files/task2/text_task.txt", "me")
        )
        cursor.execute(
            "INSERT INTO tasks (name_task, pdf_file, text_task, author) VALUES (?, ?, ?, ?)",
            ("Диаметр", "files/task3/Диаметр.pdf", "files/task3/text_task.txt", "me")
        )
        cursor.execute(
            "INSERT INTO tasks (name_task, pdf_file, text_task, author) VALUES (?, ?, ?, ?)",
            ("метеоритный дождь", "files/task4/метеоритный дождь.pdf", "files/task4/text_task.txt", "me")
        )
        cursor.execute(
            "INSERT INTO tasks (name_task, pdf_file, text_task, author) VALUES (?, ?, ?, ?)",
            ("Опять проекты.pdf", "files/task5/Опять проекты.pdf", "files/task5/text_task.txt", "me")
        )
        cursor.execute(
            "INSERT INTO tasks (name_task, pdf_file, text_task, author) VALUES (?, ?, ?, ?)",
            ("Танцы с бубном.pdf", "files/task6/Танцы с бубном.pdf", "files/task6/text_task.txt", "me")
        )
    cursor.execute("SELECT COUNT(*) FROM tasks_and_competitions")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO tasks_and_competitions (competition_id, task_id, num) VALUES (?, ?, ?)",
            (1, 1, 1)
        )
        cursor.execute(
            "INSERT INTO tasks_and_competitions (competition_id, task_id, num) VALUES (?, ?, ?)",
            (2, 4, 1)
        )
        cursor.execute(
            "INSERT INTO tasks_and_competitions (competition_id, task_id, num) VALUES (?, ?, ?)",
            (2, 5, 2)
        )
        cursor.execute(
            "INSERT INTO tasks_and_competitions (competition_id, task_id, num) VALUES (?, ?, ?)",
            (3, 6, 1)
        )
        cursor.execute(
            "INSERT INTO tasks_and_competitions (competition_id, task_id, num) VALUES (?, ?, ?)",
            (3, 2, 2)
        )
        cursor.execute(
            "INSERT INTO tasks_and_competitions (competition_id, task_id, num) VALUES (?, ?, ?)",
            (3, 3, 3)
        )
    cursor.execute("SELECT COUNT(*) FROM task_user_codes")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO task_user_codes (user_id, task_id, competition_id, mark) VALUES (?, ?, ?, ?)",
            (999999999, 4, 2, 9)
        )
        cursor.execute(
            "INSERT INTO task_user_codes (user_id, task_id, competition_id, mark) VALUES (?, ?, ?, ?)",
            (999999999, 5, 2, 10)
        )
        cursor.execute(
            "INSERT INTO task_user_codes (user_id, task_id, competition_id, mark) VALUES (?, ?, ?, ?)",
            (999999999, 6, 3, 5)
        )
        cursor.execute(
            "INSERT INTO task_user_codes (user_id, task_id, competition_id, mark) VALUES (?, ?, ?, ?)",
            (666666666, 4, 2, 6)
        )
        cursor.execute(
            "INSERT INTO task_user_codes (user_id, task_id, competition_id, mark) VALUES (?, ?, ?, ?)",
            (666666666, 5, 2, 5)
        )
        cursor.execute(
            "INSERT INTO task_user_codes (user_id, task_id, competition_id, mark) VALUES (?, ?, ?, ?)",
            (111111111, 6, 3, 1)
        )

    conn.commit()
    conn.close()
