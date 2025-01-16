import sqlite3

DB_NAME = "bot.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            username TEXT NOT NULL
        )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            name TEXT NOT NULL,
            participants TEXT,
            admins TEXT,
            date_start DATETIME,
            duration int,
            tasks TEXT
        )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_task TEXT NOT NULL,
            pdf_file TEXT NOT NULL,
            author TEXT
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks_and_competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id int NOT NULL,
            task_id int NOT NULL,
            num int NOT NULL
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS task_user_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id int NOT NULL,
            task_id int NOT NULL,
            competition_id int NOT NULL,
            number_send int,
            is_relevant bool,
            code_link TEXT,
            mark int         
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id int NOT NULL,
            action TEXT,
            time TIMESTAMP
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS history_llm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_user_code_id int NOT NULL,
            context TEXT,
            is_bot bool,
            number int
        )"""
    )

    conn.commit()
    conn.close()
