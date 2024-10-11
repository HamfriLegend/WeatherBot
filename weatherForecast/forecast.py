import logging
import requests
from cachetools import TTLCache
import json
from models.models import City, Session
cache = TTLCache(maxsize=100, ttl=7200)


class WeatherForecast:
    """
    Класс для предоставления данных о погоде
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = 'https://api.openweathermap.org/data/2.5/weather?'
        self.geoapi_url = 'http://api.openweathermap.org/geo/1.0/direct?'

    def _get_coordinates(self, city):
        """
        Геокодирование названия города
        :param city: Название города
        :return: координаты lat lon
        """
        db = Session()
        city_obj = db.query(City).filter(City.name == city).one_or_none()
        if city_obj:
            lat, lon = city_obj.lat, city_obj.lon
            db.close()
            return lat, lon

        response = requests.get(self.geoapi_url + f'q={city}&appid={self.api_key}')
        if response.status_code == 200:
            data = response.json()
            if len(data) == 0:
                return None, None
            lat = data[0]['lat']
            lon = data[0]['lon']
            city_obj = City(name=city, lat=lat, lon=lon)
            db.add(city_obj)
            db.commit()
            db.close()
            return lat, lon

    def get_weather(self, city):
        """
        Предоставление данных о погоде
        :param city: Название города
        :return: Данные погоды
        """
        if city in cache:
            logging.info(f"Загружаем данные для города {city} из кэша")
            return cache[city]

        lat, lon = self._get_coordinates(city)
        if lat is None or lon is None:
            return None

        response = requests.get(self.api_url + f'lat={lat}&lon={lon}&appid={self.api_key}&lang=ru')
        if response.status_code == 200:
            data = response.json()
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']-273.15
            feels_like = data['main']['feels_like']-273.15
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            wind_deg = data['wind']['deg']

            if 0 <= wind_deg < 45:
                wind_dir="С"
            elif 45 <= wind_deg < 90:
                wind_dir="С-В"
            elif 90 <= wind_deg < 135:
                wind_dir="В"
            elif 135 <= wind_deg < 180:
                wind_dir="Ю-В"
            elif 180 <= wind_deg < 225:
                wind_dir="Ю"
            elif 225 <= wind_deg < 270:
                wind_dir="Ю-З"
            elif 270 <= wind_deg < 315:
                wind_dir="З"
            elif 315 <= wind_deg < 360:
                wind_dir="С-З"
            else:
                wind_dir="С"
            logging.info(weather_desc)
            logging.info(temp)
            logging.info(feels_like)
            logging.info(humidity)
            logging.info(wind_speed)
            logging.info(wind_dir)
            forecast = {
                "city": city,
                "weather_description": weather_desc,
                "temperature": round(temp, 2),
                "feels_like": round(feels_like, 2),
                "humidity": humidity,
                "wind_speed": wind_speed,
                "wind_direction": wind_dir
            }
            cache[city] = forecast
            logging.info(f"Данные для города {city} сохранены в кэш")
            return forecast

