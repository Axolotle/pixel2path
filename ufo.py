from defcon import Font as DefFont

from objects import Stroke


def genUFO(glyphs, stroke_style):
    font = Font()
    font.info.ascender = 700
    font.info.capHeight= 200
    font.info.xHeight  = 300
    font.info.capHeight= 500
    font.info.unitsPerEm = 1000
    newZero = 6 * 100 + 50

    for glyph_name in glyphs:
        font_glyph = Stroke(glyphs[glyph_name]).scale(100).vectorize(**stroke_style).toUFOCoord(newZero)
        font.insertGlyph(font_glyph, glyph_name)
    font.save(path='../pxph.ufo')

class Font(DefFont):
    def __init__(self, **options):
        super().__init__()
        
