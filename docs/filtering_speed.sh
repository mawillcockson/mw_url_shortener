#!/bin/sh
set -eu
SETUP='
from mw_url_shortener.utils import unsafe_random_string
from filter_unwanted_unicode_codepoints import unsafe_random_string as unsafe_random_string2
length = 100_000
'
python -m timeit -s "${SETUP}" 'unsafe_random_string(length)'
python -m timeit -s "${SETUP}" 'unsafe_random_string2(length)'
