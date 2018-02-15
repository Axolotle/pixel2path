from base_objects import Stroke
from defcon import Font

def gen_ufo(glyphs, stroke_style):
    font = Font()
    for glyph_name in glyphs:
        font_glyph = Stroke(glyphs[glyph_name]).scale(5).vectorize(**stroke_style)
        font.insertGlyph(font_glyph, glyph_name)
    font.save(path='../pxph.ufo')
