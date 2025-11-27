FROM python:3.12-slim
EXPOSE 5000
WORKDIR /app

# Installing Cron for scheduling
RUN apt-get update && apt-get install -y cron
# Install dos2unix to ensure that the entrypoint file starts as expected
RUN apt install -y dos2unix

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY scripts/cron/crontab /etc/cron.d/crontab
RUN dos2unix /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab

COPY scripts/app/entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]