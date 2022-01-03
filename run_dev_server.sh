#!/bin/sh
set -eu
export MW_URL_SHORTENER__DATABASE_PATH="$(pwd)/temp.sqlitedb"
export MW_URL_SHORTENER__JWT_SECRET_KEY="not very secret"

hypercorn \
    mw_url_shortener.server.routes:app \
    --worker-class uvloop \
    --access-logfile -\
    --error-logfile -\
    --debug \
    --reload
