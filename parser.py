import json
import os
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup


DEFAULT_DB_PATH = "data/db.json"
DEFAULT_VODOKANAL_URL = "http://www.tgnvoda.ru/avarii.php"

@dataclass(frozen=True)
class Post:
    date: str
    text: str

    @property
    def key(self):
        return self.date + "$" + self.text


def create_session(proxy_url=""):
    session = requests.Session()

    if proxy_url:
        session.proxies.update({
            "http": proxy_url,
            "https": proxy_url,
        })

    return session

def load_database(path=DEFAULT_DB_PATH):
    if not os.path.isfile(path):
        print("Database not loaded")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_database(posts, path=DEFAULT_DB_PATH):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, "w", encoding="utf-8") as f:
        json.dump([post.key for post in posts], f, ensure_ascii=False)
        print("Database updated")


def fetch_posts(session, url, today=None):
    req = session.get(url)

    if req.status_code != 200:
        raise RuntimeError("Request error: " + str(req.status_code))

    return parse_posts(req.content, today=today)


def parse_posts(content, today=None):
    today = today or datetime.today()
    soup = BeautifulSoup(content, "html.parser")

    posts = []
    for tag in soup.find_all("font", size="2", face="VERDANA"):
        date = tag.select_one("font:nth-of-type(1)").b.text
        if not is_today(date, today):
            continue

        text = tag.select_one("font:nth-of-type(2)").text.replace("\n", "")
        posts.append(Post(date=date, text=text))

    return posts


def is_today(date, today):
    day, month = date.split(".")[:2]
    return day == str(today.day).zfill(2) and month == str(today.month).zfill(2)


def get_new_posts(posts, database):
    if database is None:
        return posts

    database_keys = set(database)
    return [post for post in posts if post.key not in database_keys]


def publish_new_posts(send_message, session, db_path=DEFAULT_DB_PATH):
    database = load_database(db_path)
    posts = fetch_posts(session, DEFAULT_VODOKANAL_URL)

    if not posts:
        print("No posts")
        return

    print("The number of posts for this day:", len(posts))

    new_posts = get_new_posts(posts, database)
    if not new_posts:
        print("No new posts")
        return

    for post in new_posts:
        send_message(post.text)

    save_database(posts, db_path)
