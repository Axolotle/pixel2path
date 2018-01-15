from os import listdir
from os.path import isfile, join

import cv2
from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path
from svgwrite.shapes import Rect
from svgwrite.base import BaseElement

from base_objects import Point, Line


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

        paths = list()

        for l, layer in enumerate(char['points']):
            # if l != 6:
            #     continue
            outer = list()
            inner = list()
            for i, phase in enumerate(layer):
                if i < len(layer)- 1:
                    a, b, c = layer[i-1], layer[i], layer[i+1]
                else:
                    a, b, c = layer[i-1], layer[i], layer[0]

                if i == 0 and not char['closed']:
                    outer.append(b.parallel(c, -90, 0.5))
                    outer.insert(0, b.parallel(c, 90, 0.5))
                elif i == len(layer) -1 and not char['closed']:
                    outer.append(b.parallel(a, 90, 0.5))
                    inner.insert(0, b.parallel(a, -90, 0.5))
                else:
                    outer.append(self.get_intersection(a, b, c, -90))
                    inner.insert(0, self.get_intersection(a, b, c, 90))

            paths.append(Path(d=self.generate_string(outer, inner, char['closed']), fill='red', stroke='none',stroke_width='0.1px'))

        self.generate_file(paths)


    def generate_string(self, outer, inner, closed):
        d = str()
        for i, value in enumerate(outer):
            if i == 1 and not closed:
                d += 'A 0.5 0.5 0 0 1 {},{}'.format(*value)
            elif isinstance(value, Line):
                print(value.a.vector(value.b))
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
                    print(value.a.vector(value.b))
                    if j == 0:
                        d += 'M{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.b, *value.a)
                    else:
                        d += 'L{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.b, *value.a)
                else:
                    if j == 0:
                        d += 'M{},{}'.format(*value)
                    else:
                        d += 'L{},{}'.format(*value)
        else:
            point = inner[0]
            d += 'A 0.5 0.5 0 0 1 {},{}'.format(*point)
            for j, value in enumerate(inner[1:]):
                if isinstance(value, Line):
                    # print(value.a.vector(value.b))
                    d += 'L{},{} A 0.5 0.5 0 0 1 {},{}'.format(*value.b, *value.a)
                else:
                    d += 'L{},{}'.format(*value)
        d += 'Z'
        return d

    def get_intersection(self, a, b, c, theta):
        d1, d2 = Line(a, b).parallel(theta, 0.5), Line(b, c).parallel(theta, 0.5)
        intersection = d1.intersection(d2)
        if intersection is None:
            return Line(d1.b, d2.a)
        return intersection

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
