import os

from parser import create_session, publish_new_posts


URL = os.environ.get('VODOKANAL_URL', 'http://www.tgnvoda.ru/avarii.php')
SEND_SILENT = os.environ.get('SEND_SILENT', False)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHANNEL = os.environ.get('TELEGRAM_CHANNEL', '')
PROXY_URL = os.environ.get('PROXY_URL', '')


def send_telegram_message(session, message):
    req = session.get(
        "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage",
        params={
            'chat_id': TELEGRAM_CHANNEL,
            'disable_notification': str(SEND_SILENT),
            'text': message,
        },
    )
    if (req.status_code != 200):
        print("Telegram request error: " + str(req.status_code))
        exit()
    else:
        print("Telegram message sent, mess id: " + str(req.json()['result']['message_id']))


def main():
    if TELEGRAM_TOKEN == '':
        print("Telegram token is not set")
        exit()

    if TELEGRAM_CHANNEL == '':
        print("Telegram channel is not set")
        exit()

    session = create_session(PROXY_URL)
    try:
        publish_new_posts(
            send_message=lambda message: send_telegram_message(session, message),
            session=session,
            url=URL,
        )
    except RuntimeError as error:
        print(error)
        exit()


if __name__ == "__main__":
    main()
