import numpy as np
import matplotlib.pyplot as plt

# Read in G-code file
with open("gcode.txt", "r") as f:
    gcode = f.readlines()

# Initialize bitmap with white background
bitmap = np.ones((500, 500, 3))

# Initialize current position
x = 0
y = 0

# Iterate through G-code commands
for line in gcode:
    # Split line into components
    components = line.split()
    # Check for G0 or G1 command (movement)
    if components[0] == "G0" or components[0] == "G1":
        # Extract X and Y positions
        for component in components:
            if component[0] == "X":
                x = float(component[1:])
            elif component[0] == "Y":
                y = float(component[1:])
        # Draw line on bitmap
        plt.plot([x, x], [y, y], "k-", linewidth=2)

# Display bitmap
plt.imshow(bitmap)
plt.show()
