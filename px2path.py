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
    def __init__(self, filepath, characters, grid, w=2.25):
        self.w = w
        super().__init__(filepath, characters, grid)

    def absolute_line(self, char, dx=0):
        """ Generate a path line with absolute positions (only L key)
        """
        char = self.characters[char]
        d = str()
        for i, layer in enumerate(char['coords']):
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
        for i, layer in enumerate(char['coords']):
            start = prev_point = layer[0]
            d += self.get_pos('M', start, dx)
            for coord in layer[1:]:
                direction = [p - pp for p, pp in zip(coord, prev_point)]
                if direction[0] == 0:
                    d += 'v{} '.format(direction[1] * self.w)
                elif direction[1] == 0:
                    d += 'h{} '.format(direction[0] * self.w)
                else:
                    d += self.get_pos('l', direction)
                prev_point = coord
            if i == 0 and char['closed']:
                d += 'Z '

        return Path(d=d)

    def get_pos(self, command, pos, dx=0):
        """ Return a SVG d's command """
        return '{}{},{} '.format(command, pos[0] * self.w + dx * self.w,
                                 pos[1] * self.w)

    def write(self, string, absolute=True):
        if absolute:
            paths = [ self.absolute_line(char, dx * self.x)
                      for dx, char in enumerate(list(string))]
        else:
            paths = [ self.relative_line(char, dx * self.x)
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
        size = ('{}px'.format(x),
                '{}px'.format(y))
        viewBox = '0 0 {} {}'.format(x, y)

        doc = Drawing(self.filename + '.svg', profile='tiny',
                      size=size, viewBox=viewBox)
        main = Group(fill='none', stroke='black', stroke_linejoin='round',
                     stroke_width=str(self.w) + 'px', stroke_linecap='round')

        for path in paths:
            main.add(path)

        main['transform'] = 'translate({},{})'.format(self.w/2, self.w/2)
        doc.add(main)
        doc.save(pretty=True)
