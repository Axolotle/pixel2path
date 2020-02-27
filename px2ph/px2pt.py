from os import listdir, path

from numpy import asarray
from PIL import Image


ext = '.png'


def find_images_in_folder(folder):
    """
    Searches for png files in the provided folder and returns their absolute path.
    """
    return [
        path.join(folder, file) for file in listdir(folder)
        if path.isfile(path.join(folder, file)) and path.splitext(file)[1] == ext
    ]


def get_image_as_nparray(filepath):
    """
    Reads an image file, converts it to greyscale then returns it as a numpy array.
    """
    with Image.open(filepath) as img:
        return asarray(img.convert('LA'))


def split_nparray(nparray, grid, margin=[1, 1]):
    """
    Splits the numpy array into several chunks representing a glyph.
    """
    width = grid[0] + margin[0]
    glyph_quantity = int((nparray.shape[1] - margin[0]) / width)
    return [
        nparray[margin[1]:grid[1] + margin[1], n:n + grid[0]]
        for n in range(1, glyph_quantity * width, width)
    ]


def nparray_to_points(nparray, grid):
    """
    Arranges the pixels in order of brightness and returns an array of
    points positions specifying a path.
    Coordinates origin is top-left.
    """
    points = [
        {'pos': [posx, posy], 'intensity': nparray[posy, posx][0]}
        for posx in range(grid[0])
        for posy in range(grid[1])
        if nparray[posy, posx][1] > 0
    ]

    if len(points) != 0:
        points = sorted(points, key=lambda pt: pt['intensity'])
        return [ pt['pos'] for pt in points ]
    else:
        return None


def px2pt(folder, grid, margin=[1, 1]):
    """
    Reads several images and parse pixel position in absolute position
    for each glyphs.

    Returns an array of glyphs represented by an array of series of points (one
    for each given layer)
    """
    layers_paths = find_images_in_folder(folder)

    glyphs = None
    for i, layer_path in enumerate(layers_paths):
        nparray = get_image_as_nparray(layer_path)
        splitted_nparray = split_nparray(nparray, grid)

        if glyphs is None:
            glyphs = [None for n in splitted_nparray]

        for index, glyph_nparray in enumerate(splitted_nparray):
            glyph_part = nparray_to_points(glyph_nparray, grid)
            if glyph_part is not None:
                if glyphs[index] is None:
                    glyphs[index] = []
                glyphs[index].append(glyph_part)

    return glyphs


if __name__ == '__main__':
    from os.path import abspath
    from argparse import ArgumentParser

    from px2ph.utils.yaml import get_yaml, save_as_yaml


    parser = ArgumentParser(
        prog='px2pt',
        description='read png images and retreive path data'
    )
    parser.add_argument('-c', '--config_file',
                        required=True,
                        help='path to a yaml file containing an input key with pixel informations',
                        type=abspath)
    parser.add_argument('-o', '--output',
                        help='file path where to dump the result as yaml',
                        type=abspath)

    args = parser.parse_args()
    options = get_yaml(args.config_file)
    glyphs = px2pt(**options['input'])

    if args.output is not None:
        save_as_yaml(args.output, glyphs)
    else:
        print(glyphs)
