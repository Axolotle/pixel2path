import math

from defcon import Point as DefPoint, Contour as DefContour, Glyph as DefGlyph


class Point(DefPoint):
    """Subclassed Point object that give some tools for point
    manipulation and vectorization.

    Every methods returns a new instance of either Point or Vector object

    TODO(maybe): implements __add__, __sub__
    instead/in addition of displace(), vector()
    """
    def __init__(self, x, y, segmentType=None):
        super().__init__((x,y), segmentType)

    def __repr__(self):
        return "<{} coord: ({}, {}) type: {}>".format(
            self.__class__.__name__, self.x, self.y, self.segmentType)

    def vector(self, other):
        """Return the vector of two points"""
        return Vector(other.x - self.x, other.y - self.y)

    def relative(self, other):
        """Return the vector of two points as a new point with segmentType"""
        return Point(other.x - self.x, other.y - self.y, self.segmentType)

    def distance(self, other):
        """Return the length of the vector self->other"""
        return self.vector(other).norm()

    def scale(self, value):
        return Point(self.x * value, self.y * value, self.segmentType)

    def displace(self, vector, segmentType='line'):
        """Return a new point with coordinates = point + vector
        It differs from the Defcon Point's move method by returning a new
        point instead of updating the instance point position.
        """
        return Point(self.x + vector.x, self.y + vector.y, segmentType)

    def toSvgCommand(self):
        NotImplemented


class Vector():
    __slots__ = ('_x', '_y')

    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __repr__(self):
        return "<{} coord: ({}, {})>".format(
            self.__class__.__name__, self.x, self.y)

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

    def unitVector(self):
        norm = self.norm()
        return Vector(self.x / norm, self.y / norm)

    def rotate(self, theta, rad=False):
        """ Rotate vector of angle theta given in deg or rad"""
        if not rad:
            theta = math.radians(theta)
        cos, sin = math.cos(theta), math.sin(theta)
        return Vector(cos * self.x - sin * self.y,
                      sin * self.x + cos * self.y)

    def combine(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def scale(self, value):
        return Vector(self.x * value, self.y * value)


class Segment:
    """Helper object that give tools for intersections dectection to produce
    stroke vectorization
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b if isinstance(b, Point) else b.displace(a)

    def __repr__(self):
        return "<{} points: ({},{}), ({},{})>".format(
            self.__class__.__name__, self.a.x, self.a.y, self.b.x, self.b.y)

    def vector(self):
        """ Return the vector of the line
        """
        return self.a.vector(self.b)

    def intersection(self, other, force=False):
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
            if 0 < m < 1 or force:
                return [c.displace(j.scale(m))]
            else:
                return [b, c]
        else:
            return None

    def getParallel(self, theta, value):
        vector = self.vector().unitVector().rotate(theta).scale(value)
        return Segment(self.a.displace(vector), self.b.displace(vector))


class Contour(DefContour):
    def __init__(self, points, relative=False):
        super().__init__()
        for point in points:
            self.appendPoint(point)
        self.isRelative = relative

    def scale(self, value):
        return Contour([point.scale(value) for point in self._points])

    def relative(self):
        """ Return a new Contour with points in relative position"""
        assert not self.isRelative
        points = self._points
        newPoints = [points[i-1].relative(points[i]) if i != 0 else points[i]
                      for i in range(len(points))]
        return Contour(newPoints, relative=True)

    def vectorize(self, delta, linejoin, linecap):
        l = len(self._points)
        outer, inner = [], []
        start = 1 if self.open else 0
        end = l - 1 if self.open else l

        if self.open:
            outer += self.getEdgeProjection(0, 1, delta, linecap)
        for i in range(start, end):
            outer += self.getCornerProjection(i, delta, 90, linejoin)
            inner += self.getCornerProjection(i, delta, -90, linejoin)
        if self.open:
            outer += self.getEdgeProjection(l-1, l-2, delta, linecap)
            if len(inner) > 0:
                outer.extend(list(reversed(inner)))
            return [Contour(outer)]
        else:
            return [Contour(outer), Contour(list(reversed(inner)))]

    def getCornerProjection(self, i, delta, theta, linejoin):
        last = 0 if i == len(self._points) - 1 else i + 1
        p1, p2, p3 = self._points[i-1], self._points[i], self._points[last]
        s1 = Segment(p1, p2).getParallel(theta, delta)
        s2 = Segment(p2, p3).getParallel(theta, delta)
        if linejoin == 'bevel':
            return s1.intersection(s2)
        elif linejoin == 'miter':
            return s1.intersection(s2, force=True)
        elif linejoin == 'round':
            intersection = s1.intersection(s2)
            if len(intersection) == 1:
                return intersection
            else:
                c = p2
                p0, p3 = intersection
                a, b, c = p0.vector(c), p3.vector(c), p0.vector(p3)
                theta = 1/2 * ((a.x**2 + a.y**2) + (b.x**2 + b.y**2) - (c.x**2 + c.y**2))
                theta = math.acos(theta / (delta**2))
                alpha = (4/3) * math.tan(theta/4)
                a = a.rotate(math.pi/2, rad=True).scale(alpha)
                b = b.rotate(math.pi/2, rad=True).scale(alpha)
                p1 = p0.displace(a, segmentType=None)
                p2 = p3.displace(Vector(-b.x, -b.y), segmentType=None)
                p1._segmentType = 'curve'
                p3._segmentType = None
                return [p0, p1, p2, p3]
        else:
            raise ValueError('Unknown linejoin value : \'{}\''.format(linecap))

    def getEdgeProjection(self, i, j, delta, linecap):
        p1, p2 = self._points[i], self._points[j]
        uv = p1.vector(p2).unitVector()
        vs = [uv.rotate(-90).scale(delta),
              uv.rotate(180).scale(delta),
              uv.rotate(90).scale(delta)]
        if linecap == 'spike':
            return [p1.displace(v, 'line') for v in vs]
        elif linecap == 'square':
            return [p1.displace(vs[1].combine(vs[0])),
                    p1.displace(vs[1].combine(vs[2]))]
        elif linecap == 'butt':
            return [p1.displace(vs[0]), p1.displace(vs[2])]
        elif linecap == 'round':
            NotImplemented
        else:
            raise ValueError('Unknown linecap value : \'{}\''.format(linecap))

    #TODO add oblique


class Stroke(DefGlyph):
    def __init__(self, contours, relative=False):
        super().__init__()
        for contour in contours:
            self.appendContour(contour)
        self.isRelative = relative

    def relative(self):
        """ Return a new Stroke with points in relative position"""
        assert not self.isRelative
        newContours = [contour.relative() for contour in self._contours]
        return Stroke(newContours, relative=True)

    def scale(self, value):
        scaled = [contour.scale(value) for contour in self._contours]
        return Stroke(scaled)

    def vectorize(self, width, linejoin='miter', linecap='square'):
        vectorized = []
        for contour in self._contours:
            vectorized += contour.vectorize(width/2, linejoin, linecap)
        # TODO add boolean union operation
        return Stroke(vectorized)