from pprint import pprint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from starlette.requests import Request


def print_request(request: "Request") -> None:
    request_dict = {
        attr: getattr(request, attr)  # type: ignore
        for attr in dir(request)
        if attr not in {"user", "auth", "session", "__dict__"}
    }
    pprint(request_dict)  # type: ignore
