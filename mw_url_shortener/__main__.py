"""
This is the file that python runs when this package is run as a module:
https://docs.python.org/3.6/using/cmdline.html#cmdoption-m

python -m mw_url_shortener

It runs the main command-line interface
"""
from .console import main

if __name__ == "__main__":
    main()
