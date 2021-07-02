import os
import time
import requests
import telegram
from telegram.ext import Updater, CommandHandler, updater
import logging
from dotenv import load_dotenv
from pprint import pprint

from telegram import message


load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

api_url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

bot = telegram.Bot(token=TELEGRAM_TOKEN)
updater


logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = None
    try:
        if homework_status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        elif homework_status == 'reviewing':
            verdict = 'работа взята на проверку.'
        else:
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    except Exception as error:
        logging.error(error, exc_info=True)
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            api_url,
            params=payload,
            headers=headers
        )
        return homework_statuses.json()
    except Exception as error:
        logging.error(error, exc_info=True)
    return None


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            if len(homeworks['homeworks']) > 0:
                message = parse_homework_status(homeworks['homeworks'][0])
                send_message(message)
                time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    logging.debug('Start')
    main()
