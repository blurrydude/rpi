import numpy as np
from PIL import Image

# Open the image file
im = Image.open('/home/ian/rpi/Laser/thing.bmp')

# Convert the image to a numpy array
pixels = np.array(im)

# Get the shape of the array
height, width, channels = pixels.shape

# Initialize an empty list to store the edge pixels
edge_pixels = []

# Iterate over the pixels and check if they are part of the edge
for i in range(height):
  for j in range(width):
    # Check if the current pixel is black
    if pixels[i, j, 0] == 0 and pixels[i, j, 1] == 0 and pixels[i, j, 2] == 0:
      # Check if the current pixel has at least one white neighbor
      if (i > 0 and pixels[i-1, j, 0] != 0) or (i < height - 1 and pixels[i+1, j, 0] != 0) or (j > 0 and pixels[i, j-1, 0] != 0) or (j < width - 1 and pixels[i, j+1, 0] != 0):
        # If the conditions are met, store the pixel coordinates in the edge_pixels list
        edge_pixels.append((i, j))

# The edge_pixels list now contains the coordinates of the edge pixels of the black shape
#print(edge_pixels)
# Iterate over the points and output G-code "move to" commands
for point in edge_pixels:
  x, y = point
  print(f"G1 X{x} Y{y}")