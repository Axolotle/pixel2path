import argparse

from yaml import load

from px2pt import px2pt
from svg import gen_svg
from ufo import gen_ufo

# For testing
from base_objects import Stroke, Point, Vector


def args():
    parser = argparse.ArgumentParser(prog='px2ph',
                                     description='Pixel to vector converter')
    parser.add_argument('yamlpath', help='path to the yaml config file')
    parser.add_argument('--svg', action='store_true')
    parser.add_argument('--ufo', action='store_true')
    return parser.parse_args()

if __name__ == "__main__":
    args = args()
    config = None
    with open(args.yamlpath, 'r') as yaml:
        config = load(yaml.read())

    stroke_style = config['font-family'][0]['stroke']
    glyphs = px2pt(config['glyph_set'], **config['px_infos'])

    if args.svg:
        shape = Stroke(glyphs['A']).scale(5).vectorize(**stroke_style)
        gen_svg(shape)

    if args.ufo:
        gen_ufo(glyphs, stroke_style)
