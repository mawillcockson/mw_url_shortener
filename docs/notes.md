# Notes

These are my notes about and for the development process.

## Interface

### Firt-time setup

I'm hoping for installation to look something like this:

```
python -m pip install --user -U pipx
python -m pipx ensurepath
python -m pipx install mw_url_shortener
exec "${SHELL}"
mw_url_shortener
>> No config found; run 'mw_url_shortener setup' to create on
mw_url_shortener setup
>> First-time setup
>> No database found
>>> [C]reate one, [u]se existing: C
>> Database location:
>>> [Empty for default (~/.mw_url_shortener/urls.db)]: 
>> Add user?
>>> [Y]es, [n]o I'll add one myself: y
>>>> Username: example
>>>> Password: 
>> Generate systemd files?
>>> [u]ser, [s]ystem, [N]o: s
>> Systemd unit file created
>> To start the server, run:
>> systemctl enable mw_url_shortener
```

### Local database manipulation

A cli method of entering new URLs:

```
$ mw_url_shortener add 'https://example.com/awesome-page'
short-link: /aF3
$ mw_url_shortener add 'https://example.com/another-page' awesome
short-link: /awesome
```

#### Implementation

Could the FastAPI TestClient be used for manipulating the database locally? That way, the configuration can be injected and everything.

#### Unauthenticated local access

I picture the local version doing the same thing as the remote version, but using "`127.0.0.1`" for the URL instead.

It could also directly use the database calls from 
In order to have the interaction above, 

### Multiple keys shortcut

Any way that they're entered, there should be a mechanism to give multiple short links for one link. For example:

```
$ mw_url_shortener add 'https://example.com/another-page' awesome-thing awesome_thing awesomething
short-links: /awesome-thing /awesome_thing /awesomething
```

### Finding a new key

I prefer generating the keys randomly, so that it's more difficult to iterate through them. If I'm running this on my own, I don't want someone to be able to look at all of my links very easily. [`fail2ban` integration would help](#integrate-with-fail2ban), but still.

Python has a a builtin function `random.choice`, which is what's currently being used to generate keys. As the number of used keys goes up, especially if the key length stays the same, eventually the probability of generating a key that's already been chosen reaches an appreciable amount.

At some point, I want to implement a threshold setting, that takes an integer representing the percentage of the keyspace that's already been taken, and once that threshold is reached, it bumps the key length up by 1.

Also, I want the algorithm to keep count of how many duplicate keys have been generated in a row, and to have a different threshold value that, when reached, it will switch globally from generating the keys randomly, to generating them with linearly with something like `itertools.product`.

That way, if the "percent filled" threshold is 100%, the algorithm wouldn't spend forever searching for that last one. It may take a minute, but on my laptop, with my bad algorithm, written in Python, it takes about 572 msec to iterate through the whole key space of 4 characters.

However, that's without database lookups in between. Still, I think a threshold of something like 10 to 50 duplicate keys in a row would be a good time to move to a larger key space.

Also, it would be especially cool if the generator could be pickled, so that it could be resumed on server start, so that it doesn't have to spend time playing catch up on the first create request if it's already been using the linear algorithm for a while.

For now, I'm going to optimistically hope that I don't need to do any of that, but I will add in a check that will give up after 10 failed attempts. I want to make this configurable once I figure out the configuration situation.

### Integrate with fail2ban

Being able to at least ban an address that's generating a lot of 404s would be nice. Same thing for attempts at brute-forcing the api authentication.

## Authentication

It would be awesome if it could authenticate users with the same mechanism that miab uses, as that would eliminate the need to store authentication information in the same database.

## Features

### Emoji normalization

Also, I'd want an option for emoji normalization, where things like {❤️, 🧡, 💛} and {👃, 👃🏿} are both collapsed to one common key (e.g. either a textual representation, like "heart" and "nose", or an emoji representation).

It'd be important for this to be a setting that defaults to on, so that emoji links work, but can be turned off.


### `base64url` or `base62`

Speaking of, it might be a good idea to drop `-` and `_`, as even without them, 2, 3, and 4-characters strings still hold a lot of possible entries:

- 2: 3,844
- 3: 238,328
- 4: 14,776,336

Also, thankfully, SQLite would be able to handle that many rows, as [indicated on their page of limits](https://www.sqlite.org/limits.html), and all the rest of the databases would, too.

I think a default string length of 3 would be sufficient for most people. Of course, these defaults would be listed and changeable during setup, and in the config file.

An extended feature to work on would be link generation using a word list, and allowing arbitrary separators:

```
a.test/two words
a.test/two-words
a.test/two_words
a.test/TwoWords
a.test/twowords
```

That last one would be challenging, especially if mixed with the random characters thing. The first one appears to be parsed correctly when typed into address bars, but the link would have to be percent-encoded if it's to be posted anywhere.

### Automatic upgrades

A feature I'd like to add to make it "production-ready" would be automatic upgrades. It wouldn't be too difficult to have the server poll its own GitHub repository for releases.

Then I guess one way to update things would be to figure out how it was installed, spawn a detached process, and run update commands from that detached process.

The downside is this wouldn't be very resilient to things like power-loss, or glitches that cause the update process to crash. Also, if the update causes issues, there's no way to automatically roll back.

On the page [Appropriate Uses for SQLite](https://www.sqlite.org/whentouse.html), it mentions the idea of using a SQLite database as a method of transferring data.

It would certainly be an interesting idea:

- Package the files from the release into a SQLite database, attached to the release as an asset
- The server downloads the db, merges the contents with an `update` table or something
- Restarts itself
- As part of startup, a custom import function is able to read the db
- The main process tries to `import` the updated files instead of the current ones
- If there's an error that doesn't crash the entire server, it's logged
- After the server is restarted, if there's an error logged that somehow ties to the update,
  either through chronology or a database relation, the update is marked as bad
- Otherwise, the server continues to load the updates on every boot

This seems like it could be complicated to implement, but also in theory sounds less susceptible to mishaps than the separate update process.

Of course, the first version will not have an auto-update function. Way easier to simply let the administrator decide when to update.

Also, the [uvicorn documentation has a note about how gunicorn can make live updating easier](http://www.uvicorn.org/deployment/#using-a-process-manager). This is something I want to know more about.

### Configuration

As part of configuration, I'd love to have an option for hiding the administrative API at a url, either randomly generated or user-provided. For example:

```
https://example.com/OlZmBacdnh/{api_endpoints}
```

This way, someone would have a 0.00000000000000011915% chance of guessing the correct endpoint, and it would take 2,660 years to enumerate all of the possibilities at 10 million guesses per second.

If this application is run on a server that is reached through multiple hostnames, then the current design would have it return the same redirects, regardless of the hostname.

To change this, multiple servers can be run behind a proxy, with the proxy redirecting traffic to different hostnames to different servers.

That'd be the simple solution.

The other solution would be to allow an option that, when set, turns on a more complex scheme:

- Instead of storing redirects using their key as the Primary Key, they can be stored with a database-generated Primary Key
- In addition, all of the potential headers and metadata about a request can be specified when creating a redirect, and the redirect will be shown only if all the set parameters match
- The key would still form an index, but the index wouldn't have unique keys

For example:

- `a.example/key` and `b.example/key` would resolve to different URIs
- `example.com/key` and `example.org/key` would resolve to different URIs

It might be better to use this scheme all the time, and the config option determines whether the host name should be used to differentiate requests.

### Expiring Redirects

A cool feature to add would be expiring redirects. Two major ways I can think of expiring them:

1. By number of uses
1. By time

The first one would be very easy to implement: A counter associated with the entry is incremented, and once it equals or exceeds a limit, the entire redirect is deleted.

The second one would be a bit more difficult:

I would not want any polling, so one technique I've heard of would be to start a scheduler.

Another technique would be storing the expiration date, and if the entry is accessed after that expiration date:

1. It behaves as if there's no entry
1. It deletes the expired entry

There would also be a nightly vacuuming routine that goes through all timed entries and deletes them if they're expired.

The one issue I'd be worried about is funnybusiness with timezones:

1. an entry is created with an expiration in 2 hours, at 4:00 P.M. GMT (UTC+0)
1. the database is backed up
1. the backup is restored on a computer in the PST (UTC-8) timezone
1. the redirect is accessed

This would probably be fine if the date and time are stored with timezone information, but the worrisome part is that this completely relies on the date and time to be set correctly on the local computer, as well as the timezone.

With a running, in-memory task, it would take care of itself, regardless of whether or not the timezone has been changed while the computer is running (Daylight Saving Time).

However, this would still be an issue in the above scenario, when saving and loading the database, and it's unlikely that proper datetime timestamps would not be able to handle timezones changing while it's running, any differently than loading them on startup.

### Export and Import of Configuration and Data

### Image hosting

An unexpected feature is image hosting: if the image is encoded in a "`data:`" URI, it will be returne in the redirect, and the browser appears to simply disply the image as expected.

For example:

```
data:image/gif;base64,R0lGODlhEAAQAMQAAORHHOVSKudfOulrSOp3WOyDZu6QdvCchPGolfO0o/XBs/fNwfjZ0frl3/zy7////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAkAABAALAAAAAAQABAAAAVVICSOZGlCQAosJ6mu7fiyZeKqNKToQGDsM8hBADgUXoGAiqhSvp5QAnQKGIgUhwFUYLCVDFCrKUE1lBavAViFIDlTImbKC5Gm2hB0SlBCBMQiB0UjIQA7
```

Will work just fine when returned by the application. This could be made easier by the application providing an API to receive these images, limited in file size by the server, and then will encode them and store them as the redirect URI.

That way, something like `example.com/i/fekjnfkjn.jpg` would return an image directly.

## Random character generator

Random character generator, quick and dirty:

```python
import string
from random import choice
from itertools import islice
from typing import Iterable

VALID_CHARS = list(set(string.ascii_letters + string.digits + "-_"))


def rand_char() -> str:
    "returns a random character from CHARS"
    return choice(VALID_CHARS)


def char_gen() -> Iterable[str]:
    "makes an infinite generator of random characters"
    while True:
        yield rand_char()


chars = char_gen()


def rand_chars(num: int) -> str:
    "produces a string of length num of random characters"
    return "".join(islice(chars, abs(int(num))))
```

Now as a factory:

```python
"a factory function for a random character generator"
import random
import string
from itertools import islice
from typing import Callable, Iterable


def make_random_characters() -> Callable[[int], str]:
    """
    Returns a function that produces strings of specified length,
    composed of random characters
    """
    valid_chars = list(set(string.ascii_letters + string.digits + "-_"))

    def char_gen() -> Iterable[str]:
        "makes an infinite generator of random characters"
        while True:
            yield random.choice(valid_chars)

    chars = char_gen()

    def rand_chars(num: int) -> str:
        "produces a string of length num of random characters"
        return "".join(islice(chars, abs(int(num))))

    return rand_chars


random_characters = make_random_characters()
```

It doesn't need to generate random characters securely, as it's only used to come up with an identifier for a URL, and not a password, and it's fine if someone can predict the next link, and it's even fine if someone can enumerate the whole space.

It also doesn't need to be fast, as I only intend this to be called on average once every few minutes, at the most extreme upper-end, unless I intend to deploy this on an extremely busy site, but then I'd probably want to rearchitecture a lot of the application. It's also only generating a few characters at a time. If it's generating a lot, then it's not much of a short URL.

### Local API documentation

Documentation should be able to be viewed locally, without having to configure the server:

```
mw_url_shortener server --docs --port 8000
```

How would the authenticated part of the API be demoed?

- `--user` option: `--user "username:password"`
- All authentication passes (controlled by setting `--docs`)
- It's just documentation: `--just-docs`

## Testing

This should only be tested against the [currently supported versions of python](https://endoflife.date/python).

And the current python package version in the version of Ubuntu MIAB runs on: Python 3.6.9

Currently, this list is:

- 3.6.5
- 3.6.7
- 3.6.9
- 3.6.12
- 3.7.9
- 3.8.6
- 3.9.0

## Minimum Viable Product

MVP would be no authentication, and possibly no database: just an in-memory table, with a routine for creating a new user and password for API authentication on startup.

## Implementation

### Unlimited path

Also, using the `"/{chars:path}"` specifier to be able to collect all the path components as one string would be important, so that things like `example.com/h/e/l/l/o` work as expected, though I think including `/` in the list of random characters would be confusing.

### Database persistence

If run with `--reload`, another process is created, and that process does not share global state with the initial process, which means that my previous attempt of having an in-memory database as part of the MVP won't work, and neither will creating a temporary database, as both are created each time the process is started.

Instead, a persistent database file is needed, and the whole path has to be enumerated, as Python is started from various locations.

I think a solid solution is to require the database file be added set in an environment variable. That way, it's always available, to every thread, and every child process.

Python can also set it's own environment, but there's a note about that causing memory leaks on FreeBSD and MacOS.

I'm sure there's got to be a solution out there that would work better than using the environment for state management.

Something crazy like starting a separate process to act as a message brokering service, and will respond with the current database file.

I'll admit that the above idea is inspired from reading the synopsis for ZeroMQ, and seeing that Python has a mature binding for it.

Really, though, and network server, available at a well-known location, would be great. One that only responds to traffic from the application, and can store some state.

I was wondering how it'd work if the `config.get` function would first check to see if there's a valid `_config` variable set in the module, and return a copy of that if there is.

That way, it only really needs to gather all the settings once per worker process, hopefully. Are module variables given to each thread? Probably not. I've heard that sharing memory between threads is something that requires extra-special handling, not just setting a global variable.

### Client

I think the project should share as much implementation with the client as possible. I'm thinking the ORM would be very handy to share, so that the database can be interacted with locally.

I'm picturing something like:

```sh
pip install mw-url-shortener
```

gets the client and server code, but doesn't install the server code "script" and doesn't install the packages the server needs to run.

```sh
pip install mw-url-shortener[server]
```

installs both: `mw-redir` and `mw-redir-server`.

#### Usage

Examples:

```sh
$ mw-redir --local user add admin
No settings found in default location (~/.config/mw_url_shortener/0.0.5/config.json)
Path to database file: /var/db/redirects.sqlite
Create database? (Y/n):
Creating database at '/var/db/redirects.sqlite'
Adding user 'admin' with user ID 0
Password:
Again:
User 'admin' added
```

#### Design

I think the client and server should share as much as possible.

Currently, I'm thinking the database access layer would probably be shared wholesale. Much of that will be async since FastAPI can use async functions, so there'll have to be some use of either `asyncio`, or more likely, `trio` in the client to be able to call the DB functions.

It also hopefully means the database functions will be tested before the server portion is added, reducing the surface the new tests would have to cover.
