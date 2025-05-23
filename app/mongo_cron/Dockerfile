FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y cron mongodb-clients && \
    mkdir -p /data/backup

COPY backup.sh /usr/local/bin/backup.sh
COPY crontab.txt /etc/cron.d/mongo-cron

RUN chmod +x /usr/local/bin/backup.sh && \
    chmod 0644 /etc/cron.d/mongo-cron && \
    crontab /etc/cron.d/mongo-cron

CMD cron -f