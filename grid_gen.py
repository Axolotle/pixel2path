from cv2 import imwrite as save_as
from numpy import ones, uint8

def generate_img_grid(fp, n, grid, color, bg_color, inner_grid=[1,1], alt_color=None):
    """ Generate an image with a grid to draw characters """
    row = grid[1] + 2
    col = (grid[0] + 1) * n + 1
    bg_color = list(reversed(bg_color))
    color = list(reversed(color))
    alt_color = list(reversed(alt_color)) if alt_color is not None else None

    img = ones((row, col, 3), uint8) * 255

    for a in range(1, n*(grid[0]+1), grid[0]+1):
        img[1:row - 1, a:a + grid[0]] = color
        if alt_color is not None:
            marg_y = 1 + inner_grid[1]
            marg_x = inner_grid[0]
            img[marg_y:row - marg_y, a + marg_x:a + grid[0] - marg_x] = alt_color

    save_as(fp, img)

options = {
    'fp': 'PxPath[5,9].png',
    'n': 10,
    'grid': [5, 9],
    'inner_grid': [1, 2],
    'color': [255, 0, 0],
    'alt_color' : [255, 50, 50],
    'bg_color': [255, 255, 255]
}

generate_img_grid(**options)
