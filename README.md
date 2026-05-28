# VodokanalParser

[![MIT License](https://img.shields.io/github/license/serega404/VodokanalBot)](https://github.com/serega404/VodokanalBot)

## Запуск TG интеграции в Docker

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

### Запуск в Docker Compose

Укажи `TELEGRAM_TOKEN` и `TELEGRAM_CHANNEL` в [`docker-compose.yml`](./docker-compose.yml), затем запусти:

``` Docker
docker compose up -d --build
```

## Запуск с MeshCore + Home Assistant

Вариант для MeshCore отправляет новые сообщения в webhook Home Assistant, а Home Assistant пересылает их в канал MeshCore.

1. Добавь в Home Assistant автоматизацию [`Webhook to MeshCore channel`](https://github.com/serega404/HA-MeshCore#webhook-to-meshcore-channel).
2. Замени `CHANGE_ME_RANDOM_WEBHOOK_ID` в автоматизации на случайную строку.

``` Docker
docker volume create vodokanal_bot_data
docker run -d --name VodokanalBot \
    --restart=always \
    -v vodokanal_bot_data:/app/data \
    -e TZ='Europe/Moscow' \
    -e HOME_ASSISTANT_WEBHOOK_ID='CHANGE_ME_RANDOM_WEBHOOK_ID' \
    -e HOME_ASSISTANT_URL='http://homeassistant.local:8123' \
    -e HOME_ASSISTANT_WEBHOOK_CHANNEL='0' \
    ghcr.io/serega404/vodokanalbot-meshcore-ha:main
```

### Запуск в Docker Compose

Укажи `HOME_ASSISTANT_WEBHOOK_ID` и `HOME_ASSISTANT_WEBHOOK_CHANNEL` в [`docker-compose.ha.yml`](./docker-compose.ha.yml), затем запусти:

``` Docker
docker compose up -d --build -f docker-compose.ha.yml
```

## Интеграции

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
