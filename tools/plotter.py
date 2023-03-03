import matplotlib.pyplot as plt
import numpy as np

# Define the size of the bitmap
width = 800
height = 600

# Create a black background bitmap
bitmap = np.zeros((height, width, 3), dtype=np.uint8)

# Define the array of objects
objects = [
    {'x': [100, 200, 300], 'y': [200, 300, 400], 'color': 'r', 'thickness': 2},
    {'x': [400, 500, 600], 'y': [200, 300, 400], 'color': 'g', 'thickness': 3},
    {'x': [200, 400, 600], 'y': [400, 300, 200], 'color': 'b', 'thickness': 4},
]

# Plot each object onto the bitmap
for obj in objects:
    x = obj['x']
    y = obj['y']
    color = obj['color']
    thickness = obj['thickness']
    plt.plot(x, y, color=color, linewidth=thickness)

# Show the plot and save the bitmap
plt.axis('off')
plt.imshow(bitmap)
plt.savefig('/home/ian/rpi/tools/output.png')