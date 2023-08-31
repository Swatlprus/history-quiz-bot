# ВК и Telegram бот викторина
Два бота: ВК и Telegram, которые предназначены для проведения викторины

## Подготовка к запуску
Для запуска сайта вам понадобится Python 3.8+ версии. 

Чтобы скачать код с Github, используйте команду:
```shell
git clone git@github.com:Swatlprus/history-quiz-bot.git
```
Для создания виртуального окружения используйте команду (Linux):
```shell
python3 -m venv venv
```
Для установки зависимостей, используйте команду:
```shell
pip3 install -r requirements.txt
```
## Настройка переменных окружения
Создайте файл `.env.` в корне проекта. Пример .env файла:
```shell
QUIZ_FOLDER='./quiz-questions'
TG_TOKEN='1230fefewfewfew'
VK_TOKEN='vk1.a.N0bsDfsdfsdtiWjc9xdsuF_v'
RESERVE_TELEGRAM_TOKEN='1fsdf5tg40fefewfewfew'
ADMIN_TG_ID='31636552'
REDIS_HOST='redis-15322.c135.com'
REDIS_PORT='15322'
REDIS_PASSWORD='6f0auLPutretlkmLWtretfTvaUkc'
```
Описание Переменных окружения:
QUIZ_FOLDER - путь к папке, где находятся txt файлы с вопросами<br>
TG_TOKEN - Токен от Telegram бота. Создать его можно через https://t.me/BotFather<br>
VK_TOKEN - Токен от группы ВК. Получить его можно в настройках группы<br>
RESERVE_TELEGRAM_TOKEN - Токен от Telegram бота, который будет оповещать вас об ошибках. Создать его можно через https://t.me/BotFather<br>
ADMIN_TG_ID - Уникальный ID чата админа, куда будут приходит уведомления о работе бота. Узнать свой можно с помощью бота - https://t.me/userinfobot<br>
REDIS_HOST - Адрес от базы Redis<br>
REDIS_PORT - порт от базы Redis<br>
REDIS_PASSWORD - пароль от базы Redis<br>

## Как запустить локально
Команда для запуска проекта локально (Linux).
Запуск бота в Telegram
```shell
python3 tg_bot.py
```

Запуск бота в Вконтакте
```shell
python3 vk_bot.py
```

## Как запустить на сервере
Необходимо настроить демонизацию (https://dvmn.org/encyclopedia/deploy/systemd-tutorial/).
Для этого в папке `etc/systemd/system` создайте файл `tgbot.service` с таким содержимым:

```
[Service]
ExecStart=/opt/history-quiz-bot/venv/bin/python3 /opt/history-quiz-bot/tg_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

ExecStart - указываем путь к python3 (который принадлежит к venv) и путь к скрипту для запуска бота (tg_bot.py)<br>
Restart - Перезапускает бота, если произошел какой-либо сбой<br>
WantedBy - Запускает бота, если сервер перезагрузился<br>

Далее запустите юнит с помощью команды:
```shell
systemctl start tgbot
```

И добавьте юнит в автозагрузку сервера:
```shell
systemctl enable tgbot
```

Проверить, запустился ли юнит, используйте команду:
```shell
systemctl status tgbot
```

Аналогично нужно проделать и для Вконтакте-бота.

## Запуск с помощью Docker

На основе файла Dockerfile, создадим образ:
```
sudo docker build -t quizbot:1.0 .
```
Где:<br>
`quizbot` - название образа<br>
`1.0` - версия образа

Не забываем поставить точку в конце, что означает текущую директорию

Команда для проверки созданного образа:
```shell
sudo docker images
```

Запустим контейнер с нашим образом:
```shell
sudo docker run --env-file .env quizbot:1.0
```
Где:<br>
`.env` - файл с переменным окружения Python<br>
`quizbot` - название образа
`1.0` - версия образа

Посмотреть список запущенных контейнеров:
```shell
sudo docker ps
```