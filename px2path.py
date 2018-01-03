import cv2
from json import load

from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path
from svgwrite.shapes import Rect


class Px2path:
    def __init__(self, filename, w=2.25):
        self.w = w
        self.paths = []
        self.filename, ext = filename.split('.', -1)
        self.closed = False

        if ext.lower() == 'json':
            self.points = self.from_json(filename)
        else:
            self.points = self.from_img(filename)

    def from_img(self, filename):
        img = cv2.imread('0.png')
        # Convert the image to greyscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        max_x, max_y = img.shape

        # Extract the colored pixels
        px = []
        for x in range(max_x):
            for y in range(max_y):
                if img[x, y] < 255:
                    px.append([(y, x), img[x, y]])

        # Sort the list by intensity
        points = sorted(px, key=lambda info: info[1])
        # Remove the intensity information
        points = [p[0] for p in points]

        return points

    def from_json(self, filename):
        with open(filename, 'r') as f:
            coordinates = load(f)['0']

        if coordinates.find(' Z') > -1:
            self.closed = True
            coordinates = coordinates.replace(' Z', '')

        points = [[int(axe) for axe in point.split(',')]
                  for point in coordinates.split(' ')]

        return points

    def to_absolute_line(self, dx=0):
        """ Generate a path line with absolution positions (only L key)
        """
        def pos(string, x, y, dx=0):
            return string.format(x * self.w + dx,
                                 y * self.w)

        d = pos('M{},{} ', *self.points.pop(0))
        for p in self.points:
            d += pos('L{},{} ', *p)

        self.paths.append(Path(d=d + 'Z'))

    def to_relative_line(self, dx=0):
        # Generate a path line with relative positions (with l, v & h keys)

        def pos(char, x, y, dx=0):
            return '{}{},{} '.format(char, x * self.w + dx, y * self.w)

        start = prev_point = self.points.pop(0)
        d = pos('M', *start, dx=dx)
        for point in self.points:
            direction = [p - pp for p, pp in zip(point, prev_point)]
            prev_point = point
            if direction[0] == 0:
                d += 'v{} '.format(direction[1] * self.w)
            elif direction[1] == 0:
                d += 'h{} '.format(direction[0] * self.w)
            else:
                d += pos('l', *direction)
        if self.closed:
            d += ' Z'
        self.points.insert(0, start)
        self.paths.append(Path(d=d))

    def draw_grid(self, max_x, max_y):
        group = Group(fill='grey')
        rects = [Rect(insert=(x * self.w, y * self.w), size=(self.w, self.w))
                 for x in range(max_x) for y in range(max_y)]
        for i, rect in enumerate(rects):
            if i % 2 == 0:
                rect['fill'] = "#AAAAAA"
            group.add(rect)
        return group

    def generate_file(self, grid=None):
        doc = Drawing(self.filename + '.svg', profile='tiny',
                      size=('300px', '300px'), viewBox='0 0 15 15')
        main = Group(fill='none', stroke='black', stroke_linejoin='round',
                     stroke_width=str(self.w) + 'px', stroke_linecap='round')

        if grid is not None:
            doc.add(self.draw_grid(*grid))
            main['opacity'] = 0.5
            main['stroke'] = 'red'

        for path in self.paths:
            main.add(path)
        main['transform'] = 'translate({},{})'.format(1.125, 1.125)
        doc.add(main)
        doc.save(pretty=True)


drawing = Px2path('0.json')
drawing.to_relative_line()
drawing.to_relative_line(dx=drawing.w*3.5)
drawing.generate_file(grid=[3, 5])
