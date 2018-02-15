import argparse

from yaml import load

from px2pt import px2pt
from svg import genSVG
from ufo import genUFO

# For testing
from objects import Stroke, Point, Vector


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

    strokeStyle = config['fontFamily'][0]['stroke']
    glyphs = px2pt(config['glyphSet'], **config['pxInfos'])

    if args.svg:
        shape = Stroke(glyphs['A']).scale(5).vectorize(**strokeStyle)
        genSVG(shape)

    if args.ufo:
        genUFO(glyphs, strokeStyle)
