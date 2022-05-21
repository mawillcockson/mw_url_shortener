"""
https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html#via-a-python-file
"""
if """
this is only necessary because this file isn't part of the mw_url_shortener
module, and the directory it's in is not in the import path
""":
    import os
    import sys

    sys.path.append(os.getcwd())

from hypercorn_access_log_class import JSONLogger

logger_class = JSONLogger
debug = True
accesslog = "-"
errorlog = "-"
use_reloader = True
graceful_timeout = 60
