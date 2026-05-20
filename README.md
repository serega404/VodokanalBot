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

## Библиотеки

* [Requests](https://requests.readthedocs.io/en/latest/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## Лицензия

Распространяется под MIT License. Смотри файл [`LICENSE`](./LICENSE) для того что бы узнать подробности.
