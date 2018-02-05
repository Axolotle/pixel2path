from os import listdir
from os.path import isfile, join, splitext

import cv2

from base_objects import Point

def px2pt(glyph_set, images_dir, grid, ext='.png', **kwargs):
    """
    Read several images and parse pixel position in absolute position
    for each glyphs given as argument. points's lists are ordered
    by grey intensity.

    Return a dict of glyphs with series of point and closed information
    """
    x, y = grid

    if images_dir[-1] != '/':
        # FIXME to remove
        images_dir = '../' + images_dir + '/'

    layers_path = [images_dir + f for f in listdir(images_dir)
                   if isfile(join(images_dir, f))
                   and splitext(f)[1] == ext]

    glyph_list = list(glyph_set)

    # generate a dict with all glyphs given
    glyphs = {glyph: [] for glyph in glyph_list}

    for layer in layers_path:
        # Read & convert the image to greyscale
        img = cv2.imread(layer)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Extract every glyphs from the image
        rects = [img[1:y + 1, a:a + x]
                 for a in range(1, len(glyph_list)*(x + 1), x + 1)]

        for glyph, rect in zip(glyph_list, rects):
            glyph_layer = {'closed': False, 'points': []}

            # get the pixel position (x,y) and intensity if it's not white
            points = [[Point(pos_x, pos_y), rect[pos_y, pos_x]]
                      for pos_x in range(x)
                      for pos_y in range(y)
                      if rect[pos_y, pos_x] < 255]


            if len(points) == 0:
                continue
            # Sort the list by intensity
            points = sorted(points, key=lambda info: info[1])
            # If the light intensity of the first point is 0 (black)
            # then the character's path has to be closed
            if points[0][1] == 0:
                glyph_layer['closed'] = True
            # Remove the intensity information
            points = [p[0] for p in points]
            glyph_layer['points'] = points
            glyphs[glyph].append(glyph_layer)

    # if none of the layers gave pixel informations, set glyph to None
    for glyph in glyphs:
        if len(glyphs[glyph]) == 0:
            glyphs[glyph] = None

    return glyphs
