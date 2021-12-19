import sys
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional, Tuple, TypedDict, Union
from unicodedata import category as unicode_category


@dataclass
class Range:
    start: int
    end: int

    def overlaps(self, other: "Range") -> bool:
        return other.start in self or other.end in self

    def __add__(self, other: "Range") -> "Range":
        if other.start in self:
            return type(self)(start=self.start, end=other.end)
        if other.end in self:
            return type(self)(start=other.start, end=self.end)
        raise ValueError(f"Can't add {self} + {other}")

    def __contains__(self, value: "Union[int, Range]") -> bool:
        if isinstance(value, int):
            return self.start <= value <= self.end
        return value.start >= self.start and value.end <= self.end

    def merge(self, other: "Range") -> "Optional[Range]":
        try:
            return self + other
        except ValueError:
            if other in self:
                return self
            if self in other:
                return other
        return None

    def __lt__(self, other: "Range") -> bool:
        return self.end < other.end

    def __le__(self, other: "Range") -> bool:
        return self.end <= other.end

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplemented
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplemented
        return self.start != other.start and self.end != other.end

    def __gt__(self, other: "Range") -> bool:
        return self.end > other.end

    def __ge__(self, other: "Range") -> bool:
        return self.end >= other.end

    def __repr__(self) -> str:
        return f"range({self.start:#08x}, {self.end:#08x})"


class Category(TypedDict):
    long: str
    description: str
    ranges: List[Range]


UnicodeCategories = Dict[str, Category]

# From: https://www.unicode.org/reports/tr44/#GC_Values_Table
UNICODE_CATEGORIES: UnicodeCategories = {
    "Lu": {
        "long": "Uppercase_Letter",
        "description": "an uppercase letter",
        "ranges": [],
    },
    "Ll": {
        "long": "Lowercase_Letter",
        "description": "a lowercase letter",
        "ranges": [],
    },
    "Lt": {
        "long": "Titlecase_Letter",
        "description": "a digraphic character, with first part uppercase",
        "ranges": [],
    },
    "LC": {
        "long": "Cased_Letter",
        "description": "Lu | Ll | Lt",
        "ranges": [],
    },
    "Lm": {
        "long": "Modifier_Letter",
        "description": "a modifier letter",
        "ranges": [],
    },
    "Lo": {
        "long": "Other_Letter",
        "description": "other letters, including syllables and ideographs",
        "ranges": [],
    },
    "L": {
        "long": "Letter",
        "description": "Lu | Ll | Lt | Lm | Lo",
        "ranges": [],
    },
    "Mn": {
        "long": "Nonspacing_Mark",
        "description": "a nonspacing combining mark (zero advance width)",
        "ranges": [],
    },
    "Mc": {
        "long": "Spacing_Mark",
        "description": "a spacing combining mark (positive advance width)",
        "ranges": [],
    },
    "Me": {
        "long": "Enclosing_Mark",
        "description": "an enclosing combining mark",
        "ranges": [],
    },
    "M": {
        "long": "Mark",
        "description": "Mn | Mc | Me",
        "ranges": [],
    },
    "Nd": {
        "long": "Decimal_Number",
        "description": "a decimal digit",
        "ranges": [],
    },
    "Nl": {
        "long": "Letter_Number",
        "description": "a letterlike numeric character",
        "ranges": [],
    },
    "No": {
        "long": "Other_Number",
        "description": "a numeric character of other type",
        "ranges": [],
    },
    "N": {
        "long": "Number",
        "description": "Nd | Nl | No",
        "ranges": [],
    },
    "Pc": {
        "long": "Connector_Punctuation",
        "description": "a connecting punctuation mark, like a tie",
        "ranges": [],
    },
    "Pd": {
        "long": "Dash_Punctuation",
        "description": "a dash or hyphen punctuation mark",
        "ranges": [],
    },
    "Ps": {
        "long": "Open_Punctuation",
        "description": "an opening punctuation mark (of a pair)",
        "ranges": [],
    },
    "Pe": {
        "long": "Close_Punctuation",
        "description": "a closing punctuation mark (of a pair)",
        "ranges": [],
    },
    "Pi": {
        "long": "Initial_Punctuation",
        "description": "an initial quotation mark",
        "ranges": [],
    },
    "Pf": {
        "long": "Final_Punctuation",
        "description": "a final quotation mark",
        "ranges": [],
    },
    "Po": {
        "long": "Other_Punctuation",
        "description": "a punctuation mark of other type",
        "ranges": [],
    },
    "P": {
        "long": "Punctuation",
        "description": "Pc | Pd | Ps | Pe | Pi | Pf | Po",
        "ranges": [],
    },
    "Sm": {
        "long": "Math_Symbol",
        "description": "a symbol of mathematical use",
        "ranges": [],
    },
    "Sc": {
        "long": "Currency_Symbol",
        "description": "a currency sign",
        "ranges": [],
    },
    "Sk": {
        "long": "Modifier_Symbol",
        "description": "a non-letterlike modifier symbol",
        "ranges": [],
    },
    "So": {
        "long": "Other_Symbol",
        "description": "a symbol of other type",
        "ranges": [],
    },
    "S": {
        "long": "Symbol",
        "description": "Sm | Sc | Sk | So",
        "ranges": [],
    },
    "Zs": {
        "long": "Space_Separator",
        "description": "a space character (of various non-zero widths)",
        "ranges": [],
    },
    "Zl": {
        "long": "Line_Separator",
        "description": "U+2028 LINE SEPARATOR only",
        "ranges": [],
    },
    "Zp": {
        "long": "Paragraph_Separator",
        "description": "U+2029 PARAGRAPH SEPARATOR only",
        "ranges": [],
    },
    "Z": {
        "long": "Separator",
        "description": "Zs | Zl | Zp",
        "ranges": [],
    },
    "Cc": {
        "long": "Control",
        "description": "a C0 or C1 control code",
        "ranges": [],
    },
    "Cf": {
        "long": "Format",
        "description": "a format control character",
        "ranges": [],
    },
    "Cs": {
        "long": "Surrogate",
        "description": "a surrogate code point",
        "ranges": [],
    },
    "Co": {
        "long": "Private_Use",
        "description": "a private-use character",
        "ranges": [],
    },
    "Cn": {
        "long": "Unassigned",
        "description": "a reserved unassigned code point or a noncharacter",
        "ranges": [],
    },
    "C": {
        "long": "Other",
        "description": "Cc | Cf | Cs | Co | Cn",
        "ranges": [],
    },
}

GROUP_CATEGORIES = [
    category
    for category in UNICODE_CATEGORIES
    if len(category) == 1 or category.isupper()
]

UNWANTED_CATEGORIES = ["Zl", "Zp", "C"]

UNICODE_CODEPOINT_START = 0
UNICODE_CODEPOINT_END = sys.maxunicode


class Percentage(NamedTuple):
    percent: float
    point: float


def print_message(message: str) -> None:
    print(message, file=sys.stderr)


def main() -> UnicodeCategories:
    unicode_category_ranges: Dict[str, List[Range]] = {}

    progress_steps: List[Percentage] = []
    step = (UNICODE_CODEPOINT_END - UNICODE_CODEPOINT_START) / 100
    point = step
    while point <= UNICODE_CODEPOINT_END:
        progress_steps.append(
            Percentage(percent=point / UNICODE_CODEPOINT_END, point=point)
        )
        point += step
    # print(" ".join(f"{p.percent:.0%}" for p in progress_steps))
    # print(progress_steps)

    current_percent = 0
    current_point = progress_steps[current_percent].point
    printed_progress: bool = False
    for codepoint in range(UNICODE_CODEPOINT_START, UNICODE_CODEPOINT_END + 1):
        # progress
        if codepoint > current_point:
            current_percent += 1
            if current_percent < len(progress_steps) - 1:
                current_point = progress_steps[current_percent].point
                printed_progress = False

        if not printed_progress:
            print_message(f"{progress_steps[current_percent].percent:.0%}")
            printed_progress = True

        category = unicode_category(chr(codepoint))

        ranges = unicode_category_ranges.get(category, None)
        if ranges is None:
            unicode_category_ranges[category] = [Range(start=codepoint, end=codepoint)]
            continue

        last_range = ranges[-1]
        if codepoint > last_range.end + 1:
            # the new codepoint is more than 1 away from all existing ranges in the
            # category, so there's a gap, so a new range has to be defined
            ranges.append(Range(start=codepoint, end=codepoint))
            continue

        last_range.end = codepoint

    # print(unicode_category_ranges)
    # print(
    #     "\n".join(
    #         f"{category}:\n" + "\n".join(f"  {_range}" for _range in ranges)
    #         for category, ranges in unicode_category_ranges.items()
    #     )
    # )

    for category, ranges in list(unicode_category_ranges.items()):
        if category[0] not in unicode_category_ranges:
            unicode_category_ranges[category[0]] = []
        unicode_category_ranges[category[0]].extend(ranges)

    unicode_category_ranges["LC"] = [
        *unicode_category_ranges["Lu"],
        *unicode_category_ranges["Ll"],
        *unicode_category_ranges["Lt"],
    ]

    for group_category in GROUP_CATEGORIES:
        print_message(f"merging {group_category}...")
        ranges = unicode_category_ranges[group_category]
        ranges.sort()

        current_range_index = 0
        max_range_index = len(ranges) - 1
        while current_range_index <= max_range_index - 1:
            current_range = ranges[current_range_index]
            next_range = ranges[current_range_index + 1]

            current_range_index += 1

            merged_range = current_range.merge(next_range)
            if merged_range is None:
                continue
            ranges.pop(current_range_index + 1)
            ranges[current_range_index] = merged_range

    categories = deepcopy(UNICODE_CATEGORIES)
    for category in categories:
        categories[category]["ranges"] = unicode_category_ranges[category]

    return categories


class Count(NamedTuple):
    # mypy complains if an attribute is named "count"
    how_many: int
    category: str

    def __str__(self) -> str:
        return f"{self.category: <2}: {self.how_many:,}"


def sort_categories_by_count(categories: UnicodeCategories) -> List[Count]:
    categories_and_counts: List[Tuple[int, str]] = []
    for category in categories:
        ranges = categories[category]["ranges"]
        count = sum(len(range(_range.start, _range.end + 1)) for _range in ranges)
        categories_and_counts.append((count, category))

    categories_and_counts.sort()
    return [
        Count(category=category, how_many=count)
        for count, category in categories_and_counts
    ]


if __name__ == "__main__":
    categories = main()
    if len(sys.argv) > 0 and "unwanted" in sys.argv:
        for category in list(categories):
            if category not in UNWANTED_CATEGORIES:
                del categories[category]

    print("UNICODE_CATEGORIES = ", end="")
    print(categories)
