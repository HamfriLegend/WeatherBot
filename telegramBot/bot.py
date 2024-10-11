import os
from aiogram import Bot, types, Dispatcher
from .routers import router
from settings import API_KEY, BOT_TOKEN


bot = Bot(token=BOT_TOKEN)

dispatcher = Dispatcher()

dispatcher.include_router(router)


async def start_bot():
    await dispatcher.start_polling(bot)