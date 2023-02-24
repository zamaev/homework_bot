import os
import sys
import time
import logging
import requests
import telegram

from exceptions import (
    InvalidApiResponseException,
    InvalidApiResponseHomeworkException,
    InvalidVerdictException,
)
from http import HTTPStatus
from logging import StreamHandler
from dotenv import load_dotenv

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
    for const in ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID'):
        if not eval(const):
            logger.critical(
                f'Отсутствует обязательная переменная окружения: \'{const}\'')
            return False
    return True


def get_api_answer(timestamp):
    """Получения ответа от API."""
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp},
    )
    if response.status_code != HTTPStatus.OK:
        raise InvalidApiResponseException(
            f'Эндпоинт "{ENDPOINT}" недоступен. '
            f'Код ответа API: {response.status_code}'
        )
    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    return (isinstance(response.get('homeworks'), list)
            and isinstance(response.get('current_date'), int))


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
    except Exception as error:
        logger.error(
            f'Неудачная отправка сообщения "{message}". Ошибка: {error}')
    else:
        logger.debug(f'Бот отправил сообщение "{message}"')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return print('Программа принудительно остановлена.')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            if not check_response(response):
                raise InvalidApiResponseException(
                    f'Некорректный ответ API: {response}')
            timestamp = response.get('current_date')
            homeworks = response.get('homeworks')
            if not homeworks:
                logger.debug('Нет новых статусов')
            else:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
