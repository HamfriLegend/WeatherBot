import asyncio
import logging

from aiogram import Dispatcher
from fastapi import FastAPI
from routers.logs import router as logs_router
from telegramBot.bot import bot, dispatcher, start_bot
from contextlib import asynccontextmanager
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Функция для отслеживания запуска остановки FastApi сервера и включения/выключения чат бота
    :param app:
    :return:
    """
    task = asyncio.create_task(start_bot())
    logging.info("Bot started")

    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logging.info("Bot task was cancelled")

    logging.info("Bot stopped")
app = FastAPI(lifespan=lifespan)

app.include_router(logs_router, prefix="/logs")

