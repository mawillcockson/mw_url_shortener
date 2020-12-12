"""
tests the redirect part of the database interface
"""
from mw_url_shortener.database.errors import RedirectNotFoundError
from mw_url_shortener.database import redirect
from mw_url_shortener.types import Key, Uri
from .utils import random_redirect, random_uri, random_key
from pony.orm import Database
import pytest


def test_create_redirect(database: Database) -> None:
    "can a redirect be added and read back"
    example_redirect: redirect.Model = random_redirect()

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    returned_redirect = redirect.get(db=database, key=created_redirect.key)
    assert returned_redirect == created_redirect


@pytest.mark.xfail
def test_auto_create_key(database: Database) -> None:
    "can a redirect be created by giving just a key"
    raise NotImplementedError


@pytest.mark.xfail
def test_no_arguments_error(database: Database) -> None:
    "is an error raised if redirect.create is called without enough arguments"
    raise NotImplementedError


def test_create_duplicate_key(database: Database) -> None:
    "is an error raised if a key is already taken"
    example_redirect: redirect.Model = random_redirect()
    example_key: Key = random_key()
    assert example_redirect.key != example_key, "keys need to be different"

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    duplicate_redirect = created_redirect.copy(update={"key": example_key})
    with pytest.raises(KeyError) as err:
        redirect.create(db=database, redirect=duplicate_redirect)
    assert f"a redirect with key '{duplicate_redirect.key}' already exists" in str(err.value)


def test_create_duplicate_uri(database: Database) -> None:
    "is it okay to create a redirect for a uri that already exists"
    raise NotImplementedError


def test_update_redirect(database: Database) -> None:
    "can an existing redirect be modified"
    example_redirect: redirect.Model = random_redirect()
    example_uri: Uri = random_uri()
    assert example_redirect.uri != example_uri, "URIs need to be different"

    created_redirect = redirect.create(db=database, redirect=example_redirect)
    updated_redirect = created_redirect.copy(update={"uri": example_uri})
    redirect.update(db=database, key=created_redirect.key, updated_redirect=updated_redirect)
    returned_updated_redirect = redirect.get(db=database, key=created_redirect.key)
    assert returned_updated_redirect == updated_redirect


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
    assert f"no redirect found with key '{example_redirect.ley}'" in str(err.value)


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
        redirect.update(db=database, uri=updated_redirect.uri, updated_redirect=updated_redirect)
    assert f"no redirect found with uri '{updated_redirect.uri}'" in str(err.value)


@pytest.mark.xfail(raises=NotImplementedError)
def test_delete_user_by_username() -> None:
    "can a redirect be deleted by username"
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_delete_nonmatching_redirect() -> None:
    """
    is an error raised if a deletion is requested for a redirect model that doesn't
    match what's in the database
    """
    raise NotImplementedError


@pytest.mark.xfail
def test_new_key() -> None:
    "redirect.new_key()"
    raise NotImplementedError
