import os

import dotenv

from create_database import init_db
from db_work import *
from handlers import main_handlers, connect_with_gigachat, competition_handlers, upload
from middlewares import RegisterMiddleware, LoggingMiddleware
from scheduler import *
from fill_db import seed_competitions

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    dotenv.load_dotenv()
    API_TOKEN = os.getenv("API_TOKEN")

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(main_handlers.router)
    dp.include_router(connect_with_gigachat.gigachat_router)
    dp.include_router(competition_handlers.router_competition)
    dp.include_router(upload.router_upload)
    dp.update.outer_middleware(RegisterMiddleware())
    dp.update.outer_middleware(LoggingMiddleware())
    init_db()
    seed_competitions()
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
