import math

def find_point_c_and_lengths(point_a, point_b, angle_abc, angle_bac):
    # Convert angles to radians
    angle_abc = math.radians(angle_abc)
    angle_bac = math.radians(angle_bac)

    # Calculate length of line segment AB
    length_ab = math.dist(point_a, point_b)

    # Calculate length of line segments AC and BC
    length_ac = length_ab * math.sin(angle_bac) / math.sin(math.pi - angle_abc - angle_bac)
    length_bc = length_ab * math.sin(angle_abc) / math.sin(math.pi - angle_abc - angle_bac)

    # Calculate coordinates of point C
    x_c = point_a[0] + length_ac * math.cos(angle_bac)
    y_c = point_a[1] + length_ac * math.sin(angle_bac)
    point_c = (x_c, y_c)

    # Return results
    return point_c, length_ac, length_bc

# # Define the coordinates of points A and B, and the angles ABC and BAC (in radians)
# a = (0, 0)
# b = (12, 0)
# angle_abc = 60
# angle_bac = 45

# # Call the function to calculate the coordinates of point C and the lengths of line segments AC and BC
# c, ac, bc = find_point_c_and_lengths(a, b, angle_abc, angle_bac)

# # Print the result
# print(f"The coordinates of point C are ({c[0]:.2f}, {c[1]:.2f})")
# print(f"The length of line segment AC is {ac:.2f}")
# print(f"The length of line segment BC is {bc:.2f}")


# Given two points A and B and the angles ABC and BAC, 
# the function calculates the coordinates of a third point C 
# and the lengths of the line segments AC and BC.

# First, the function calculates the length of line segment AB using the Euclidean distance formula:

# length_ab = math.dist(point_a, point_b)
# The function then uses the Law of Sines to calculate the lengths of line segments AC and BC:

# length_ac = length_ab * math.sin(angle_bac) / math.sin(math.pi - angle_abc - angle_bac)
# length_bc = length_ab * math.sin(angle_abc) / math.sin(math.pi - angle_abc - angle_bac)
# The Law of Sines states that for any triangle with angles A, B, and C and opposite sides a, b, and c, the following formula holds true:

# a / sin(A) = b / sin(B) = c / sin(C)
# In this case, we know the lengths of sides AB, AC, and BC and the angles ABC and BAC, so we can rearrange the formula to solve for the unknown sides AC and BC.

# Finally, the function uses the coordinates of point A and the length and angle of line segment AC to calculate the coordinates of point C using basic trigonometry:

# x_c = point_a[0] + length_ac * math.cos(angle_bac)
# y_c = point_a[1] + length_ac * math.sin(angle_bac)
# point_c = (x_c, y_c)
# Specifically, we use the fact that the x-coordinate of point C is 
# equal to the x-coordinate of point A plus the length of line segment AC 
# times the cosine of the angle BAC, and the y-coordinate of point C is 
# equal to the y-coordinate of point A plus the length of line segment AC 
# times the sine of the angle BAC. 
# This gives us the final coordinates of point C.

a = (0, 0)
b = (20, 0)
for sa in range(9):
    for sb in range(9):
        angle_a = (sa + 1) * 9
        angle_b = (sb + 1) * 9
        c, ac, bc = find_point_c_and_lengths(a, b, angle_a, angle_b)
        print(f"({c[0]:.2f}, {c[1]:.2f}),")