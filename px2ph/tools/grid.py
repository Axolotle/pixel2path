from numpy import ones, uint8
from PIL import Image


def generate_numpy_img(grid, quantity, color, bg_color=[255, 255, 255], inner_grid=[1,1], alt_color=None):
    """ Generate an image as a grid to draw glyphs """
    row = grid[1] + 2
    col = (grid[0] + 1) * quantity + 1
    bg_color = list(reversed(bg_color))
    color = list(reversed(color))
    alt_color = list(reversed(alt_color)) if alt_color is not None else None

    img = ones((row, col, 3), uint8) * 255

    for a in range(1, quantity * (grid[0]+1), grid[0]+1):
        img[1:row - 1, a:a + grid[0]] = color
        if alt_color is not None:
            marg_y = 1 + inner_grid[1]
            marg_x = inner_grid[0]
            img[marg_y:row - marg_y, a + marg_x:a + grid[0] - marg_x] = alt_color

    return img


def generate_file(filename, options):
    """ Generate an image as a grid to draw glyphs and save it as a png file """
    img = Image.fromarray(generate_numpy_img(**options))
    img.save(filename, format='png')


if __name__ == '__main__':
    from os.path import abspath
    from argparse import ArgumentParser

    from yaml import load, CLoader as Loader


    parser = ArgumentParser(
        prog='px2ph.tools.grid',
        description='png font grid generator'
    )
    parser.add_argument('-c', '--config_file',
                        required=True,
                        help='path to a yaml file containing the grid options',
                        type=abspath)

    args = parser.parse_args()

    options = None
    with open(args.config_file, 'r') as yaml_file:
        options = load(yaml_file.read(), Loader=Loader)

    generate_file(options.pop('output'), options)
