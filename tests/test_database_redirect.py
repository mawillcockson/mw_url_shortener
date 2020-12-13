"""
tests the redirect part of the database interface
"""
import string

import pytest
from pony.orm import Database

from mw_url_shortener.database import redirect
from mw_url_shortener.database.redirect import (
    DuplicateKeyError,
    DuplicateThresholdError,
    Key,
    RedirectNotFoundError,
    Uri,
)

from .utils import all_combinations, random_key, random_redirect, random_uri


def test_create_redirect(database: Database) -> None:
    "can a redirect be added and read back"
    example_redirect: redirect.Model = random_redirect()

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    returned_redirect = redirect.get(db=database, key=created_redirect.key)
    assert returned_redirect == created_redirect


@pytest.mark.timeout(5)
def test_new_key(database: Database) -> None:
    "does new_key() return a unique key"
    sample_keys = (Key("abc"), Key("123"), Key("AFF"))
    example_uri: Uri = random_uri()
    for key in sample_keys:
        redirect.create(db=database, redirect=redirect.Model(key=key, uri=example_uri))

    new_key = redirect.new_key(db=database)
    assert len(str(new_key)) == 3
    for character in str(new_key):
        assert character in (string.ascii_letters + string.digits)


@pytest.mark.timeout(5)
def test_new_key_full(database: Database) -> None:
    "will new_key() give up after a number of duplicate keys have been generated"
    # Fill the database of all single character key combinations
    characters = string.ascii_letters + string.digits
    example_uri: Uri = random_uri()
    for character in characters:
        redirect.create(
            db=database, redirect=redirect.Model(key=Key(character), uri=example_uri)
        )

    # Requesting a new key should throw an error
    with pytest.raises(DuplicateThresholdError) as err:
        redirect.new_key(db=database, length=1)
    assert "duplicate threshold of 10 reached" in str(err.value)


@pytest.mark.xfail
def test_new_key_switch_algorithms() -> None:
    """
    if the duplicate threshold is reached, will new_key() switch to a linear
    algorithm, and will it find the key
    """
    raise NotImplementedError


def test_auto_create_key(database: Database) -> None:
    "can a redirect be created by giving just a key"
    example_uri: Uri = random_uri()

    created_redirect = redirect.create(db=database, uri=example_uri)
    assert created_redirect.uri == example_uri
    assert isinstance(created_redirect, redirect.Model)
    assert redirect.Model(**created_redirect.dict())


def test_no_arguments_error(database: Database) -> None:
    "is an error raised if redirect.create is called without enough arguments"
    with pytest.raises(TypeError) as err:
        redirect.create(db=database)
    assert "need exactly one of either uri or redirect" in str(err.value)


def test_both_arguments_error(database: Database) -> None:
    "is an error raised if redirect.create is called without too many arguments"
    example_redirect: redirect.Model = random_redirect()
    example_uri: Uri = random_uri()

    with pytest.raises(TypeError) as err:
        redirect.create(db=database, redirect=example_redirect, uri=example_uri)
    assert "need exactly one of either uri or redirect" in str(err.value)


def test_create_duplicate_key(database: Database) -> None:
    "is an error raised if a key is already taken"
    example_redirect: redirect.Model = random_redirect()
    example_uri: Uri = random_uri()
    assert example_redirect.uri != example_uri, "URIs should be different"

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    duplicate_redirect = created_redirect.copy(update={"uri": example_uri})
    with pytest.raises(DuplicateKeyError) as err:
        redirect.create(db=database, redirect=duplicate_redirect)
    assert f"a redirect with key '{duplicate_redirect.key}' already exists" in str(
        err.value
    )


def test_create_duplicate_uri(database: Database) -> None:
    "is it okay to create a redirect for a uri that already exists"
    example_redirect: redirect.Model = random_redirect()
    example_key: Key = random_key()
    assert example_redirect.key != example_key, "keys need to be different"

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    duplicate_uri_redirect = created_redirect.copy(update={"key": example_key})
    created_duplicate_uri_redirect = redirect.create(
        db=database, redirect=duplicate_uri_redirect
    )
    assert created_redirect.uri == created_duplicate_uri_redirect.uri
    assert created_redirect.key != created_duplicate_uri_redirect.key


def test_create_duplicate_uri_auto_key(database: Database) -> None:
    "is it okay to ask to create a redirect for the same uri multiple times"
    example_uri: Uri = random_uri()

    created_redirect = redirect.create(db=database, uri=example_uri)
    created_redirect_duplicate_uri = redirect.create(db=database, uri=example_uri)
    assert created_redirect.uri == created_redirect_duplicate_uri.uri
    assert created_redirect.key != created_redirect_duplicate_uri.key


def test_update_redirect(database: Database) -> None:
    "can an existing redirect be modified"
    example_redirect: redirect.Model = random_redirect()
    example_uri: Uri = random_uri()
    assert example_redirect.uri != example_uri, "URIs need to be different"

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    updated_redirect = created_redirect.copy(update={"uri": example_uri})
    redirect.update(
        db=database, key=created_redirect.key, updated_redirect=updated_redirect
    )
    returned_updated_redirect = redirect.get(db=database, key=created_redirect.key)
    assert returned_updated_redirect == updated_redirect
    assert created_redirect.key == returned_updated_redirect.key


def test_delete_redirect(database: Database) -> None:
    """
    if a redirect is deleted, is it removed from the list of redirects,
    and is an error raised when a unique id is used to retrieve it
    """
    example_redirect: redirect.Model = random_redirect()

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    redirect.delete(db=database, redirect=created_redirect)
    redirects = redirect.list(db=database)
    for redir in redirects:
        assert redir != created_redirect
    with pytest.raises(RedirectNotFoundError) as err:
        redirect.get(db=database, key=created_redirect.key)
    assert f"no redirect found with key '{created_redirect.key}'" in str(err.value)


def test_delete_nonexistent_redirect(database: Database) -> None:
    """
    is an error raised when a deletion is performed on a redirect that doesn't
    exist
    """
    example_redirect: redirect.Model = random_redirect()

    with pytest.raises(RedirectNotFoundError) as err:
        redirect.delete(db=database, redirect=example_redirect)
    assert f"no redirect found with key '{example_redirect.key}'" in str(err.value)


def test_redirct_duplicate_deletion(database: Database) -> None:
    "is an error raised when a redirect is deleted a second time"
    example_redirect: redirect.Model = random_redirect()

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    redirect.delete(db=database, redirect=created_redirect)
    with pytest.raises(RedirectNotFoundError) as err:
        redirect.delete(db=database, redirect=example_redirect)
    assert f"no redirect found with key '{example_redirect.key}'" in str(err.value)


def test_update_deleted_redirect(database: Database) -> None:
    """
    is an error raised when an update is performed on a redirect that doesn't exist
    """
    example_redirect: redirect.Model = random_redirect()
    example_uri: Uri = random_uri()
    assert example_redirect.uri != example_uri, "URIs need to be different"

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    redirect.delete(db=database, redirect=created_redirect)
    updated_redirect = created_redirect.copy(update={"uri": example_uri})
    with pytest.raises(RedirectNotFoundError) as err:
        redirect.update(
            db=database, key=updated_redirect.key, updated_redirect=updated_redirect
        )
    assert f"no redirect found with key '{updated_redirect.key}'" in str(err.value)


# NOTE:FEAT Currently, redirects are deleted by looking at the key attribute on
# the model, but they should be deleted by matching the whole redirect structure.
# This would support having a url that returns different redirects based on
# request parameters, like the same key returns one redirect for IPs in one
# region of the world, and another for a different region.
@pytest.mark.xfail()
def test_delete_redirect_by_key() -> None:
    "can a redirect be deleted by key"
    raise NotImplementedError


@pytest.mark.xfail()
def test_delete_nonmatching_redirect() -> None:
    """
    is an error raised if a deletion is requested for a redirect model that doesn't
    match what's in the database
    """
    raise NotImplementedError
