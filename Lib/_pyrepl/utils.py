import re
import unicodedata
import functools

from idlelib import colorizer
from typing import cast, Iterator, Literal, Match, NamedTuple, Pattern
from _colorize import ANSIColors

from .trace import trace

ANSI_ESCAPE_SEQUENCE = re.compile(r"\x1b\[[ -@]*[A-~]")
ZERO_WIDTH_BRACKET = re.compile(r"\x01.*?\x02")
ZERO_WIDTH_TRANS = str.maketrans({"\x01": "", "\x02": ""})
COLORIZE_RE: Pattern[str] = colorizer.prog
COLORIZE_GROUP_NAME_MAP: dict[str, str] = colorizer.prog_group_name_to_tag

type ColorTag = (
    Literal["KEYWORD"]
    | Literal["BUILTIN"]
    | Literal["COMMENT"]
    | Literal["STRING"]
    | Literal["SYNC"]
)


class Span(NamedTuple):
    start: int
    end: int


class ColorSpan(NamedTuple):
    span: Span
    tag: ColorTag


TAG_TO_ANSI: dict[ColorTag, str] = {
    "KEYWORD": ANSIColors.BOLD_BLUE,
    "BUILTIN": ANSIColors.CYAN,
    "COMMENT": ANSIColors.RED,
    "STRING": ANSIColors.GREEN,
    "SYNC": ANSIColors.RESET,
}


@functools.cache
def str_width(c: str) -> int:
    if ord(c) < 128:
        return 1
    w = unicodedata.east_asian_width(c)
    if w in ('N', 'Na', 'H', 'A'):
        return 1
    return 2


def wlen(s: str) -> int:
    if len(s) == 1 and s != '\x1a':
        return str_width(s)
    s = ZERO_WIDTH_BRACKET.sub("", s)
    length = sum(str_width(i) for i in s)
    # remove lengths of any escape sequences
    sequence = ANSI_ESCAPE_SEQUENCE.findall(s)
    ctrl_z_cnt = s.count('\x1a')
    return length - sum(len(i) for i in sequence) + ctrl_z_cnt


def unbracket(s: str) -> str:
    return s.translate(ZERO_WIDTH_TRANS)


def gen_colors(buffer: str) -> Iterator[ColorSpan]:
    """Returns a list of index spans to color using the given color tag.

    The input `buffer` should be a valid start of a Python code block, i.e.
    it cannot be a block starting in the middle of a multiline string.
    """
    for match in COLORIZE_RE.finditer(buffer):
        yield from gen_color_spans(match)


def gen_color_spans(re_match: Match[str]) -> Iterator[ColorSpan]:
    """Generate non-empty color spans.

    Span indexing is inclusive on both ends.
    """
    re_span = re_match.span()
    span = Span(re_span[0], re_span[1] - 1)
    for tag, data in re_match.groupdict().items():
        if data:
            tag = COLORIZE_GROUP_NAME_MAP.get(tag, tag)
            yield ColorSpan(span, cast(ColorTag, tag))


def disp_str(
    buffer: str, offset: int, colors: list[ColorSpan]
) -> tuple[str, list[int]]:
    """Return a printable variant of `buffer` with usage metadata.

    Note: the `colors` list is partially consumed within.

    The list details where the characters of buffer get used up.
    Examples:
    >>> utils.disp_str("a = 9", offset=0, colors=[])
    ('a = 9', [1, 1, 1, 1, 1])

    """
    b: list[int] = []
    s: list[str] = []

    while colors and colors[0].span.end < offset:
        colors.pop(0)

    # maybe we're continuing a multiline string color...
    if colors and colors[0].span.start < offset:
        s.append(TAG_TO_ANSI[colors[0].tag])

    for i, c in enumerate(buffer, offset):
        if colors and colors[0].span.start == i:
            s.append(TAG_TO_ANSI[colors[0].tag])
        if c == '\x1a':
            s.append(c)
            b.append(2)
        elif ord(c) < 128:
            s.append(c)
            b.append(1)
        elif unicodedata.category(c).startswith("C"):
            c = r"\u%04x" % ord(c)
            s.append(c)
            b.append(len(c))
        else:
            s.append(c)
            b.append(str_width(c))
        if colors and colors[0].span.end == i:
            s.append(TAG_TO_ANSI["SYNC"])
            colors.pop(0)

    # if we're in a multiline string, close the color to keep things clean
    if colors and colors[0].span.start < i and colors[0].span.end > i:
        s.append(ANSIColors.RESET)
        b.append(0)

    result = "".join(s)
    trace("disp_str({buffer}) = {result}, {b}", buffer=repr(buffer), result=repr(result), b=b)
    return result, b
