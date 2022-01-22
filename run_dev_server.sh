#!/bin/sh
set -eu
export MW_URL_SHORTENER__DATABASE_PATH="$(pwd)/temp.sqlitedb"
export MW_URL_SHORTENER__JWT_SECRET_KEY="not very secret"
# export MW_URL_SHORTENER__ROOT_PATH="root_path"
export MW_URL_SHORTENER__API_PREFIX="api_prefix"

mw-redir-server debug
