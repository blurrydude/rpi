import math
import matplotlib.pyplot as plt

# Number of teeth on the gear
n = int(input("Enter the number of teeth on the gear: "))

# Pitch diameter of the gear (distance between the pitch points of the gear)
p = float(input("Enter the pitch diameter of the gear (in mm): "))

# Pressure angle (angle between the line of action and the common normal)
alpha = float(input("Enter the pressure angle (in degrees): "))

# Module (ratio of the pitch diameter to the number of teeth)
m = p/n

# Base diameter (diameter of the pitch circle of the basic rack)
b = m*math.cos(alpha*math.pi/180)

# Distance from the center of the gear to the base diameter
r = p/2

# Angular resolution (angle between points in the involute curve)
angular_resolution = float(input("Enter the angular resolution (in degrees): "))

# Create a figure and set the limits
fig, ax = plt.subplots()
ax.set_xlim(-p/2-m, p/2+m)
ax.set_ylim(-p/2-m, p/2+m)

# Generate the points for the involute curve
points = []
for i in range(1, int(360/angular_resolution)+1):
  angle = i*angular_resolution
  x = r*math.cos((alpha+angle)*math.pi/180) + r*math.tan(angle*math.pi/180)*math.sin((alpha+angle)*math.pi/180)
  y = r*math.sin((alpha+angle)*math.pi/180) - r*math.tan(angle*math.pi/180)*math.cos((alpha+angle)*math.pi/180)
  points.append([x, y])

# Add the points to the plot
ax.plot([x[0] for x in points], [y[1] for y in points])

# Draw the base circle
base_circle = plt.Circle((0, 0), r, fill=False)
ax.add_artist(base_circle)

# Draw the pitch circle
pitch_circle = plt.Circle((0, 0), p/2, fill=False)
ax.add_artist(pitch_circle)

# Show the plot
plt.show()
