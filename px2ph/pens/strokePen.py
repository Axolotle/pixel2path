from fontTools.pens.pointPen import PointToSegmentPen

import px2ph.utils.math as math_


class StrokeToShapeSegmentPen(PointToSegmentPen):
    '''
    Convert output of a PointPen to a contour that will be processed by a SegmentPen
    It converts an outline as if it had a stroke width by defining the
    outline that would have surrounded it.

    The given segment_pen will deal with linejoins and linecaps to finish the
    contour. That contour can then be processed by other pens or point pens.
    '''

    def __init__(self, segment_pen, stroke_width, outputImpliedClosingLine=False):
        super().__init__(segment_pen, outputImpliedClosingLine)
        self.offset = stroke_width/2

    def endPath(self):
        """
        Overwriting of the endPath method to first converts the given stroke
        into a shape contour.
        """
        points = self.currentPath
        self.currentPath = None
        assert points is not None
        assert len(points) >= 1
        self._stroke_to_contour(points)

    def _stroke_to_contour(self, points):
        """
        Sort of _flushContour method that will be triggered before the inherited
        _flushContour.
        It transforms a simple stroke contour into a shape contour by drawing its
        parallels and then calls the real endPath() method with 'super()' to
        trigger the basic behavior of a "PointToSegmentPen' pen.
        """
        pointslen = len(points)
        open = points[0][1] == 'move'

        self.beginPath()
        if pointslen == 1:
            self._one_point(points[0])
            super().endPath()
            return

        self.innerPath = []
        for i in range(pointslen):
            if open and (i == 0 or i == pointslen-1):
                self._linecap(points[i], points[i+1 if i == 0 else i-1])
                continue
            p0, p1 = points[i-1], points[i]
            p2 = points[i+1] if i != pointslen-1  else points[0]
            self._linejoin(p0, p1, p2)

        self.innerPath.reverse()
        # merge paths if contour is an open contour else ask to draw two contours
        if open:
            self.currentPath += self.innerPath
        else:
            super().endPath()
            self.beginPath()
            self.currentPath = self.innerPath
        super().endPath()
        self.innerPath = None

    def _linecap(self, p0, p1):
        uv = math_.scale(math_.uvector(p0[0], p1[0]), self.offset)
        for theta, segmentType in [(-90, 'line'), (180, 'line'), (90, 'line')]:
            pt = math_.move(p0[0], math_.rotate(uv, theta))
            self.currentPath.append((pt, segmentType, False, None, {}))

    def _linejoin(self, p0, p1, p2):
        s0a, s0b = math_.double_parallel((p0[0], p1[0]), self.offset)
        s1a, s1b = math_.double_parallel((p1[0], p2[0]), self.offset)
        i0 = math_.intersect(s0a, s1a)
        i1 = math_.intersect(s0b, s1b)
        if i0 is None:
            self.currentPath.append((s0a[1], 'line', False, None, {}))
            self.currentPath.append((s1a[0], 'line', False, None, {}))
        else:
            self.currentPath.append((i0, 'line', False, None, {}))

        if i1 is None:
            self.innerPath.append((s0b[1], 'line', False, None, {}))
            self.innerPath.append((s1b[0], 'line', False, None, {}))
        else:
            self.innerPath.append((i1, 'line', False, None, {}))

    def _one_point(self, pt):
        vs = [(0, -self.offset), (self.offset, 0), (0, self.offset), (-self.offset, 0)]
        for v in vs:
            self.currentPath.append((math_.move(pt[0], v), 'line', False, None, {}))
