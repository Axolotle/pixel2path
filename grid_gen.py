from cv2 import imwrite as save_as
from numpy import zeros, uint8

def generate_img_grid(filename, number, grid, color, bg_color=[255] * 3):
    """ Generate an image with a grid to draw characters """
    row = grid[1] + 2
    col = (grid[0] + 1) * number + 1
    bg_color = list(reversed(bg))
    color = list(reversed(color))

    img = zeros((row, col, 3), uint8)
    img[:,:] = color
    img[0,:] = bg
    img[row - 1,:] = bg

    for i in range(col):
        if i % (grid[0] + 1) == 0:
            img[:,i] = bg

    save_as(filename, img)

options = {
    'filename': 'PxPath.png',
    'number': 249,
    'grid': [5, 9],
    'color': [255, 0, 0],
}

generate_img_grid(**options)
