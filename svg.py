from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path

def gen_svg(shape):
    paths = [gen_str(contours) for contours in shape.layers]
    gen_file(paths)

def gen_str(contours):
    d = list()
    for contour in contours:
        d += ['M {},{}'.format(*contour[0][0])]
        d += ['L {},{}'.format(*pos[0]) for pos in contour]
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
