import sys
from dataclasses import dataclass
from typing import Dict, List, NamedTuple
from unicodedata import category as unicode_category

# From: https://www.unicode.org/reports/tr44/#GC_Values_Table
UNICODE_CATEGORIES = {
    "Lu": {"long": "Uppercase_Letter", "description": "an uppercase letter"},
    "Ll": {"long": "Lowercase_Letter", "description": "a lowercase letter"},
    "Lt": {
        "long": "Titlecase_Letter",
        "description": "a digraphic character, with first part uppercase",
    },
    "LC": {"long": "Cased_Letter", "description": "Lu | Ll | Lt"},
    "Lm": {"long": "Modifier_Letter", "description": "a modifier letter"},
    "Lo": {
        "long": "Other_Letter",
        "description": "other letters, including syllables and ideographs",
    },
    "L": {"long": "Letter", "description": "Lu | Ll | Lt | Lm | Lo"},
    "Mn": {
        "long": "Nonspacing_Mark",
        "description": "a nonspacing combining mark (zero advance width)",
    },
    "Mc": {
        "long": "Spacing_Mark",
        "description": "a spacing combining mark (positive advance width)",
    },
    "Me": {"long": "Enclosing_Mark", "description": "an enclosing combining mark"},
    "M": {"long": "Mark", "description": "Mn | Mc | Me"},
    "Nd": {"long": "Decimal_Number", "description": "a decimal digit"},
    "Nl": {"long": "Letter_Number", "description": "a letterlike numeric character"},
    "No": {"long": "Other_Number", "description": "a numeric character of other type"},
    "N": {"long": "Number", "description": "Nd | Nl | No"},
    "Pc": {
        "long": "Connector_Punctuation",
        "description": "a connecting punctuation mark, like a tie",
    },
    "Pd": {
        "long": "Dash_Punctuation",
        "description": "a dash or hyphen punctuation mark",
    },
    "Ps": {
        "long": "Open_Punctuation",
        "description": "an opening punctuation mark (of a pair)",
    },
    "Pe": {
        "long": "Close_Punctuation",
        "description": "a closing punctuation mark (of a pair)",
    },
    "Pi": {"long": "Initial_Punctuation", "description": "an initial quotation mark"},
    "Pf": {"long": "Final_Punctuation", "description": "a final quotation mark"},
    "Po": {
        "long": "Other_Punctuation",
        "description": "a punctuation mark of other type",
    },
    "P": {"long": "Punctuation", "description": "Pc | Pd | Ps | Pe | Pi | Pf | Po"},
    "Sm": {"long": "Math_Symbol", "description": "a symbol of mathematical use"},
    "Sc": {"long": "Currency_Symbol", "description": "a currency sign"},
    "Sk": {
        "long": "Modifier_Symbol",
        "description": "a non-letterlike modifier symbol",
    },
    "So": {"long": "Other_Symbol", "description": "a symbol of other type"},
    "S": {"long": "Symbol", "description": "Sm | Sc | Sk | So"},
    "Zs": {
        "long": "Space_Separator",
        "description": "a space character (of various non-zero widths)",
    },
    "Zl": {"long": "Line_Separator", "description": "U+2028 LINE SEPARATOR only"},
    "Zp": {
        "long": "Paragraph_Separator",
        "description": "U+2029 PARAGRAPH SEPARATOR only",
    },
    "Z": {"long": "Separator", "description": "Zs | Zl | Zp"},
    "Cc": {"long": "Control", "description": "a C0 or C1 control code"},
    "Cf": {"long": "Format", "description": "a format control character"},
    "Cs": {"long": "Surrogate", "description": "a surrogate code point"},
    "Co": {"long": "Private_Use", "description": "a private-use character"},
    "Cn": {
        "long": "Unassigned",
        "description": "a reserved unassigned code point or a noncharacter",
    },
    "C": {"long": "Other", "description": "Cc | Cf | Cs | Co | Cn"},
}

UNICODE_CODEPOINT_START = 0
UNICODE_CODEPOINT_END = sys.maxunicode


@dataclass
class Range:
    start: int
    end: int

    def __contains__(self, value: int) -> bool:
        return self.start <= value <= self.end

    def __repr__(self) -> str:
        return f"<{self.start} - {self.end}>"


class Percentage(NamedTuple):
    percent: float
    point: float


unicode_category_ranges: Dict[str, List[Range]] = {}


def main() -> None:
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
            print(f"{progress_steps[current_percent].percent:.0%}")
            printed_progress = True

        category = unicode_category(chr(codepoint))

        if category not in unicode_category_ranges:
            unicode_category_ranges[category] = [Range(start=codepoint, end=codepoint)]
            continue

        ranges = unicode_category_ranges[category]

        # since we're counting linearly, this is unlikely to be useful
        # if any(codepoint in range for range in ranges):
        #     # codepoint is already inside the range
        #     print("contained!")
        #     continue

        for _range in ranges:
            if _range.end + 1 == codepoint:
                _range.end = codepoint
                continue
            # since we're counting linearly, this won't be used
            # if _range.start - 1 == codepoint:
            #     print("got here")
            #     _range.start = codepoint
            #     continue

        # no ranges could be extended
        # the new codepoint is more than 1 away from all existing ranges in the
        # category, so there's a gap, so a new range has to be defined

        ranges.append(Range(start=codepoint, end=codepoint))

    print(unicode_category_ranges)
    print(
        "\n".join(
            f"{category}:\n" + "\n".join(f"  {_range}" for _range in ranges)
            for category, ranges in unicode_category_ranges.items()
        )
    )


if __name__ == "__main__":
    main()
