import fcntl
import os
import signal

from parser import create_session, publish_new_posts


URL = os.environ.get('VODOKANAL_URL', 'http://www.tgnvoda.ru/avarii.php')
RUN_TIMEOUT_SECONDS = 9 * 60
TELEGRAM_TIMEOUT = 60
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
        timeout=TELEGRAM_TIMEOUT,
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


def _stop_overdue_run(signum, frame):
    raise SystemExit(f"Bot run exceeded time limit ({RUN_TIMEOUT_SECONDS} seconds)")


def run_once(lock_path="/tmp/vodokanalbot.lock"):
    with open(lock_path, "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Previous run is still active; skipping")
            return
        previous_handler = signal.signal(signal.SIGALRM, _stop_overdue_run)
        try:
            signal.alarm(RUN_TIMEOUT_SECONDS)
            main()
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)


if __name__ == "__main__":
    run_once()
