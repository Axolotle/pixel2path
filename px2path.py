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
    def __init__(self, filepath, characters, grid=[3,5]):
        self.x, self.y = grid

        if filepath[-1] == '/':
            self.characters = self.from_img(filepath, characters)

    def from_img(self, filepath, characters):
        """
        Read several images and parse pixel position in absolute position
        for each characters given as argument. points's lists are ordered
        by grey intensity.
        """

        layers = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        char_str = list(characters)
        # generate a dict with all characters given
        characters = {x: {'closed': False, 'coords': []}
                      for x in char_str}

        for layer in layers:
            # Read & convert the image to greyscale
            img = cv2.imread(filepath + layer)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Extract every characters from the image
            rects = [img[1:self.y + 1, a:a + self.x]
                     for a in range(1, len(char_str)*(self.x + 1), self.x + 1)]

            for char, rect in zip(char_str, rects):
                # get the pixel position (x,y) and intensity if it's not white
                points = [[(x, y), rect[y, x]]
                          for x in range(self.x)
                          for y in range(self.y)
                          if rect[y, x] < 255]

                if len(points) == 0:
                    continue
                # Sort the list by intensity
                points = sorted(points, key=lambda info: info[1])
                # If the light intensity of the first point is 0 (black)
                # then the character's path has to be closed
                if points[0][1] == 0:
                    characters[char]['closed'] = True
                # Remove the intensity information
                points = [p[0] for p in points]
                characters[char]['coords'].append(points)

        return characters

class Px2path(Px2coord):
    def __init__(self, filepath, characters, grid=[3,5], w=2.25):
        self.w = w
        super().__init__(filepath, characters, grid)

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
