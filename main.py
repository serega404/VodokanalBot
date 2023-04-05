import requests, json, os
from bs4 import BeautifulSoup
from datetime import datetime

# Config

URL = os.environ.get('VODOKANAL_URL', 'http://www.tgnvoda.ru/avarii.php')
SEND_SILENT = os.environ.get('SEND_SILENT', False)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHANNEL = os.environ.get('TELEGRAM_CHANNEL', '')

if TELEGRAM_TOKEN == '':
    print("Telegram token is not set")
    exit()

if TELEGRAM_CHANNEL == '':
    print("Telegram channel is not set")
    exit()

# Load database

db = None
if (os.path.isfile('data/db.json')):
    with open('data/db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
else:
    print("Database not loaded")

# Get data

req = requests.get(URL)

if (req.status_code != 200):
    print("Request error: " + str(req.status_code))
    exit()

soup = BeautifulSoup(req.content, "html.parser")

elements = []
for tag in soup.find_all('font', size='2', face='VERDANA'):
    date = tag.select_one('font:nth-of-type(1)').b.text
    if not(date.split('.')[0] == str(datetime.today().day).zfill(2) and date.split('.')[1] == str(datetime.today().month).zfill(2)):
        continue
    elements.append(tag.select_one('font:nth-of-type(2)').text.replace('\n', ''))

if elements == []:
    print("No posts")
    exit()

print("The number of posts for this day:", len(elements))

# Send telegram message

def send_message(message):
    req = requests.get("https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage?chat_id=" + TELEGRAM_CHANNEL + "&disable_notification=" + str(SEND_SILENT) + "&text=" + message)
    if (req.status_code != 200):
        print("Telegram request error: " + str(req.status_code))
        exit()
    else:
        print("Telegram message sent, mess id: " + str(req.json()['result']['message_id']))

# Compare db and elements

if db is not None:
    diff = list(set(elements).symmetric_difference(set(db)))
    if diff == []:  
        print("No new posts")
        exit()

    for i in diff:
        send_message(i)
else:
    for element in elements:
        send_message(element)

# Save database

if not os.path.exists("data"):
   os.makedirs("data")

with open('data/db.json', 'w', encoding='utf-8') as f:
    json.dump(elements, f, ensure_ascii=False)
    print("Database updated")
