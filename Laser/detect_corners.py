import numpy as np
from PIL import Image

# Open the image file
im = Image.open('/home/ian/rpi/Laser/thing.bmp')

# Convert the image to a numpy array
pixels = np.array(im)

# Get the shape of the array
height, width, channels = pixels.shape

# Initialize an empty list to store the corner pixels
corner_pixels = []

# Iterate over the pixels and check if they are corners of the black polygon
for i in range(1, height - 1):
  for j in range(1, width - 1):
    # Check if the current pixel is black
    if pixels[i, j, 0] == 0 and pixels[i, j, 1] == 0 and pixels[i, j, 2] == 0:
      # Check if the current pixel has two black and two white neighbors
      if (pixels[i-1, j, 0] == 0 and pixels[i+1, j, 0] == 0 and pixels[i, j-1, 0] != 0 and pixels[i, j+1, 0] != 0) or (pixels[i-1, j, 0] != 0 and pixels[i+1, j, 0] != 0 and pixels[i, j-1, 0] == 0 and pixels[i, j+1, 0] == 0):
        # If the conditions are met, store the pixel coordinates in the corner_pixels list
        corner_pixels.append((i, j))

# The corner_pixels list now contains the coordinates of the corner pixels of the black polygon
print(corner_pixels)
