FROM python:3.12-alpine

LABEL Maintainer="serega404"

WORKDIR /app
ARG START_FILE=start_telegram.py

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Setting up crontab
COPY crontab /tmp/crontab
RUN cat /tmp/crontab > /etc/crontabs/root

COPY ${START_FILE} start.py
COPY parser.py parser.py

# run crond as main process of container
CMD ["crond", "-f", "-l", "2"]
