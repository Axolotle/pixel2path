import cv2
from json import load
import math
from os import listdir
from os.path import isfile, join

from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path
from svgwrite.shapes import Rect
from svgwrite.base import BaseElement

class Px2coord:
    def __init__(self, filepath='layers/', grid=[3,5]):
        self.grid = grid

        if filepath[-1] == '/':
            self.coords = self.from_img(filepath)
        else:
            self.coords = self.from_json(filepath)

    def from_img(self, filepath):
        layers = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        coords_layers = []

        for layer in layers:
            img = cv2.imread(filepath + layer)
            # Convert the image to greyscale
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            max_y, max_x = img.shape
            nb_chars = round(max_x / (self.grid[0] + 1))

            coords = []
            actual_x = 1
            for char in range(nb_chars):
                points = []
                for x in range(self.grid[0]):
                    for y in range(self.grid[1]):
                        if img[y + 1, x + actual_x] < 255:
                            points.append([(x, y), img[y + 1, x + actual_x]])

                # Sort the list by intensity
                points = sorted(points, key=lambda info: info[1])
                # Remove the intensity information
                points = [p[0] for p in points]

                actual_x += self.grid[0] + 1
                coords.append(points)

            coords_layers.append(coords)

        return coords_layers

    def from_json(self, filepath):
        with open(filepath, 'r') as f:
            coordinates = load(f)['0']

        if coordinates.find(' Z') > -1:
            self.closed = True
            coordinates = coordinates.replace(' Z', '')

        points = [[int(axe) for axe in point.split(',')]
                  for point in coordinates.split(' ')]

        return points


class Px2path(Px2coord):
    def __init__(self, filepath, grid=[3,5], w=2.25):
        self.w = w
        super().__init__(filepath, grid)

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

with open('lettres.txt', 'w') as f:
    lettre = ''
    for l in range(20, 200):
        print(l)
        lettre += chr(l)
    print(lettre)
    f.write(lettre)

font = Px2path('pxpath/')
# drawing = Px2path('0.json')
# drawing.to_relative_line()
# drawing.generate_file(grid=[3, 5])
