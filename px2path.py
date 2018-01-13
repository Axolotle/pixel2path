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


class Point(tuple):
    def __new__(self, *args):
        value = args[0] if len(args) == 1 else args
        return tuple.__new__(Point, value)

    def __init__(self, *args):
        value = args[0] if len(args) == 1 else args
        self.x, self.y = value

    def vector(self, other):
        return Vector(other.x - self.x, other.y - self.y)

    def distance(self, other):
        return self.vector(other).norm()

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __radd__(self, n):
        return Point(self.x + n, self.y + n)

    def __rmult__(self, n):
        return Point(self.x * n, self.y * n)

class Vector(tuple):
    def __new__(self, *args):
        value = args[0] if len(args) == 1 else args
        return tuple.__new__(Vector, value)

    def __init__(self, *args):
        value = args[0] if len(args) == 1 else args
        self.x, self.y = value

    def norm(self):
        return math.hypot(self.x, self.y)

    def unit_vector(self):
        return Vector(self.x / self.norm(), self.y / self.norm())

    def rotate(self, theta):
        """ Rotate vector of angle theta given in deg
        """
        rad = math.radians(theta)
        cos, sin = math.cos(rad), math.sin(rad)
        return Vector(cos * self.x - sin * self.y,
                      sin * self.x + cos * self.y)

    def point(self, point, div=1):
        return Point(point.x + self.x, point.x + self.y)

    def __rmul__(self, n):
        return Vector(self.x * n, self.y * n)

    def __mul__(self, other):
        return Vector(self.x * other.x + self.y * other.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

class Line:
    def __init__(self, a, b):
        self.a = a
        self.b = b if isinstance(b, Point) else b.point(a)

    def vector(self):
        """ Return the vector of the line
        """
        return self.a.vector(self.b)

    def intersection(self, other):
        a, b, c, d = self.a, self.b, other.a, other.b
        i, j = self.vector(), other.vector()

        div = i.x * j.y - i.y * j.x

        if div != 0:
            # if i & j are not parallel
            # k = (j.x * a.y - j.x * c.y - j.y * a.x + j.y * c.x) / div
            # return Point(a + k * i)
            m = (i.x * a.y - i.x * c.y - i.y * a.x + i.y * c.x) / div
            # check if lines intersect
            if 0 < m < 1:
                return Point(c + m * j)
            else:
                return None

class Px2coord:
    def __init__(self, filepath, characters, grid):
        self.x, self.y = grid

        if filepath[-1] == '/':
            self.filename = filepath.strip('/')
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
        characters = {x: {'closed': False, 'points': []}
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
                points = [[Point(x, y), rect[y, x]]
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
                characters[char]['points'].append(points)

        return characters

class Px2path(Px2coord):
    def __init__(self, filepath, characters, grid, w=2.25):
        self.w = w
        super().__init__(filepath, characters, grid)

    def absolute_line(self, char, dx=0):
        """ Generate a path line with absolute positions (only L key)
        """
        char = self.characters[char]
        d = str()
        for i, layer in enumerate(char['points']):
            d += self.get_pos('M', layer[0], dx)
            for coord in layer[1:]:
                d += self.get_pos('L', coord, dx)
            if i == 0 and char['closed']:
                d += 'Z '

        return Path(d=d)

    def relative_line(self, char, dx=0):
        """ Generate a path line with relative positions (with l, v & h keys)
        """
        char = self.characters[char]
        d = str()
        for i, layer in enumerate(char['points']):
            start = prev_pt = layer[0]
            d += self.get_pos('M', start, dx)
            for coord in layer[1:]:
                direction = [p - pp for p, pp in zip(coord, prev_pt)]
                if direction[0] == 0:
                    d += 'v{} '.format(direction[1] * self.w)
                elif direction[1] == 0:
                    d += 'h{} '.format(direction[0] * self.w)
                else:
                    d += self.get_pos('l', direction)
                prev_pt = coord
            if i == 0 and char['closed']:
                d += 'Z '

        return Path(d=d)

    def rel_path(self, char, dx=0):
        def mult(vector):
            decal = self.w / 2
            return Vector(vector[0] * decal, vector[1] * decal)
        def mult2(vector):
            return Vector(vector[0] * self.w, vector[1] * self.w)

        char = self.characters[char]

        for l, layer in enumerate(char['points']):
            outer = list()
            inner = list()
            for i, phase in enumerate(layer):
                if i < len(layer)- 1:
                    a, b, c = layer[i-1], layer[i], layer[i+1]
                else:
                    a, b, c = layer[i-1], layer[i], layer[0]

                if i == 0 and not char['closed']:
                    print('coucou')
                    vec1 = 0.5 * b.vector(c).unit_vector().rotate(-90)
                    vec2 = 0.5 * b.vector(c).unit_vector().rotate(90)
                    p1, p2 = b + vec1, b + vec2
                    outer.append(p1)
                    inner.append(p2)
                    print(p1, p2)
                else:
                    outer.append(self.get_intersection(a, b, c, -90))
                    inner.append(self.get_intersection(a, b, c, 90))

            #d1 = 'M{},{} L{},{} L{},{}'.format(*a, *b, *c)
            paths = [
                #Path(d=d1, stroke='red'),
                Path(d=self.generate_string(outer, list(reversed(inner)), char['closed']), fill='red', stroke='none',stroke_width='0.1px'),
            ]
            self.generate_file(paths)
            return

    def generate_string(self, outer, inner, closed):
        d = str()
        for i, value in enumerate(outer):
            if isinstance(value, Line):
                if i == 0:
                    d += 'M{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.a, *value.b)
                else:
                    d += 'L{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.a, *value.b)
            else:
                if i == 0:
                    d += 'M{},{}'.format(*value)
                else:
                    d += 'L{},{}'.format(*value)
        if closed:
            d += 'Z '
            for j, value in enumerate(inner):
                if isinstance(value, Line):
                    if j == 0:
                        d += 'M{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.a, *value.b)
                    else:
                        d += 'L{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.a, *value.b)
                else:
                    if j == 0:
                        d += 'M{},{}'.format(*value)
                    else:
                        d += 'L{},{}'.format(*value)
            d += 'Z'
        else:
            point = inner[0]
            d += 'A 0.5 0.5 0 0 1 {},{}'.format(*point)
            for j, value in enumerate(inner[1:]):
                if isinstance(value, Line):
                    d += 'L{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.a, *value.b)
                else:
                    d += 'L{},{}'.format(*value)
            d += 'Z'
        return d

    def get_intersection(self, a, b, c, theta):
        vec1 = 0.5 * a.vector(b).unit_vector().rotate(theta)
        p1, p2 = b + vec1, a + vec1
        d1 = Line(p1, p2)

        vec2 = 0.5 * b.vector(c).unit_vector().rotate(theta)
        p3, p4 = b + vec2, c + vec2
        d2 = Line(p3, p4)

        intersection = d1.intersection(d2)
        if intersection:
            return intersection
        elif intersection is None:
            return Line(p1, p3)

    def get_pos(self, command, pos, dx=0):
        """ Return a SVG d's command """
        return '{}{},{} '.format(command, pos[0] * self.w + dx * self.w,
                                 pos[1] * self.w)

    def write(self, string, absolute=True):
        if absolute:
            paths = [self.absolute_line(char, dx * self.x)
                     for dx, char in enumerate(list(string))]
        else:
            paths = [self.relative_line(char, dx * self.x)
                     for dx, char in enumerate(list(string))]

        self.generate_file(paths)

    def draw_grid(self, max_x, max_y):
        group = Group(fill='grey')
        rects = [Rect(insert=(x * self.w, y * self.w), size=(self.w, self.w))
                 for x in range(max_x) for y in range(max_y)]
        for i, rect in enumerate(rects):
            if i % 2 == 0:
                rect['fill'] = "#AAAAAA"
            group.add(rect)
        return group

    def generate_file(self, paths):
        x = self.w * (self.x * len(paths) + 1)
        y = self.w * self.y + 2
        size = ('{}px'.format(x*15),
                '{}px'.format(y*15))
        viewBox = '0 0 {} {}'.format(x, y)

        doc = Drawing(self.filename + '.svg', profile='tiny',
                      size=size, viewBox=viewBox)
        main = Group(fill='none', stroke='black', stroke_linejoin='round',
                     stroke_width=str(1) + 'px', stroke_linecap='round')

        for path in paths:
            main.add(path)

        main['transform'] = 'translate({},{})'.format(self.w/2, self.w/2)
        doc.add(main)
        doc.save(pretty=True)
