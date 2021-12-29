"""
it's the mutable default parameter:

https://towardsdatascience.com/python-pitfall-mutable-default-arguments-9385e8265422
"""
from typing import List


def function_with_mutable_default_parameter(
    items: List[str] = [],
) -> List[str]:
    items.append("item1")

    return items


def test_call_without_parameters() -> None:
    items = function_with_mutable_default_parameter()

    assert len(items) == 1


def test_second_time_just_to_be_sure() -> None:
    items = function_with_mutable_default_parameter()

    assert len(items) == 1, f"somehow got more than 1 item!\n{items}"
