import numpy as np
import matplotlib.pyplot as plt

# Read in G-code file
with open("/home/ian/rpi/Laser/gear.gcode", "r") as f:
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
    # Check for G2 or G3 command (arc)
    elif components[0] == "G2" or components[0] == "G3":
        # Extract center position and radius
        cx = cy = r = 0
        for component in components:
            if component[0] == "I":
                cx = float(component[1:])
            elif component[0] == "J":
                cy = float(component[1:])
            elif component[0] == "R":
                r = float(component[1:])
        # Draw arc on bitmap
        theta1 = np.radians(0)
        theta2 = np.radians(90)
        if components[0] == "G3":
            theta1, theta2 = theta2, theta1
        plt.plot(cx + r*np.cos(np.linspace(theta1, theta2, 100)), 
                 cy + r*np.sin(np.linspace(theta1, theta2, 100)), "k-", linewidth=2)
    # Check for G4 command (curve)
    elif components[0] == "G4":
        # Extract X and Y positions
        cx = cy = 0
        for component in components:
            if component[0] == "X":
                cx = float(component[1:])
            elif component[0] == "Y":
                cy = float(component[1:])
        # Draw curve on bitmap
        plt.plot(np.linspace(x, cx, 100), np.linspace(y, cy, 100), "k-", linewidth=2)
    # Check for G5 command (circle)
    elif components[0] == "G5":
        # Extract center position and radius
        cx = cy = r = 0
        for component in components:
            if component[0] == "I":
                cx = float(component[1:])
            elif component[0] == "J":
                cy = float(component[1:])
            elif component[0] == "R":
                r = float(component[1:])
        # Draw circle on bitmap
        theta = np.linspace(0, 2*np.pi, 100)
        plt.plot(cx + r*np.cos(theta), cy + r*np.sin(theta), "k-", linewidth=2)

# Display bitmap
plt.imshow(bitmap)
plt.show()

