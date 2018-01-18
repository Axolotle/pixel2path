import cv2
from os import listdir
from os.path import isfile, join

from .base_objects import Point


class Px2Pt:
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
        characters = {x: {'closed': False, 'points': []} for x in char_str}

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
