# VodokanalParser

[![MIT License](https://img.shields.io/github/license/serega404/VodokanalBot)](https://github.com/serega404/VodokanalBot)

## Запуск в Docker

``` Docker
docker volume create vodokanal_bot_data
docker run -d --name VodokanalBot \
    --restart=always \
    -v vodokanal_bot_data:/app/data \
    -e TZ='Europe/Moscow' \
    -e TELEGRAM_TOKEN='TOKEN' \
    -e TELEGRAM_CHANNEL='CHAT_ID' \
    ghcr.io/serega404/vodokanalbot:main
```

## Запуск в Docker Compose

Укажи `TELEGRAM_TOKEN` и `TELEGRAM_CHANNEL` в [`docker-compose.yml`](./docker-compose.yml), затем запусти:

``` Docker
docker compose up -d --build
```

## Интеграции

Бот проверяет сообщения каждые 10 минут. Параллельные запуски защищены
файловой блокировкой: если предыдущий запуск ещё работает, очередная проверка
пропускается, не помечая сообщения обработанными. Следующий успешный запуск
снова сравнит сообщения за текущий день с базой.

Один запуск ограничен 9 минутами. Запрос к сайту водоканала имеет таймаут
10 секунд на подключение и 60 секунд ожидания данных, запросы к Telegram —
60 секунд. База `data/db.json` заменяется атомарно, чтобы прерывание записи
не повредило предыдущие данные.

Общая логика парсинга, работы с `data/db.json` и поиска новых сообщений вынесена в [`parser.py`](./parser.py).

Для новой интеграции достаточно создать свой адаптер отправки и передать его в `publish_new_posts`:

``` Python
from parser import create_session, publish_new_posts

session = create_session()

publish_new_posts(
    send_message=lambda message: print(message),
    session=session,
    url="http://www.tgnvoda.ru/avarii.php",
)
```

## Библиотеки

* [Requests](https://requests.readthedocs.io/en/latest/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## Лицензия

Распространяется под MIT License. Смотри файл [`LICENSE`](./LICENSE) для того что бы узнать подробности.
