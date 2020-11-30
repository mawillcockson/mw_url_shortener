"""
Primarily uses https://github.com/tmbo/questionary
"""
from questionary import Separator, prompt
from enum import Enum
from typing import List


class CreateDatabase(str, Enum):
    create = "Create a database"
    use_existing = "Use an existing database (choose file)"

    def __str__(self) -> str:
        """
        from:
        https://www.cosmicpython.com/blog/2020-10-27-i-hate-enums.html
        """
        return str.__str__(self)


questions = [
    {
        "type": "select",
        "name": "create_database",
        "message": "No database found",
        "choices": list(CreateDatabase)
    },
    {
        "type": "text",
        "name": "next_question",
        "message": "Name this library?",
        # Validate if the first question was answered with yes or no
        "when": lambda x: x["conditional_step"],
        # Only accept questionary as answer
        "validate": lambda val: val == "questionary",
    },
    {
        "type": "select",
        "name": "second_question",
        "message": "Select item",
        "choices": [
            "item1",
            "item2",
            Separator(),
            "other",
        ],
    },
    {
        "type": "text",
        "name": "second_question",
        "message": "Insert free text",
        "when": lambda x: x["second_question"] == "other",
    },
]

if __name__ == "__main__":
    prompt(questions)
