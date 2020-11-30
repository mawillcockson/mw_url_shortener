"""
Module for generating random characters of a particular length
"""
import random
import secrets
import string
from itertools import islice
from typing import Callable, Iterable


def make_unsafe_random_characters() -> Callable[[int], str]:
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


unsafe_rand_chars = make_unsafe_random_characters()


def safe_rand_chars(num_bytes: int) -> str:
    "Generates a random, url-safe string of specified length"
    return secrets.token_hex(nbytes=num_bytes)
