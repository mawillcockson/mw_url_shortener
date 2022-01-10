#!/bin/sh
set -eu
export MW_URL_SHORTENER__DATABASE_PATH="$(pwd)/temp.sqlitedb"

mw-redir-server \
    debug \
    --database-path "${MW_URL_SHORTENER__DATABASE_PATH}"
