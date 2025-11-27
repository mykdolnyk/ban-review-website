#!/bin/sh

echo "Migrating the DB..."
python -u -m flask --app app/run db upgrade

echo "Starting Cron..."
service cron start

echo "Misc Configuration..."
mkdir /var/log/pinban/

echo "Set Up Done! Proceeding further..."
exec "$@"