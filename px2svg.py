import cv2

img = cv2.imread('0.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

max_x, max_y = img.shape

px = []
for x in range(max_x):
    print(x)
    for y in range(max_y):
        if img[x, y] < 255:
            px.append([(x, y), img[x, y]])

sort = sorted(px, key=lambda tup: tup[1])
points = [p[0] for p in sort]

print(points)
