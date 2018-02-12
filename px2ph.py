import argparse

from yaml import load

from px2pt import px2pt
from base_objects import Stroke, Shape
from svg import gen_svg
import ufo


def args():
    parser = argparse.ArgumentParser(prog='px2ph',
                                     description='Pixel to vector converter')
    parser.add_argument('yamlpath', help='path to the yaml config file')
    return parser.parse_args()

if __name__ == "__main__":
    args = args()
    config = None
    with open(args.yamlpath, 'r') as yaml:
        config = load(yaml.read())

    stroke_style = config['font-family'][0]['stroke']

    glyphs = px2pt(config['glyph_set'], **config['px_infos'])
    # strokes = {glyph: Stroke(glyphs[glyph]) for glyph in glyphs}
    # print(strokes['A'].layers)
    # shapes = {glyph: Shape(glyphs[glyph], **stroke_style)
    #           for glyph in glyphs}
    # shape = Shape(glyphs['F'], **stroke_style)
    # gen_svg(shape)
    ufo.gen_font(glyphs, stroke_style)

    # glyphs['B'].layers = glyphs['B'].points_position(True)
    # print(glyphs['B'].layers)
    # glyphs['B'].layers = glyphs['B'].points_position(False)
    # print(glyphs['B'].layers)

    #
    # print(glyphs)
