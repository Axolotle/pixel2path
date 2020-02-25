from glyphNameFormatter.unicodeRangeNames import (
    getRangeByName as get_range_by_name,
    getSupportedRangeNames as get_supported_range_names
)
from glyphNameFormatter.reader import u2n, n2u
from glyphNameFormatter.tools import (
    charToUnicode as chr_to_unicode,
    unicodeToChar as unicode_to_char
)


def parse_range(selectors):
    """
    Returns a dict containing all glyphs found thru the selectors.
    A selector can be:
        - a string that match one or more unicode range name like 'Basic Latin'
        - a string of an explicit series of characters like 'A9ç' or ranges like 'a-z'
    """
    if not isinstance(selectors, list):
        selectors = [selectors]

    glyph_set = {}
    for selector in selectors:
        glyph_set_part = get_range_by_name(selector)
        if glyph_set_part is not None:
            glyph_set_part = range_to_glyphset(glyph_set_part)
        else:
            glyph_set_part = str_to_glyphset(selector)

        glyph_set = {**glyph_set, **glyph_set_part}
    return glyph_set


def range_to_glyphset(range_):
    """
    Returns a dict containing all glyphs in the given range.
    range_ must be an iterable of length 2 containing a decimal representation
    of two glyphs.
    """
    glyph_set = {}
    for n in range(range_[0], range_[1] + 1):
        name = u2n(n)
        if name is not None:
            glyph_set[n] = {
                'chr': unicode_to_char(n),
                'name': name,
                'hex': hex(n)
            }

    return glyph_set


def str_to_glyphset(str_):
    """
    Returns a dict containing all glyphs present in the string.
    Range-like syntax with '-' can be used to retreive multiple glyph
    Ex: 'a-e' returns a dict with glyph informations for the series [abcde]
    """
    glyph_set = {}
    escaped = False

    for i, chr_ in enumerate(str_):
        n = chr_to_unicode(chr_)
        if n == 92 and not escaped: # '\'
            escaped = True
            continue
        if n == 45 and not escaped: # '-'
            start = chr_to_unicode(str_[i-1]) + 1
            end = chr_to_unicode(str_[i+1]) - 1
            glyph_set = {**glyph_set, **range_to_glyphset((start, end))}
            continue

        name = u2n(n)
        if name is not None:
            glyph_set[n] = {
                'chr': unicode_to_char(n),
                'name': name,
                'hex': hex(n)
            }

        if escaped:
            escaped = False

    return glyph_set


def print_ranges():
    names = get_supported_range_names()
    names.sort()
    print("\n".join(names))
