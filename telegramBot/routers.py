import logging
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from weatherForecast.forecast import WeatherForecast
from models.models import Log, Session, UserCity, City
from settings import API_KEY

router = Router()


@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    """
    Обработчик команды start
    :param message: сообщение ТГ
    :return:
    """
    db = Session()
    answer = "Данный бот предоставляет информацию о погоде.\n"\
             "Введите команду /weather <Город>, чтобы найти информацию.\n"\
             "Данный бот разработан в качестве теста для компании BobrAi"
    log = Log(user_id=message.from_user.id, command='start', datetime=datetime.now(), answer=answer)
    db.add(log)
    db.commit()
    logging.info(f"Ответ для пользователя {message.from_user.id} на команду start сохранен в логи")
    user_city = db.query(UserCity).filter(UserCity.id_user==message.from_user.id).first()
    if user_city:
        city = db.query(City.name).filter(City.id==user_city.id_city).first()
        kb = [
            [
                KeyboardButton(text=f"/weather {city.capitalize()}"),
            ],
        ]
        greet_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        db.close()
        await message.reply(answer, reply_markup=greet_kb)
    db.close()
    await message.answer(answer)


@router.message(Command(commands=["weather"]))
async def weather(message: types.Message, command: CommandObject):
    """
    Обработчик команды weather
    :param message: сообщение ТГ
    :param command: Сообщение после команды weather
    :return:
    """
    db = Session()
    if command.args:
        city = command.args.lower()
        weather_forecast = WeatherForecast(API_KEY).get_weather(city)

        if weather_forecast is None:
            answer = "Проверьте введенный город"
            log = Log(user_id=message.from_user.id, command=f'weather {city}', datetime=datetime.now(), answer=answer)
            db.add(log)
            db.commit()
            db.close()
            await message.answer(answer)

        else:
            city_id = db.query(City).filter(City.name == city).first().id
            user_city = db.query(UserCity).filter(UserCity.id_user==message.from_user.id).first()
            if user_city:
                user_city.id_city = city_id
            else:
                user_city = UserCity(id_user=message.from_user.id, id_city=city_id)
                db.add(user_city)

            answer = f"Выбранный город {weather_forecast['city'].capitalize()}\n"\
                     f"Температура: {weather_forecast['temperature']} С\n"\
                     f"По ощущениям: {weather_forecast['feels_like']} С\n"\
                     f"На улице: {weather_forecast['weather_description']}\n"\
                     f"Влажность: {weather_forecast['humidity']} %\n"\
                     f"Скорость ветра: {weather_forecast['wind_speed']} м/с\n"\
                     f"Направление ветра: {weather_forecast['wind_direction']}"

            kb = [
                [
                    KeyboardButton(text=f"/weather {city.capitalize()}"),
                ],
            ]
            greet_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

            log = Log(user_id=message.from_user.id, command=f'weather {city}', datetime=datetime.now(), answer=answer)
            db.add(log)
            db.commit()
            db.close()
            await message.reply(answer, reply_markup=greet_kb)

    else:
        answer = "Проверьте введенный город"
        log = Log(user_id=message.from_user.id, command=f'weather', datetime=datetime.now(), answer=answer)
        db.add(log)
        db.commit()
        db.close()
        await message.answer(answer)


@router.message()
async def simple_answer(message: types.Message):
    """
    Обработчик других сообщений
    :param message:
    :return:
    """
    db = Session()
    answer = "Неверная команда, введите /weather <город>, чтобы узнать погоду"
    log = Log(user_id=message.from_user.id, command=message.text, datetime=datetime.now(), answer=answer)
    db.add(log)
    db.commit()
    logging.info(f"Ответ для пользователя {message.from_user.id} на команду {message.text} сохранен в логи")
    user_city = db.query(UserCity).filter(UserCity.id_user == message.from_user.id).first()
    if user_city:
        city = db.query(City.name).filter(City.id == user_city.id_city).first()
        kb = [
            [
                KeyboardButton(text=f"/weather {city.name.capitalize()}"),
            ],
        ]
        greet_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        db.close()
        await message.reply(answer, reply_markup=greet_kb)
    else:
        db.close()
        await message.answer(answer)
