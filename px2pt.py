from os import listdir
from os.path import isfile, join, splitext

import cv2

from base_objects import Point, Contour

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
        pixel_glyphs = [img[1:y + 1, a:a + x]
                        for a in range(1, len(glyph_list)*(x + 1), x + 1)]

        for glyph, pixel_glyph in zip(glyph_list, pixel_glyphs):
            # get the pixel position (x,y) and intensity if it's not white
            pixels = [{'position': Point(pos_x, pos_y, 'line'),
                       'intensity': pixel_glyph[pos_y, pos_x]}
                      for pos_x in range(x)
                      for pos_y in range(y)
                      if pixel_glyph[pos_y, pos_x] < 255]
            if len(pixels) == 0:
                continue
            # Sort the list by intensity
            pixels = sorted(pixels, key=lambda px: px['intensity'])
            # If the light intensity of the first point is 0 (black)
            # then the character's path has to be closed
            if pixels[0]['intensity'] != 0:
                pixels[0]['position']._set_segmentType('move')
            # build the contour
            contour = Contour([px['position'] for px in pixels])
             # = [px['position'] for px in pixels]
            glyphs[glyph].append(contour)

    # if none of the layers gave pixel informations, set glyph to None
    for glyph in glyphs:
        if len(glyphs[glyph]) == 0:
            glyphs[glyph] = None

    return glyphs
