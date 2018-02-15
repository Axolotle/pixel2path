from defcon import Font

from objects import Stroke


def genUFO(glyphs, stroke_style):
    font = Font()
    for glyph_name in glyphs:
        font_glyph = Stroke(glyphs[glyph_name]).scale(5).vectorize(**stroke_style)
        font.insertGlyph(font_glyph, glyph_name)
    font.save(path='../pxph.ufo')
