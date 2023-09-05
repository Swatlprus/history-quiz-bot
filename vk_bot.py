import random
import requests
import logging
import time
import redis
from environs import Env

import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from tg_logger import TelegramLogsHandler

from learn_bot import read_questions

logger = logging.getLogger('Logger')


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)
    return keyboard


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)

    vk_api.messages.send(
        peer_id=event.user_id,
        message='Привет! Я бот для викторин!',
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard(),
    )


def new_question(questions, r, event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)

    question = random.choice(list(questions.keys()))
    r.set(event.user_id, question)

    vk_api.messages.send(
        peer_id=event.user_id,
        message=question,
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard(),
    )


def giveup(questions, r, event, vk_api):
    keyboard = create_keyboard()
    question = (r.get(event.user_id)).decode('utf-8')
    answer = questions[question]
    vk_api.messages.send(
        peer_id=event.user_id,
        message='Правильный ответ: ' + answer,
        random_id=random.randint(1,1000),
    )

    question = random.choice(list(questions.keys()))
    vk_api.messages.send(
        peer_id=event.user_id,
        message='Новый вопрос: ' + question,
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard(),
    )

    r.set(event.user_id, question)


def solution_attempt(questions, r, event, vk_api):
    keyboard = create_keyboard()
    question = (r.get(event.user_id)).decode('utf-8')
    answer = questions[question]
    if event.text in answer:
        vk_api.messages.send(
            peer_id=event.user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            random_id=random.randint(1,1000),
            keyboard=keyboard.get_keyboard()
        )
    else:
        vk_api.messages.send(
            peer_id=event.user_id,
            message='Неправильно… Попробуй еще раз',
            random_id=random.randint(1,1000),
            keyboard=keyboard.get_keyboard()
        )


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    env = Env()
    env.read_env()
    vk_token = env('VK_TOKEN')
    quiz_folder = env('QUIZ_FOLDER')
    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')
    questions = read_questions(quiz_folder)
    redis_pool = redis.ConnectionPool(
        host=redis_host,
        port=redis_port,
        password=redis_password
    )
    r = redis.Redis(connection_pool=redis_pool)
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    questions = read_questions(quiz_folder)
    reserve_telegram_token = env('RESERVE_TELEGRAM_TOKEN')
    admin_tg_id = env('ADMIN_TG_ID')
    logger.addHandler(TelegramLogsHandler(reserve_telegram_token, admin_tg_id))
    logger.info('ВК бот начал работу')
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == 'Начать':
                    start(event, vk_api)
                elif event.text == 'Новый вопрос':
                    new_question(questions, r, event, vk_api)
                elif event.text == 'Сдаться':
                    giveup(questions, r, event, vk_api)
                elif event.text == 'Мой счёт':
                    pass
                else:
                    solution_attempt(questions, r, event, vk_api)
    except requests.exceptions.HTTPError:
        logger.error('ВК бот упал с ошибкой HTTPError')
    except requests.exceptions.ReadTimeout:
        logger.debug('ВК бот. Wait... I will try to send the request again')
    except requests.exceptions.ConnectionError:
        logger.error('ВК бот упал с ошибкой ConnectionError')
        time.sleep(10)


if __name__ == '__main__':
    main()
