import math

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

    def parallel(self, other, theta, distance):
        vector = distance * self.vector(other).unit_vector().rotate(theta)
        return Point(self + vector)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

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

    def intersection(self, other, join=False):
        a, b, c, d = self.a, self.b, other.a, other.b
        i, j = self.vector(), other.vector()

        div = i.x * j.y - i.y * j.x

        # check if i & j are not parallel
        if div != 0:
            # k = (j.x * a.y - j.x * c.y - j.y * a.x + j.y * c.x) / div
            # return Point(a + k * i)
            m = (i.x * a.y - i.x * c.y - i.y * a.x + i.y * c.x) / div
            # check if lines intersect
            if 0 < m < 1 or join:
                return Point(c + m * j)
            else:
                return None

    def parallel(self, theta, distance):
        vector = distance * self.vector().unit_vector().rotate(theta)
        return Line(self.a + vector, self.b + vector)

class Stroke:
    def __init__(self, layers, relative=False):
        self.layers = self.format(layers)
        self.relative = False
        if relative:
            self.layers = self.points_position(relative)

    def format(self, layers):
        """ Format points position to a list of tuples composed of the point's
        coordinates and the segment's type. If the stroke is not closed,
        the first point is a 'move' segment.
        """
        glyph_pts = list()
        for path in layers:
            path_pts = list()
            if not path['closed']:
                path_pts.append((path['points'].pop(0), 'move'))
            path_pts += [(pt, 'line') for pt in path['points']]
            glyph_pts.append(path_pts)
        return glyph_pts

    def points_position(self, relative=False):
        """ Change points to relative or absolute position
        """
        if self.relative is relative:
            pass
        glyph_pts = list()
        for pts in self.layers:
            new_pts = [pts[0]]
            for i in range(1, len(path)):
                # rebuild the tuple by changing points position
                if relative:
                    new_pts.append((pts[i][0] - pts[i-1][0], pts[i][1]))
                else:
                    new_pts.append((new_pts[i-1][0] + pts[i][0], pts[i][1]))
            glyph_pts.append(new_pts)
        self.relative = relative
        return glyph_pts

    # TODO: apply oblique style to points

class Shape(Stroke):
    def __init__(self, layers, width, linejoin='round', linecap='round', angle=None):
        super().__init__(layers, relative=False)
        decal = width / 20
        self.layers = self.vectorize(decal, linejoin, linecap)

    def vectorize(self, decal, linejoin, linecap):
        new_layers = list()
        for layer in self.layers:
            # TODO check direction of stroke to define theta_in and theta_out
            closed = layer[0][1] != 'move'
            length = len(layer)
            starter = 0
            outer, inner = list(), list()
            new_layer = list()
            points = [path[0] for path in layer]

            if not closed:
                a, b = points[0], points[1]
                outer += [(a.parallel(b, -90, decal), 'line')]
                inner += [(a.parallel(b, 180, decal), 'curve'),
                          (a.parallel(b, 90, decal), 'curve')]
                starter = 1

            for i in range(starter, length - 1):
                z, a, b = points[i-1], points[i], points[i+1]
                outer += self.get_intersection(z, a, b, -90)
                inner += self.get_intersection(z, a, b, 90)

            if closed:
                z, a, b = points[length-2], points[length-1], points[0]
                outer += self.get_intersection(z, a, b, -90)
                inner += self.get_intersection(z, a, b, 90)
                new_layer += [outer, list(reversed(inner))]

            else:
                a, b = points[length-1], points[length-2]
                inner += [(a.parallel(b, -90, decal), 'line'),
                          (a.parallel(b, 180, decal), 'curve')]
                outer += [(a.parallel(b, 90, decal), 'curve')]
                new_layer.append(outer + list(reversed(inner)))

            new_layers.append(new_layer)

        return new_layers

    def get_intersection(self, a, b, c, theta, join=False):
        d1, d2 = Line(a, b).parallel(theta, 0.5), Line(b, c).parallel(theta, 0.5)
        intersection = d1.intersection(d2)
        if intersection is None:
            return [(d1.b, 'curve'), (d2.a, 'curve')]
        return [(intersection, 'curve')]
