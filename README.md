# mw_url_shortener

A server that hosts a URL shortener

## Installation

Can be installed with `pip`, but [`pipx`][] is recommended:

```sh
python -m pip install --user --upgrade pipx
python -m pipx ensurepath
python -m pipx install mw_url_shortener
```

While it's not recommended, do note that when installing with `pip`, if
`pip` is not new enough, an error will be thrown when install `orjson`.
To avoid this, and install the package, upgrade `pip` first:

```sh
python -m pip install --user --upgrade pip setuptool wheel
python -m pip install mw_url_shortener
```

`pipx` does this automatically, as well as creating an isolated
environment for each installed package.

## Setup

```sh
mw_url_shortener setup
```

## Documentation

First, run:

```sh
mw_url_shortener server --docs
```

Then visit the URL it shows, likely
[`http://localhost:8000/api/docs`](http://localhost:8000/api/docs).

Also, check out the `--help` flag (the example below may not be up to
date):

```sh
mw_url_shortener --help
```


[`pipx`]: <https://pipxproject.github.io/pipx/>
