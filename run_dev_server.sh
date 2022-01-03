#!/bin/sh
set -eu
export MW_URL_SHORTENER__DATABASE_PATH="$(pwd)/temp.sqlitedb"

hypercorn \
    mw_url_shortener.server.routes:app \
    --worker-class uvloop \
    --accesslog-file -\
    --errorlog-file -\
    --debug \
    --reload
