import string
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from asgi_correlation_id.context import correlation_id
from pydantic import UUID4, ConstrainedInt, Field, IPvAnyAddress

from mw_url_shortener.settings import defaults

from .base import BaseInDBSchema, BaseSchema
from .redirect import Redirect
from .user import User

if TYPE_CHECKING:
    from starlette.responses import Response as StarletteResponse

# Since HTTP doesn't seem to support an empty header name, using an empty
# header name should prevent a client from being able to set a correlation id
# in its request
# https://stackoverflow.com/a/58056620
CORRELATION_ID_HEADER_NAME: str = ""


def now() -> datetime:
    return datetime.utcnow().astimezone()


class Port(ConstrainedInt):
    ge: int = 1
    le: int = 2 ** 16 - 1


class BuiltinActor(Enum):
    cli = "cli"
    api = "api"


class HTTPMethod(Enum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"


class APIResponse(BaseSchema):
    @classmethod
    def from_response(cls, response: "StarletteResponse") -> "APIResponse":
        raise NotImplementedError


class HTTPClient(BaseSchema):
    ip: IPvAnyAddress
    port: Port
    http_version: str
    method: Union[HTTPMethod, str]
    path: bytes
    scheme: Union[Literal["http"], Literal["https"]]
    request_headers: Dict[str, str]
    response: APIResponse
    cookies: Dict[str, str]
    correlation_id: UUID4

    @classmethod
    def from_response(cls, response: "StarletteResponse") -> "HTTPClient":
        http_version = response.request.http_version
        # drop CORRELATION_ID_HEADER_NAME from headers since it has its own
        # attribute
        return cls(
            http_version=http_version,
            method=method,
            path=path,
            scheme=scheme,
            request_headers=request_headers,
            response=APIResponse.from_response(response),
            cookies=cookies,
            client=client,
            correlation_id=correlation_id.get(),
        )


Actor = Union[BuiltinActor, User, HTTPClient]


class Event(BaseSchema):
    actor: Actor


class EventType(Enum):
    user_create = "user_create"
    user_read = "user_read"
    user_update = "user_update"
    user_remove = "user_remove"
    redirect_create = "redirect_create"
    redirect_read = "redirect_read"
    redirect_update = "redirect_update"
    redirect_remove = "redirect_remove"
    redirect_match = "redirect_match"


class UserEvent(BaseSchema):
    user: User


class UserCreateEvent(UserEvent, Event):
    event_type: Literal[EventType.user_create.value] = EventType.user_create.value


class UserReadEvent(UserEvent, Event):
    event_type: Literal[EventType.user_read.value] = EventType.user_read.value


class UserUpdateEvent(UserEvent, Event):
    event_type: Literal[EventType.user_update.value] = EventType.user_update.value
    old_user: User


class UserRemoveEvent(UserEvent, Event):
    event_type: Literal[EventType.user_remove.value] = EventType.user_remove.value


UserEvents = Union[
    UserCreateEvent,
    UserReadEvent,
    UserUpdateEvent,
    UserRemoveEvent,
]


class RedirectEvent(BaseSchema):
    redirect: Redirect


class RedirectCreateEvent(RedirectEvent, Event):
    event_type: Literal[
        EventType.redirect_create.value
    ] = EventType.redirect_create.value


class RedirectReadEvent(RedirectEvent, Event):
    event_type: Literal[EventType.redirect_read.value] = EventType.redirect_read.value


class RedirectUpdateEvent(RedirectEvent, Event):
    event_type: Literal[
        EventType.redirect_update.value
    ] = EventType.redirect_update.value
    old_redirect: Redirect


class RedirectRemoveEvent(RedirectEvent, Event):
    event_type: Literal[
        EventType.redirect_remove.value
    ] = EventType.redirect_remove.value


class RedirectMatchEvent(RedirectEvent, Event):
    event_type: Literal[EventType.redirect_match.value] = EventType.redirect_match.value


RedirectEvents = Union[
    RedirectCreateEvent,
    RedirectReadEvent,
    RedirectUpdateEvent,
    RedirectRemoveEvent,
]

APIEvents = Union[UserEvents, RedirectEvents]


AnyEvent = Union[APIEvents]


class LogBase(BaseSchema):
    date_time: datetime = Field(default_factory=now)
    event: AnyEvent = Field(..., descriminator="event_type")


class LogCreate(LogBase):
    pass


# I don't think I want to support changing the contents of a log entry.
# Deleting, sure, but modifying, no
# class LogUpdate(LogBase):
#     pass


class LogInDBBase(LogBase, BaseInDBSchema):
    pass


class Log(LogInDBBase):
    pass


class LogInDB(LogInDBBase):
    pass
