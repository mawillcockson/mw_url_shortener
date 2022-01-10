#!/bin/sh
set -eu
export MW_URL_SHORTENER__DATABASE_PATH="$(pwd)/temp.sqlitedb"
export MW_URL_SHORTENER__JWT_SECRET_KEY="not very secret"

mw-redir-server debug
