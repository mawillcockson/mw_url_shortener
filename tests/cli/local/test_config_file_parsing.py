"""
if the config is given in a file, can the app:

- find the config through a command line option
- find the config through an environment variable
- fall back on a default

I don't know if the last one is very testable, or useful to test: if I know
that it can read from a config file, and I know that it can use the config
filepath given to it, I think it's safe to assume that a straightforward
fallback to the default configuration would perform the same thing.
"""
