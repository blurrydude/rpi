import matplotlib.pyplot as plt
import numpy as np

def involute_gear(teeth, pitch_diameter, pressure_angle):
  # Calculate gear dimensions
  diameter_at_base = pitch_diameter / 2
  diameter_at_top = diameter_at_base * np.tan(np.radians(pressure_angle))
  tooth_thickness = diameter_at_top - diameter_at_base
  radius_for_compensation = tooth_thickness / 2
  radius_for_involute = diameter_at_base + radius_for_compensation
  angle_between_teeth = 360 / teeth

  # Initialize list of points
  points = []

  # Generate involute curve for one tooth
  theta = np.linspace(0, np.pi / teeth, 100)
  x = radius_for_involute * np.cos(theta) + radius_for_involute
  y = radius_for_involute * np.sin(theta)
  points.extend(list(zip(x, y)))

  # Generate line from top of involute curve to top of tooth
  x = np.linspace(x[-1], diameter_at_top, 100)
  y = np.linspace(y[-1], 0, 100)
  points.extend(list(zip(x, y)))

  # Generate involute curve for opposite side of tooth
  theta = np.linspace(np.pi / teeth, 0, 100)
  x = radius_for_involute * np.cos(theta) + radius_for_involute
  y = -radius_for_involute * np.sin(theta)
  points.extend(list(zip(x, y)))

  # Generate line from bottom of involute curve to bottom of tooth
  x = np.linspace(x[-1], diameter_at_base, 100)
  y = np.linspace(y[-1], 0, 100)
  points.extend(list(zip(x, y)))

  # Rotate and translate points to generate remaining teeth
  for i in range(1, teeth):
    angle = angle_between_teeth * i
    rot_matrix = np.array([[np.cos(np.radians(angle)), -np.sin(np.radians(angle))],
                           [np.sin(np.radians(angle)), np.cos(np.radians(angle))]])
    rotated_points = np.matmul(points, rot_matrix)
    translated_points = rotated_points + np.array([diameter_at_base, 0])
    points.extend(list(translated_points))

  # Plot gear
  x, y = zip(*points)
  plt.plot(x, y)
  plt.axis("equal")
  plt.show()

# Example usage: generate an involute gear with 30 teeth, 90 mm pitch diameter, and 25 degree

involute_gear(30, 90, 25)
