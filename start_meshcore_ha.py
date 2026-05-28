import os

from parser import create_session, publish_new_posts


PROXY_URL = os.environ.get('PROXY_URL', '')
HOME_ASSISTANT_URL = os.environ.get('HOME_ASSISTANT_URL', '')
HOME_ASSISTANT_WEBHOOK_ID = os.environ.get('HOME_ASSISTANT_WEBHOOK_ID', '')
HOME_ASSISTANT_WEBHOOK_CHANNEL = os.environ.get('HOME_ASSISTANT_WEBHOOK_CHANNEL', '0')


def create_webhook_url():
    return (
        HOME_ASSISTANT_URL.rstrip('/')
        + "/api/webhook/"
        + HOME_ASSISTANT_WEBHOOK_ID
    )


def send_webhook_message(session, message):
    req = session.get(
        create_webhook_url(),
        params={
            'channel': HOME_ASSISTANT_WEBHOOK_CHANNEL,
            'message': message,
        },
    )
    if not 200 <= req.status_code < 300:
        print("Home Assistant webhook request error: " + str(req.status_code))
        exit()
    else:
        print("Home Assistant webhook message sent")


def main():
    if HOME_ASSISTANT_URL == '':
        print("Home Assistant URL is not set")
        exit()

    if HOME_ASSISTANT_WEBHOOK_ID == '':
        print("Home Assistant webhook id is not set")
        exit()

    session = create_session(PROXY_URL)
    try:
        publish_new_posts(
            send_message=lambda message: send_webhook_message(session, message),
            session=session,
        )
    except RuntimeError as error:
        print(error)
        exit()


if __name__ == "__main__":
    main()
