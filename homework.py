import json
import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from exceptions import (
    InvalidApiResponseException,
    InvalidApiResponseHomeworkException,
    InvalidVerdictException,
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверка доступности переменных окружения."""
    if not PRACTICUM_TOKEN:
        logger.critical(
            'Отсутствует обязательная переменная окружения: "PRACTICUM_TOKEN"'
        )
        exit()
    if not TELEGRAM_TOKEN:
        logger.critical(
            'Отсутствует обязательная переменная окружения: "TELEGRAM_TOKEN"'
        )
        exit()
    if not TELEGRAM_CHAT_ID:
        logger.critical(
            'Отсутствует обязательная переменная окружения: '
            '"TELEGRAM_CHAT_ID"'
        )
        exit()


def get_api_answer(timestamp):
    """Получения ответа от API."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp},
        )
    except requests.RequestException:
        raise InvalidApiResponseException(
            f'Эндпоинт "{ENDPOINT}" недоступен.'
        )
    if response.status_code != HTTPStatus.OK:
        raise InvalidApiResponseException(
            f'Эндпоинт "{ENDPOINT}" недоступен. '
            f'Код ответа API: {response.status_code}'
        )
    try:
        response = response.json()
    except json.decoder.JSONDecodeError:
        raise InvalidApiResponseException(
            f'Эндпоинт "{ENDPOINT}" вернул ответ, '
            'в котором недекодируемый JSON'
        )
    return response


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ response должен быть словарем')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Элемент homeworks должен быть списком')
    if not isinstance(response.get('current_date'), int):
        raise TypeError('Элемент current_date должен быть числом')


def parse_status(homework):
    """Извлечение статуса домашней работы."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if not homework_name or not status:
        raise InvalidApiResponseHomeworkException(
            f'Некорректный homework в ответе API: {homework}')
    verdict = HOMEWORK_VERDICTS.get(status)
    if not verdict:
        raise InvalidVerdictException(
            'Некорректный вердикт проверки домашнего задания')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except (TelegramError, Exception) as error:
        logger.error(
            f'Неудачная отправка сообщения "{message}". Ошибка: {error}')
    else:
        logger.debug(f'Бот отправил сообщение "{message}"')


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    last_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            timestamp = response.get('current_date')
            homeworks = response.get('homeworks')
            if not homeworks:
                logger.debug('Нет новых статусов')
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != last_message:
                send_message(bot, message)
            last_message = message

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
