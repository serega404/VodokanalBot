FROM python:3.11.2-alpine3.17

LABEL Maintainer="serega404"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Setting up crontab
COPY crontab /tmp/crontab
RUN cat /tmp/crontab > /etc/crontabs/root

COPY main.py main.py

# run crond as main process of container
CMD ["crond", "-f", "-l", "2"]