from string import ascii_letters, digits
from typing import List, Tuple, Union

import pytest

from mw_url_shortener.utils import orjson_dumps, safe_random_chars, unsafe_random_chars


def test_orjson_dumps_types() -> None:
    """
    Tests that orjson_dumps returns strings, and not bytes
    """
    # NOTE:TESTS::RANDOMIZATION not randomization necessary here
    example_dict = {
        "words words": "more words",
        "word 1 and 2": {
            "words words words": "words words",
            "a": 1.1,
        },
        "": 1,
    }
    output = orjson_dumps(example_dict, default=repr)
    assert isinstance(output, str)


def test_unsafe_random_chars() -> None:
    """
    Ensures that random chars returns both:
    - Returns only strings
    - Matches the length given
    - Only characters in A-Z a-z 0-9
    """
    length = 100
    characters = unsafe_random_chars(length)
    assert isinstance(characters, str)
    assert len(characters) == length

    # NOTE:TESTS::RANDOMIZATION randomize the length requested
    allowed_characters = ascii_letters + digits
    for character in characters:
        assert character in allowed_characters


# NOTE:TESTS::RANDOMIZATION randomize selection of non-numeric types
@pytest.mark.parametrize(
    "var", ["string", b"\xff\xff", object(), list((1, 2, 3)), tuple((1, 2, 3))]
)
def test_unsafe_random_chars_bad_types(
    var: Union[str, bytes, object, List[int], Tuple[int, int, int]]
) -> None:
    """
    Checks if random chars throws errors on bad input length
    """
    with pytest.raises(TypeError) as err:
        unsafe_random_chars(var)
    assert "unsafe_random_chars only takes positive integer values" in str(err.value)


@pytest.mark.parametrize(
    "var",
    [
        -1,
        -0.01,
        0,
    ],
)
def test_unsafe_random_chars_bad_values(var: Union[int, float]) -> None:
    """
    Checks if random chars throws errors on bad input length
    """
    with pytest.raises(ValueError) as err:
        unsafe_random_chars(var)
    assert "unsafe_random_chars only takes positive integer values" in str(err.value)


def test_safe_random_chars() -> None:
    """
    Ensures that random chars returns both:
    - Returns only strings
    - Matches the length given
    - Only characters in A-Z a-z 0-9
    """
    length = 100
    characters = safe_random_chars(length)
    assert isinstance(characters, str)
    assert (
        len(characters) == length * 2
    )  # https://docs.python.org/3/library/secrets.html#secrets.token_hex

    # NOTE:TESTS::RANDOMIZATION randomize the length requested
    allowed_characters = ascii_letters + digits
    for character in characters:
        assert character in allowed_characters


# NOTE:TESTS::RANDOMIZATION randomize selection of non-numeric types
@pytest.mark.parametrize(
    "var", ["string", b"\xff\xff", object(), list((1, 2, 3)), tuple((1, 2, 3))]
)
def test_safe_random_chars_bad_types(
    var: Union[str, bytes, object, List[int], Tuple[int, int, int]]
) -> None:
    """
    Checks if random chars throws errors on bad input length
    """
    with pytest.raises(TypeError) as err:
        safe_random_chars(var)
    assert "safe_random_chars only takes positive integer values" in str(err.value)


@pytest.mark.parametrize(
    "var",
    [
        -1,
        -0.01,
        0,
    ],
)
def test_safe_random_chars_bad_values(var: Union[int, float]) -> None:
    """
    Checks if random chars throws errors on bad input length
    """
    with pytest.raises(ValueError) as err:
        safe_random_chars(var)
    assert "safe_random_chars only takes positive integer values" in str(err.value)
