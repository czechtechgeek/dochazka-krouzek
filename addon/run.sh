#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting Docházka server..."

cd /app

# Database stored in persistent config dir
export SQLITE_URL="sqlite:////config/dochazka.db"
export PORT=9120
python3 -u app.py