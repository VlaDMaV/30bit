import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import config
from app.handlers import router
from app.database.models import init_db

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Подключаем токен бота
bot = Bot(token=config.bot_token.get_secret_value())

# Диспетчер
dp = Dispatcher()

async def main():
    await init_db()  # Инициализация базы данных
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот выключен")