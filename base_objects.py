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

    def intersection(self, other):
        a, b, c, d = self.a, self.b, other.a, other.b
        i, j = self.vector(), other.vector()

        div = i.x * j.y - i.y * j.x

        # check if i & j are not parallel
        if div != 0:
            # k = (j.x * a.y - j.x * c.y - j.y * a.x + j.y * c.x) / div
            # return Point(a + k * i)
            m = (i.x * a.y - i.x * c.y - i.y * a.x + i.y * c.x) / div
            # check if lines intersect
            if 0 < m < 1:
                return Point(c + m * j)
            else:
                return None

    def parallel(self, theta, distance):
        vector = distance * self.vector().unit_vector().rotate(theta)
        return Line(self.a + vector, self.b + vector)

class Stroke:
    def __init__(self, layers):
        self.layers = self.format(layers)

    def format(self, layers):
        glyph_pts = list()
        for path in layers:
            path_pts = list()
            if not path['closed']:
                path_pts.append((path['points'].pop(0), 'move'))
            path_pts += [(pt, 'line') for pt in path['points']]
            glyph_pts.append(path_pts)
        return glyph_pts

    def relative_points(self):
        glyph_pts = list()
        for n, path in enumerate(self.layers):
            new_points = [path[0]]
            new_points += [(path[i-1][0] - path[i][0], path[i][1])
                           for i in range(1, len(path))]
            glyph_pts.append(new_points)
        return glyph_pts
