import logging
import requests
import time
import functools
import random
import redis
from environs import Env
from enum import Enum

import telegram
from tg_logger import TelegramLogsHandler
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from learn_bot import read_questions

logger = logging.getLogger('Logger')

class Type(Enum):
    QUESTION = 0
    ANSWER = 1


def start_bot(bot, update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Привет! Я бот для викторин!",
                     reply_markup=reply_markup)
    
    return Type.QUESTION


def handle_new_question_request(questions, r, update: Update, context: CallbackContext) -> None:
    question = random.choice(list(questions.keys()))
    update.message.reply_text(question)
    r.set(update.message.chat_id, question)

    return Type.ANSWER


def handle_solution_attempt(questions, r, update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    question = (r.get(update.message.chat_id)).decode('utf-8')
    answer = questions[question]
    if message.text in answer:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
    else:
        update.message.reply_text('Неправильно… Попробуй еще раз')
    
    return Type.ANSWER


def giveup(questions, r, update: Update, context: CallbackContext) -> None:
    question = (r.get(update.message.chat_id)).decode('utf-8')
    answer = questions[question]
    update.message.reply_text('Правильный ответ: ' + answer)
    question = random.choice(list(questions.keys()))
    update.message.reply_text('Новый вопрос: ' + question)
    r.set(update.message.chat_id, question)
    
    return Type.ANSWER


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("Пользователь %s отменил прохождение викторины", user.first_name)
    update.message.reply_text('Пока! Я надеюсь ты вернёшься к нам.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main(tg_token, questions, r) -> None:
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    bot = telegram.Bot(token=tg_token)

    start = functools.partial(start_bot, bot)
    new_question = functools.partial(handle_new_question_request, questions, r)
    new_answer = functools.partial(handle_solution_attempt, questions, r)
    give_up = functools.partial(giveup, questions, r)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),],

        states={
            Type.QUESTION: [MessageHandler(Filters.regex('^Новый вопрос$'), new_question)],

            Type.ANSWER: [MessageHandler(Filters.regex('^Сдаться$'), give_up), MessageHandler(~Filters.command, new_answer)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')
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
    reserve_telegram_token = env('RESERVE_TELEGRAM_TOKEN')
    admin_tg_id = env('ADMIN_TG_ID')
    logger.addHandler(TelegramLogsHandler(reserve_telegram_token, admin_tg_id))
    logger.info('Telegram бот начал работу')
    try:
        main(tg_token, questions, r)
    except requests.exceptions.HTTPError:
        logger.error('Telegram бот упал с ошибкой HTTPError')
    except requests.exceptions.ReadTimeout:
        logger.debug('Telegram бот. Wait... I will try to send the request again')
    except requests.exceptions.ConnectionError:
        logger.error('Telegram бот упал с ошибкой ConnectionError')
        time.sleep(10)


if __name__ == '__main__':
    main()
