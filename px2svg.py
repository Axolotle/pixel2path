import cv2
from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path


class Px2path:
    def __init__(self, filename, w=2.25):
        self.w = w
        self.paths = []

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

        # Adjust the position from the given stroke_width
        # Also round it if there's no decimals
        for i, point in enumerate(points):
            position = [p * self.w for p in point]
            points[i] = [round(p) if round(p) == p else p for p in position]

        return points

    def to_line(self, x=0):
        # Generate a path line from given points positions
        a, b = self.points.pop(0)
        d = 'M{},{} L'.format(a + x, b)
        for p in self.points:
            a, b = p
            d += '{},{} '.format(a + x, b)
            
        self.paths.append(Path(d=d + 'Z'))

    def generate_file(self, filename):
        doc = Drawing(filename + '.svg', profile='tiny',
                      size=('200px', '200px'), viewBox='0 0 200 200')
        main = Group(fill='none', stroke='black', stroke_linejoin='round',
                     stroke_width=str(self.w) + 'px', stroke_linecap='round')
        for path in self.paths:
            main.add(path)
        main['transform'] = 'translate({},{})'.format(10, 10)
        doc.add(main)
        doc.save(pretty=True)


drawing = Px2path('0.png')
drawing.to_line()
drawing.generate_file('path')
