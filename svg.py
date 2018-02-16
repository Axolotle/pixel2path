from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path


def genSVG(shape):
    paths = genStr(shape)
    genFile(paths)

def genStr(contours):
    d = ''
    print(len(contours))
    for contour in contours:
        d += 'M{},{} '.format(contour[0].x, contour[0].y)
        for point in contour[1:]:
            stype = point._segmentType
            print(stype)
            if stype == None:
                d += '{},{} '.format(point.x, point.y)
            if stype == 'line':
                d += 'L{},{} '.format(point.x, point.y)
            elif stype == 'curve':
                d += 'C{},{} '.format(point.x, point.y)


        # d += ['M {},{}'.format(contour[0].x, contour[0].y)]
        # d += ['L {},{}'.format(point.x, point.y) for point in contour[1:]]
    # return Path(d=''.join(d))
    return Path(d=d)

def genFile(paths):
    size = ('{}px'.format(1000),
            '{}px'.format(1000))
    viewBox = '0 0 {} {}'.format(100, 100)
    doc = Drawing('../test.svg', profile='tiny',
                  size=size, viewBox=viewBox)
    # main = Group(fill='none', stroke='black', stroke_linejoin='round',
    #              stroke_width=str(1) + 'px', stroke_linecap='round')
    main = Group(fill='black')

    main.add(paths)

    main['transform'] = 'translate({},{})'.format(10, 10)
    doc.add(main)
    doc.save(pretty=True)
