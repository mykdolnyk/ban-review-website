#!/bin/bash
LOG_FILE="/var/log/pinban/thread_deletion.log"

cd /app

# Catch the output
OUTPUT=$(/usr/local/bin/python -m flask --app app/run conversations deleteoldthreads 2>&1)

# Log the data
echo "$(date '+%Y-%m-%d %H:%M:%S') - $OUTPUT" >> "$LOG_FILE" 