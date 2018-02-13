import math
from defcon import Point as DefPoint, Contour as DefContour


class Point(DefPoint):
    """Subclassed Point object that give some tools for point
    manipulation and vectorization.
    """
    def __init__(self, x, y, segmentType=None):
        super().__init__((x,y), segmentType)

    def __repr__(self):
        return "<{} coord: ({}, {}) type: {}>".format(self.__class__.__name__, self.x, self.y, self.segmentType)

    def vector(self, other):
        """Return the vector of two points"""
        return Vector(other.x - self.x, other.y - self.y)

    def relative(self, other):
        """Return the vector of two points as a new point with segmentType"""
        return Point(other.x - self.x, other.y - self.y, self.segmentType)

    def point(self, vector):
        """Return a new point by adding a vector to the actual point"""
        return Point(self.x + vector.x, self.y + vector.y)

    def distance(self, other):
        """Return the length of the vector self->other"""
        return self.vector(other).norm()

    def parallel(self, other, theta, distance):
        vector = distance * self.vector(other).unit_vector().rotate(theta)
        return Point(self + vector)


class Vector():
    __slots__ = ('_x', '_y')

    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __repr__(self):
        return "<{} coord: ({}, {})>".format(self.__class__.__name__, self.x, self.y)

    def _get_x(self):
        return self._x

    def _set_x(self, value):
        self._x = value

    x = property(_get_x, _set_x, doc="The x direction.")

    def _get_y(self):
        return self._y

    def _set_y(self, value):
        self._y = value

    y = property(_get_y, _set_y, doc="The y direction.")

    def norm(self):
        return math.hypot(self.x, self.y)

    def unit_vector(self):
        norm = self.norm()
        return Vector(self.x / norm, self.y / norm)

    def rotate(self, theta):
        """ Rotate vector of angle theta given in deg
        """
        rad = math.radians(theta)
        cos, sin = math.cos(rad), math.sin(rad)
        return Vector(cos * self.x - sin * self.y,
                      sin * self.x + cos * self.y)

    def scalar(self, number):
        return Vector(self.x * number, self.y * number)


class Segment:
    def __init__(self, a, b):
        self.a = a
        self.b = b if isinstance(b, Point) else b.point(a)

    def vector(self):
        """ Return the vector of the line
        """
        return self.a.vector(self.b)

    def intersection(self, other):
        """ Return the intersection point of two lines
        """
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
        vector = self.vector().unit_vector().rotate(theta) * distance
        return Segment(self.a + vector, self.b + vector)


class Contour(DefContour):
    def __init__(self, points):
        super().__init__()
        for point in points:
            self.appendPoint(point)


class Stroke():
    def __init__(self, contours, relative=False):
        self
        self.relative = relative

    def to_relative(self):
        """ Return a new Stroke object with points in relative position
        """
        if self.relative:
            pass
        new_contours = list()
        for contour in self.contours:

            print('aaa',contour)
            for i in range(1, len(contour)):
                contour[i-1].relative(contour[i])
            print('ccc', contour)
            contours.append(contour)
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
                inner += [(a.parallel(b, 180, decal), 'line'),#'curve'),
                          (a.parallel(b, 90, decal), 'line')]#'curve')]
                starter = 1

            for i in range(starter, length - 1):
                z, a, b = points[i-1], points[i], points[i+1]
                outer += self.get_intersection(z, a, b, -90)
                inner += self.get_intersection(z, a, b, 90)

            if closed:
                z, a, b = points[length-2], points[length-1], points[0]
                outer += self.get_intersection(z, a, b, -90)
                inner += self.get_intersection(z, a, b, 90)
                new_layer = [outer, list(reversed(inner))]

            else:
                a, b = points[length-1], points[length-2]
                inner += [(a.parallel(b, -90, decal), 'line'),
                          (a.parallel(b, 180, decal), 'line')]#'curve')]
                outer += [(a.parallel(b, 90, decal), 'line')]#'curve')]
                new_layer = [outer + list(reversed(inner))]

            new_layers.append(new_layer)

        return new_layers

    def get_intersection(self, a, b, c, theta, join=False):
        d1, d2 = Line(a, b).parallel(theta, 0.5), Line(b, c).parallel(theta, 0.5)
        intersection = d1.intersection(d2)
        if intersection is None:
            return [(d1.b, 'line'), (d2.a, 'line')]
        return [(intersection, 'line')]
