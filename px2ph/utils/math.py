import math


# point/vector operations

def vector(p0, p1):
    return (p1[0] - p0[0], p1[1] - p0[1])


def uvector(v, p1=None):
    """
    Returns the unit vector of a vector.
    If an additional point is given, we assume that arguments are points, then we
    first define the vector of these two points.
    """
    if p1 is not None:
        v = vector(v, p1)
    norm = math.hypot(v[0], v[1])
    return (v[0]/norm, v[1]/norm)


def scale(iterable, scalar):
    """ Returns the scaled value of an iterable. """
    return tuple(value * scalar for value in iterable)


def move(pt, v):
    """ Returns the new position of a point after addtion of a vector. """
    return (pt[0] + v[0], pt[1] + v[1])


def rotate(v, theta):
    """ Rotate vector of angle theta given in degrees"""
    theta = math.radians(theta)
    cos = math.cos(theta)
    sin = math.sin(theta)
    return (cos*v[0] - sin*v[1], sin*v[0] + cos*v[1])

def roundpt(pt):
    return (round(pt[0], 1), round(pt[1], 1))

# Segments operations

def parallel(segment, distance, direction):
    v = rotate(scale(uvector(*segment), distance), 90*direction)
    return ((move(segment[0], v), move(segment[1], v)))

def double_parallel(segment, distance):
    v = scale(uvector(*segment), distance)
    v0 = rotate(v, 90)
    v1 = rotate(v, -90)
    return [
        ((move(segment[0], v0), move(segment[1], v0))),
        ((move(segment[0], v1), move(segment[1], v1))),
    ]

def intersect(s0, s1, force=False):
    a, b, c, d = *s0, *s1
    i, j = vector(a, b), vector(c, d)

    div = i[0] * j[1] - i[1] * j[0]
    # check if i & j are not parallel
    if div != 0:
        # k = (j[0] * a[1] - j[0] * c[1] - j[1] * a[0] + j[1] * c[0]) / div
        # return Point(a + k * i)
        m = (i[0] * a[1] - i[0] * c[1] - i[1] * a[0] + i[1] * c[0]) / div
        # check if lines intersect
        if 0 < m < 1 or force:
            return move(c, scale(j, m))

    return None
