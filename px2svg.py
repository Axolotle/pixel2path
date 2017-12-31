import cv2
from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.path import Path

img = cv2.imread('0.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

max_x, max_y = img.shape
w = 2.25

def get_path(points, x=0):
    a, b = points.pop(0)
    d = 'M{},{}L'.format(a + x, b)
    for p in points:
        a, b = p
        d += '{},{} '.format(a + x, b)
    return Path(d=d + 'Z')

def generate_file(path):
    doc = Drawing('path.svg', profile='tiny',
                  size=('200px', '200px'), viewBox='0 0 200 200')
    main = Group(fill='none', stroke='black', stroke_linejoin='round',
                 stroke_width=str(w) + 'px', stroke_linecap='round')
    main.add(path)
    main['transform'] = 'translate({},{})'.format(10, 10)
    doc.add(main)
    doc.save(pretty=True)

px = []
for x in range(max_x):
    for y in range(max_y):
        if img[x, y] < 255:
            px.append([(y, x), img[x, y]])

points = sorted(px, key=lambda info: info[1])
points = [p[0] for p in points]

for i, point in enumerate(points):
    position = [p * w for p in point]
    points[i] = [round(p) if round(p) == p else p for p in position ]

generate_file(get_path(points))
