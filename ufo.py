from base_objects import Shape
from defcon import Font, Glyph, Contour, Point

def gen_font(glyphs, stroke_style):
    font = Font()
    for glyph_name in glyphs:
        shape = Shape(glyphs[glyph_name], **stroke_style)
        font_glyph = Glyph()
        for layer in shape.layers:
            for contour in layer:
                new_contour = Contour()
                for point in contour:
                    # print(point)
                    # continue
                    new_contour.addPoint(point[0], point[1])
                    # print(new_contour[0].x)
                font_glyph.appendContour(new_contour)
            font.insertGlyph(font_glyph, glyph_name)


    print(font.unicodeData.forcedUnicodeForGlyphName('A'))
    font.save(path='../pxph.ufo')
