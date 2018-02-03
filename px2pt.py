import cv2
from os import listdir
from os.path import isfile, join, splitext

from .base_objects import Point


class Px2Pt:
    def __init__(self, filepath, glyphs, grid):
        self.x, self.y = grid

        if filepath[-1] == '/':
            self.filename = filepath.strip('/')
            self.glyphs = self.from_img(filepath, glyphs)

    def from_img(self, filepath, glyphs):
        """
        Read several images and parse pixel position in absolute position
        for each glyphs given as argument. points's lists are ordered
        by grey intensity.
        """
        layers = [f for f in listdir(filepath)
                  if isfile(join(filepath, f))
                  and splitext(filepath)[1] is '.png']
        glyph_str = list(glyphs)
        # generate a di0ct with all glyphs given
        glyphs = {glypĥ: {'closed': False, 'points': []} for glypĥ in glyph_str}

        for layer in layers:
            # Read & convert the image to greyscale
            img = cv2.imread(filepath + layer)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Extract every glyphs from the image
            rects = [img[1:self.y + 1, a:a + self.x]
                     for a in range(1, len(glyph_str)*(self.x + 1), self.x + 1)]

            for glyph, rect in zip(glyph_str, rects):
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
                    glyphs[glyph]['closed'] = True
                # Remove the intensity information
                points = [p[0] for p in points]
                glyphs[glyph]['points'].append(points)

        return glyphs
