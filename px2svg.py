import cv2
from json import load
from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path


class Px2path:
    def __init__(self, filename, w=2.25):
        self.w = w
        self.paths = []
        self.filename = filename.split('.')[0]

        if filename.find('json') > -1:
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
            elems = load(f)

        points = [[int(e)  for e in elem.split(',')]
                  for elem in elems['0'].split(' ')]

        return points

    def to_line(self, x=0):
        # Generate a path line from given points positions
        def pos(string, x=0):
            return string.format(a * self.w + self.w / 2 + x,
                                 b * self.w + self.w / 2)

        a, b = self.points.pop(0)
        d = pos('M{},{} L')
        for p in self.points:
            a, b = p
            d += pos('{},{} ')

        self.paths.append(Path(d=d + 'Z'))

    def generate_file(self):
        doc = Drawing(self.filename + '.svg', profile='tiny',
                      size=('200px', '200px'), viewBox='0 0 200 200')
        main = Group(fill='none', stroke='black', stroke_linejoin='round',
                     stroke_width=str(self.w) + 'px', stroke_linecap='round')
        for path in self.paths:
            main.add(path)
        main['transform'] = 'translate({},{})'.format(10, 10)
        doc.add(main)
        doc.save(pretty=True)


drawing = Px2path('0.json')
drawing.to_line()
drawing.generate_file()
