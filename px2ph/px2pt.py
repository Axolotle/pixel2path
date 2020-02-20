from os import listdir
from os.path import isfile, join, splitext

import cv2

from objects import Point, Contour

def px2pt(glyphSet, imagesDir, grid, ext='.png', **kwargs):
    """
    Read several images and parse pixel position in absolute position
    for each glyphs given as argument. points's lists are ordered
    by grey intensity.

    Return a dict of glyphs with series of point and closed information
    """
    x, y = grid

    if imagesDir[-1] != '/':
        # FIXME to remove
        imagesDir = '../' + imagesDir + '/'

    layersPath = [imagesDir + f for f in listdir(imagesDir)
                   if isfile(join(imagesDir, f))
                   and splitext(f)[1] == ext]
    glyphList = list(glyphSet)
    # generate a dict with all glyphs given
    glyphs = {glyph: [] for glyph in glyphList}

    for layer in layersPath:
        # Read & convert the image to greyscale
        img = cv2.imread(layer)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Extract every glyphs from the image
        pixelGlyphs = [img[1:y + 1, a:a + x]
                        for a in range(1, len(glyphList)*(x + 1), x + 1)]

        for glyph, pixelGlyph in zip(glyphList, pixelGlyphs):
            # get the pixel position (x,y) and intensity if it's not white
            pixels = [{'position': Point((posx, posy), segmentType='line'),
                       'intensity': pixelGlyph[posy, posx]}
                      for posx in range(x)
                      for posy in range(y)
                      if pixelGlyph[posy, posx] < 255]
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
