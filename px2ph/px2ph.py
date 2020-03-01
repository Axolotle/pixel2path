from os import path

from fontTools.misc.transform import Identity, Transform
from fontTools.pens.pointPen import SegmentToPointPen
from defcon import Font

from px2ph.tools.glyphset import parse_range
from px2ph.px2pt import px2pt
from px2ph.pens.strokePen import StrokeToShapeSegmentPen


def parse_font_info(data):
    px = data['pixelSizeInEm']
    del data['pixelSizeInEm']
    return {
        **data,
        'unitsPerEm': 1000,
        'ascender': data['ascender'] * px,
        'capHeight': data['capHeight'] * px,
        'xHeight': data['xHeight'] * px,
        'descender': data['descender'] * px,
    }


def px2font(input, info, output):
    glyphs_points = px2pt(**input)
    glyph_set = parse_range(output['glyphSet'])
    assert len(glyphs_points) == len(glyph_set), \
        "glyphs and glyph_set doesn't have the same size"

    px_size = info['pixelSizeInEm']
    scale_tf = Transform(px_size, 0, 0, px_size, 0, 0)
    # transformation that inverts the y axis coordinates, translate so the descender
    # part of the glyph falls beyond the baseline and translate 'half' a pixel
    UFO_tf = scale_tf.transform(
        (1, 0, 0, -1, 0.5, input['grid'][1] + info['descender'] - 0.5))

    info = parse_font_info(info)

    font = Font()
    font.info.setDataFromSerialization(info)

    for glyph_repr, contours in zip(glyph_set, glyphs_points):
        glyph = font.newGlyph(glyph_set[glyph_repr]['name'])
        glyph.unicodes = [glyph_repr]
        out_pen = glyph.getPointPen()
        pen = StrokeToShapeSegmentPen(SegmentToPointPen(out_pen), px_size)

        for contour in contours:
            # contour = UFO_tf.transformPoints(contour)
            pen.beginPath()
            for point in contour:
                pen.addPoint(UFO_tf.transformPoint(point[0]), point[1])
            pen.endPath()

    font.save(path=path.abspath(output['folder']))


if __name__ == '__main__':
    from argparse import ArgumentParser

    from px2ph.utils.yaml import get_yaml


    parser = ArgumentParser(
        prog='px2ph.tools.grid',
        description='png font grid generator'
    )
    parser.add_argument('-c', '--config_file',
                        required=True,
                        help='path to a yaml file containing the grid options',
                        type=path.abspath)
    args = parser.parse_args()

    px2font(**get_yaml(args.config_file))
