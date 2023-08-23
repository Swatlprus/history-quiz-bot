import logging
import requests
import time
import functools
import random
import redis
from environs import Env

import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from learn_bot import read_questions

logger = logging.getLogger('Logger')


def start_bot(tg_token, update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot = telegram.Bot(token=tg_token)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Привет! Я бот для викторин!",
                     reply_markup=reply_markup)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def send_question(questions, update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    if message.text == 'Новый вопрос':
        update.message.reply_text(random.choice(list(questions.keys())))


def main(tg_token, questions) -> None:
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    start = functools.partial(start_bot, tg_token)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    random_question = functools.partial(send_question, questions)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, random_question))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')
    quiz_folder = env('QUIZ_FOLDER')
    questions = read_questions(quiz_folder)
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    logger.info('Telegram бот начал работу')
    try:
        main(tg_token, questions)
    except requests.exceptions.HTTPError:
        logger.error('Telegram бот упал с ошибкой HTTPError')
    except requests.exceptions.ReadTimeout:
        logger.debug('Telegram бот. Wait... I will try to send the request again')
    except requests.exceptions.ConnectionError:
        logger.error('Telegram бот упал с ошибкой ConnectionError')
        time.sleep(10)
