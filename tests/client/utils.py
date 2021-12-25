import asyncio
from typing import Callable, TypeVar

from mw_url_shortener.dependency_injection import initialize_depency_injection

T = TypeVar("T")


def run_test_client(test_command: Callable[[], T]) -> T:
    async def runner() -> T:
        initialize_depency_injection()

        return await asyncio.get_running_loop().run_in_executor(None, test_command)

    return asyncio.run(runner())
