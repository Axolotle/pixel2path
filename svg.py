from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path

def gen_svg(shape):
    paths = [gen_str(contour) for contour in shape]
    gen_file(paths)

def gen_str(contour):
    d = ['M {},{}'.format(contour[0].x, contour[0].y)]
    d += ['L {},{}'.format(point.x, point.y) for point in contour[1:]]
    return Path(d=''.join(d))

def gen_file(paths):
    size = ('{}px'.format(1000),
            '{}px'.format(1000))
    viewBox = '0 0 {} {}'.format(100, 100)
    doc = Drawing('../test.svg', profile='tiny',
                  size=size, viewBox=viewBox)
    # main = Group(fill='none', stroke='black', stroke_linejoin='round',
    #              stroke_width=str(1) + 'px', stroke_linecap='round')
    main = Group(fill='black')

    for path in paths:
        main.add(path)

    main['transform'] = 'translate({},{})'.format(10, 10)
    doc.add(main)
    doc.save(pretty=True)
